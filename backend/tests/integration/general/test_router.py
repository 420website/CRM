# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportOperatorIssue=none
import asyncio
from unittest import IsolatedAsyncioTestCase
from fastapi import HTTPException
from app.authentication.schemas import UserRead
from app.database import database
from app.general.router import (
    create_clinical_template,
    create_disposition,
    create_document_type,
    create_note_template,
    create_referral_site,
    delete_clinical_template_id,
    delete_clinical_template_name,
    delete_disposition_id,
    delete_disposition_name,
    delete_document_type_id,
    delete_document_type_name,
    delete_note_template_id,
    delete_note_template_name,
    delete_referral_site_id,
    delete_referral_site_name,
    get_clinical_templates,
    get_dispositions,
    get_document_types,
    get_note_templates,
    get_referral_sites,
    update_disposition,
    update_clinical_template,
    update_document_type,
    update_note_template,
    update_referral_site,
)
from app.general.schemas import (
    ClinicalTemplate,
    ClinicalTemplateUpdate,
    Disposition,
    DispositionUpdate,
    DocumentType,
    DocumentTypeUpdate,
    NotesTemplate,
    NotesTemplateUpdate,
    ReferralSite,
    ReferralSiteUpdate,
)
from app.general.services import GeneralService


email = "test444@example.com"
password = "securepassword123"


