# pyright: reportOptionalMemberAccess=none, reportArgumentType=none
import asyncio
from unittest import IsolatedAsyncioTestCase
from app.general.schemas import (
    ClinicalTemplate,
    ClinicalTemplateUpdate,
    Disposition,
    DispositionUpdate,
    NotesTemplate,
    NotesTemplateUpdate,
    ReferralSite,
    ReferralSiteUpdate,
)
from app.database import database
from app.general.services import GeneralService


class TestGeneralServiceNotes(IsolatedAsyncioTestCase):
    """Integration tests for GeneralService - requires test database setup"""

    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        # Clean up test templates
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
                pass  # Ignore if template doesn't exist

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)

        await database.connect()
        await self._cleanup_test_data()

    async def asyncTearDown(self) -> None:
        await database.disconnect()

    async def test_create_notes_template_success(self):
        """Test successful creation of a notes template"""
        template = NotesTemplate(
            name="test_template",
            content="This is a test template content",
            is_default=False,
        )

        # Test
        result = await GeneralService.create_notes_template(template)
        self.assertTrue(result)

        # Validate
        templates = await GeneralService.get_note_templates()
        note = [t for t in templates if t.name == "test_template"]

        self.assertTrue(note[0].name == "test_template")

        await GeneralService.delete_notes_template("test_template")

    async def test_create_notes_template_with_default(self):
        """Test creation of a default notes template"""
        template = NotesTemplate(
            name="default_template",
            content="Default template content",
            is_default=True,
        )

        # Test
        result = await GeneralService.create_notes_template(template)
        self.assertTrue(result)

        # Validate
        templates = await GeneralService.get_note_templates()
        note = [t for t in templates if t.name == "default_template"]

        self.assertEqual(note[0].name, "default_template")
        self.assertTrue(note[0].is_default)

        await GeneralService.delete_notes_template("default_template")

    async def test_create_duplicate_template_name(self):
        """Test creating template with duplicate name (should handle gracefully)"""
        template = NotesTemplate(
            name="test_template",
            content="First template",
            is_default=False,
        )

        # Create first template
        result1 = await GeneralService.create_notes_template(template)
        self.assertTrue(result1)

        # This might raise an exception or return False depending on implementation
        with self.assertRaises(Exception):
            await GeneralService.create_notes_template(template)

        await GeneralService.delete_notes_template("test_template")

    async def test_get_notes_template_empty(self):
        """Test getting templates when none exist"""
        templates = await GeneralService.get_note_templates()

        self.assertIsInstance(templates, list)

    async def test_get_notes_template_with_data(self):
        """Test getting templates when data exists"""
        # Create test templates
        template1 = NotesTemplate(
            name="test_template",
            content="Template 1 content",
            is_default=False,
        )
        template2 = NotesTemplate(
            name="test_template_2",
            content="Template 2 content",
            is_default=True,
        )

        await GeneralService.create_notes_template(template1)
        await GeneralService.create_notes_template(template2)

        templates = await GeneralService.get_note_templates()

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

        await GeneralService.delete_notes_template("test_template")
        await GeneralService.delete_notes_template("test_template_2")

    async def test_delete_notes_template_success(self):
        """Test successful deletion of a notes template"""
        # Create template first
        template = NotesTemplate(
            name="test_template",
            content="Template to delete",
            is_default=False,
        )
        await GeneralService.create_notes_template(template)

        # Delete the template
        result = await GeneralService.delete_notes_template("test_template")
        self.assertTrue(result)

        # Verify template was deleted
        templates = await GeneralService.get_note_templates()
        template_names = [t.name for t in templates]
        self.assertNotIn("test_template", template_names)

    async def test_delete_notes_template_not_found(self):
        """Test deletion of non-existent template"""
        result = await GeneralService.delete_notes_template(
            "non_existent_template"
        )

        self.assertFalse(result)

    async def test_update_notes_template_success(self):
        """Test successful update of a notes template"""
        # Create template first
        template = NotesTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        id = await GeneralService.create_notes_template(template)

        # Update the template
        update_data = NotesTemplateUpdate(
            name="test_template",
            content="Updated content",
            is_default=True,
        )

        result = await GeneralService.update_notes_template(id, update_data)
        self.assertTrue(result)

        # Verify template was updated
        templates = await GeneralService.get_note_templates()
        note = [t for t in templates if t.name == "test_template"]

        self.assertIsNotNone(note[0])
        self.assertEqual(note[0].content, "Updated content")
        self.assertTrue(note[0].is_default)

        await GeneralService.delete_notes_template("test_template")

    async def test_update_notes_template_partial(self):
        """Test partial update of a notes template"""
        # Create template first
        template = NotesTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        id = await GeneralService.create_notes_template(template)

        # Partial update - only content
        update_data = NotesTemplateUpdate(
            name="test_template",
            content="Partially updated content",
        )

        templates = await GeneralService.get_note_templates()
        note = [t for t in templates if t.name == "test_template"]

        result = await GeneralService.update_notes_template(id, update_data)
        self.assertTrue(result)

        # Verify only content was updated
        templates = await GeneralService.get_note_templates()
        note = [t for t in templates if t.name == "test_template"]

        self.assertIsNotNone(note[0])
        self.assertEqual(note[0].content, "Partially updated content")
        self.assertFalse(note[0].is_default)

        await GeneralService.delete_notes_template("test_template")

    async def test_update_notes_template_empty_updates(self):
        """Test update with no actual changes"""
        # Create template first
        template = NotesTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        id = await GeneralService.create_notes_template(template)

        # Empty update
        update_data = NotesTemplateUpdate()
        result = await GeneralService.update_notes_template(id, update_data)

        self.assertFalse(result)

        await GeneralService.delete_notes_template("test_template")

    async def test_update_notes_template_not_found(self):
        """Test update of non-existent template"""
        update_data = NotesTemplateUpdate(
            name="non_existent_template",
            content="New content",
        )

        result = await GeneralService.update_notes_template(1000, update_data)

        self.assertFalse(result)


