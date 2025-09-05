from app.analytics.utils import LegacyDataAnalyzer, summarize_data
from app.config import settings
from app.database import mongo_db
from app.analytics.prompts import (
    legacy_context_prompt,
    system_message,
)
from app.analytics.schema import (
    ClaudeChatRequest,
    ClaudeChatResponse,
    DataSummaryResponse,
    LegacyData,
)


# Usage example:
async def generate_legacy_analytics_context(legacy_upload: dict) -> str:
    """Generate analytics context for Claude"""
    try:
        stats = LegacyDataAnalyzer.analyze_legacy_data(legacy_upload)

        # Generate context prompt
        context_text = legacy_context_prompt(
            legacy_upload,
            stats.total_records,
            stats.rewards_stats,
            stats.address_stats,
            stats.dispositions,
            stats.dispositions_2024,
            stats.dispositions_2025,
            stats.dispositions,  # clean_dispositions
            stats.genders_2024,
            stats.genders_2025,
            stats.phone_stats,
            stats.health_card_stats,
            stats.age_stats,
            stats.genders,
            stats.yearly_data,
            stats.monthly_counts,
            stats.monthly_counts,
            stats.yearly_data,
        )

        return context_text

    except Exception as e:
        return f"Error analyzing legacy data: {str(e)}"


class AnalyticsService:
    @staticmethod
    async def delete_all_legacy_data(user_id: int) -> bool:
        result = await mongo_db.legacy_data.delete_many({"user_id": user_id})
        return result.acknowledged

    @staticmethod
    async def insert_legacy_data(data: LegacyData) -> bool:
        result = await mongo_db.legacy_data.insert_one(data.model_dump())
        return result.acknowledged

    @staticmethod
    async def get_legacy_data_by_userid(user_id: int) -> dict | None:
        result = await mongo_db.legacy_data.find_one({"user_id": user_id})

        if result:
            return result
        return None

    @staticmethod
    async def upload_legacy_data(data: LegacyData, user_id: int) -> bool:
        """Upload Excel file with legacy patient data for Claude analysis"""
        if not await AnalyticsService.delete_all_legacy_data(user_id):
            raise Exception("Error deleting old legacy data.")

        if not await AnalyticsService.insert_legacy_data(data):
            raise Exception("Error uploading legacy data.")

        return True

    @staticmethod
    async def get_legacy_data_summary(user_id: int) -> DataSummaryResponse:
        """Get summary of uploaded legacy data"""
        result = await AnalyticsService.get_legacy_data_by_userid(user_id)

        if not result:
            raise Exception(
                "No legacy data found. Please upload an Excel file first."
            )
        summary = await summarize_data(result)

        return summary

    @staticmethod
    async def claude_chat(
        request: ClaudeChatRequest, user_id: int
    ) -> ClaudeChatResponse:
        """Claude AI chat endpoint for admin analytics with legacy data access and chart generation"""
        legacy_upload = await AnalyticsService.get_legacy_data_by_userid(
            user_id
        )

        if not legacy_upload:
            raise Exception(
                "No legacy data found. Please upload an Excel file first."
            )

        try:
            context = await generate_legacy_analytics_context(legacy_upload)
            system_msg = system_message(context)

            message = await settings.anthropic_client.messages.create(
                model=settings.anthropic_model,
                max_tokens=settings.anthropic_max_tokens,
                system=system_msg,
                messages=[{"role": "user", "content": request.message}],
            )

            response_text = message.content[0].text

            return ClaudeChatResponse(
                response=response_text,
                session_id=request.session_id or "99",
                # chart_html=chart_html,
                # chart_image_url=chart_image_url,
            )
        except Exception:
            raise Exception(
                "No legacy data found. Please upload an Excel file first."
            )
