# tests/unit/test_rag_service.py
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime
from types import SimpleNamespace
from app.analytics.rag import RagService
from app.analytics.schema import ClaudeChatResponse
from app.exceptions import AnthropicRequestError


class TestRagServiceChatHistory(IsolatedAsyncioTestCase):
    """Tests for chat history management"""

    async def test_update_chat_appends_message(self):
        """Should append message to Redis"""
        user_id = "123"
        role = "user"
        content = "Hello Claude"

        mock_client = MagicMock()
        mock_client.rpush = AsyncMock()
        mock_client.ltrim = AsyncMock()
        mock_client.expire = AsyncMock()

        with patch('app.analytics.rag.redis_client.get_client', return_value=mock_client):
            await RagService.update_chat(user_id, role, content)
            
            mock_client.rpush.assert_called_once()
            args = mock_client.rpush.call_args[0]
            self.assertEqual(args[0], f"{user_id}:chatSession")
            
            # Verify message structure
            stored_msg = json.loads(args[1])
            self.assertEqual(stored_msg["role"], role)
            self.assertEqual(stored_msg["content"], content)

    async def test_update_chat_trims_history(self):
        """Should trim to max length"""
        mock_client = MagicMock()
        mock_client.rpush = AsyncMock()
        mock_client.ltrim = AsyncMock()
        mock_client.expire = AsyncMock()

        with patch('app.analytics.rag.redis_client.get_client', return_value=mock_client), \
             patch('app.analytics.rag.settings.max_chat_length', 20):
            
            await RagService.update_chat("123", "user", "test")
            
            mock_client.ltrim.assert_called_once()
            args = mock_client.ltrim.call_args[0]
            self.assertEqual(args[1], -20)  # Keep last 20 messages
            self.assertEqual(args[2], -1)

    async def test_update_chat_sets_expiry(self):
        """Should set TTL on chat history"""
        mock_client = MagicMock()
        mock_client.rpush = AsyncMock()
        mock_client.ltrim = AsyncMock()
        mock_client.expire = AsyncMock()

        with patch('app.analytics.rag.redis_client.get_client', return_value=mock_client), \
             patch('app.analytics.rag.settings.chat_history_ttl', 3600):
            
            await RagService.update_chat("123", "user", "test")
            
            mock_client.expire.assert_called_once()
            args = mock_client.expire.call_args[0]
            self.assertEqual(args[1], 3600)

    async def test_get_chat_returns_messages(self):
        """Should retrieve and parse chat history"""
        user_id = "123"
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        mock_client = MagicMock()
        mock_client.lrange = AsyncMock(return_value=[
            json.dumps(msg) for msg in messages
        ])

        with patch('app.analytics.rag.redis_client.get_client', return_value=mock_client):
            result = await RagService.get_chat(user_id)
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["role"], "user")
            self.assertEqual(result[1]["role"], "assistant")

    async def test_get_chat_empty_history(self):
        """Should return empty list for no history"""
        mock_client = MagicMock()
        mock_client.lrange = AsyncMock(return_value=[])

        with patch('app.analytics.rag.redis_client.get_client', return_value=mock_client):
            result = await RagService.get_chat("123")
            
            self.assertEqual(result, [])

    async def test_clear_chat_deletes_key(self):
        """Should delete chat history key"""
        user_id = 123
        
        mock_client = MagicMock()
        mock_client.delete = AsyncMock()

        with patch('app.analytics.rag.redis_client.get_client', return_value=mock_client):
            await RagService.clear_chat(user_id)
            
            mock_client.delete.assert_called_once_with(f"{user_id}:chatSession")