class TestGeneralServiceClinical(IsolatedAsyncioTestCase):

    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        # Clean up test templates
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
                pass  # Ignore if template doesn't exist

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)

        await database.connect()
        await self._cleanup_test_data()

    async def asyncTearDown(self) -> None:
        await database.disconnect()

    async def test_create_clinical_template_success(self):
        """Test successful creation of a clinical template"""
        template = ClinicalTemplate(
            name="test_template",
            content="This is a test template content",
            is_default=False,
        )

        # Test
        result = await GeneralService.create_clinical_template(template)
        self.assertTrue(result)

        # Validate
        templates = await GeneralService.get_clinical_templates()
        template = [t for t in templates if t.name == "test_template"]
        self.assertEqual(template[0].name, "test_template")

        await GeneralService.delete_clinical_template("test_template")

    async def test_create_clinical_template_with_default(self):
        """Test creation of a default clinical template"""
        template = ClinicalTemplate(
            name="default_template",
            content="Default template content",
            is_default=True,
        )

        # Test
        result = await GeneralService.create_clinical_template(template)
        self.assertTrue(result)

        # Validate
        templates = await GeneralService.get_clinical_templates()
        template = [t for t in templates if t.name == "default_template"]

        self.assertEqual(template[0].name, "default_template")
        self.assertTrue(template[0].is_default)

        await GeneralService.delete_clinical_template("default_template")

    async def test_create_duplicate_template_name(self):
        """Test creating template with duplicate name (should handle gracefully)"""
        template = ClinicalTemplate(
            name="test_template",
            content="First template",
            is_default=False,
        )

        # Create first template
        result1 = await GeneralService.create_clinical_template(template)
        self.assertTrue(result1)

        # This might raise an exception or return False depending on implementation
        with self.assertRaises(Exception):
            await GeneralService.create_clinical_template(template)

        await GeneralService.delete_clinical_template("test_template")

    async def test_get_clinical_template_empty(self):
        """Test getting templates when none exist"""
        templates = await GeneralService.get_clinical_templates()

        self.assertIsInstance(templates, list)

    async def test_get_clinical_template_with_data(self):
        """Test getting templates when data exists"""
        # Create test templates
        template1 = ClinicalTemplate(
            name="test_template",
            content="Template 1 content",
            is_default=False,
        )
        template2 = ClinicalTemplate(
            name="test_template_2",
            content="Template 2 content",
            is_default=True,
        )

        await GeneralService.create_clinical_template(template1)
        await GeneralService.create_clinical_template(template2)

        templates = await GeneralService.get_clinical_templates()

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

        await GeneralService.delete_clinical_template("test_template")
        await GeneralService.delete_clinical_template("test_template_2")

    async def test_delete_clinical_template_success(self):
        """Test successful deletion of a clinical template"""
        # Create template first
        template = ClinicalTemplate(
            name="test_template",
            content="Template to delete",
            is_default=False,
        )
        await GeneralService.create_clinical_template(template)

        # Delete the template
        result = await GeneralService.delete_clinical_template("test_template")
        self.assertTrue(result)

        # Verify template was deleted
        templates = await GeneralService.get_clinical_templates()
        template_names = [t.name for t in templates]
        self.assertNotIn("test_template", template_names)

    async def test_delete_clinical_template_not_found(self):
        """Test deletion of non-existent template"""
        result = await GeneralService.delete_clinical_template(
            "non_existent_template"
        )

        self.assertFalse(result)

    async def test_update_clinical_template_success(self):
        """Test successful update of a clinical template"""
        # Create template first
        template = ClinicalTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        id = await GeneralService.create_clinical_template(template)

        # Update the template
        update_data = ClinicalTemplateUpdate(
            name="test_template",
            content="Updated content",
            is_default=True,
        )

        result = await GeneralService.update_clinical_template(id, update_data)
        self.assertTrue(result)

        # Verify template was updated
        templates = await GeneralService.get_clinical_templates()
        template = [t for t in templates if t.name == "test_template"]

        self.assertIsNotNone(template[0])
        self.assertEqual(template[0].content, "Updated content")
        self.assertTrue(template[0].is_default)

        await GeneralService.delete_clinical_template("test_template")

    async def test_update_clinical_template_partial(self):
        """Test partial update of a clinical template"""
        # Create template first
        template = ClinicalTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        id = await GeneralService.create_clinical_template(template)

        # Partial update - only content
        update_data = ClinicalTemplateUpdate(
            name="test_template",
            content="Partially updated content",
        )

        result = await GeneralService.update_clinical_template(id, update_data)
        self.assertTrue(result)

        # Verify only content was updated
        templates = await GeneralService.get_clinical_templates()
        template = [t for t in templates if t.name == "test_template"]

        self.assertIsNotNone(template[0])
        self.assertEqual(template[0].content, "Partially updated content")
        self.assertFalse(template[0].is_default)

        await GeneralService.delete_clinical_template("test_template")

    async def test_update_clinical_template_empty_updates(self):
        """Test update with no actual changes"""
        # Create template first
        template = ClinicalTemplate(
            name="test_template",
            content="Original content",
            is_default=False,
        )
        id = await GeneralService.create_clinical_template(template)

        # Empty update
        update_data = ClinicalTemplateUpdate()
        result = await GeneralService.update_clinical_template(id, update_data)

        self.assertFalse(result)

        await GeneralService.delete_clinical_template("test_template")

    async def test_update_clinical_template_not_found(self):
        """Test update of non-existent template"""
        update_data = ClinicalTemplateUpdate(
            name="non_existent_template",
            content="New content",
        )

        result = await GeneralService.update_clinical_template(
            1000, update_data
        )

        self.assertFalse(result)


