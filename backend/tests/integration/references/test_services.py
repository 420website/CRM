# pyright: reportOptionalMemberAccess=none, reportArgumentType=none
import asyncio
from unittest import IsolatedAsyncioTestCase
from app.database import database
from app.references.schemas import (
    ReferenceOption,
    ReferenceOptionUpdate,
    ReferenceTemplate,
    ReferenceTemplateUpdate,
)
from app.references.services import (
    ReferenceOptionService,
    ReferenceTemplateService,
)


class TestReferenceOptionService(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        # Clean up test general sites
        types = ["interaction", "coverage"]
        test_names = [
            "test_general_site",
            "test_general_site_2",
            "updated_general_site",
            "default_general_site",
            "test_option",
            "default_option",
        ]
        for t in types:
            for name in test_names:
                try:
                    await ReferenceOptionService.delete_option(name, t)
                except Exception:
                    pass  # Ignore if general site doesn't exist

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        await self._cleanup_test_data()

    async def asyncTearDown(self) -> None:
        await database.disconnect()

    async def test_create_option_success(self):
        """Test successful creation of a option"""
        option = ReferenceOption(
            name="test_option",
            type="interaction",
            is_frequent=False,
            is_default=False,
        )

        # Test
        result = await ReferenceOptionService.create_option(option)
        self.assertTrue(result)

        # Validate
        options = await ReferenceOptionService.get_options("interaction")
        option = [t for t in options if t.name == "test_option"]

        self.assertEqual(option[0].name, "test_option")
        await ReferenceOptionService.delete_option(
            "test_option", "interaction"
        )

    async def test_check_option_exists(self):
        """Test creation of a default option"""
        option = ReferenceOption(
            name="default_option",
            type="coverage",
            is_frequent=True,
            is_default=True,
        )

        await ReferenceOptionService.create_option(option)

        # Test
        result = await ReferenceOptionService.check_exists(
            "default_option", "coverage"
        )
        self.assertTrue(result)

        result = await ReferenceOptionService.check_exists(
            "default_general_site", "interaction"
        )
        self.assertFalse(result)

    async def test_create_duplicate_name_diff_type_option(self):
        """Test creation of a default general site"""
        option = ReferenceOption(
            name="default_general_site",
            type="coverage",
            is_frequent=True,
            is_default=True,
        )

        await ReferenceOptionService.create_option(option)

        # Test
        option.type = "interaction"
        result = await ReferenceOptionService.create_option(option)
        self.assertIsNotNone(result)

    async def test_create_option_with_default(self):
        """Test creation of a default general site"""
        option = ReferenceOption(
            name="default_general_site",
            type="coverage",
            is_frequent=True,
            is_default=True,
        )

        # Test
        result = await ReferenceOptionService.create_option(option)
        self.assertTrue(result)

        # Validate
        options = await ReferenceOptionService.get_options("coverage")
        option = [t for t in options if t.name == "default_general_site"]

        self.assertEqual(option[0].name, "default_general_site")
        self.assertTrue(option[0].is_default)
        await ReferenceOptionService.delete_option(
            "default_general_site", "coverage"
        )

    async def test_create_duplicate_option_name(self):
        """Test creating general site with duplicate name (should handle gracefully)"""
        option = ReferenceOption(
            name="test_general_site",
            type="interaction",
            is_frequent=False,
            is_default=False,
        )

        # Create first general site
        result1 = await ReferenceOptionService.create_option(option)
        self.assertTrue(result1)

        # This might raise an exception or return False depending on implementation
        with self.assertRaises(Exception):
            await ReferenceOptionService.create_option(option)

        await ReferenceOptionService.delete_option(
            "test_general_site", "interaction"
        )

    async def test_get_option_empty(self):
        """Test getting general sites when none exist"""
        options = await ReferenceOptionService.get_options("other")
        self.assertIsInstance(options, list)
        # self.assertEqual(len(general_sites), 0)

    async def test_get_option_with_data(self):
        """Test getting general sites when data exists"""
        # Create test general sites
        option1 = ReferenceOption(
            name="test_general_site",
            type="interaction",
            is_frequent=False,
            is_default=False,
        )
        option2 = ReferenceOption(
            name="test_general_site_2",
            type="interaction",
            is_frequent=True,
            is_default=True,
        )

        await ReferenceOptionService.create_option(option1)
        await ReferenceOptionService.create_option(option2)

        options = await ReferenceOptionService.get_options("interaction")
        self.assertIsInstance(options, list)
        self.assertGreaterEqual(len(options), 2)

        # Verify our general sites are in the results
        option_names = [d.name for d in options]
        self.assertIn("test_general_site", option_names)
        self.assertIn("test_general_site_2", option_names)

        # Verify general site structure
        for option in options:
            self.assertIsInstance(option, ReferenceOption)
            self.assertIsInstance(option.name, str)
            self.assertIsInstance(option.is_frequent, bool)
            self.assertIsInstance(option.is_default, bool)

        await ReferenceOptionService.delete_option(
            "test_general_site", "interaction"
        )
        await ReferenceOptionService.delete_option(
            "test_general_site_2", "interaction"
        )

    async def test_delete_option_success(self):
        """Test successful deletion of a general site"""
        # Create general site first
        option = ReferenceOption(
            name="test_general_site",
            type="coverage",
            is_frequent=False,
            is_default=False,
        )

        await ReferenceOptionService.create_option(option)

        # Delete the general site
        result = await ReferenceOptionService.delete_option(
            "test_general_site", "coverage"
        )
        self.assertTrue(result)

        # Verify general site was deleted
        options = await ReferenceOptionService.get_options("coverage")
        option_names = [d.name for d in options]
        self.assertNotIn("test_general_site", option_names)

    async def test_delete_option_not_found(self):
        """Test deletion of non-existent general site"""
        result = await ReferenceOptionService.delete_option(
            "non_existent_general_site", "other"
        )
        self.assertFalse(result)

    async def test_update_option_success(self):
        """Test successful update of a general site"""
        # Create general site first
        option = ReferenceOption(
            name="test_general_site",
            type="interaction",
            is_frequent=False,
            is_default=False,
        )

        id = await ReferenceOptionService.create_option(option)

        # Update the general site
        update_data = ReferenceOptionUpdate(
            name="test_general_site",
            is_frequent=True,
            is_default=True,
        )

        result = await ReferenceOptionService.update_option(id, update_data)
        self.assertTrue(result)

        # Verify general site was updated
        options = await ReferenceOptionService.get_options("interaction")
        option = [t for t in options if t.name == "test_general_site"]
        self.assertIsNotNone(option[0])
        self.assertTrue(option[0].is_frequent)
        self.assertTrue(option[0].is_default)

        await ReferenceOptionService.delete_option(
            "test_general_site", "interaction"
        )

    async def test_update_option_partial(self):
        """Test partial update of a general site"""
        # Create general site first
        option = ReferenceOption(
            name="test_general_site",
            type="coverage",
            is_frequent=False,
            is_default=False,
        )

        id = await ReferenceOptionService.create_option(option)

        # Partial update - only is_frequent
        update_data = ReferenceOptionUpdate(
            name="test_general_site",
            is_frequent=True,
        )

        # general_sites = await GeneralService.get_general_sites()
        result = await ReferenceOptionService.update_option(id, update_data)
        self.assertTrue(result)

        # Verify only is_frequent was updated
        options = await ReferenceOptionService.get_options("coverage")
        option = [t for t in options if t.name == "test_general_site"]
        self.assertIsNotNone(option[0])
        self.assertTrue(option[0].is_frequent)
        self.assertFalse(option[0].is_default)

        await ReferenceOptionService.delete_option(
            "test_general_site", "coverage"
        )

    async def test_update_option_empty_updates(self):
        """Test update with no actual changes"""
        # Create general site first
        option = ReferenceOption(
            name="test_general_site",
            type="interaction",
            is_frequent=False,
            is_default=False,
        )

        id = await ReferenceOptionService.create_option(option)

        # Empty update
        update_data = ReferenceOptionUpdate()
        result = await ReferenceOptionService.update_option(id, update_data)
        self.assertFalse(result)

        await ReferenceOptionService.delete_option(
            "test_general_site", "interaction"
        )

    async def test_update_option_not_found(self):
        """Test update of non-existent general site"""
        update_data = ReferenceOptionUpdate(
            name="non_existent_general_site",
            is_frequent=True,
        )

        result = await ReferenceOptionService.update_option(1000, update_data)
        self.assertFalse(result)


class TestReferenceTemplateService(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        # Clean up test general sites
        types = ["interaction", "coverage"]
        test_names = [
            "test_general_site",
            "test_general_site_2",
            "updated_general_site",
            "default_general_site",
        ]
        for t in types:
            for name in test_names:
                try:
                    await ReferenceTemplateService.delete_template(name, t)
                except Exception:
                    pass  # Ignore if general site doesn't exist

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        await self._cleanup_test_data()

    async def asyncTearDown(self) -> None:
        await database.disconnect()

    async def test_create_template_success(self):
        """Test successful creation of a general site"""
        template = ReferenceTemplate(
            name="test_general_site",
            type="interaction",
            content="This is a test template content",
            is_default=False,
        )

        # Test
        result = await ReferenceTemplateService.create_template(template)
        self.assertTrue(result)

        # Validate
        templates = await ReferenceTemplateService.get_templates("interaction")
        template = [t for t in templates if t.name == "test_general_site"]

        self.assertEqual(templates[0].name, "test_general_site")
        await ReferenceTemplateService.delete_template(
            "test_general_site", "interaction"
        )

    async def test_check_exists(self):
        """Test creation of a default general site"""
        template = ReferenceTemplate(
            name="default_general_site",
            type="coverage",
            content="This is a test template content",
            is_default=True,
        )

        await ReferenceTemplateService.create_template(template)

        # Test
        result = await ReferenceTemplateService.check_exists(
            "default_general_site", "coverage"
        )
        self.assertTrue(result)

        result = await ReferenceTemplateService.check_exists(
            "default_general_site", "interaction"
        )
        self.assertFalse(result)

    async def test_create_duplicate_name_diff_type_template(self):
        """Test creation of a default general site"""
        template = ReferenceTemplate(
            name="default_general_site",
            type="coverage",
            content="This is a test template content",
            is_default=True,
        )

        await ReferenceTemplateService.create_template(template)

        # Test
        template.type = "interaction"
        result = await ReferenceTemplateService.create_template(template)
        self.assertIsNotNone(result)

    async def test_create_template_with_default(self):
        """Test creation of a default general site"""
        template = ReferenceTemplate(
            name="default_general_site",
            type="coverage",
            content="This is a test template content",
            is_default=True,
        )

        # Test
        result = await ReferenceTemplateService.create_template(template)
        self.assertTrue(result)

        # Validate
        templates = await ReferenceTemplateService.get_templates("coverage")
        template = [t for t in templates if t.name == "default_general_site"]

        self.assertEqual(template[0].name, "default_general_site")
        self.assertTrue(template[0].is_default)
        await ReferenceTemplateService.delete_template(
            "default_general_site", "coverage"
        )

    async def test_create_duplicate_template_name(self):
        """Test creating general site with duplicate name (should handle gracefully)"""
        template = ReferenceTemplate(
            name="test_general_site",
            type="interaction",
            content="This is a test template content",
            is_default=False,
        )

        # Create first general site
        result1 = await ReferenceTemplateService.create_template(template)
        self.assertTrue(result1)

        # This might raise an exception or return False depending on implementation
        with self.assertRaises(Exception):
            await ReferenceTemplateService.create_template(template)

        await ReferenceTemplateService.delete_template(
            "test_general_site", "interaction"
        )

    async def test_get_template_empty(self):
        """Test getting general sites when none exist"""
        templates = await ReferenceTemplateService.get_templates("other")
        self.assertIsInstance(templates, list)
        # self.assertEqual(len(general_sites), 0)

    async def test_get_template_with_data(self):
        """Test getting general sites when data exists"""
        # Create test general sites
        template1 = ReferenceTemplate(
            name="test_general_site",
            type="interaction",
            content="This is a test template content",
            is_default=False,
        )
        template2 = ReferenceTemplate(
            name="test_general_site_2",
            type="interaction",
            content="This is a test template content",
            is_default=True,
        )

        await ReferenceTemplateService.create_template(template1)
        await ReferenceTemplateService.create_template(template2)

        templates = await ReferenceTemplateService.get_templates("interaction")
        self.assertIsInstance(templates, list)
        self.assertGreaterEqual(len(templates), 2)

        # Verify our general sites are in the results
        template_names = [d.name for d in templates]
        self.assertIn("test_general_site", template_names)
        self.assertIn("test_general_site_2", template_names)

        # Verify general site structure
        for template in templates:
            self.assertIsInstance(template, ReferenceTemplate)
            self.assertIsInstance(template.name, str)
            self.assertIsInstance(template.content, str)
            self.assertIsInstance(template.is_default, bool)

        await ReferenceTemplateService.delete_template(
            "test_general_site", "interaction"
        )
        await ReferenceTemplateService.delete_template(
            "test_general_site_2", "interaction"
        )

    async def test_delete_template_success(self):
        """Test successful deletion of a general site"""
        # Create general site first
        template = ReferenceTemplate(
            name="test_general_site",
            type="coverage",
            content="This is a test template content",
            is_default=False,
        )

        await ReferenceTemplateService.create_template(template)

        # Delete the general site
        result = await ReferenceTemplateService.delete_template(
            "test_general_site", "coverage"
        )
        self.assertTrue(result)

        # Verify general site was deleted
        templates = await ReferenceTemplateService.get_templates("coverage")
        template_names = [d.name for d in templates]
        self.assertNotIn("test_general_site", template_names)

    async def test_delete_template_not_found(self):
        """Test deletion of non-existent general site"""
        result = await ReferenceTemplateService.delete_template(
            "non_existent_general_site", "other"
        )
        self.assertFalse(result)

    async def test_update_template_success(self):
        """Test successful update of a general site"""
        # Create general site first
        template = ReferenceTemplate(
            name="test_general_site",
            type="interaction",
            content="This is a test template content",
            is_default=False,
        )

        id = await ReferenceTemplateService.create_template(template)

        # Update the general site
        update_data = ReferenceTemplateUpdate(
            name="test_general_site",
            is_default=True,
        )

        result = await ReferenceTemplateService.update_template(
            id, update_data
        )
        self.assertTrue(result)

        # Verify general site was updated
        templates = await ReferenceTemplateService.get_templates("interaction")
        template = [t for t in templates if t.name == "test_general_site"]

        self.assertIsNotNone(template[0])
        self.assertIsNotNone(template[0].content)
        self.assertTrue(template[0].is_default)

        await ReferenceTemplateService.delete_template(
            "test_general_site", "interaction"
        )

    async def test_update_template_partial(self):
        """Test partial update of a general site"""
        # Create general site first
        template = ReferenceTemplate(
            name="test_general_site",
            type="coverage",
            content="This is a test template content",
            is_default=False,
        )

        id = await ReferenceTemplateService.create_template(template)

        # Partial update - only is_frequent
        update_data = ReferenceTemplateUpdate(
            name="test_general_site",
            content="new content",
        )

        # general_sites = await GeneralService.get_general_sites()
        result = await ReferenceTemplateService.update_template(
            id, update_data
        )
        self.assertTrue(result)

        # Verify only is_frequent was updated
        templates = await ReferenceTemplateService.get_templates("coverage")
        template = [t for t in templates if t.name == "test_general_site"]

        self.assertIsNotNone(template[0])
        self.assertEqual(template[0].content, "new content")
        self.assertFalse(template[0].is_default)

        await ReferenceTemplateService.delete_template(
            "test_general_site", "coverage"
        )

    async def test_update_templates_empty_updates(self):
        """Test update with no actual changes"""
        # Create general site first
        template = ReferenceTemplate(
            name="test_general_site",
            type="interaction",
            content="This is a test template content",
            is_default=False,
        )

        id = await ReferenceTemplateService.create_template(template)

        # Empty update
        update_data = ReferenceTemplateUpdate()
        result = await ReferenceTemplateService.update_template(
            id, update_data
        )
        self.assertFalse(result)

        await ReferenceTemplateService.delete_template(
            "test_general_site", "interaction"
        )

    async def test_update_templates_not_found(self):
        """Test update of non-existent general site"""
        update_data = ReferenceTemplateUpdate(
            name="non_existent_general_site",
        )

        result = await ReferenceTemplateService.update_template(
            1000, update_data
        )
        self.assertFalse(result)
