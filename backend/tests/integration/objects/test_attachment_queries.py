# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from datetime import date
from unittest import IsolatedAsyncioTestCase

from asyncpg import UniqueViolationError
from app.common.storage.postgres import database
from app.core.objects.attachment_queries import AttachmentQueries
from app.core.objects.schemas import AttachmentCreate
from app.core.registration.schemas import PatientCreate
from app.core.registration.services import PatientService


def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        file_bytes = file.read()
        return file_bytes


class TestAttachmentsService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()

        # Ensure no leftover patients
        await PatientService.delete_patient("Jim", "Doe")

        # Create a minimal patient for linking attachments
        self.minimal_patient = PatientCreate(
            first_name="Jim",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        # A valid attachment to use
        self.key = f"{self.patient_id}/test_document.pdf"
        self.attachment_data = AttachmentCreate(
            file_name="test_document.pdf",
            file_key=self.key,
            file_size=1024,
            mime_type="application/pdf",
            document_type="consultation report",
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    #### CREATE
    async def test_create_attachment_success(self):
        async with database.get_transaction() as conn:
            attachment_id = await AttachmentQueries.create_attachment_record(
                conn,
                self.patient_id,
                self.attachment_data,
            )
        self.assertIsInstance(attachment_id, int)
        self.assertGreater(attachment_id, 0)

        # Validate
        async with database.get_transaction() as conn:
            attachments = await AttachmentQueries.get_patient_attachments(
                conn, self.patient_id
            )
        self.assertGreaterEqual(len(attachments), 1)

    async def test_create_attachment_duplicate_error(self):
        # Upload attachment
        async with database.get_transaction() as conn:
            attachment_id = await AttachmentQueries.create_attachment_record(
                conn,
                self.patient_id,
                self.attachment_data,
            )
        self.assertIsInstance(attachment_id, int)

        # Create new with the same file_key (should violate unique constraint)
        old_name = self.attachment_data.file_name
        self.attachment_data.file_name = "new_name.jpg"

        # file_key remains the same, which should cause UniqueViolationError
        with self.assertRaises(UniqueViolationError):
            async with database.get_transaction() as conn:
                await AttachmentQueries.create_attachment_record(
                    conn,
                    self.patient_id,
                    self.attachment_data,
                )

        # Validate - should still have only 1 attachment
        async with database.get_transaction() as conn:
            attachments = await AttachmentQueries.get_patient_attachments(
                conn, self.patient_id
            )
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0].file_name, old_name)

    #### UPDATE
    async def test_update_attachment_key_success(self):
        # Create attachment first
        async with database.get_transaction() as conn:
            attachment_id = await AttachmentQueries.create_attachment_record(
                conn,
                self.patient_id,
                self.attachment_data,
            )

        # Update file key
        new_key = f"{self.patient_id}/updated_document.pdf"
        async with database.get_transaction() as conn:
            result = await AttachmentQueries.update_attachment_key(
                conn,
                attachment_id,
                new_key,
            )
        self.assertTrue(result)

        # Validate
        async with database.get_transaction() as conn:
            attachment = await AttachmentQueries.get_attachment_by_id(
                conn, attachment_id
            )
        self.assertIsNotNone(attachment)
        self.assertEqual(attachment.file_key, new_key)

    async def test_update_attachment_key_not_found(self):
        async with database.get_transaction() as conn:
            result = await AttachmentQueries.update_attachment_key(
                conn,
                9999,  # Non-existent ID
                "some/key.pdf",
            )
        self.assertFalse(result)

    #### GET
    async def test_get_attachments_empty(self):
        async with database.get_transaction() as conn:
            attachments = await AttachmentQueries.get_patient_attachments(
                conn, self.patient_id
            )
        self.assertIsInstance(attachments, list)
        self.assertEqual(len(attachments), 0)

    async def test_get_attachments(self):
        async with database.get_transaction() as conn:
            attachment_id = await AttachmentQueries.create_attachment_record(
                conn,
                self.patient_id,
                self.attachment_data,
            )
        self.assertIsInstance(attachment_id, int)

        async with database.get_transaction() as conn:
            attachments = await AttachmentQueries.get_patient_attachments(
                conn, self.patient_id
            )
        self.assertEqual(len(attachments), 1)
        self.assertEqual(
            attachments[0].file_name, self.attachment_data.file_name
        )

    async def test_get_attachment(self):
        async with database.get_transaction() as conn:
            attachment_id = await AttachmentQueries.create_attachment_record(
                conn,
                self.patient_id,
                self.attachment_data,
            )
        self.assertIsInstance(attachment_id, int)

        async with database.get_transaction() as conn:
            attachment = await AttachmentQueries.get_attachment(
                conn, self.attachment_data.file_key
            )
        self.assertIsNotNone(attachment)
        self.assertEqual(attachment.file_name, self.attachment_data.file_name)
        self.assertEqual(attachment.file_size, self.attachment_data.file_size)
        self.assertEqual(attachment.file_key, self.attachment_data.file_key)

    async def test_get_attachment_none(self):
        async with database.get_transaction() as conn:
            attachment = await AttachmentQueries.get_attachment(
                conn, "nonexistent/key.pdf"
            )
        self.assertIsNone(attachment)

    async def test_get_attachment_by_id(self):
        async with database.get_transaction() as conn:
            attachment_id = await AttachmentQueries.create_attachment_record(
                conn,
                self.patient_id,
                self.attachment_data,
            )
        self.assertIsInstance(attachment_id, int)

        async with database.get_transaction() as conn:
            attachment = await AttachmentQueries.get_attachment_by_id(
                conn, attachment_id
            )
        self.assertIsNotNone(attachment)
        self.assertEqual(attachment.file_name, self.attachment_data.file_name)
        self.assertEqual(attachment.file_size, self.attachment_data.file_size)
        self.assertEqual(attachment.file_key, self.attachment_data.file_key)

    async def test_get_attachment_by_id_none(self):
        async with database.get_transaction() as conn:
            attachment = await AttachmentQueries.get_attachment_by_id(
                conn, 9999
            )
        self.assertIsNone(attachment)

    #### DELETE
    async def test_delete_attachment_success(self):
        # Create attachment
        async with database.get_transaction() as conn:
            attachment_id = await AttachmentQueries.create_attachment_record(
                conn,
                self.patient_id,
                self.attachment_data,
            )
        self.assertIsInstance(attachment_id, int)

        # Test deletion
        async with database.get_transaction() as conn:
            result = await AttachmentQueries.delete_attachment(
                conn, self.attachment_data.file_key
            )
        self.assertTrue(result)

        # Validate
        async with database.get_transaction() as conn:
            remaining = await AttachmentQueries.get_patient_attachments(
                conn, self.patient_id
            )
        self.assertEqual(len(remaining), 0)

    async def test_delete_attachment_not_found(self):
        async with database.get_transaction() as conn:
            result = await AttachmentQueries.delete_attachment(
                conn, "nonexistent/key.pdf"
            )
        self.assertFalse(result)


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