class TestGeneralServiceDisposition(IsolatedAsyncioTestCase):

    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        # Clean up test dispositions
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
                pass  # Ignore if disposition doesn't exist

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)

        await database.connect()
        await self._cleanup_test_data()

    async def asyncTearDown(self) -> None:
        await database.disconnect()

    async def test_create_disposition_success(self):
        """Test successful creation of a disposition"""
        disposition = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )

        # Test
        result = await GeneralService.create_disposition(disposition)
        self.assertTrue(result)

        # Validate
        dispositions = await GeneralService.get_dispositions()
        disposition = [t for t in dispositions if t.name == "test_disposition"]
        self.assertEqual(disposition[0].name, "test_disposition")

        await GeneralService.delete_disposition("test_disposition")

    async def test_create_disposition_with_default(self):
        """Test creation of a default disposition"""
        disposition = Disposition(
            name="default_disposition",
            is_frequent=True,
            is_default=True,
        )

        # Test
        result = await GeneralService.create_disposition(disposition)
        self.assertTrue(result)

        # Validate
        dispositions = await GeneralService.get_dispositions()
        disposition = [
            t for t in dispositions if t.name == "default_disposition"
        ]

        self.assertEqual(disposition[0].name, "default_disposition")
        self.assertTrue(disposition[0].is_default)

        await GeneralService.delete_disposition("default_disposition")

    async def test_create_duplicate_disposition_name(self):
        """Test creating disposition with duplicate name (should handle gracefully)"""
        disposition = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )

        # Create first disposition
        result1 = await GeneralService.create_disposition(disposition)
        self.assertTrue(result1)

        # This might raise an exception or return False depending on implementation
        with self.assertRaises(Exception):
            await GeneralService.create_disposition(disposition)

        await GeneralService.delete_disposition("test_disposition")

    async def test_get_disposition_empty(self):
        """Test getting dispositions when none exist"""
        dispositions = await GeneralService.get_dispositions()

        self.assertIsInstance(dispositions, list)

    async def test_get_disposition_with_data(self):
        """Test getting dispositions when data exists"""
        # Create test dispositions
        disposition1 = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )
        disposition2 = Disposition(
            name="test_disposition_2",
            is_frequent=True,
            is_default=True,
        )

        await GeneralService.create_disposition(disposition1)
        await GeneralService.create_disposition(disposition2)

        dispositions = await GeneralService.get_dispositions()

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

        await GeneralService.delete_disposition("test_disposition")
        await GeneralService.delete_disposition("test_disposition_2")

    async def test_delete_disposition_success(self):
        """Test successful deletion of a disposition"""
        # Create disposition first
        disposition = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )
        await GeneralService.create_disposition(disposition)

        # Delete the disposition
        result = await GeneralService.delete_disposition("test_disposition")
        self.assertTrue(result)

        # Verify disposition was deleted
        dispositions = await GeneralService.get_dispositions()
        disposition_names = [d.name for d in dispositions]
        self.assertNotIn("test_disposition", disposition_names)

    async def test_delete_disposition_not_found(self):
        """Test deletion of non-existent disposition"""
        result = await GeneralService.delete_disposition(
            "non_existent_disposition"
        )

        self.assertFalse(result)

    async def test_update_disposition_success(self):
        """Test successful update of a disposition"""
        # Create disposition first
        disposition = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )
        id = await GeneralService.create_disposition(disposition)

        # Update the disposition
        update_data = DispositionUpdate(
            name="test_disposition",
            is_frequent=True,
            is_default=True,
        )

        result = await GeneralService.update_disposition(id, update_data)
        self.assertTrue(result)

        # Verify disposition was updated
        dispositions = await GeneralService.get_dispositions()
        disposition = [t for t in dispositions if t.name == "test_disposition"]

        self.assertIsNotNone(disposition[0])
        self.assertTrue(disposition[0].is_frequent)
        self.assertTrue(disposition[0].is_default)

        await GeneralService.delete_disposition("test_disposition")

    async def test_update_disposition_partial(self):
        """Test partial update of a disposition"""
        # Create disposition first
        disposition = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )
        id = await GeneralService.create_disposition(disposition)

        # Partial update - only is_frequent
        update_data = DispositionUpdate(
            name="test_disposition",
            is_frequent=True,
        )

        result = await GeneralService.update_disposition(id, update_data)
        self.assertTrue(result)

        # Verify only is_frequent was updated
        dispositions = await GeneralService.get_dispositions()
        disposition = [t for t in dispositions if t.name == "test_disposition"]

        self.assertIsNotNone(disposition[0])
        self.assertTrue(disposition[0].is_frequent)
        self.assertFalse(disposition[0].is_default)

        await GeneralService.delete_disposition("test_disposition")

    async def test_update_disposition_empty_updates(self):
        """Test update with no actual changes"""
        # Create disposition first
        disposition = Disposition(
            name="test_disposition",
            is_frequent=False,
            is_default=False,
        )
        id = await GeneralService.create_disposition(disposition)

        # Empty update
        update_data = DispositionUpdate()
        result = await GeneralService.update_disposition(id, update_data)

        self.assertFalse(result)

        await GeneralService.delete_disposition("test_disposition")

    async def test_update_disposition_not_found(self):
        """Test update of non-existent disposition"""
        update_data = DispositionUpdate(
            name="non_existent_disposition",
            is_frequent=True,
        )

        result = await GeneralService.update_disposition(1000, update_data)

        self.assertFalse(result)


