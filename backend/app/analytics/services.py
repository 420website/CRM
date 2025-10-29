from typing import List
from app.analytics.utils import LegacyDataAnalyzer, summarize_data
from app.database import mongo_db
from app.analytics.prompts import legacy_context_prompt
from app.analytics.schema import (
    DataSummaryResponse,
    LegacyData,
    RawAnalytics,
)


def normalize_keys(record: dict) -> dict:
    return {k.lower(): v for k, v in record.items()}


class LegacyDataService:
    @staticmethod
    async def delete_all_legacy_data(user_id: int) -> bool:
        result = await mongo_db.legacy_data.delete_many({"user_id": user_id})
        return result.acknowledged

    @staticmethod
    async def insert_legacy_data(data: LegacyData) -> bool:
        result = await mongo_db.legacy_data.insert_one(data.model_dump())
        return result.acknowledged

    @staticmethod
    async def upload_legacy_data(data: LegacyData, user_id: int) -> bool:
        """Upload Excel file with legacy patient data for Claude analysis"""
        if not await LegacyDataService.delete_all_legacy_data(user_id):
            raise Exception("Error deleting old legacy data.")

        if not await LegacyDataService.insert_legacy_data(data):
            raise Exception("Error uploading legacy data.")

        return True

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