#
# class TestAttachmentsService(IsolatedAsyncioTestCase):
#     async def asyncSetUp(self) -> None:
#         asyncio.get_event_loop().set_debug(False)
#         await database.connect()
#         await minio_client.connect()
#
#         # Ensure no leftover patients
#         await PatientService.delete_patient("Jim", "Doe")
#
#         # Create a minimal patient for linking attachments
#         self.minimal_patient = PatientCreate(
#             first_name="Jim",
#             last_name="Doe",
#             dob=date(1990, 3, 22),
#             health_card="1234567890",
#             health_card_version="AB",
#             disposition="Active",
#             referral_site="Toronto",
#             province="Ontario",
#             age=30,
#             gender="Male",
#         )
#
#         await PatientService.create_patient(self.minimal_patient)
#         patients = await PatientService.get_patients()
#         self.patient_id = patients[0].id
#
#         # A valid attachment to use
#         self.key = f"{self.patient_id}/test_document.pdf"
#         self.attachment_data = AttachmentCreate(
#             file_name="test_document.pdf",
#             file_key=self.key,
#             file_size=1024,
#             mime_type="application/pdf",
#             document_type="consultation report",
#         )
#
#     async def asyncTearDown(self) -> None:
#         await ObjectService.delete_object("photo", "test_file")
#         await ObjectService.delete_bucket("testing")
#         await minio_client.disconnect()
#
#         await PatientService.delete_patient("Jim", "Doe")
#         await database.disconnect()
#
#     async def test_create_attachment_success(self):
#         async with database.get_transaction() as conn:
#             result = await AttachmentQueries.create_attachment_record(
#                 conn,
#                 self.patient_id,
#                 self.attachment_data,
#             )
#
#         self.assertTrue(result)
#
#         # Validate
#         attachments = await AttachmentService.get_patient_attachments(
#             self.patient_id
#         )
#         self.assertGreaterEqual(len(attachments), 1)
#
#     async def test_create_attachment_duplicate_error(self):
#         # Upload attachment
#         async with database.get_transaction() as conn:
#             result = await AttachmentQueries.create_attachment_record(
#                 conn,
#                 self.patient_id,
#                 self.attachment_data,
#             )
#
#         self.assertTrue(result)
#
#         # Create new with the same name/id
#         old_name = self.attachment_data.file_name
#         self.attachment_data.file_name = "new_name.jpg"
#
#         with self.assertRaises(UniqueViolationError):
#             async with database.get_transaction() as conn:
#                 result = await AttachmentQueries.create_attachment_record(
#                     conn,
#                     self.patient_id,
#                     self.attachment_data,
#                 )
#
#         # Validate
#         attachments = await AttachmentService.get_patient_attachments(
#             self.patient_id
#         )
#         self.assertEqual(len(attachments), 1)
#         self.assertEqual(attachments[0].file_name, old_name)
#
#     #### GET
#     async def test_get_attachments_empty(self):
#         attachments = await AttachmentService.get_patient_attachments(
#             self.patient_id
#         )
#
#         self.assertIsInstance(attachments, list)
#         self.assertEqual(len(attachments), 0)
#
#     async def test_get_attachments(self):
#         async with database.get_transaction() as conn:
#             result = await AttachmentQueries.create_attachment_record(
#                 conn,
#                 self.patient_id,
#                 self.attachment_data,
#             )
#
#         self.assertTrue(result)
#
#         attachments = await AttachmentService.get_patient_attachments(
#             self.patient_id
#         )
#
#         self.assertEqual(len(attachments), 1)
#         self.assertEqual(
#             attachments[0].file_name, self.attachment_data.file_name
#         )
#
#     async def test_get_attachment(self):
#         async with database.get_transaction() as conn:
#             result = await AttachmentQueries.create_attachment_record(
#                 conn,
#                 self.patient_id,
#                 self.attachment_data,
#             )
#
#         self.assertTrue(result)
#
#         attachment = await AttachmentService.get_attachment(
#             self.attachment_data.file_key
#         )
#
#         self.assertEqual(attachment.file_name, self.attachment_data.file_name)
#         self.assertEqual(attachment.file_size, self.attachment_data.file_size)
#         self.assertEqual(attachment.file_key, self.attachment_data.file_key)
#
#     async def test_get_attachment_none(self):
#         attachment = await AttachmentService.get_attachment(
#             self.attachment_data.file_key
#         )
#         self.assertIsNone(attachment)
#
#     async def test_get_attachment_by_id(self):
#         async with database.get_transaction() as conn:
#             result = await AttachmentQueries.create_attachment_record(
#                 conn,
#                 self.patient_id,
#                 self.attachment_data,
#             )
#
#         self.assertTrue(result)
#
#         attachment = await AttachmentService.get_attachment_by_id(id)
#         self.assertEqual(attachment.file_name, self.attachment_data.file_name)
#         self.assertEqual(attachment.file_size, self.attachment_data.file_size)
#         self.assertEqual(attachment.file_key, self.attachment_data.file_key)
#
#
# #     #### DELETE
# #     async def test_delete_attachment_by_id_success(self):
# #         await AttachmentService.upload_attachment(
# #             self.patient_id,
# #             self.attachment_data,
# #         )
# #         attachments = await AttachmentService.get_patient_attachments(
# #             self.patient_id
# #         )
# #         attachment_id = attachments[0].id
# #
# #         # Test
# #         result = await AttachmentService.delete_attachment_by_id(attachment_id)
# #         self.assertTrue(result)
# #
# #         # Validate
# #         remaining = await AttachmentService.get_patient_attachments(
# #             self.patient_id
# #         )
# #         self.assertEqual(len(remaining), 0)
# #
# #     async def test_delete_attachment_by_id_not_found(self):
# #         result = await AttachmentService.delete_attachment_by_id(9999)
# #         self.assertFalse(result)
# #
# #     async def test_delete_attachment_success(self):
# #         id = await AttachmentService.upload_attachment(
# #             self.patient_id,
# #             self.attachment_data,
# #         )
# #         self.assertTrue(id)
# #
# #         # Test
# #         result = await AttachmentService.delete_attachment(
# #             self.patient_id,
# #             self.attachment_data.file_name,
# #         )
# #         self.assertTrue(result)
# #
# #         # Validate
# #         remaining = await AttachmentService.get_patient_attachments(
# #             self.patient_id
# #         )
# #         self.assertEqual(len(remaining), 0)
# #
# #     async def test_delete_attachment_not_found(self):
# #         result = await AttachmentService.delete_attachment(
# #             self.patient_id,
# #             self.attachment_data.file_name,
# #         )
# #         self.assertFalse(result)
