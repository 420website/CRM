from datetime import datetime
import uuid
from fastapi import Depends, File, APIRouter, HTTPException, UploadFile
from app.analytics.rag import RagService
from app.analytics.services import LegacyDataService
from app.analytics.schema import (
    ClaudeChatRequest,
    ClaudeChatResponse,
    DataSummaryResponse,
    ExcelUploadResponse,
    LegacyData,
)
from app.analytics.utils import read_legacy_data_file
from app.dependencies import get_current_user
from app.authentication.schemas import UserRead

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/legacy-data-summary", response_model=DataSummaryResponse)
async def get_legacy_data_summary(user: UserRead = Depends(get_current_user)):
    """Get summary of uploaded legacy data"""
    try:
        result = await LegacyDataService.get_legacy_data_summary(user.id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get summary data: {str(e)}",
        )


@router.delete("/legacy-data-summary")
async def clear_legacy_data_summary(
    user: UserRead = Depends(get_current_user),
):
    try:
        await RagService.clear_chat_history(user.id)

        result = await LegacyDataService.delete_all_legacy_data(user.id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete summary data: {str(e)}",
        )


@router.post("/upload-legacy-data", response_model=ExcelUploadResponse)
async def upload_legacy_data(
    file: UploadFile = File(...),
    user: UserRead = Depends(get_current_user),
):
    """Upload Excel file with legacy patient data for Claude analysis"""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please provide file. ",
        )

    if not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(
            status_code=400,
            detail="Please upload an Excel (.xlsx, .xls) or CSV (.csv) file",
        )

    df = await read_legacy_data_file(file)

    expected_columns = [
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
    missing_cols = [col for col in expected_columns if col not in df.columns]

    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail="Columns not as expected please update file column names.",
        )

    if len(df) == 0:
        raise HTTPException(status_code=400, detail="File is empty.")

    data = LegacyData(
        user_id=user.id,
        upload_id=str(uuid.uuid4()),
        filename=file.filename,
        upload_date=datetime.now(),
        records_count=len(df),
        columns=list(df.columns),
        data=df.to_dict("records"),
    )

    try:
        await LegacyDataService.upload_legacy_data(data, user.id)
        await RagService.clear_chat_history(user.id)

        preview = data.data[:5] if len(data.data) > 5 else data.data

        return ExcelUploadResponse(
            message=f"Successfully uploaded {data.records_count} records from {data.filename}",
            records_count=data.records_count,
            preview=preview,
            upload_id=data.upload_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process file: {str(e)}",
        )


@router.post("/claude-chat", response_model=ClaudeChatResponse)
async def claude_chat(
    request: ClaudeChatRequest,
    user: UserRead = Depends(get_current_user),
):
    """Claude AI chat endpoint for admin analytics with legacy data access and chart generation"""
    try:
        if request.legacy_data:
            result = await RagService.claude_chat_file(request, user.id)
        else:
            result = await RagService.claude_chat_internal(request, user.id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process file: {str(e)}",
        )
