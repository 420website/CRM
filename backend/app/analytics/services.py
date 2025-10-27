from typing import List
from app.database import database
from app.analytics.utils import LegacyDataAnalyzer, summarize_data
from app.config import settings
from app.database import mongo_db
from app.analytics.prompts import (
    internal_system_message,
    legacy_context_prompt,
    legacy_system_message,
)
from app.analytics.schema import (
    ClaudeChatRequest,
    ClaudeChatResponse,
    DataSummaryResponse,
    LegacyData,
    RawAnalytics,
)


def normalize_keys(record: dict) -> dict:
    return {k.lower(): v for k, v in record.items()}


# Usage example:
async def generate_context(
    legacy_upload: List[RawAnalytics],
) -> str:
    """Generate analytics context for Claude"""
    try:
        stats = LegacyDataAnalyzer.analyze_legacy_data(legacy_upload)

        # Generate context prompt
        context_text = legacy_context_prompt(
            stats.total_records,
            stats.rewards_stats,
            stats.address_stats,
            stats.dispositions,
            stats.dispositions_2024,
            stats.dispositions_2025,
            stats.dispositions,
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
    async def get_legacy_data_by_userid(
        user_id: int,
    ) -> List[RawAnalytics] | None:
        result = await mongo_db.legacy_data.find_one({"user_id": user_id})

        if result and result["data"]:
            normalized = [normalize_keys(r) for r in result["data"]]
            return [RawAnalytics(**r) for r in normalized]
        return None

    @staticmethod
    async def get_data() -> List[RawAnalytics]:
        query = """
        SELECT 
            p.id as patientid, 
            p.dob, 
            p.gender,
            p.address, 
            p.city, 
            p.province, 
            p.postal_code as postalcode, 
            p.phone1 as phone, 
            p.health_card as healthcard,
            p.disposition, 
            p.reg_date as regdate,
            p.referral_site as referralsite,
            i.description as interactiontype,
            i.amount 
        FROM patients p 
        LEFT JOIN interactions i ON p.id = i.patient_id;
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                print(row)
                result.append(RawAnalytics(**dict(row)))
        return result

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
        result = await mongo_db.legacy_data.find_one({"user_id": user_id})

        if not result:
            raise Exception(
                "No legacy data found. Please upload an Excel file first."
            )
        summary = await summarize_data(result)

        return summary

    @staticmethod
    async def claude_chat(
        request: ClaudeChatRequest,
        user_id: int,
    ) -> ClaudeChatResponse:
        """Claude AI chat endpoint for admin analytics with legacy data access and chart generation"""
        is_file = True
        raw_data = await AnalyticsService.get_legacy_data_by_userid(user_id)

        if not raw_data:
            raw_data = await AnalyticsService.get_data()

            if len(raw_data) == 0:
                raise Exception(
                    "No legacy data found. Please upload an Excel file first."
                )
            is_file = False

        try:
            context = await generate_context(raw_data)
            if is_file:
                system_msg = legacy_system_message(context)
            else:
                system_msg = internal_system_message(context)

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
