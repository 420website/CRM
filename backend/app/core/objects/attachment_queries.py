from typing import List, Union
from asyncpg import Connection
from app.core.objects.schemas import AttachmentCreate, AttachmentRead


class AttachmentQueries:
    @staticmethod
    async def create_attachment_record(
        conn: Connection,
        patient_id: int,
        attachment: AttachmentCreate,
    ) -> int:
        """Insert initial attachment record without file_key, return ID."""
        query = """
        INSERT INTO attachments (
            patient_id, file_name, file_size,
            mime_type, document_type, file_key
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id;
        """

        row = await conn.fetchrow(
            query,
            patient_id,
            attachment.file_name,
            attachment.file_size,
            attachment.mime_type,
            attachment.document_type,
            attachment.file_key,
        )

        if not row or not row["id"]:
            raise Exception(
                "Failed to insert attachment record - no ID returned"
            )

        return row["id"]

    @staticmethod
    async def update_attachment_key(
        conn: Connection,
        attachment_id: int,
        file_key: str,
    ) -> bool:
        """Update attachment record with MinIO file key."""
        query = """
        UPDATE attachments 
        SET file_key = $1
        WHERE id = $2;
        """
        result = await conn.execute(query, file_key, attachment_id)
        return int(result.split()[1]) > 0

    @staticmethod
    async def get_patient_attachments(
        conn: Connection,
        patient_id: int,
    ) -> List[AttachmentRead]:
        query = """
        SELECT * 
        FROM attachments 
        WHERE patient_id = $1 
        ORDER BY uploaded_at DESC;
        """
        rows = await conn.fetch(query, patient_id)

        result = []
        if rows:
            for row in rows:
                result.append(AttachmentRead(**dict(row)))
        return result

    @staticmethod
    async def get_attachment(
        conn: Connection,
        file_key: str,
    ) -> Union[AttachmentRead, None]:
        query = """
        SELECT * 
        FROM attachments  
        WHERE file_key = $1;
        """
        row = await conn.fetchrow(query, file_key)
        return AttachmentRead(**dict(row)) if row else None

    @staticmethod
    async def get_attachment_by_id(
        conn: Connection,
        id: int,
    ) -> Union[AttachmentRead, None]:
        query = """
        SELECT * 
        FROM attachments  
        WHERE id = $1; 
        """
        row = await conn.fetchrow(query, id)
        return AttachmentRead(**dict(row)) if row else None

    @staticmethod
    async def delete_attachment(conn: Connection, file_key: str) -> bool:
        query = """DELETE FROM attachments WHERE file_key=$1;"""
        result = await conn.execute(query, file_key)
        return int(result.split()[1]) > 0
