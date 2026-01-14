from app.database import database
from app.analytics.prompts import legacy_data_prompt, postgres_schema_prompt, system_message, time_prompt
import io
import pandas as pd
from fastapi import UploadFile


async def read_legacy_data_file(file: UploadFile) -> pd.DataFrame:
    # Read file content
    content = await file.read()

    # Parse Excel/CSV file
    if file.filename.endswith(".csv"):
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    else:
        df = pd.read_excel(io.BytesIO(content))

    df = df.fillna("")
    df.columns = df.columns.str.strip()

    return df 


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

async def get_database_schema() -> str:
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

    return schema_text

def get_system_prompt(schema:str ) -> list:
    return [
            {
                "type": "text",
                "text": system_message(),
                "cache_control": {"type": "ephemeral"}
            },
            {
                "type": "text",
                "text": postgres_schema_prompt(schema),
                "cache_control": {"type": "ephemeral"}
            },
                   {
                "type": "text",
                "text": legacy_data_prompt(),
                "cache_control": {"type": "ephemeral"}
            },
            {
                "type": "text",
                "text": time_prompt(),
                "cache_control": {"type": "ephemeral"}
            }
        ]


