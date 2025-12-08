import json
from typing import List
from app.analytics.services import LegacyDataService
from app.database import database, redis_client
from app.config import settings
from app.analytics.prompts import (
    time_prompt,
    schema_prompt,
    internal_system_message,
    legacy_system_message,
)
from app.analytics.schema import (
    ClaudeChatRequest,
    ClaudeChatResponse,
)
from app.exceptions import AnthropicRequestError, ContextRetrievalError
from app.logger import logger

# import asyncio
# from anthropic import APIConnectionError, APITimeoutError, RateLimitError


RELEVANT_TABLES = {
    "patients",
    "patient_photos",
    "assessments",
    "medications",
    "dispensing",
    "notes",
    "activities",
    "interactions",
    "attachments",
    "reference_options",
    "reference_templates",
}


class RagService:
    # -- Schema
    @staticmethod
    async def store_schema(schema: str):
        redis = redis_client.get_client()
        await redis.set("postgres:schema", schema)

    @staticmethod
    async def get_schema() -> str:
        redis = redis_client.get_client()
        result = await redis.get("postgres:schema")

        if result:
            return result

        query = """
        SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        schema = {}
        for table, column, dtype in rows:
            if table in RELEVANT_TABLES:
                schema.setdefault(table, []).append(f"{column} ({dtype})")

        schema_text = "\n".join(
            f"{table}: {', '.join(cols)}" for table, cols in schema.items()
        )
        await RagService.store_schema(schema_text)

        return schema_text

    # -- Chat history
    @staticmethod
    async def update_chat_sesssion(
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
    async def get_chat_history(user_id: str) -> List[dict]:
        client = redis_client.get_client()

        key = f"{user_id}:chatSession"
        raw_msgs = await client.lrange(key, 0, -1)
        clean_msgs = [json.loads(m) for m in raw_msgs] if raw_msgs else []
        return clean_msgs

    @staticmethod
    async def clear_chat_history(user_id: int):
        client = redis_client.get_client()
        key = f"{user_id}:chatSession"
        await client.delete(key)

    #  -- Retrieve internal context
    @staticmethod
    async def generate_query(schema: str, request: ClaudeChatRequest) -> str:
        try:
            message = await settings.anthropic_client.messages.create(
                model=settings.anthropic_model,
                max_tokens=settings.anthropic_max_tokens,
                system=[
                    {
                        "type": "text",
                        "text": schema_prompt(schema),
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": time_prompt(request.datetime),
                    },
                ],
                messages=[
                    {
                        "role": "user",
                        "content": f"Question: {request.message}",
                    },
                ],
            )

            response_text = message.content[0].text
            return response_text
        except Exception as e:
            logger.error(f"Error in query generation: {type(e).__name__}: {e}")
            raise AnthropicRequestError(
                "I had an issue generating the query for your request. Please try again in a moment.",
            )

    @staticmethod
    async def retrieve_context(query: str) -> list:
        try:
            if not query.lower().strip().startswith("select"):
                raise ValueError("Only SELECT queries are allowed")

            async with database.get_connection() as conn:
                rows = await conn.fetch(query)
                results = [dict(row) for row in rows]

            return results
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            raise ContextRetrievalError(
                "I had an issue looking up the data needed to processing your request. Please try again in a moment."
            )

    # -- Internal data
    @staticmethod
    async def prompt_llm_internal(
        context: str,
        user_msg: str,
        user_id: str,
        session_id: str = "99",
    ):
        history = await RagService.get_chat_history(user_id)
        history.append({"role": "user", "content": user_msg})

        try:
            message = await settings.anthropic_client.messages.create(
                model=settings.anthropic_model,
                max_tokens=settings.anthropic_max_tokens,
                system=[
                    {
                        "type": "text",
                        "text": internal_system_message(),
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": context,
                    },
                ],
                messages=history,
            )

            response_text = message.content[0].text

            await RagService.update_chat_sesssion(user_id, "user", user_msg)
            await RagService.update_chat_sesssion(
                user_id, "assistant", response_text
            )

            return ClaudeChatResponse(
                response=response_text,
                session_id=session_id,
            )
        except Exception as e:
            logger.error(f"Error retrieving answer: {e}")
            raise AnthropicRequestError(
                "I had an issue while generating your answer. Please try again in a moment."
            )

    @staticmethod
    async def claude_chat_internal(
        request: ClaudeChatRequest,
        user_id: int,
    ) -> ClaudeChatResponse:
        try:
            schema = await RagService.get_schema()
            query = await RagService.generate_query(schema, request)
            logger.info(f"Query: {query}")
            context = await RagService.retrieve_context(query)
            logger.info(f"Context: {context}")

            return await RagService.prompt_llm_internal(
                str(context),
                request.message,
                str(user_id),
                request.session_id or "99",
            )
        except AnthropicRequestError:
            raise
        except ContextRetrievalError:
            raise
        except Exception as e:
            raise Exception(f"Chat error {e}")

    # -- Upload file
    @staticmethod
    async def prompt_llm_file(
        context: str,
        user_msg: str,
        user_id: str,
        session_id: str = "99",
    ):
        history = await RagService.get_chat_history(user_id)
        history.append({"role": "user", "content": user_msg})

        try:
            message = await settings.anthropic_client.messages.create(
                model=settings.anthropic_model,
                max_tokens=settings.anthropic_max_tokens,
                system=[
                    {
                        "type": "text",
                        "text": legacy_system_message(),
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": context,
                    },
                ],
                messages=history,
            )

            response_text = message.content[0].text

            await RagService.update_chat_sesssion(user_id, "user", user_msg)
            await RagService.update_chat_sesssion(
                user_id, "assistant", response_text
            )

            return ClaudeChatResponse(
                response=response_text,
                session_id=session_id,
            )
        except Exception as e:
            logger.error(f"Error retrieving answer: {e}")
            raise AnthropicRequestError(
                "I had an issue while generating your answer. Please try again in a moment."
            )

    @staticmethod
    async def claude_chat_file(
        request: ClaudeChatRequest,
        user_id: int,
    ) -> ClaudeChatResponse:
        raw_data = await LegacyDataService.get_legacy_data_by_userid(user_id)

        if not raw_data:
            raise Exception(
                "No legacy data found. Please upload an Excel file first."
            )

        try:
            context = await LegacyDataService.generate_context(raw_data)
            return await RagService.prompt_llm_file(
                context,
                request.message,
                str(user_id),
                request.session_id or "99",
            )
        except Exception:
            raise Exception(
                "No legacy data found. Please upload an Excel file first."
            )


# --- With retry
# #  -- Retrieve internal context
# @staticmethod
# async def generate_query(schema: str, request: ClaudeChatRequest) -> str:
#     max_retries = 3
#     retry_delay = 1  # Start with 1 second
#
#     for attempt in range(max_retries):
#         try:
#             message = await settings.anthropic_client.messages.create(
#                 model=settings.anthropic_model,
#                 max_tokens=settings.anthropic_max_tokens,
#                 system=[
#                     {
#                         "type": "text",
#                         "text": schema_prompt(schema),
#                         "cache_control": {"type": "ephemeral"},
#                     },
#                     {
#                         "type": "text",
#                         "text": time_prompt(request.datetime),
#                     },
#                 ],
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": f"Question: {request.message}",
#                     },
#                 ],
#             )
#
#             response_text = message.content[0].text
#             return response_text
#         except (APIConnectionError, APITimeoutError, RateLimitError) as e:
#             if attempt == max_retries - 1:  # Last attempt
#                 logger.error(f"Failed after {max_retries} attempts: {e}")
#                 raise AnthropicRequestError(
#                     "I had an issue generating the query for your request. Please try again in a moment.",
#                 )
#
#             logger.warning(
#                 f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s..."
#             )
#             await asyncio.sleep(retry_delay)
#             retry_delay *= 2  # Exponential backoff: 1s, 2s, 4s
#
#         except Exception as e:
#             logger.error(
#                 f"Non-retryable error in query generation: {type(e).__name__}: {e}"
#             )
#             raise AnthropicRequestError(
#                 "I had an issue generating the query for your request. Please try again in a moment.",
#             )