class TestRagServiceToolHandlers(IsolatedAsyncioTestCase):
    """Tests for database query handlers"""

    async def test_handle_query_postgres_rejects_non_select(self):
        """Should reject non-SELECT queries"""
        query = "DELETE FROM patients WHERE id = 1"

        result = await RagService.handle_query_postgres(query)
        parsed = json.loads(result)

        self.assertIn("Only SELECT queries", parsed["error"])

    async def test_handle_query_postgres_database_error(self):
        """Should raise ContextRetrievalError on DB error"""
        query = "SELECT * FROM nonexistent_table"

        mock_conn = MagicMock()
        mock_conn.fetch = AsyncMock(side_effect=Exception("Table not found"))

        with patch('app.analytics.rag.database.get_connection') as mock_db:
            mock_db.return_value.__aenter__.return_value = mock_conn
            
            result = await RagService.handle_query_postgres(query)
            parsed = json.loads(result)
            self.assertIn("Table not found", parsed['error'])

    async def test_handle_query_mongodb_valid_pipeline(self):
        user_id = "123"
        pipeline = [{"$group": {"_id": "$city", "count": {"$sum": 1}}}]
        
        mock_results = [
            {"_id": "Toronto", "count": 50},
            {"_id": "Mississauga", "count": 30}
        ]

        # Mock the collection and cursor
        mock_collection = MagicMock()
        mock_collection.count_documents = AsyncMock(return_value=100)
        
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_results)
        mock_collection.aggregate = MagicMock(return_value=mock_cursor)

        # Mock the database returned by get_db()
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection  # db["legacy_data"] => mock_collection

        # Patch mongo_client.get_db to return our mock_db
        with patch("app.analytics.rag.mongo_client.get_db", return_value=mock_db):
            result = await RagService.handle_query_mongodb(user_id, pipeline)
            
            parsed = json.loads(result)
            self.assertEqual(len(parsed), 2)
            self.assertEqual(parsed[0]["_id"], "Toronto")


    async def test_handle_query_mongodb_no_data(self):
        user_id = "123"
        pipeline = [{"$match": {}}]

        mock_collection = MagicMock()
        mock_collection.count_documents = AsyncMock(return_value=0)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch("app.analytics.rag.mongo_client.get_db", return_value=mock_db):
            result = await RagService.handle_query_mongodb(user_id, pipeline)
            
            parsed = json.loads(result)
            self.assertIn("error", parsed)
            self.assertIn("No legacy data found", parsed["error"])


    async def test_handle_query_mongodb_injects_user_filter(self):
        user_id = "123"
        pipeline = [{"$group": {"_id": "$city"}}]

        mock_collection = MagicMock()
        mock_collection.count_documents = AsyncMock(return_value=10)
        
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_collection.aggregate = MagicMock(return_value=mock_cursor)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch("app.analytics.rag.mongo_client.get_db", return_value=mock_db):
            await RagService.handle_query_mongodb(user_id, pipeline)
            
            # Verify user filter was injected
            call_args = mock_collection.aggregate.call_args[0][0]
            self.assertEqual(call_args[0], {"$match": {"user_id": 123}})

