from app.database import mongo_client
from app.analytics.schema import (
    DataSummaryResponse,
    LegacyData,
)
import pandas as pd


def normalize_keys(record: dict) -> dict:
    return {k.lower(): v for k, v in record.items()}

async def summarize_data(data: dict) -> DataSummaryResponse:
    records = data["data"]

    # Basic analytics
    total_records = len(records)

    # Date range analysis
    date_fields = ["RegDate", "regDate", "registrationDate", "date"]
    date_range = {"start": None, "end": None}

    for field in date_fields:
        if field in records[0]:
            dates = [r.get(field) for r in records if r.get(field)]
            if dates:
                try:
                    parsed_dates = [pd.to_datetime(d) for d in dates if d]
                    if parsed_dates:
                        date_range["start"] = str(min(parsed_dates).date())
                        date_range["end"] = str(max(parsed_dates).date())
                        break
                except Exception:
                    continue

    # Disposition analysis
    dispositions = {}
    for record in records:
        disp = (
            record.get("disposition") or record.get("Disposition") or "Unknown"
        )
        dispositions[disp] = dispositions.get(disp, 0) + 1

    top_dispositions = [
        {"disposition": k, "count": v}
        for k, v in sorted(
            dispositions.items(), key=lambda x: x[1], reverse=True
        )[:10]
    ]

    return DataSummaryResponse(
        total_records=total_records,
        date_range=date_range,
        top_dispositions=top_dispositions,
        upload_info={
            "filename": data["filename"],
            "upload_date": data["upload_date"],
            "upload_id": data["upload_id"],
        },
    )

class LegacyDataService:
    @staticmethod
    async def delete_all_legacy_data(user_id: int) -> bool:
        db = mongo_client.get_db()
        result = await db.legacy_data.delete_many({"user_id": user_id})
        return result.acknowledged

    @staticmethod
    async def insert_legacy_data(data: LegacyData) -> bool:
        db = mongo_client.get_db()
        result = await db.legacy_data.insert_one(data.model_dump())
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
    async def get_legacy_data_summary(user_id: int) -> DataSummaryResponse:
        """Get summary of uploaded legacy data"""
        db = mongo_client.get_db()
        result = await db.legacy_data.find_one({"user_id": user_id})

        if not result:
            raise Exception(
                "No legacy data found. Please upload an Excel file first."
            )
        summary = await summarize_data(result)

        return summary