class TestNotesTemplateAPI(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""

        test_names = [
            "test_template",
            "test_template_2",
            "updated_template",
            "default_template",
        ]
        for name in test_names:
            try:
                await GeneralService.delete_notes_template(name)
            except Exception:
                pass

    async def asyncSetUp(self) -> None:
        await database.connect()
        asyncio.get_event_loop().set_debug(False)
        await self._cleanup_test_data()

        # Get authenticated user for all tests
        self.user = UserRead(
            id=1,
            email=email,
            role="admin",
            permissions=[],
            authenticator_mfa_enabled=True,
        )

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        await database.disconnect()

    # Create
    async def test_create_notes_template_success(self):
        """Test successful creation of a notes template via API"""
        template_data = NotesTemplate(
            name="test_template",
            content="This is a test template content",
            is_default=False,
        )

        # Test
        result = await create_note_template(template_data, self.user)

        self.assertEqual(
            result["message"],
            "Notes template created successfully.",
        )

        # Validate by getting templates
        templates = await get_note_templates(self.user)
        template_names = [t.name for t in templates]
        self.assertIn("test_template", template_names)

    async def test_create_notes_template_with_default(self):
        """Test creation of a default notes template via API"""
        template_data = NotesTemplate(
            name="default_template",
            content="Default template content",
            is_default=True,
        )

        # Test
        result = await create_note_template(template_data, self.user)
        self.assertEqual(
            result["message"],
            "Notes template created successfully.",
        )

        # Validate
        templates = await get_note_templates(self.user)
        default_template = next(
            (t for t in templates if t.name == "default_template"), None
        )
        self.assertIsNotNone(default_template)
        self.assertTrue(default_template.is_default)

    async def test_create_duplicate_template_name(self):
        """Test creating template with duplicate name via API"""
        template_data = NotesTemplate(
            name="test_template",
            content="First template",
            is_default=False,
        )

        # Create first template
        result1 = await create_note_template(template_data, self.user)
        self.assertEqual(
            result1["message"],
            "Notes template created successfully.",
        )

        # Try to create duplicate - should raise HTTPException
        with self.assertRaises(HTTPException) as context:
            await create_note_template(template_data, self.user)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Template already exists.", context.exception.detail)

    # Get
    async def test_get_notes_template_empty(self):
        """Test getting templates when none exist via API"""
        templates = await get_note_templates(self.user)

        self.assertIsInstance(templates, list)
        # self.assertEqual(len(templates), 0)

    async def test_get_notes_template_with_data(self):
        """Test getting templates when data exists via API"""
        # Create test templates
        template1_data = NotesTemplate(
            name="test_template",
            content="Template 1 content",
            is_default=False,
        )
        template2_data = NotesTemplate(
            name="test_template_2",
            content="Template 2 content",
            is_default=True,
        )

        await create_note_template(template1_data, self.user)
        await create_note_template(template2_data, self.user)

        # Test
        templates = await get_note_templates(self.user)

        self.assertIsInstance(templates, list)
        self.assertGreaterEqual(len(templates), 2)

        # Verify our templates are in the results
        template_names = [t.name for t in templates]
        self.assertIn("test_template", template_names)
        self.assertIn("test_template_2", template_names)

        # Verify template structure
        for template in templates:
            self.assertIsInstance(template, NotesTemplate)
            self.assertIsInstance(template.name, str)
            self.assertIsInstance(template.content, str)
            self.assertIsInstance(template.is_default, bool)
            self.assertIsNotNone(template.id)

    # Delete
    async def test_delete_notes_template_by_name_success(self):
        """Test successful deletion of a notes template by name via API"""
        # Create template first
        template_data = NotesTemplate(
            name="test_template",
            content="Template to delete",
            is_default=False,
        )
        await create_note_template(template_data, self.user)

        # Delete the template
        result = await delete_note_template_name("test_template", self.user)
        self.assertEqual(
            result["message"], "Notes template deleted successfully."
        )

        # Verify template was deleted
        templates = await get_note_templates(self.user)
        template_names = [t.name for t in templates]
        self.assertNotIn("test_template", template_names)

    async def test_delete_notes_template_by_id_success(self):
        """Test successful deletion of a notes template by ID via API"""
        # Create template first
        template_data = NotesTemplate(
            name="test_template",
            content="Template to delete by ID",
            is_default=False,
        )
        await create_note_template(template_data, self.user)

        # Get template to find its ID
        templates = await get_note_templates(self.user)
        template = next(
            (t for t in templates if t.name == "test_template"), None
        )
        self.assertIsNotNone(template)
        template_id = template.id

        # Delete the template by ID
        result = await delete_note_template_id(template_id, self.user)
        self.assertEqual(
            result["message"], "Notes template deleted successfully."
        )

        # Verify template was deleted
        templates = await get_note_templates(self.user)
        template_names = [t.name for t in templates]
        self.assertNotIn("test_template", template_names)

    async def test_delete_notes_template_not_found_by_name(self):
        """Test deletion of non-existent template by name via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_note_template_name("non_existent_template", self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Notes template not found", context.exception.detail)

    async def test_delete_notes_template_not_found_by_id(self):
        """Test deletion of non-existent template by ID via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_note_template_id(99999, self.user)  # Non-existent ID

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Notes template not found", context.exception.detail)

    # Update
    async def test_update_notes_template_success(self):
        """Test successful update of a notes template via API"""
        # Create template first
        template_data = NotesTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        await create_note_template(template_data, self.user)

        # Get template to find its ID
        templates = await get_note_templates(self.user)
        template = next(
            (t for t in templates if t.name == "test_template"), None
        )
        template_id = template.id

        # Update the template
        update_data = NotesTemplateUpdate(
            name="test_template",
            content="Updated content",
            is_default=True,
        )
        result = await update_note_template(
            template_id,
            update_data,
            self.user,
        )
        self.assertEqual(
            result["message"],
            "Notes template updated successfully.",
        )

        # Verify template was updated
        templates = await get_note_templates(self.user)
        updated_template = next(
            (t for t in templates if t.name == "test_template"), None
        )

        self.assertIsNotNone(updated_template)
        self.assertEqual(updated_template.content, "Updated content")
        self.assertTrue(updated_template.is_default)

    async def test_update_notes_template_partial(self):
        """Test partial update of a notes template via API"""
        # Create template first
        template_data = NotesTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        await create_note_template(template_data, self.user)

        # Get template ID
        templates = await get_note_templates(self.user)
        template = next(
            (t for t in templates if t.name == "test_template"), None
        )
        template_id = template.id

        # Partial update - only content
        update_data = NotesTemplateUpdate(
            content="Partially updated content",
        )
        result = await update_note_template(
            template_id,
            update_data,
            self.user,
        )
        self.assertEqual(
            result["message"],
            "Notes template updated successfully.",
        )

        # Verify only content was updated
        templates = await get_note_templates(self.user)
        updated_template = next(
            (t for t in templates if t.name == "test_template"), None
        )

        self.assertIsNotNone(updated_template)
        self.assertEqual(updated_template.content, "Partially updated content")
        self.assertFalse(updated_template.is_default)

    async def test_update_notes_template_empty_updates(self):
        """Test update with no actual changes via API"""
        # Create template first
        template_data = NotesTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        await create_note_template(template_data, self.user)

        # Get template ID
        templates = await get_note_templates(self.user)
        template = next(
            (t for t in templates if t.name == "test_template"), None
        )
        template_id = template.id

        # Empty update
        update_data = NotesTemplateUpdate()

        with self.assertRaises(HTTPException) as context:
            await update_note_template(template_id, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Notes template not found or could not be updated",
            context.exception.detail,
        )

    async def test_update_notes_template_not_found(self):
        """Test update of non-existent template via API"""
        update_data = NotesTemplateUpdate(
            name="non_existent_template",
            content="New content",
        )

        with self.assertRaises(HTTPException) as context:
            await update_note_template(99999, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Notes template not found or could not be updated",
            context.exception.detail,
        )


class TestClinicalTemplateAPI(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""

        test_names = [
            "test_template",
            "test_template_2",
            "updated_template",
            "default_template",
        ]
        for name in test_names:
            try:
                await GeneralService.delete_clinical_template(name)
            except Exception:
                pass

    async def asyncSetUp(self) -> None:
        await database.connect()
        asyncio.get_event_loop().set_debug(False)
        await self._cleanup_test_data()

        # Get authenticated user for all tests
        self.user = UserRead(
            id=1,
            email=email,
            role="admin",
            permissions=[],
            authenticator_mfa_enabled=True,
        )

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        await database.disconnect()

    # Create
    async def test_create_clinical_template_success(self):
        """Test successful creation of a clinical template via API"""
        template_data = ClinicalTemplate(
            name="test_template",
            content="This is a test template content",
            is_default=False,
        )

        # Test
        result = await create_clinical_template(template_data, self.user)

        self.assertEqual(
            result["message"],
            "Clinical template created successfully.",
        )

        # Validate by getting templates
        templates = await get_clinical_templates(self.user)
        template_names = [t.name for t in templates]
        self.assertIn("test_template", template_names)

    async def test_create_clinical_template_with_default(self):
        """Test creation of a default clinical template via API"""
        template_data = ClinicalTemplate(
            name="default_template",
            content="Default template content",
            is_default=True,
        )

        # Test
        result = await create_clinical_template(template_data, self.user)
        self.assertEqual(
            result["message"],
            "Clinical template created successfully.",
        )

        # Validate
        templates = await get_clinical_templates(self.user)
        default_template = next(
            (t for t in templates if t.name == "default_template"), None
        )
        self.assertIsNotNone(default_template)
        self.assertTrue(default_template.is_default)

    async def test_create_duplicate_template_name(self):
        """Test creating template with duplicate name via API"""
        template_data = ClinicalTemplate(
            name="test_template",
            content="First template",
            is_default=False,
        )

        # Create first template
        result1 = await create_clinical_template(template_data, self.user)
        self.assertEqual(
            result1["message"],
            "Clinical template created successfully.",
        )

        # Try to create duplicate - should raise HTTPException
        with self.assertRaises(HTTPException) as context:
            await create_clinical_template(template_data, self.user)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Template already exists.", context.exception.detail)

    # Get
    async def test_get_clinical_template_empty(self):
        """Test getting templates when none exist via API"""
        templates = await get_clinical_templates(self.user)

        self.assertIsInstance(templates, list)
        # self.assertEqual(len(templates), 0)

    async def test_get_clinical_template_with_data(self):
        """Test getting templates when data exists via API"""
        # Create test templates
        template1_data = ClinicalTemplate(
            name="test_template",
            content="Template 1 content",
            is_default=False,
        )
        template2_data = ClinicalTemplate(
            name="test_template_2",
            content="Template 2 content",
            is_default=True,
        )

        await create_clinical_template(template1_data, self.user)
        await create_clinical_template(template2_data, self.user)

        # Test
        templates = await get_clinical_templates(self.user)

        self.assertIsInstance(templates, list)
        self.assertGreaterEqual(len(templates), 2)

        # Verify our templates are in the results
        template_names = [t.name for t in templates]
        self.assertIn("test_template", template_names)
        self.assertIn("test_template_2", template_names)

        # Verify template structure
        for template in templates:
            self.assertIsInstance(template, ClinicalTemplate)
            self.assertIsInstance(template.name, str)
            self.assertIsInstance(template.content, str)
            self.assertIsInstance(template.is_default, bool)
            self.assertIsNotNone(template.id)

    # Delete
    async def test_delete_clinical_template_by_name_success(self):
        """Test successful deletion of a clinical template by name via API"""
        # Create template first
        template_data = ClinicalTemplate(
            name="test_template",
            content="Template to delete",
            is_default=False,
        )
        await create_clinical_template(template_data, self.user)

        # Delete the template
        result = await delete_clinical_template_name(
            "test_template", self.user
        )
        self.assertEqual(
            result["message"], "Clinical template deleted successfully."
        )

        # Verify template was deleted
        templates = await get_clinical_templates(self.user)
        template_names = [t.name for t in templates]
        self.assertNotIn("test_template", template_names)

    async def test_delete_clinical_template_by_id_success(self):
        """Test successful deletion of a clinical template by ID via API"""
        # Create template first
        template_data = ClinicalTemplate(
            name="test_template",
            content="Template to delete by ID",
            is_default=False,
        )
        await create_clinical_template(template_data, self.user)

        # Get template to find its ID
        templates = await get_clinical_templates(self.user)
        template = next(
            (t for t in templates if t.name == "test_template"), None
        )
        self.assertIsNotNone(template)
        template_id = template.id

        # Delete the template by ID
        result = await delete_clinical_template_id(template_id, self.user)
        self.assertEqual(
            result["message"], "Clinical template deleted successfully."
        )

        # Verify template was deleted
        templates = await get_clinical_templates(self.user)
        template_names = [t.name for t in templates]
        self.assertNotIn("test_template", template_names)

    async def test_delete_clinical_template_not_found_by_name(self):
        """Test deletion of non-existent template by name via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_clinical_template_name(
                "non_existent_template", self.user
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Clinical template not found", context.exception.detail)

    async def test_delete_clinical_template_not_found_by_id(self):
        """Test deletion of non-existent template by ID via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_clinical_template_id(
                99999, self.user
            )  # Non-existent ID

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Clinical template not found", context.exception.detail)

    # Update
    async def test_update_clinical_template_success(self):
        """Test successful update of a clinical template via API"""
        # Create template first
        template_data = ClinicalTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        await create_clinical_template(template_data, self.user)

        # Get template to find its ID
        templates = await get_clinical_templates(self.user)
        template = next(
            (t for t in templates if t.name == "test_template"), None
        )
        template_id = template.id

        # Update the template
        update_data = ClinicalTemplateUpdate(
            name="test_template",
            content="Updated content",
            is_default=True,
        )
        result = await update_clinical_template(
            template_id,
            update_data,
            self.user,
        )
        self.assertEqual(
            result["message"],
            "Clinical template updated successfully.",
        )

        # Verify template was updated
        templates = await get_clinical_templates(self.user)
        updated_template = next(
            (t for t in templates if t.name == "test_template"), None
        )

        self.assertIsNotNone(updated_template)
        self.assertEqual(updated_template.content, "Updated content")
        self.assertTrue(updated_template.is_default)

    async def test_update_clinical_template_partial(self):
        """Test partial update of a clinical template via API"""
        # Create template first
        template_data = ClinicalTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        await create_clinical_template(template_data, self.user)

        # Get template ID
        templates = await get_clinical_templates(self.user)
        template = next(
            (t for t in templates if t.name == "test_template"), None
        )
        template_id = template.id

        # Partial update - only content
        update_data = ClinicalTemplateUpdate(
            content="Partially updated content",
        )
        result = await update_clinical_template(
            template_id,
            update_data,
            self.user,
        )
        self.assertEqual(
            result["message"],
            "Clinical template updated successfully.",
        )

        # Verify only content was updated
        templates = await get_clinical_templates(self.user)
        updated_template = next(
            (t for t in templates if t.name == "test_template"), None
        )

        self.assertIsNotNone(updated_template)
        self.assertEqual(updated_template.content, "Partially updated content")
        self.assertFalse(updated_template.is_default)

    async def test_update_clinical_template_empty_updates(self):
        """Test update with no actual changes via API"""
        # Create template first
        template_data = ClinicalTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        await create_clinical_template(template_data, self.user)

        # Get template ID
        templates = await get_clinical_templates(self.user)
        template = next(
            (t for t in templates if t.name == "test_template"), None
        )
        template_id = template.id

        # Empty update
        update_data = ClinicalTemplateUpdate()

        with self.assertRaises(HTTPException) as context:
            await update_clinical_template(template_id, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Clinical template not found or could not be updated",
            context.exception.detail,
        )

    async def test_update_clinical_template_not_found(self):
        """Test update of non-existent template via API"""
        update_data = ClinicalTemplateUpdate(
            name="non_existent_template",
            content="New content",
        )

        with self.assertRaises(HTTPException) as context:
            await update_clinical_template(99999, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Clinical template not found or could not be updated",
            context.exception.detail,
        )


class TestDocumentTypenAPI(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        test_names = [
            "Consultation Report",
            "HCV Perscription",
            "Treatment Consent",
            "test_document",
            "new_document",
        ]
        for name in test_names:
            try:
                await GeneralService.delete_document_type(name)
            except Exception:
                pass

    async def asyncSetUp(self) -> None:
        await database.connect()
        asyncio.get_event_loop().set_debug(False)
        await self._cleanup_test_data()

        # Get authenticated user for all tests
        self.user = UserRead(
            id=1,
            email=email,
            role="admin",
            permissions=[],
            authenticator_mfa_enabled=True,
        )

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        await database.disconnect()

    # Create
    async def test_create_document_type_success(self):
        document_type = DocumentType(
            name="Consultation Report",
            is_default=False,
            is_frequent=False,
        )

        # Test
        result = await create_document_type(document_type, self.user)

        self.assertEqual(
            result["message"],
            "Document type created successfully.",
        )

        # Validate by getting
        result = await get_document_types(self.user)
        doc_names = [d.name for d in result]
        self.assertIn("Consultation Report", doc_names)

    async def test_create_document_type_with_default(self):
        document_type = DocumentType(
            name="Consultation Report",
            is_default=True,
            is_frequent=False,
        )

        # Test
        result = await create_document_type(document_type, self.user)
        self.assertEqual(
            result["message"],
            "Document type created successfully.",
        )

        # Validate
        result = await get_document_types(self.user)

        default_doc = next(
            (d for d in result if d.name == "Consultation Report"), None
        )
        self.assertIsNotNone(default_doc)
        self.assertTrue(default_doc.is_default)

    async def test_create_duplicate_doc_type_name(self):
        document_type = DocumentType(
            name="Consultation Report",
            is_default=True,
            is_frequent=False,
        )

        # Create first disposition
        result = await create_document_type(document_type, self.user)
        self.assertEqual(
            result["message"],
            "Document type created successfully.",
        )

        # Try to create duplicate - should raise HTTPException
        with self.assertRaises(HTTPException) as context:
            await create_document_type(document_type, self.user)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn(
            "Document type already exists.", context.exception.detail
        )

    # Get
    async def test_get_document_type_empty(self):
        result = await get_document_types(self.user)

        self.assertIsInstance(result, list)

    async def test_get_document_type_with_data(self):
        document_type1 = DocumentType(
            name="Consultation Report",
            is_default=True,
            is_frequent=False,
        )
        document_type2 = DocumentType(
            name="HCV Perscription",
            is_default=True,
            is_frequent=False,
        )

        await create_document_type(document_type1, self.user)
        await create_document_type(document_type2, self.user)

        # Test
        result = await get_document_types(self.user)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 2)

        doc_names = [d.name for d in result]
        self.assertIn("Consultation Report", doc_names)
        self.assertIn("HCV Perscription", doc_names)

        # Verify disposition structure
        for doc in result:
            self.assertIsInstance(doc, DocumentType)
            self.assertIsInstance(doc.name, str)
            self.assertIsInstance(doc.is_default, bool)
            self.assertIsNotNone(doc.id)

    # Delete
    async def test_delete_document_type_by_name_success(self):
        document_type = DocumentType(
            name="HCV Perscription",
            is_default=True,
            is_frequent=False,
        )
        await create_document_type(document_type, self.user)

        # Delete the disposition
        result = await delete_document_type_name("HCV Perscription", self.user)
        self.assertEqual(
            result["message"], "Document type deleted successfully."
        )

        # Verify  was deleted
        result = await get_document_types(self.user)
        docs = [d.name for d in result]
        self.assertNotIn("HCV Perscription", docs)

    async def test_delete_document_type_by_id_success(self):
        document_type = DocumentType(
            name="HCV Perscription",
            is_default=True,
            is_frequent=False,
        )
        await create_document_type(document_type, self.user)

        # Get doc type to find its ID
        result = await get_document_types(self.user)
        doc = next((d for d in result if d.name == "HCV Perscription"), None)
        self.assertIsNotNone(doc)
        doc_id = doc.id

        # Delete  by ID
        result = await delete_document_type_id(doc_id, self.user)
        self.assertEqual(
            result["message"], "Document type deleted successfully."
        )

        # Verify was deleted
        result = await get_document_types(self.user)
        doc_names = [d.name for d in result]
        self.assertNotIn("HCV Perscription", doc_names)

    async def test_delete_document_type_not_found_by_name(self):
        with self.assertRaises(HTTPException) as context:
            await delete_document_type_name("non_existent", self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Document type not found", context.exception.detail)

    async def test_delete_document_type_not_found_by_id(self):
        with self.assertRaises(HTTPException) as context:
            await delete_document_type_id(99999, self.user)  # Non-existent ID

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Document type not found", context.exception.detail)

    # Update
    async def test_update_document_type_success(self):
        document_type = DocumentType(
            name="HCV Perscription",
            is_default=True,
            is_frequent=False,
        )
        await create_document_type(document_type, self.user)

        # Get ID
        result = await get_document_types(self.user)
        doc = next((d for d in result if d.name == "HCV Perscription"), None)
        doc_id = doc.id

        # Update
        update_data = DocumentTypeUpdate(
            name="test_document",
            is_default=True,
        )

        result = await update_document_type(doc_id, update_data, self.user)
        self.assertEqual(
            result["message"],
            "Document type updated successfully.",
        )

        # Verify updated
        docs = await get_document_types(self.user)
        updated_doc = next(
            (d for d in docs if d.name == "test_document"), None
        )

        self.assertIsNotNone(updated_doc)
        self.assertTrue(updated_doc.is_default)

        await delete_document_type_id(doc_id, self.user)

    async def test_update_document_type_partial(self):
        document_type = DocumentType(
            name="Document1",
            is_default=True,
            is_frequent=False,
        )
        await create_document_type(document_type, self.user)

        # Get ID
        result = await get_document_types(self.user)
        doc = next((d for d in result if d.name == "Document1"), None)
        doc_id = doc.id

        # Partial update - only is_frequent
        update_data = DocumentTypeUpdate(name="new_document")

        result = await update_document_type(doc_id, update_data, self.user)
        self.assertEqual(
            result["message"],
            "Document type updated successfully.",
        )

        # Verify only is_frequent was updated
        result = await get_document_types(self.user)
        updated_doc = next(
            (d for d in result if d.name == "new_document"), None
        )

        self.assertIsNotNone(updated_doc)
        self.assertTrue(updated_doc.is_default)

        # clean up
        await delete_document_type_id(doc_id, self.user)

    async def test_update_document_type_empty_updates(self):
        document_type = DocumentType(
            name="HCV Perscription",
            is_default=True,
            is_frequent=False,
        )
        await create_document_type(document_type, self.user)

        # Get ID
        result = await get_document_types(self.user)
        doc = next((d for d in result if d.name == "HCV Perscription"), None)
        doc_id = doc.id

        # Empty update
        update_data = DocumentTypeUpdate()

        with self.assertRaises(HTTPException) as context:
            await update_document_type(doc_id, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Document type not found or could not be updated",
            context.exception.detail,
        )

        # clean up
        await delete_document_type_id(doc_id, self.user)

    async def test_update_document_type_not_found(self):
        update_data = DocumentTypeUpdate(name="new_document")

        with self.assertRaises(HTTPException) as context:
            await update_document_type(99999, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Document type not found or could not be updated",
            context.exception.detail,
        )


class TestDispositionAPI(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""

        test_names = [
            "test_disposition",
            "test_disposition_2",
            "updated_disposition",
            "default_disposition",
        ]
        for name in test_names:
            try:
                await GeneralService.delete_disposition(name)
            except Exception:
                pass

    async def asyncSetUp(self) -> None:
        await database.connect()
        asyncio.get_event_loop().set_debug(False)
        await self._cleanup_test_data()

        # Get authenticated user for all tests
        self.user = UserRead(
            id=1,
            email=email,
            role="admin",
            permissions=[],
            authenticator_mfa_enabled=True,
        )

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        await database.disconnect()

    # Create
    async def test_create_disposition_success(self):
        """Test successful creation of a disposition via API"""
        disposition_data = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )

        # Test
        result = await create_disposition(disposition_data, self.user)

        self.assertEqual(
            result["message"],
            "Disposition created successfully.",
        )

        # Validate by getting dispositions
        dispositions = await get_dispositions(self.user)
        disposition_names = [d.name for d in dispositions]
        self.assertIn("test_disposition", disposition_names)

    async def test_create_disposition_with_default(self):
        """Test creation of a default disposition via API"""
        disposition_data = Disposition(
            name="default_disposition",
            is_frequent=True,
            is_default=True,
        )

        # Test
        result = await create_disposition(disposition_data, self.user)
        self.assertEqual(
            result["message"],
            "Disposition created successfully.",
        )

        # Validate
        dispositions = await get_dispositions(self.user)
        default_disposition = next(
            (d for d in dispositions if d.name == "default_disposition"), None
        )
        self.assertIsNotNone(default_disposition)
        self.assertTrue(default_disposition.is_default)
        self.assertTrue(default_disposition.is_frequent)

    async def test_create_duplicate_disposition_name(self):
        """Test creating disposition with duplicate name via API"""
        disposition_data = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )

        # Create first disposition
        result1 = await create_disposition(disposition_data, self.user)
        self.assertEqual(
            result1["message"],
            "Disposition created successfully.",
        )

        # Try to create duplicate - should raise HTTPException
        with self.assertRaises(HTTPException) as context:
            await create_disposition(disposition_data, self.user)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Disposition already exists.", context.exception.detail)

    # Get
    async def test_get_disposition_empty(self):
        """Test getting dispositions when none exist via API"""
        dispositions = await get_dispositions(self.user)

        self.assertIsInstance(dispositions, list)
        # self.assertEqual(len(dispositions), 0)

    async def test_get_disposition_with_data(self):
        """Test getting dispositions when data exists via API"""
        # Create test dispositions
        disposition1_data = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )
        disposition2_data = Disposition(
            name="test_disposition_2",
            is_frequent=True,
            is_default=True,
        )

        await create_disposition(disposition1_data, self.user)
        await create_disposition(disposition2_data, self.user)

        # Test
        dispositions = await get_dispositions(self.user)

        self.assertIsInstance(dispositions, list)
        self.assertGreaterEqual(len(dispositions), 2)

        # Verify our dispositions are in the results
        disposition_names = [d.name for d in dispositions]
        self.assertIn("test_disposition", disposition_names)
        self.assertIn("test_disposition_2", disposition_names)

        # Verify disposition structure
        for disposition in dispositions:
            self.assertIsInstance(disposition, Disposition)
            self.assertIsInstance(disposition.name, str)
            self.assertIsInstance(disposition.is_frequent, bool)
            self.assertIsInstance(disposition.is_default, bool)
            self.assertIsNotNone(disposition.id)

    # Delete
    async def test_delete_disposition_by_name_success(self):
        """Test successful deletion of a disposition by name via API"""
        # Create disposition first
        disposition_data = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )
        await create_disposition(disposition_data, self.user)

        # Delete the disposition
        result = await delete_disposition_name("test_disposition", self.user)
        self.assertEqual(
            result["message"], "Disposition deleted successfully."
        )

        # Verify disposition was deleted
        dispositions = await get_dispositions(self.user)
        disposition_names = [d.name for d in dispositions]
        self.assertNotIn("test_disposition", disposition_names)

    async def test_delete_disposition_by_id_success(self):
        """Test successful deletion of a disposition by ID via API"""
        # Create disposition first
        disposition_data = Disposition(
            name="test_disposition",
            is_frequent=True,
            is_default=False,
        )
        await create_disposition(disposition_data, self.user)

        # Get disposition to find its ID
        dispositions = await get_dispositions(self.user)
        disposition = next(
            (d for d in dispositions if d.name == "test_disposition"), None
        )
        self.assertIsNotNone(disposition)
        disposition_id = disposition.id

        # Delete the disposition by ID
        result = await delete_disposition_id(disposition_id, self.user)
        self.assertEqual(
            result["message"], "Disposition deleted successfully."
        )

        # Verify disposition was deleted
        dispositions = await get_dispositions(self.user)
        disposition_names = [d.name for d in dispositions]
        self.assertNotIn("test_disposition", disposition_names)

    async def test_delete_disposition_not_found_by_name(self):
        """Test deletion of non-existent disposition by name via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_disposition_name(
                "non_existent_disposition", self.user
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Disposition not found", context.exception.detail)

    async def test_delete_disposition_not_found_by_id(self):
        """Test deletion of non-existent disposition by ID via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_disposition_id(99999, self.user)  # Non-existent ID

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Disposition not found", context.exception.detail)

    # Update
    async def test_update_disposition_success(self):
        """Test successful update of a disposition via API"""
        # Create disposition first
        disposition_data = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )
        await create_disposition(disposition_data, self.user)

        # Get disposition to find its ID
        dispositions = await get_dispositions(self.user)
        disposition = next(
            (d for d in dispositions if d.name == "test_disposition"), None
        )
        disposition_id = disposition.id

        # Update the disposition
        update_data = DispositionUpdate(
            name="test_disposition",
            is_frequent=True,
            is_default=True,
        )
        result = await update_disposition(
            disposition_id,
            update_data,
            self.user,
        )
        self.assertEqual(
            result["message"],
            "Disposition updated successfully.",
        )

        # Verify disposition was updated
        dispositions = await get_dispositions(self.user)
        updated_disposition = next(
            (d for d in dispositions if d.name == "test_disposition"), None
        )

        self.assertIsNotNone(updated_disposition)
        self.assertTrue(updated_disposition.is_frequent)
        self.assertTrue(updated_disposition.is_default)

    async def test_update_disposition_partial(self):
        """Test partial update of a disposition via API"""
        # Create disposition first
        disposition_data = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )
        await create_disposition(disposition_data, self.user)

        # Get disposition ID
        dispositions = await get_dispositions(self.user)
        disposition = next(
            (d for d in dispositions if d.name == "test_disposition"), None
        )
        disposition_id = disposition.id

        # Partial update - only is_frequent
        update_data = DispositionUpdate(
            is_frequent=True,
        )
        result = await update_disposition(
            disposition_id,
            update_data,
            self.user,
        )
        self.assertEqual(
            result["message"],
            "Disposition updated successfully.",
        )

        # Verify only is_frequent was updated
        dispositions = await get_dispositions(self.user)
        updated_disposition = next(
            (d for d in dispositions if d.name == "test_disposition"), None
        )

        self.assertIsNotNone(updated_disposition)
        self.assertTrue(updated_disposition.is_frequent)
        self.assertFalse(updated_disposition.is_default)

    async def test_update_disposition_empty_updates(self):
        """Test update with no actual changes via API"""
        # Create disposition first
        disposition_data = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )
        await create_disposition(disposition_data, self.user)

        # Get disposition ID
        dispositions = await get_dispositions(self.user)
        disposition = next(
            (d for d in dispositions if d.name == "test_disposition"), None
        )
        disposition_id = disposition.id

        # Empty update
        update_data = DispositionUpdate()

        with self.assertRaises(HTTPException) as context:
            await update_disposition(disposition_id, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Disposition not found or could not be updated",
            context.exception.detail,
        )

    async def test_update_disposition_not_found(self):
        """Test update of non-existent disposition via API"""
        update_data = DispositionUpdate(
            name="non_existent_disposition",
            is_frequent=True,
        )

        with self.assertRaises(HTTPException) as context:
            await update_disposition(99999, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Disposition not found or could not be updated",
            context.exception.detail,
        )


