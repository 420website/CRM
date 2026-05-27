# tests/unit/test_analytics_router.py
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from datetime import datetime
import pandas as pd
from app.core.analytics.schema import (
    ClaudeChatRequest,
    ClaudeChatResponse,
    DataSummaryResponse,
)
from app.core.authentication.schemas import UserRead


class TestLegacyDataSummaryEndpoint(IsolatedAsyncioTestCase):
    """Tests for GET /analytics/legacy-data-summary"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_user = UserRead(
            id=1,
            email="test@example.com",
            role="admin",
            permissions=["All"],
            province="Ontario",
            location_permissions=["All"],
            authenticator_mfa_enabled=True,
        )

    async def test_get_summary_success(self):
        """Should return summary when data exists"""
        mock_summary = DataSummaryResponse(
            total_records=100,
            date_range={},
            top_dispositions=[{"Active": 1, "Other": 3}],
            upload_info={"info": "none"},
        )

        with patch(
            "app.core.analytics.services.LegacyDataService.get_legacy_data_summary",
            new_callable=AsyncMock,
            return_value=mock_summary,
        ) as mock_service:

            from app.core.analytics.router import get_legacy_data_summary

            result = await get_legacy_data_summary(user=self.mock_user)

            self.assertEqual(result, mock_summary)
            mock_service.assert_called_once_with(self.mock_user.id)

    async def test_get_summary_service_error(self):
        """Should raise HTTPException when service fails"""
        with patch(
            "app.core.analytics.services.LegacyDataService.get_legacy_data_summary",
            side_effect=Exception("No data found"),
        ):

            from app.core.analytics.router import get_legacy_data_summary

            with self.assertRaises(HTTPException) as context:
                await get_legacy_data_summary(user=self.mock_user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertIn(
                "Failed to get summary data", context.exception.detail
            )

    async def test_get_summary_empty_result(self):
        """Should handle empty summary gracefully"""
        mock_summary = DataSummaryResponse(
            total_records=100,
            date_range={},
            top_dispositions=[{"Active": 1, "Other": 3}],
            upload_info={"info": "none"},
        )

        with patch(
            "app.core.analytics.services.LegacyDataService.get_legacy_data_summary",
            new_callable=AsyncMock,
            return_value=mock_summary,
        ):

            from app.core.analytics.router import get_legacy_data_summary

            result = await get_legacy_data_summary(user=self.mock_user)

            self.assertEqual(result.total_records, 100)


class TestClearLegacyDataEndpoint(IsolatedAsyncioTestCase):
    """Tests for DELETE /analytics/legacy-data-summary"""

    def setUp(self):
        self.mock_user = UserRead(
            id=1,
            email="test@example.com",
            role="admin",
            permissions=["All"],
            province="Ontario",
            location_permissions=["All"],
            authenticator_mfa_enabled=True,
        )

    async def test_clear_data_success(self):
        """Should clear both chat and legacy data"""
        expected_result = {"deleted": 100, "status": "success"}

        with patch(
            "app.core.analytics.rag.RagService.clear_chat",
            new_callable=AsyncMock,
        ) as mock_clear_chat, patch(
            "app.core.analytics.services.LegacyDataService.delete_all_legacy_data",
            new_callable=AsyncMock,
            return_value=expected_result,
        ) as mock_delete:

            from app.core.analytics.router import clear_legacy_data_summary

            result = await clear_legacy_data_summary(user=self.mock_user)

            self.assertEqual(result, expected_result)
            mock_clear_chat.assert_called_once_with(self.mock_user.id)
            mock_delete.assert_called_once_with(self.mock_user.id)

    async def test_clear_data_chat_error(self):
        """Should raise HTTPException if chat clear fails"""
        with patch(
            "app.core.analytics.rag.RagService.clear_chat",
            side_effect=Exception("Redis error"),
        ):

            from app.core.analytics.router import clear_legacy_data_summary

            with self.assertRaises(HTTPException) as context:
                await clear_legacy_data_summary(user=self.mock_user)

            self.assertEqual(context.exception.status_code, 400)

    async def test_clear_data_delete_error(self):
        """Should raise HTTPException if delete fails"""
        with patch(
            "app.core.analytics.rag.RagService.clear_chat",
            new_callable=AsyncMock,
        ), patch(
            "app.core.analytics.services.LegacyDataService.delete_all_legacy_data",
            side_effect=Exception("Database error"),
        ):

            from app.core.analytics.router import clear_legacy_data_summary

            with self.assertRaises(HTTPException) as context:
                await clear_legacy_data_summary(user=self.mock_user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertIn(
                "Failed to delete summary data", context.exception.detail
            )


class TestUploadLegacyDataEndpoint(IsolatedAsyncioTestCase):
    """Tests for POST /analytics/upload-legacy-data"""

    def setUp(self):
        self.mock_user = UserRead(
            id=1,
            email="test@example.com",
            role="admin",
            permissions=["All"],
            province="Ontario",
            location_permissions=["All"],
            authenticator_mfa_enabled=True,
        )

    def _create_mock_excel_file(self, rows=3):
        """Helper to create mock Excel file"""
        df = pd.DataFrame(
            {
                "PatientID": list(range(1, rows + 1)),
                "DOB": ["1990-01-01"] * rows,
                "Gender": ["M"] * rows,
                "Address": ["123 Main St"] * rows,
                "City": ["Toronto"] * rows,
                "Province": ["ON"] * rows,
                "PostalCode": ["M5V1A1"] * rows,
                "Phone": ["416-555-0001"] * rows,
                "HealthCard": ["1234567890"] * rows,
                "Disposition": ["Active"] * rows,
                "RegDate": ["2024-01-01"] * rows,
                "ReferralSite": ["Site A"] * rows,
                "InteractionType": ["Phone"] * rows,
                "Amount": [100.0] * rows,
            }
        )
        return df

    def _create_upload_file_mock(self, filename, df=None):
        """Create a properly mocked UploadFile"""
        if df is None:
            df = self._create_mock_excel_file()

        # Create mock with async read
        mock_file = MagicMock()
        mock_file.filename = filename
        mock_file.read = AsyncMock(return_value=b"fake_excel_data")
        mock_file.file = MagicMock()

        return mock_file

    async def test_upload_valid_excel(self):
        """Should successfully upload valid Excel file"""
        df = self._create_mock_excel_file(rows=10)
        mock_file = self._create_upload_file_mock("test.xlsx", df)

        with patch(
            "app.core.analytics.router.read_legacy_data_file",
            new_callable=AsyncMock,
            return_value=df,
        ), patch(
            "app.core.analytics.services.LegacyDataService.upload_legacy_data",
            new_callable=AsyncMock,
        ) as mock_upload, patch(
            "app.core.analytics.rag.RagService.clear_chat",
            new_callable=AsyncMock,
        ):
            from app.core.analytics.router import upload_legacy_data

            result = await upload_legacy_data(
                file=mock_file, user=self.mock_user
            )

            self.assertEqual(result.records_count, 10)
            self.assertIn("Successfully uploaded", result.message)
            self.assertEqual(
                len(result.preview), 5
            )  # Should preview 5 records
            mock_upload.assert_called_once()

    async def test_upload_no_filename(self):
        """Should raise HTTPException when filename is missing"""
        mock_file = MagicMock()
        mock_file.filename = None

        from app.core.analytics.router import upload_legacy_data

        with self.assertRaises(HTTPException) as context:
            await upload_legacy_data(file=mock_file, user=self.mock_user)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Please provide file", context.exception.detail)

    async def test_upload_invalid_file_type(self):
        """Should raise HTTPException for invalid file type"""
        mock_file = MagicMock()
        mock_file.filename = "test.pdf"

        from app.core.analytics.router import upload_legacy_data

        with self.assertRaises(HTTPException) as context:
            await upload_legacy_data(file=mock_file, user=self.mock_user)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Excel (.xlsx, .xls) or CSV", context.exception.detail)

    async def test_upload_missing_columns(self):
        """Should raise HTTPException when required columns are missing"""
        df = self._create_mock_excel_file(rows=10)
        mock_file = self._create_upload_file_mock("test.xlsx", df)

        # DataFrame with missing columns
        df = pd.DataFrame(
            {
                "PatientID": [1, 2],
                "DOB": ["1990-01-01", "1985-05-15"],
                # Missing all other required columns
            }
        )

        with patch(
            "app.core.analytics.router.read_legacy_data_file",
            new_callable=AsyncMock,
            return_value=df,
        ):

            from app.core.analytics.router import upload_legacy_data

            with self.assertRaises(HTTPException) as context:
                await upload_legacy_data(file=mock_file, user=self.mock_user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertIn("Columns not as expected", context.exception.detail)

        """Should raise HTTPException for empty file"""

    async def test_upload_empty_file(self):
        df = self._create_mock_excel_file(rows=10)
        mock_file = self._create_upload_file_mock("test.xlsx", df)

        df = pd.DataFrame(
            columns=[
                "PatientID",
                "DOB",
                "Gender",
                "Address",
                "City",
                "Province",
                "PostalCode",
                "Phone",
                "HealthCard",
                "Disposition",
                "RegDate",
                "ReferralSite",
                "InteractionType",
                "Amount",
            ]
        )

        with patch(
            "app.core.analytics.router.read_legacy_data_file",
            new_callable=AsyncMock,
            return_value=df,
        ):

            from app.core.analytics.router import upload_legacy_data

            with self.assertRaises(HTTPException) as context:
                await upload_legacy_data(file=mock_file, user=self.mock_user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertIn("File is empty", context.exception.detail)

    async def test_upload_service_error(self):
        """Should raise HTTPException when upload service fails"""
        df = self._create_mock_excel_file(rows=10)
        mock_file = self._create_upload_file_mock("test.xlsx", df)

        with patch(
            "app.core.analytics.router.read_legacy_data_file",
            new_callable=AsyncMock,
            return_value=df,
        ), patch(
            "app.core.analytics.services.LegacyDataService.upload_legacy_data",
            side_effect=Exception("Database connection failed"),
        ):

            from app.core.analytics.router import upload_legacy_data

            with self.assertRaises(HTTPException) as context:
                await upload_legacy_data(file=mock_file, user=self.mock_user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertIn("Failed to process file", context.exception.detail)


class TestClaudeChatEndpoint(IsolatedAsyncioTestCase):
    """Tests for POST /analytics/claude-chat"""

    def setUp(self):
        self.mock_user = UserRead(
            id=1,
            email="test@example.com",
            role="admin",
            permissions=["All"],
            province="Ontario",
            location_permissions=["All"],
            authenticator_mfa_enabled=True,
        )

    async def test_claude_chat_success(self):
        """Should return Claude response successfully"""
        request = ClaudeChatRequest(
            message="How many patients registered today?",
            datetime=datetime.now().isoformat(),
            legacy_data=False,
        )

        expected_response = ClaudeChatResponse(
            response="Found 5 patients registered today.",
            session_id="test-session",
        )

        with patch(
            "app.core.analytics.rag.RagService.prompt_claude",
            new_callable=AsyncMock,
            return_value=expected_response,
        ) as mock_prompt:

            from app.core.analytics.router import claude_chat

            result = await claude_chat(request=request, user=self.mock_user)

            self.assertEqual(result.response, expected_response.response)
            mock_prompt.assert_called_once_with(
                str(self.mock_user.id),
                request.message,
                request.datetime,
                request.legacy_data,
            )

    async def test_claude_chat_legacy_data(self):
        """Should handle legacy data queries"""
        request = ClaudeChatRequest(
            message="Show distribution by city",
            datetime=datetime.now().isoformat(),
            legacy_data=True,
        )

        expected_response = ClaudeChatResponse(
            response="Toronto: 50, Mississauga: 30", session_id="test-session"
        )

        with patch(
            "app.core.analytics.rag.RagService.prompt_claude",
            new_callable=AsyncMock,
            return_value=expected_response,
        ):

            from app.core.analytics.router import claude_chat

            result = await claude_chat(request=request, user=self.mock_user)

            self.assertEqual(result.response, expected_response.response)

    async def test_claude_chat_anthropic_error(self):
        """Should raise HTTPException on Anthropic API error"""
        from app.common.exceptions import AnthropicRequestError

        request = ClaudeChatRequest(
            message="Test query",
            datetime=datetime.now().isoformat(),
            legacy_data=False,
        )

        with patch(
            "app.core.analytics.rag.RagService.prompt_claude",
            side_effect=AnthropicRequestError("API timeout"),
        ):

            from app.core.analytics.router import claude_chat

            with self.assertRaises(HTTPException) as context:
                await claude_chat(request=request, user=self.mock_user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertIn("API timeout", context.exception.detail)

    async def test_claude_chat_context_error(self):
        """Should raise HTTPException on context retrieval error"""
        from app.common.exceptions import ContextRetrievalError

        request = ClaudeChatRequest(
            message="Test query",
            datetime=datetime.now().isoformat(),
            legacy_data=False,
        )

        with patch(
            "app.core.analytics.rag.RagService.prompt_claude",
            side_effect=ContextRetrievalError("Database unavailable"),
        ):

            from app.core.analytics.router import claude_chat

            with self.assertRaises(HTTPException) as context:
                await claude_chat(request=request, user=self.mock_user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertIn("Database unavailable", context.exception.detail)

    async def test_claude_chat_generic_error(self):
        """Should raise HTTPException on unexpected errors"""
        request = ClaudeChatRequest(
            message="Test query",
            datetime=datetime.now().isoformat(),
            legacy_data=False,
        )

        with patch(
            "app.core.analytics.rag.RagService.prompt_claude",
            side_effect=Exception("Unexpected error"),
        ):

            from app.core.analytics.router import claude_chat

            with self.assertRaises(HTTPException) as context:
                await claude_chat(request=request, user=self.mock_user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertIn("Failed to process file", context.exception.detail)
