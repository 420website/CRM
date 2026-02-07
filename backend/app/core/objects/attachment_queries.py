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


# --- Delete below ---

# @staticmethod
# async def delete_attachment_by_id(conn: Connection, id: int) -> bool:
#     query = """DELETE FROM attachments WHERE id=$1;"""
#     result = await conn.execute(query, id)
#     return int(result.split()[1]) > 0
#
# # Attachments -- delete
# @staticmethod
# async def upload_attachment(
#     patient_id: int,
#     attachment: AttachmentCreate,
# ) -> int | None:
#     """
#     Could also jsut have not duplciate so users have to remove old one
#     before creating with same name.
#     """
#     logger.info(
#         f"AttachmentService.upload_attachment - Patient: {patient_id}, File: {attachment.file_name}, Size: {attachment.file_size}, Type: {attachment.document_type}"
#     )
#
#     query = """
#     INSERT INTO attachments (
#         patient_id, file_name, file_key, file_size,
#         mime_type, document_type
#     )
#     VALUES ($1, $2, $3, $4, $5, $6)
#     ON CONFLICT (patient_id, file_name)
#     DO UPDATE SET
#         file_name = EXCLUDED.file_name,
#         file_key = EXCLUDED.file_key,
#         file_size = EXCLUDED.file_size,
#         mime_type = EXCLUDED.mime_type,
#         document_type = EXCLUDED.document_type
#     RETURNING id;
#     """
#     async with database.get_transaction() as conn:
#         try:
#             row = await conn.fetchrow(
#                 query,
#                 patient_id,
#                 attachment.file_name,
#                 attachment.file_key,
#                 attachment.file_size,
#                 attachment.mime_type,
#                 attachment.document_type,
#             )
#         except Exception as e:
#             logger.error(
#                 f"Database error in upload_attachment - Patient: {patient_id}, File: {attachment.file_name}, Error: {str(e)}",
#                 exc_info=True,
#             )
#             raise
#
#     if row and "id" in row:
#         logger.info(
#             f"Attachment record saved - Patient: {patient_id}, ID: {row['id']}, File: {attachment.file_name}"
#         )
#         return row["id"]
#     else:
#         logger.error(
#             f"Attachment record not saved - Patient: {patient_id}, File: {attachment.file_name}"
#         )
#         return None
