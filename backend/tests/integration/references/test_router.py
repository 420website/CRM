# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportOperatorIssue=none
import asyncio
from unittest import IsolatedAsyncioTestCase
from fastapi import HTTPException
from app.authentication.schemas import UserRead
from app.database import database
from app.references.router import (
    create_option_type,
    create_template,
    delete_option_id,
    delete_option_name,
    delete_template_id,
    delete_template_name,
    get_option_type,
    get_templates,
    update_option,
    update_template,
)
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


email = "test444@example.com"
password = "securepassword123"


class TestReferecenceOptionAPI(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        types = ["interaction", "coverage"]

        test_names = [
            "test_general",
            "test_general_2",
            "updated_general",
            "default_general",
        ]
        for t in types:
            for name in test_names:
                try:
                    await ReferenceOptionService.delete_option(name, t)
                except Exception:
                    pass  # Ignore if general site doesn't exist

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
            province="Ontario",
            location_permissions=[],
        )

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        await database.disconnect()

    # Create
    async def test_create_option_success(self):
        """Test successful creation of a general via API"""
        option = ReferenceOption(
            name="test_general",
            type="interaction",
            is_frequent=False,
            is_default=False,
        )

        # Test
        result = await create_option_type(option, self.user)
        self.assertEqual(
            result["message"],
            "Option created successfully.",
        )

        # Validate by getting generals
        options = await get_option_type("interaction", self.user)
        option_names = [o.name for o in options]

        self.assertIn("test_general", option_names)

    async def test_create_option_with_default(self):
        """Test creation of a default general via API"""
        data = ReferenceOption(
            name="default_general",
            type="coverage",
            is_frequent=True,
            is_default=True,
        )

        # Test
        result = await create_option_type(data, self.user)
        self.assertEqual(
            result["message"],
            "Option created successfully.",
        )

        # Validate
        options = await get_option_type("coverage", self.user)
        default = next(
            (g for g in options if g.name == "default_general"),
            None,
        )
        self.assertIsNotNone(default)
        self.assertTrue(default.is_default)
        self.assertTrue(default.is_frequent)
        self.assertEqual(default.type, "coverage")

    async def test_create_duplicate_option_name(self):
        """Test creating general with duplicate name via API"""
        data = ReferenceOption(
            name="test_general",
            type="coverage",
            is_frequent=False,
            is_default=False,
        )

        # Create first general
        result1 = await create_option_type(data, self.user)
        self.assertEqual(
            result1["message"],
            "Option created successfully.",
        )

        # Try to create duplicate - should raise HTTPException
        with self.assertRaises(HTTPException) as context:
            await create_option_type(data, self.user)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Option already exists.", context.exception.detail)

    # Get
    async def test_get_option_empty(self):
        """Test getting generals when none exist via API"""
        options = await get_option_type("interaction", self.user)
        self.assertIsInstance(options, list)
        # self.assertEqual(len(generals), 0)

    async def test_get_option_with_data(self):
        """Test getting generals when data exists via API"""
        # Create test generals
        option1 = ReferenceOption(
            name="test_general",
            type="coverage",
            is_frequent=False,
            is_default=False,
        )
        option2 = ReferenceOption(
            name="test_general_2",
            type="coverage",
            is_frequent=True,
            is_default=True,
        )
        await create_option_type(option1, self.user)
        await create_option_type(option2, self.user)

        # Test
        options = await get_option_type("coverage", self.user)
        self.assertIsInstance(options, list)
        self.assertGreaterEqual(len(options), 2)

        # Verify our generals are in the results
        option_names = [g.name for g in options]
        self.assertIn("test_general", option_names)
        self.assertIn("test_general_2", option_names)

        # Verify general structure
        for o in options:
            self.assertIsInstance(o, ReferenceOption)
            self.assertIsInstance(o.name, str)
            self.assertIsInstance(o.is_frequent, bool)
            self.assertIsInstance(o.is_default, bool)
            self.assertIsInstance(o.type, str)
            self.assertIsNotNone(o.id)

    # Delete
    async def test_delete_option_by_name_success(self):
        """Test successful deletion of a general by name via API"""
        # Create general first
        option = ReferenceOption(
            name="test_general",
            type="coverage",
            is_frequent=False,
            is_default=False,
        )

        await create_option_type(option, self.user)

        # Delete the general
        result = await delete_option_name(
            "coverage", "test_general", self.user
        )
        self.assertEqual(result["message"], "Option deleted successfully.")

        # Verify general was deleted
        options = await get_option_type("coverage", self.user)
        option_names = [g.name for g in options]

        self.assertNotIn("test_general", option_names)

    async def test_delete_option_by_id_success(self):
        """Test successful deletion of a general by ID via API"""
        # Create general first
        option = ReferenceOption(
            name="test_general",
            type="interaction",
            is_frequent=True,
            is_default=False,
        )
        await create_option_type(option, self.user)

        # Get general to find its ID
        options = await get_option_type("interaction", self.user)
        option = next((g for g in options if g.name == "test_general"), None)
        self.assertIsNotNone(option)
        option_id = option.id

        # Delete the general by ID
        result = await delete_option_id(option_id, self.user)
        self.assertEqual(result["message"], "Option deleted successfully.")

        # Verify general was deleted
        options = await get_option_type("interaction", self.user)
        option_names = [g.name for g in options]
        self.assertNotIn("test_general", option_names)

    async def test_delete_option_not_found_by_name(self):
        """Test deletion of non-existent general by name via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_option_name(
                "interaction", "non_existent_general", self.user
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Option not found", context.exception.detail)

    async def test_delete_option_not_found_by_id(self):
        """Test deletion of non-existent general by ID via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_option_id(99999, self.user)  # Non-existent ID

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Option not found", context.exception.detail)

    # Update
    async def test_update_option_success(self):
        """Test successful update of a general via API"""
        # Create general first
        option = ReferenceOption(
            name="test_general",
            type="coverage",
            is_frequent=False,
            is_default=False,
        )
        await create_option_type(option, self.user)

        # Get general to find its ID
        options = await get_option_type("coverage", self.user)
        option = next((g for g in options if g.name == "test_general"), None)
        option_id = option.id

        # Update the general
        update_data = ReferenceOptionUpdate(
            name="test_general",
            is_frequent=True,
            is_default=True,
        )
        result = await update_option(
            option_id,
            update_data,
            self.user,
        )
        self.assertEqual(
            result["message"],
            "Option updated successfully.",
        )

        # Verify general was updated
        options = await get_option_type("coverage", self.user)
        updated = next((g for g in options if g.name == "test_general"), None)

        self.assertIsNotNone(updated)
        self.assertTrue(updated.is_frequent)
        self.assertTrue(updated.is_default)

    async def test_update_option_partial(self):
        """Test partial update of a general via API"""
        # Create general first
        option = ReferenceOption(
            name="test_general",
            type="interaction",
            is_frequent=False,
            is_default=False,
        )

        await create_option_type(option, self.user)

        # Get general ID
        options = await get_option_type("interaction", self.user)
        option = next((g for g in options if g.name == "test_general"), None)
        option_id = option.id

        # Partial update - only is_frequent
        update_data = ReferenceOptionUpdate(
            is_frequent=True,
        )
        result = await update_option(
            option_id,
            update_data,
            self.user,
        )
        self.assertEqual(
            result["message"],
            "Option updated successfully.",
        )

        # Verify only is_frequent was updated
        options = await get_option_type("interaction", self.user)
        updated = next((g for g in options if g.name == "test_general"), None)

        self.assertIsNotNone(updated)
        self.assertTrue(updated.is_frequent)
        self.assertFalse(updated.is_default)

    async def test_update_option_empty_updates(self):
        """Test update with no actual changes via API"""
        # Create general first
        option = ReferenceOption(
            name="test_general",
            type="interaction",
            is_frequent=False,
            is_default=False,
        )

        await create_option_type(option, self.user)

        # Get general ID
        options = await get_option_type("interaction", self.user)
        option = next((g for g in options if g.name == "test_general"), None)
        option_id = option.id

        # Empty update
        update_data = ReferenceOptionUpdate()
        with self.assertRaises(HTTPException) as context:
            await update_option(option_id, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Option not found or could not be updated",
            context.exception.detail,
        )

    async def test_update_option_not_found(self):
        """Test update of non-existent general via API"""
        update_data = ReferenceOptionUpdate(
            name="non_existent_general",
            is_frequent=True,
        )

        with self.assertRaises(HTTPException) as context:
            await update_option(99999, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Option not found or could not be updated",
            context.exception.detail,
        )