class TestRagServicePromptClaude(IsolatedAsyncioTestCase):
    """Tests for main Claude prompting logic"""

    def setUp(self):
        self.user_id = "123"
        self.user_msg = "How many patients?"
        self.user_date = datetime.now().isoformat()

    async def test_prompt_claude_simple_response(self):
        """Should handle simple text response from Claude"""
        mock_response = MagicMock()
        mock_response.stop_reason = "end_turn"
        mock_response.content = [
            MagicMock(type="text", text="There are 42 patients", hasattr=lambda x: x == "text")
        ]

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch('app.analytics.rag.settings.anthropic_client', mock_client), \
             patch('app.analytics.rag.RagService.get_chat', new_callable=AsyncMock, return_value=[]), \
             patch('app.analytics.rag.RagService.update_chat', new_callable=AsyncMock):
            
            result = await RagService.prompt_claude(
                self.user_id, self.user_msg, self.user_date, False
            )
            
            self.assertIsInstance(result, ClaudeChatResponse)
            self.assertEqual(result.response, "There are 42 patients")

    async def test_prompt_claude_with_tool_use_postgres(self):
        """Should handle tool use flow with Postgres"""
        # First response: tool use
        tool_response = MagicMock()
        tool_response.stop_reason = "tool_use"
        tool_response.content = [
            SimpleNamespace(
                type="tool_use",
                name="query_postgres",
                id="tool_123",
                input={"sql": "SELECT COUNT(*) FROM patients"}
            )
        ]
        
        # Second response: final answer
        final_response = MagicMock()
        final_response.stop_reason = "end_turn"
        final_response.content = [
            MagicMock(type="text", text="Found 42 patients", hasattr=lambda x: x == "text")
        ]

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(side_effect=[tool_response, final_response])

        with patch('app.analytics.rag.settings.anthropic_client', mock_client), \
             patch('app.analytics.rag.RagService.get_chat', new_callable=AsyncMock, return_value=[]), \
             patch('app.analytics.rag.RagService.update_chat', new_callable=AsyncMock), \
             patch('app.analytics.rag.RagService.handle_query_postgres',
                   new_callable=AsyncMock, return_value='[{"count": 42}]'):
            
            print("testing ")
            result = await RagService.prompt_claude(
                self.user_id, self.user_msg, self.user_date, False
            )
            
            self.assertEqual(result.response, "Found 42 patients")
            self.assertEqual(mock_client.messages.create.call_count, 2)

    async def test_prompt_claude_with_tool_use_mongodb(self):
        """Should handle tool use flow with MongoDB"""
        tool_response = MagicMock()
        tool_response.stop_reason = "tool_use"
        tool_response.content = [
            MagicMock(
                type="tool_use",
                name="query_mongo",
                id="tool_456",
                input={"pipeline": [{"$match": {}}]}
            )
        ]
        
        final_response = MagicMock()
        final_response.stop_reason = "end_turn"
        final_response.content = [
            MagicMock(type="text", text="Found data", hasattr=lambda x: x == "text")
        ]

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(side_effect=[tool_response, final_response])

        with patch('app.analytics.rag.settings.anthropic_client', mock_client), \
             patch('app.analytics.rag.RagService.get_chat', new_callable=AsyncMock, return_value=[]), \
             patch('app.analytics.rag.RagService.update_chat', new_callable=AsyncMock), \
             patch('app.analytics.rag.RagService.handle_query_mongodb',
                   new_callable=AsyncMock, return_value='[{"count": 10}]'):
            
            result = await RagService.prompt_claude(
                self.user_id, self.user_msg, self.user_date, True
            )
            
            self.assertIsNotNone(result)

    async def test_prompt_claude_uses_legacy_instruction(self):
        """Should include correct data source instruction"""
        mock_response = MagicMock()
        mock_response.stop_reason = "end_turn"
        mock_response.content = [MagicMock(type="text", text="Result", hasattr=lambda x: x == "text")]

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch('app.analytics.rag.settings.anthropic_client', mock_client), \
             patch('app.analytics.rag.RagService.get_chat', new_callable=AsyncMock, return_value=[]), \
             patch('app.analytics.rag.RagService.update_chat', new_callable=AsyncMock) as mock_update:
            
            # Test with legacy_data=True
            await RagService.prompt_claude(
                self.user_id, self.user_msg, self.user_date, True
            )
            
            # Check first call to update_chat (user message)
            first_call_content = mock_update.call_args_list[0][0][2]
            self.assertIn("query_mongo", first_call_content)

    async def test_prompt_claude_anthropic_error(self):
        """Should raise AnthropicRequestError on API failure"""
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))

        with patch('app.analytics.rag.settings.anthropic_client', mock_client), \
             patch('app.analytics.rag.RagService.get_chat', new_callable=AsyncMock, return_value=[]), \
             patch('app.analytics.rag.RagService.update_chat', new_callable=AsyncMock):
            
            with self.assertRaises(AnthropicRequestError) as context:
                await RagService.prompt_claude(
                    self.user_id, self.user_msg, self.user_date, False
                )
            
            self.assertIn("issue while generating", str(context.exception))

    async def test_prompt_claude_maintains_history(self):
        """Should include existing chat history in request"""
        existing_history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"}
        ]

        mock_response = MagicMock()
        mock_response.stop_reason = "end_turn"
        mock_response.content = [MagicMock(type="text", text="Response", hasattr=lambda x: x == "text")]

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch('app.analytics.rag.settings.anthropic_client', mock_client), \
             patch('app.analytics.rag.RagService.get_chat',
                   new_callable=AsyncMock, return_value=existing_history), \
             patch('app.analytics.rag.RagService.update_chat', new_callable=AsyncMock):
            
            await RagService.prompt_claude(
                self.user_id, self.user_msg, self.user_date, False
            )
            
            # Verify history was included
            call_args = mock_client.messages.create.call_args
            messages = call_args[1]["messages"]
            self.assertGreaterEqual(len(messages), 3)  # 2 history + 1 new

