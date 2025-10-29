from app.analytics.services import LegacyDataService
from app.database import database
from app.config import settings
from app.analytics.prompts import (
    internal_system_message,
    legacy_system_message,
)
from app.analytics.schema import (
    ClaudeChatRequest,
    ClaudeChatResponse,
)

RELEVANT_TABLES = {
    "patients",
    "tests",
    "medications",
    "dispensing",
    "notes",
    "activities",
    "interactions",
    "attachments",
}


class RagService:
    @staticmethod
    async def get_schema() -> dict:
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

        return schema

    @staticmethod
    async def generate_query(schema: dict, question: str) -> str:
        schema_text = "\n".join(
            f"{table}: {', '.join(cols)}" for table, cols in schema.items()
        )

        system_prompt = f"""
        You are a SQL expert helping analyze medical CRM data.

        Rules for SQL generation:
        1. Generate valid PostgreSQL SELECT queries ONLY.
        2. Always start your response with the keyword SELECT.
        3. Do NOT include any Markdown code fences (no ```sql or ```).
        4. Use JOINs based on the patient_id foreign key when necessary.
        5. Only include tables and columns relevant for analysis.

        Schema:
        {schema_text}
        """

        user_prompt = f"Question: {question}\nSQL:"

        message = await settings.anthropic_client.messages.create(
            model=settings.anthropic_model,
            max_tokens=settings.anthropic_max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
        )

        response_text = message.content[0].text

        return response_text

    @staticmethod
    async def retrieve_context(query: str) -> list:
        if not query.lower().strip().startswith("select"):
            raise ValueError("Only SELECT queries are allowed")

        async with database.get_connection() as conn:
            rows = await conn.fetch(query)
            cols = rows[0].keys() if rows else []
            results = [dict(row) for row in rows]

        results = [dict(zip(cols, row)) for row in rows]
        return results

    @staticmethod
    async def prompt_llm(
        system_msg: str,
        user_msg: str,
        session_id: str = "99",
    ):
        try:
            message = await settings.anthropic_client.messages.create(
                model=settings.anthropic_model,
                max_tokens=settings.anthropic_max_tokens,
                system=system_msg,
                messages=[
                    {"role": "user", "content": user_msg},
                ],
            )

            response_text = message.content[0].text

            return ClaudeChatResponse(
                response=response_text,
                session_id=session_id,
            )
        except Exception:
            raise Exception(
                "No legacy data found. Please upload an Excel file first."
            )

    @staticmethod
    async def claude_chat_internal(
        request: ClaudeChatRequest,
    ) -> ClaudeChatResponse:
        try:
            schema = await RagService.get_schema()
            query = await RagService.generate_query(schema, request.message)
            context = await RagService.retrieve_context(query)
            system_msg = internal_system_message(str(context))

            return await RagService.prompt_llm(
                system_msg,
                request.message,
                request.session_id or "99",
            )
        except Exception:
            raise Exception(
                "No legacy data found. Please upload an Excel file first."
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
            system_msg = legacy_system_message(context)
            return await RagService.prompt_llm(
                system_msg,
                request.message,
                request.session_id or "99",
            )
        except Exception:
            raise Exception(
                "No legacy data found. Please upload an Excel file first."
            )
