import json
from typing import List
from app.database import database, redis_client
from app.config import settings
from app.analytics.schema import ClaudeChatResponse
from app.analytics.tools import QUERY_MONGODB, QUERY_POSTGRES
from app.database import mongo_client
from app.exceptions import AnthropicRequestError
from app.logger import logger

class RagService:
    # -- Chat history
    @staticmethod
    async def update_chat(
        user_id: str,
        role: str,
        content: str,
    ):
        client = redis_client.get_client()
        key = f"{user_id}:chatSession"
        message = {"role": role, "content": content}

        # Append to end
        await client.rpush(key, json.dumps(message))

        # Cut to no more than 20 most recent
        await client.ltrim(key, -settings.max_chat_length, -1)

        # Updated to expire if unused
        await client.expire(key, settings.chat_history_ttl)

    @staticmethod
    async def get_chat(user_id: str) -> List[dict]:
        client = redis_client.get_client()

        key = f"{user_id}:chatSession"
        raw_msgs = await client.lrange(key, 0, -1)
        clean_msgs = [json.loads(m) for m in raw_msgs] if raw_msgs else []
        return clean_msgs

    @staticmethod
    async def clear_chat(user_id: int):
        client = redis_client.get_client()
        key = f"{user_id}:chatSession"
        await client.delete(key)

    #  -- Use tools
    @staticmethod
    async def handle_query_postgres(query: str) -> str:
        try:
            if not query.lower().strip().startswith("select"):
                return json.dumps({
                    "success": False,
                    "error": "Only SELECT queries are allowed",
                    "hint": "Make sure your query starts with SELECT"
                })

            async with database.get_connection() as conn:
                rows = await conn.fetch(query)
                results = [dict(row) for row in rows]

            return json.dumps(results, default=str) 
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "hint": "Check SQL syntax." 
            })

    @staticmethod
    async def handle_query_mongodb(user_id: str, pipeline: list) -> str:
        try:
            # Check if user has any data
            db = mongo_client.get_db()
            collection = db["legacy_data"] 
            count = await collection.count_documents({"user_id": int(user_id)})
            
            if count == 0:
                return json.dumps({"error": "No legacy data found. Please upload a file first."})
            
            # Inject user_id filter
            user_filter = {"$match": {"user_id": int(user_id)}}
            full_pipeline = [user_filter] + pipeline
            
            results = await collection.aggregate(full_pipeline).to_list(length=None)
            
            return json.dumps(results, default=str)
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return json.dumps({"error": str(e)})
    
    # -- claude 
    @staticmethod
    async def prompt_claude(
        user_id: str,
        user_msg: str,
        user_date: str,
        is_legacy: bool,
        session_id: str = "99"
    ):
        history = await RagService.get_chat(user_id)
        
        data_source_instruction = "Use query_mongo tool for legacy uploaded data." if is_legacy else "Use query_postgres tool for internal database."
        user_msg_with_time = f"User Datetime: {user_date}\n\n{data_source_instruction}\n\nQuestion: {user_msg}"
        history.append({"role": "user", "content": user_msg_with_time})
        await RagService.update_chat(user_id, "user", user_msg_with_time)

        try:
            response = await settings.anthropic_client.messages.create(
                model=settings.anthropic_model,
                max_tokens=settings.anthropic_max_tokens,
                tools=[QUERY_POSTGRES, QUERY_MONGODB],
                system=settings.system_prompt,
                messages=history,
            )

            while response.stop_reason == "tool_use":
                tool_use = next(block for block in response.content if block.type == "tool_use")
                
                if tool_use.name == "query_postgres":
                    query = tool_use.input["sql"]
                    db_results = await RagService.handle_query_postgres(query)
                else: 
                    query = tool_use.input["pipeline"]
                    db_results = await RagService.handle_query_mongodb(user_id, query)

                await RagService.update_chat(user_id, "assistant", f"Query: {query}")
                await RagService.update_chat(user_id, "user", db_results)

                history.append({"role": "assistant", "content": response.content})
                history.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": db_results
                    }]
                })
                
                # Get Claude's next response
                response = await settings.anthropic_client.messages.create(
                    model=settings.anthropic_model,
                    max_tokens=settings.anthropic_max_tokens,
                    tools=[QUERY_POSTGRES, QUERY_MONGODB],
                    system=settings.system_prompt,
                    messages=history,
                )                    

            # Extract final answer
            response_text = next(
                block.text for block in response.content 
                if hasattr(block, "text")
            )

            await RagService.update_chat(user_id, "assistant", response_text)
            return ClaudeChatResponse(response=response_text,session_id=session_id)
        except Exception as e:
            logger.error(f"Error retrieving answer: {e}")
            raise AnthropicRequestError(
                "I had an issue while generating your answer. Please try again in a moment."
            )

