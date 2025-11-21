from typing import List, Optional
from app.database import database
from app.references.schemas import (
    ReferenceOption,
    ReferenceOptionUpdate,
    ReferenceTemplate,
    ReferenceTemplateUpdate,
)


class ReferenceOptionService:
    @staticmethod
    async def check_exists(name: str, option_type: str) -> bool:
        query = """
            SELECT id 
            FROM reference_options 
            WHERE 
                name=$1 AND 
                type=$2; 
            """

        async with database.get_connection() as conn:
            row = await conn.fetch(query, name, option_type)

            return True if row else False

    @staticmethod
    async def create_option(data: ReferenceOption) -> Optional[int]:
        query = """
        INSERT INTO reference_options (name, type, is_frequent, is_default)
        VALUES ($1, $2, $3, $4)
        RETURNING id;
        """

        # Insert referral site and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                data.name,
                data.type,
                data.is_frequent,
                data.is_default,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def get_options(option_type: str) -> List[ReferenceOption]:
        query = """
        SELECT * 
        FROM reference_options 
        WHERE type=$1;
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query, option_type)

        result = []
        if rows:
            for row in rows:
                result.append(ReferenceOption(**dict(row)))

        return result

    @staticmethod
    async def delete_option(name: str, option_type: str) -> bool:
        query = """
            DELETE FROM reference_options 
            WHERE name=$1
            AND type=$2
            RETURNING id;
            """

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, name, option_type)
            return bool(row)

    @staticmethod
    async def delete_option_by_id(id: int) -> bool:
        query = """
            DELETE FROM reference_options
            WHERE id=$1 
            RETURNING id;
            """

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_option(id: int, updates: ReferenceOptionUpdate) -> bool:
        update = updates.model_dump(exclude_unset=True)

        if not update:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(update.keys())
        ]
        query = f"UPDATE reference_options SET {', '.join(set_clauses)} WHERE id = ${len(update)+1} RETURNING id;"
        values = list(update.values()) + [id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)


class ReferenceTemplateService:
    @staticmethod
    async def check_exists(name: str, template_type: str) -> bool:
        query = """
            SELECT id 
            FROM reference_templates 
            WHERE 
                name=$1 AND 
                type=$2; 
            """

        async with database.get_connection() as conn:
            row = await conn.fetch(query, name, template_type)

            return True if row else False

    @staticmethod
    async def create_template(data: ReferenceTemplate) -> Optional[int]:
        query = """
        INSERT INTO reference_templates (name, type, content, is_default)
        VALUES ($1, $2, $3, $4)
        RETURNING id;
        """

        # Insert referral site and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                data.name,
                data.type,
                data.content,
                data.is_default,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def get_templates(template_type: str) -> List[ReferenceTemplate]:
        query = """
        SELECT * 
        FROM reference_templates 
        WHERE type=$1;
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query, template_type)

        result = []
        if rows:
            for row in rows:
                result.append(ReferenceTemplate(**dict(row)))

        return result

    @staticmethod
    async def delete_template(name: str, template_type: str) -> bool:
        query = """
            DELETE FROM reference_templates
            WHERE name=$1
            AND type=$2
            RETURNING id;
            """

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, name, template_type)
            return bool(row)

    @staticmethod
    async def delete_template_by_id(id: int) -> bool:
        query = """
            DELETE FROM reference_templates
            WHERE id=$1 
            RETURNING id;
            """

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_template(
        id: int,
        updates: ReferenceTemplateUpdate,
    ) -> bool:
        update = updates.model_dump(exclude_unset=True)

        if not update:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(update.keys())
        ]
        query = f"UPDATE reference_templates SET {', '.join(set_clauses)} WHERE id = ${len(update)+1} RETURNING id;"
        values = list(update.values()) + [id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)