class TestReferralSiteAPI(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""

        test_names = [
            "test_referral_site",
            "test_referral_site_2",
            "updated_referral_site",
            "default_referral_site",
        ]
        for name in test_names:
            try:
                await GeneralService.delete_referral_site(name)
            except Exception:
                pass

    async def asyncSetUp(self) -> None:
        await database.connect()
        asyncio.get_event_loop().set_debug(False)
        await self._cleanup_test_data()

        # Get authenticated user for all tests
        self.user = UserRead(
            id=1,
            email=email,
            role="admin",
            permissions=[],
            authenticator_mfa_enabled=True,
        )

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        await database.disconnect()

    # Create
    async def test_create_referral_site_success(self):
        """Test successful creation of a referral site via API"""
        referral_site_data = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )

        # Test
        result = await create_referral_site(referral_site_data, self.user)

        self.assertEqual(
            result["message"],
            "Referral site created successfully.",
        )

        # Validate by getting referral sites
        referral_sites = await get_referral_sites(self.user)
        referral_site_names = [r.name for r in referral_sites]
        self.assertIn("test_referral_site", referral_site_names)

    async def test_create_referral_site_with_default(self):
        """Test creation of a default referral site via API"""
        referral_site_data = ReferralSite(
            name="default_referral_site",
            is_frequent=True,
            is_default=True,
        )

        # Test
        result = await create_referral_site(referral_site_data, self.user)
        self.assertEqual(
            result["message"],
            "Referral site created successfully.",
        )

        # Validate
        referral_sites = await get_referral_sites(self.user)
        default_referral_site = next(
            (r for r in referral_sites if r.name == "default_referral_site"),
            None,
        )
        self.assertIsNotNone(default_referral_site)
        self.assertTrue(default_referral_site.is_default)
        self.assertTrue(default_referral_site.is_frequent)

    async def test_create_duplicate_referral_site_name(self):
        """Test creating referral site with duplicate name via API"""
        referral_site_data = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )

        # Create first referral site
        result1 = await create_referral_site(referral_site_data, self.user)
        self.assertEqual(
            result1["message"],
            "Referral site created successfully.",
        )

        # Try to create duplicate - should raise HTTPException
        with self.assertRaises(HTTPException) as context:
            await create_referral_site(referral_site_data, self.user)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn(
            "Referral site already exists.", context.exception.detail
        )

    # Get
    async def test_get_referral_site_empty(self):
        """Test getting referral sites when none exist via API"""
        referral_sites = await get_referral_sites(self.user)

        self.assertIsInstance(referral_sites, list)
        # self.assertEqual(len(referral_sites), 0)

    async def test_get_referral_site_with_data(self):
        """Test getting referral sites when data exists via API"""
        # Create test referral sites
        referral_site1_data = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )
        referral_site2_data = ReferralSite(
            name="test_referral_site_2",
            is_frequent=True,
            is_default=True,
        )

        await create_referral_site(referral_site1_data, self.user)
        await create_referral_site(referral_site2_data, self.user)

        # Test
        referral_sites = await get_referral_sites(self.user)

        self.assertIsInstance(referral_sites, list)
        self.assertGreaterEqual(len(referral_sites), 2)

        # Verify our referral sites are in the results
        referral_site_names = [r.name for r in referral_sites]
        self.assertIn("test_referral_site", referral_site_names)
        self.assertIn("test_referral_site_2", referral_site_names)

        # Verify referral site structure
        for referral_site in referral_sites:
            self.assertIsInstance(referral_site, ReferralSite)
            self.assertIsInstance(referral_site.name, str)
            self.assertIsInstance(referral_site.is_frequent, bool)
            self.assertIsInstance(referral_site.is_default, bool)
            self.assertIsNotNone(referral_site.id)

    # Delete
    async def test_delete_referral_site_by_name_success(self):
        """Test successful deletion of a referral site by name via API"""
        # Create referral site first
        referral_site_data = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )
        await create_referral_site(referral_site_data, self.user)

        # Delete the referral site
        result = await delete_referral_site_name(
            "test_referral_site", self.user
        )
        self.assertEqual(
            result["message"], "Referral site deleted successfully."
        )

        # Verify referral site was deleted
        referral_sites = await get_referral_sites(self.user)
        referral_site_names = [r.name for r in referral_sites]
        self.assertNotIn("test_referral_site", referral_site_names)

    async def test_delete_referral_site_by_id_success(self):
        """Test successful deletion of a referral site by ID via API"""
        # Create referral site first
        referral_site_data = ReferralSite(
            name="test_referral_site",
            is_frequent=True,
            is_default=False,
        )
        await create_referral_site(referral_site_data, self.user)

        # Get referral site to find its ID
        referral_sites = await get_referral_sites(self.user)
        referral_site = next(
            (r for r in referral_sites if r.name == "test_referral_site"), None
        )
        self.assertIsNotNone(referral_site)
        referral_site_id = referral_site.id

        # Delete the referral site by ID
        result = await delete_referral_site_id(referral_site_id, self.user)
        self.assertEqual(
            result["message"], "Referral site deleted successfully."
        )

        # Verify referral site was deleted
        referral_sites = await get_referral_sites(self.user)
        referral_site_names = [r.name for r in referral_sites]
        self.assertNotIn("test_referral_site", referral_site_names)

    async def test_delete_referral_site_not_found_by_name(self):
        """Test deletion of non-existent referral site by name via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_referral_site_name(
                "non_existent_referral_site", self.user
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Referral site not found", context.exception.detail)

    async def test_delete_referral_site_not_found_by_id(self):
        """Test deletion of non-existent referral site by ID via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_referral_site_id(99999, self.user)  # Non-existent ID

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Referral site not found", context.exception.detail)

    # Update
    async def test_update_referral_site_success(self):
        """Test successful update of a referral site via API"""
        # Create referral site first
        referral_site_data = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )
        await create_referral_site(referral_site_data, self.user)

        # Get referral site to find its ID
        referral_sites = await get_referral_sites(self.user)
        referral_site = next(
            (r for r in referral_sites if r.name == "test_referral_site"), None
        )
        referral_site_id = referral_site.id

        # Update the referral site
        update_data = ReferralSiteUpdate(
            name="test_referral_site",
            is_frequent=True,
            is_default=True,
        )
        result = await update_referral_site(
            referral_site_id,
            update_data,
            self.user,
        )
        self.assertEqual(
            result["message"],
            "Referral site updated successfully.",
        )

        # Verify referral site was updated
        referral_sites = await get_referral_sites(self.user)
        updated_referral_site = next(
            (r for r in referral_sites if r.name == "test_referral_site"), None
        )

        self.assertIsNotNone(updated_referral_site)
        self.assertTrue(updated_referral_site.is_frequent)
        self.assertTrue(updated_referral_site.is_default)

    async def test_update_referral_site_partial(self):
        """Test partial update of a referral site via API"""
        # Create referral site first
        referral_site_data = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )
        await create_referral_site(referral_site_data, self.user)

        # Get referral site ID
        referral_sites = await get_referral_sites(self.user)
        referral_site = next(
            (r for r in referral_sites if r.name == "test_referral_site"), None
        )
        referral_site_id = referral_site.id

        # Partial update - only is_frequent
        update_data = ReferralSiteUpdate(
            is_frequent=True,
        )
        result = await update_referral_site(
            referral_site_id,
            update_data,
            self.user,
        )
        self.assertEqual(
            result["message"],
            "Referral site updated successfully.",
        )

        # Verify only is_frequent was updated
        referral_sites = await get_referral_sites(self.user)
        updated_referral_site = next(
            (r for r in referral_sites if r.name == "test_referral_site"), None
        )

        self.assertIsNotNone(updated_referral_site)
        self.assertTrue(updated_referral_site.is_frequent)
        self.assertFalse(updated_referral_site.is_default)

    async def test_update_referral_site_empty_updates(self):
        """Test update with no actual changes via API"""
        # Create referral site first
        referral_site_data = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )
        await create_referral_site(referral_site_data, self.user)

        # Get referral site ID
        referral_sites = await get_referral_sites(self.user)
        referral_site = next(
            (r for r in referral_sites if r.name == "test_referral_site"), None
        )
        referral_site_id = referral_site.id

        # Empty update
        update_data = ReferralSiteUpdate()

        with self.assertRaises(HTTPException) as context:
            await update_referral_site(
                referral_site_id, update_data, self.user
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Referral site not found or could not be updated",
            context.exception.detail,
        )

    async def test_update_referral_site_not_found(self):
        """Test update of non-existent referral site via API"""
        update_data = ReferralSiteUpdate(
            name="non_existent_referral_site",
            is_frequent=True,
        )

        with self.assertRaises(HTTPException) as context:
            await update_referral_site(99999, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Referral site not found or could not be updated",
            context.exception.detail,
        )