class TestReferenceTemplateAPI(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        types = ["interaction", "coverage"]

        test_names = [
            "test_general",
            "test_general_2",
            "updated_general",
            "default_general",
        ]
        for t in types:
            for name in test_names:
                try:
                    await ReferenceTemplateService.delete_template(name, t)
                except Exception:
                    pass  # Ignore if general site doesn't exist

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
            province="Ontario",
            location_permissions=[],
        )

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        await database.disconnect()

    # Create
    async def test_create_template_success(self):
        """Test successful creation of a general via API"""
        data = ReferenceTemplate(
            name="test_general",
            type="interaction",
            content="This is the content",
            is_default=False,
        )

        # Test
        result = await create_template(data, self.user)
        self.assertEqual(
            result["message"],
            "Template created successfully.",
        )

        # Validate by getting generals
        values = await get_templates("interaction", self.user)
        value_names = [v.name for v in values]

        self.assertIn("test_general", value_names)

    async def test_create_template_with_default(self):
        """Test creation of a default general via API"""
        data = ReferenceTemplate(
            name="default_general",
            type="coverage",
            content="This is the content",
            is_default=True,
        )

        # Test
        result = await create_template(data, self.user)
        self.assertEqual(
            result["message"],
            "Template created successfully.",
        )

        # Validate
        valuess = await get_templates("coverage", self.user)
        default = next(
            (g for g in valuess if g.name == "default_general"),
            None,
        )
        self.assertIsNotNone(default)
        self.assertTrue(default.is_default)
        self.assertEqual(default.content, "This is the content")
        self.assertEqual(default.type, "coverage")

    async def test_create_duplicate_template_name(self):
        """Test creating general with duplicate name via API"""
        data = ReferenceTemplate(
            name="test_general",
            type="coverage",
            content="This is the content",
            is_default=False,
        )

        # Create first general
        result1 = await create_template(data, self.user)
        self.assertEqual(
            result1["message"],
            "Template created successfully.",
        )

        # Try to create duplicate - should raise HTTPException
        with self.assertRaises(HTTPException) as context:
            await create_template(data, self.user)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Template already exists.", context.exception.detail)

    # Get
    async def test_get_template_empty(self):
        """Test getting generals when none exist via API"""
        values = await get_templates("interaction", self.user)
        self.assertIsInstance(values, list)
        # self.assertEqual(len(generals), 0)

    async def test_get_template_with_data(self):
        """Test getting generals when data exists via API"""
        # Create test generals
        option1 = ReferenceTemplate(
            name="test_general",
            type="coverage",
            content="This is the content",
            is_default=False,
        )
        option2 = ReferenceTemplate(
            name="test_general_2",
            type="coverage",
            content="This is the content",
            is_default=True,
        )
        await create_template(option1, self.user)
        await create_template(option2, self.user)

        # Test
        values = await get_templates("coverage", self.user)
        self.assertIsInstance(values, list)
        self.assertGreaterEqual(len(values), 2)

        # Verify our generals are in the results
        names = [g.name for g in values]
        self.assertIn("test_general", names)
        self.assertIn("test_general_2", names)

        # Verify general structure
        for o in values:
            self.assertIsInstance(o, ReferenceTemplate)
            self.assertIsInstance(o.name, str)
            self.assertIsInstance(o.content, str)
            self.assertIsInstance(o.is_default, bool)
            self.assertIsInstance(o.type, str)
            self.assertIsNotNone(o.id)

    # Delete
    async def test_delete_template_by_name_success(self):
        """Test successful deletion of a general by name via API"""
        # Create general first
        data = ReferenceTemplate(
            name="test_general",
            type="coverage",
            content="This is the content",
            is_default=False,
        )

        await create_template(data, self.user)

        # Delete the general
        result = await delete_template_name(
            "coverage", "test_general", self.user
        )
        self.assertEqual(result["message"], "Template deleted successfully.")

        # Verify general was deleted
        values = await get_templates("coverage", self.user)
        names = [g.name for g in values]

        self.assertNotIn("test_general", names)

    async def test_delete_template_by_id_success(self):
        """Test successful deletion of a general by ID via API"""
        # Create general first
        data = ReferenceTemplate(
            name="test_general",
            type="interaction",
            content="This is the content",
            is_default=False,
        )

        await create_template(data, self.user)

        # Get general to find its ID
        values = await get_templates("interaction", self.user)
        value = next((g for g in values if g.name == "test_general"), None)
        self.assertIsNotNone(value)
        value_id = value.id

        # Delete the general by ID
        result = await delete_template_id(value_id, self.user)
        self.assertEqual(result["message"], "Template deleted successfully.")

        # Verify general was deleted
        values = await get_templates("interaction", self.user)
        names = [g.name for g in values]
        self.assertNotIn("test_general", names)

    async def test_delete_template_not_found_by_name(self):
        """Test deletion of non-existent general by name via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_template_name(
                "interaction", "non_existent_general", self.user
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Template not found", context.exception.detail)

    async def test_delete_template_not_found_by_id(self):
        """Test deletion of non-existent general by ID via API"""
        with self.assertRaises(HTTPException) as context:
            await delete_template_id(99999, self.user)  # Non-existent ID

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Template not found", context.exception.detail)

    # Update
    async def test_update_template_success(self):
        """Test successful update of a general via API"""
        # Create general first
        data = ReferenceTemplate(
            name="test_general",
            type="coverage",
            content="This is the content",
            is_default=False,
        )

        await create_template(data, self.user)

        # Get general to find its ID
        values = await get_templates("coverage", self.user)
        value = next((g for g in values if g.name == "test_general"), None)
        id = value.id

        # Update the general
        update_data = ReferenceTemplateUpdate(
            name="test_general",
            content="new content",
            is_default=True,
        )

        result = await update_template(
            id,
            update_data,
            self.user,
        )

        self.assertEqual(
            result["message"],
            "Template updated successfully.",
        )

        # Verify general was updated
        values = await get_templates("coverage", self.user)
        updated = next((g for g in values if g.name == "test_general"), None)

        self.assertIsNotNone(updated)
        self.assertEqual(updated.content, "new content")
        self.assertTrue(updated.is_default)

    async def test_update_template_partial(self):
        """Test partial update of a general via API"""
        # Create general first
        data = ReferenceTemplate(
            name="test_general",
            type="interaction",
            content="This is the content",
            is_default=False,
        )

        await create_template(data, self.user)

        # Get general ID
        values = await get_templates("interaction", self.user)
        value = next((g for g in values if g.name == "test_general"), None)
        id = value.id

        # Partial update - only is_frequent
        update_data = ReferenceTemplateUpdate(
            content="content",
        )

        result = await update_template(
            id,
            update_data,
            self.user,
        )

        self.assertEqual(
            result["message"],
            "Template updated successfully.",
        )

        # Verify only is_frequent was updated
        values = await get_templates("interaction", self.user)
        updated = next((g for g in values if g.name == "test_general"), None)

        self.assertIsNotNone(updated)
        self.assertEqual(updated.content, "content")
        self.assertFalse(updated.is_default)

    async def test_update_templates_empty_updates(self):
        """Test update with no actual changes via API"""
        # Create general first
        data = ReferenceTemplate(
            name="test_general",
            type="interaction",
            content="This is the content",
            is_default=False,
        )

        await create_template(data, self.user)

        # Get general ID
        values = await get_templates("interaction", self.user)
        value = next((g for g in values if g.name == "test_general"), None)
        id = value.id

        # Empty update
        update_data = ReferenceTemplateUpdate()
        with self.assertRaises(HTTPException) as context:
            await update_template(id, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Template not found or could not be updated",
            context.exception.detail,
        )

    async def test_update_template_not_found(self):
        """Test update of non-existent general via API"""
        update_data = ReferenceTemplateUpdate(
            name="non_existent_general",
        )

        with self.assertRaises(HTTPException) as context:
            await update_template(99999, update_data, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(
            "Template not found or could not be updated",
            context.exception.detail,
        )