class TestGeneralServiceReferralSite(IsolatedAsyncioTestCase):

    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        # Clean up test referral sites
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
                pass  # Ignore if referral site doesn't exist

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)

        await database.connect()
        await self._cleanup_test_data()

    async def asyncTearDown(self) -> None:
        await database.disconnect()

    async def test_create_referral_site_success(self):
        """Test successful creation of a referral site"""
        referral_site = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )

        # Test
        result = await GeneralService.create_referral_site(referral_site)
        self.assertTrue(result)

        # Validate
        referral_sites = await GeneralService.get_referral_sites()
        referral_site = [
            t for t in referral_sites if t.name == "test_referral_site"
        ]
        self.assertEqual(referral_site[0].name, "test_referral_site")

        await GeneralService.delete_referral_site("test_referral_site")

    async def test_create_referral_site_with_default(self):
        """Test creation of a default referral site"""
        referral_site = ReferralSite(
            name="default_referral_site",
            is_frequent=True,
            is_default=True,
        )

        # Test
        result = await GeneralService.create_referral_site(referral_site)
        self.assertTrue(result)

        # Validate
        referral_sites = await GeneralService.get_referral_sites()
        referral_site = [
            t for t in referral_sites if t.name == "default_referral_site"
        ]

        self.assertEqual(referral_site[0].name, "default_referral_site")
        self.assertTrue(referral_site[0].is_default)

        await GeneralService.delete_referral_site("default_referral_site")

    async def test_create_duplicate_referral_site_name(self):
        """Test creating referral site with duplicate name (should handle gracefully)"""
        referral_site = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )

        # Create first referral site
        result1 = await GeneralService.create_referral_site(referral_site)
        self.assertTrue(result1)

        # This might raise an exception or return False depending on implementation
        with self.assertRaises(Exception):
            await GeneralService.create_referral_site(referral_site)

        await GeneralService.delete_referral_site("test_referral_site")

    async def test_get_referral_site_empty(self):
        """Test getting referral sites when none exist"""
        referral_sites = await GeneralService.get_referral_sites()

        self.assertIsInstance(referral_sites, list)
        # self.assertEqual(len(referral_sites), 0)

    async def test_get_referral_site_with_data(self):
        """Test getting referral sites when data exists"""
        # Create test referral sites
        referral_site1 = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )
        referral_site2 = ReferralSite(
            name="test_referral_site_2",
            is_frequent=True,
            is_default=True,
        )

        await GeneralService.create_referral_site(referral_site1)
        await GeneralService.create_referral_site(referral_site2)

        referral_sites = await GeneralService.get_referral_sites()

        self.assertIsInstance(referral_sites, list)
        self.assertGreaterEqual(len(referral_sites), 2)

        # Verify our referral sites are in the results
        referral_site_names = [d.name for d in referral_sites]
        self.assertIn("test_referral_site", referral_site_names)
        self.assertIn("test_referral_site_2", referral_site_names)

        # Verify referral site structure
        for referral_site in referral_sites:
            self.assertIsInstance(referral_site, ReferralSite)
            self.assertIsInstance(referral_site.name, str)
            self.assertIsInstance(referral_site.is_frequent, bool)
            self.assertIsInstance(referral_site.is_default, bool)

        await GeneralService.delete_referral_site("test_referral_site")
        await GeneralService.delete_referral_site("test_referral_site_2")

    async def test_delete_referral_site_success(self):
        """Test successful deletion of a referral site"""
        # Create referral site first
        referral_site = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )
        await GeneralService.create_referral_site(referral_site)

        # Delete the referral site
        result = await GeneralService.delete_referral_site(
            "test_referral_site"
        )
        self.assertTrue(result)

        # Verify referral site was deleted
        referral_sites = await GeneralService.get_referral_sites()
        referral_site_names = [d.name for d in referral_sites]
        self.assertNotIn("test_referral_site", referral_site_names)

    async def test_delete_referral_site_not_found(self):
        """Test deletion of non-existent referral site"""
        result = await GeneralService.delete_referral_site(
            "non_existent_referral_site"
        )

        self.assertFalse(result)

    async def test_update_referral_site_success(self):
        """Test successful update of a referral site"""
        # Create referral site first
        referral_site = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )
        id = await GeneralService.create_referral_site(referral_site)

        # Update the referral site
        update_data = ReferralSiteUpdate(
            name="test_referral_site",
            is_frequent=True,
            is_default=True,
        )

        result = await GeneralService.update_referral_site(id, update_data)
        self.assertTrue(result)

        # Verify referral site was updated
        referral_sites = await GeneralService.get_referral_sites()
        referral_site = [
            t for t in referral_sites if t.name == "test_referral_site"
        ]

        self.assertIsNotNone(referral_site[0])
        self.assertTrue(referral_site[0].is_frequent)
        self.assertTrue(referral_site[0].is_default)

        await GeneralService.delete_referral_site("test_referral_site")

    async def test_update_referral_site_partial(self):
        """Test partial update of a referral site"""
        # Create referral site first
        referral_site = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )
        id = await GeneralService.create_referral_site(referral_site)

        # Partial update - only is_frequent
        update_data = ReferralSiteUpdate(
            name="test_referral_site",
            is_frequent=True,
        )

        # referral_sites = await GeneralService.get_referral_sites()
        result = await GeneralService.update_referral_site(id, update_data)
        self.assertTrue(result)

        # Verify only is_frequent was updated
        referral_sites = await GeneralService.get_referral_sites()
        referral_site = [
            t for t in referral_sites if t.name == "test_referral_site"
        ]

        self.assertIsNotNone(referral_site[0])
        self.assertTrue(referral_site[0].is_frequent)
        self.assertFalse(referral_site[0].is_default)

        await GeneralService.delete_referral_site("test_referral_site")

    async def test_update_referral_site_empty_updates(self):
        """Test update with no actual changes"""
        # Create referral site first
        referral_site = ReferralSite(
            name="test_referral_site",
            is_frequent=False,
            is_default=False,
        )
        id = await GeneralService.create_referral_site(referral_site)

        # Empty update
        update_data = ReferralSiteUpdate()
        result = await GeneralService.update_referral_site(id, update_data)

        self.assertFalse(result)

        await GeneralService.delete_referral_site("test_referral_site")

    async def test_update_referral_site_not_found(self):
        """Test update of non-existent referral site"""
        update_data = ReferralSiteUpdate(
            name="non_existent_referral_site",
            is_frequent=True,
        )

        result = await GeneralService.update_referral_site(1000, update_data)

        self.assertFalse(result)
