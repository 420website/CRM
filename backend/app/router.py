from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File,
    Response,
)
from fastapi.responses import FileResponse
import os
import logging
from pydantic import ValidationError
from typing import List
import uuid
from datetime import datetime, date, timedelta
import pytz
import base64
import io
import asyncio
import pandas as pd
import subprocess
import bcrypt
from app.config import logger, settings
from app.auth import (
    generate_email_code,
    get_admin_user,
    hash_email_code,
    is_email_code_expired,
    send_2fa_email,
    verify_email_code_hash,
)
from app.database import (
    backup_client_data,
    is_test_data,
    db,
    validate_production_environment,
)
from app.schema import (
    ActivityCreate,
    ActivityRecord,
    ActivityUpdate,
    AdminRegistration,
    AdminRegistrationCreate,
    ChartRequest,
    ChartResponse,
    ChatQuery,
    ChatResponse,
    ClaudeChatRequest,
    ClaudeChatResponse,
    ClinicalTemplate,
    ClinicalTemplateCreate,
    ClinicalTemplateUpdate,
    ContactMessage,
    ContactMessageCreate,
    DataSummaryResponse,
    DispensingCreate,
    DispensingRecord,
    DispensingUpdate,
    Disposition,
    DispositionCreate,
    DispositionUpdate,
    EmailTwoFactorSetupResponse,
    EmailTwoFactorVerifyRequest,
    ExcelUploadResponse,
    InteractionCreate,
    InteractionRecord,
    InteractionUpdate,
    MedicationCreate,
    MedicationRecord,
    MedicationUpdate,
    NotesCreate,
    NotesRecord,
    NotesTemplate,
    NotesTemplateCreate,
    NotesTemplateUpdate,
    NotesUpdate,
    ReferralSite,
    ReferralSiteCreate,
    ReferralSiteUpdate,
    ShareAttachmentRequest,
    ShareAttachmentResponse,
    TestRecord,
    TestRecordCreate,
    TestRecordUpdate,
    UserCreate,
    UserRegistration,
    UserRegistrationCreate,
    UserUpdate,
)
from app.utils import (
    analyze_query,
    generate_monthly_trend_chart,
    generate_disposition_bar_chart,
    generate_yearly_comparison_chart,
    get_registration_stats,
    process_clinical_template,
    send_contact_email,
    send_email,
    send_registration_email,
)


# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Process clinical summary template with client data
@api_router.post("/process-clinical-template")
async def process_clinical_template_endpoint(request: dict):
    """Process clinical summary template with client data to make it dynamic"""
    try:
        template_content = request.get("template_content", "")
        client_data = request.get("client_data", {})

        # Process the template with client data
        processed_content = process_clinical_template(
            template_content, client_data
        )

        return {
            "success": True,
            "processed_content": processed_content,
            "original_content": template_content,
        }
    except Exception as e:
        logging.error(f"Error processing clinical template: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Template processing failed: {str(e)}"
        )


@api_router.post("/generate-chart", response_model=ChartResponse)
async def generate_chart(request: ChartRequest):
    """Generate charts for legacy data analysis"""
    try:
        # Get legacy data
        legacy_upload = await db.legacy_data.find_one(
            {}, sort=[("upload_date", -1)]
        )

        if not legacy_upload:
            raise HTTPException(
                status_code=404,
                detail="No legacy data found for chart generation",
            )

        records = legacy_upload["data"]

        # Prepare data based on chart type
        if request.chart_type == "monthly_trend":
            monthly_data = {}
            for record in records:
                reg_date = record.get("RegDate") or record.get("regDate")
                if reg_date:
                    try:
                        if isinstance(reg_date, str) and "T" in reg_date:
                            month_key = reg_date[:7]
                        else:
                            parsed_date = pd.to_datetime(reg_date)
                            month_key = parsed_date.strftime("%Y-%m")
                        monthly_data[month_key] = (
                            monthly_data.get(month_key, 0) + 1
                        )
                    except:
                        continue

            chart_html, chart_image = generate_monthly_trend_chart(
                monthly_data, request.title
            )

        elif request.chart_type == "disposition_bar":
            disposition_data = {}
            for record in records:
                disp = (
                    record.get("disposition")
                    or record.get("Disposition")
                    or "Unknown"
                )
                disposition_data[disp] = disposition_data.get(disp, 0) + 1

            chart_html, chart_image = generate_disposition_bar_chart(
                disposition_data, request.title
            )

        elif request.chart_type == "yearly_comparison":
            monthly_data = {}
            yearly_data = {}
            for record in records:
                reg_date = record.get("RegDate") or record.get("regDate")
                if reg_date:
                    try:
                        if isinstance(reg_date, str) and "T" in reg_date:
                            month_key = reg_date[:7]
                            year_key = reg_date[:4]
                        else:
                            parsed_date = pd.to_datetime(reg_date)
                            month_key = parsed_date.strftime("%Y-%m")
                            year_key = parsed_date.strftime("%Y")
                        monthly_data[month_key] = (
                            monthly_data.get(month_key, 0) + 1
                        )
                        yearly_data[year_key] = (
                            yearly_data.get(year_key, 0) + 1
                        )
                    except:
                        continue

            chart_html, chart_image = generate_yearly_comparison_chart(
                yearly_data, monthly_data, request.title
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid chart type")

        # Save image for download
        chart_image_url = None
        if request.download and chart_image:
            image_filename = f"chart_{uuid.uuid4().hex[:8]}.png"
            image_path = f"/tmp/{image_filename}"
            with open(image_path, "wb") as f:
                f.write(chart_image)
            chart_image_url = f"/api/download-chart/{image_filename}"

        return ChartResponse(
            chart_html=chart_html,
            chart_image_url=chart_image_url,
            chart_data={"message": "Chart generated successfully"},
        )

    except Exception as e:
        logging.error(f"Chart generation error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate chart: {str(e)}"
        )


@api_router.get("/download-chart/{filename}")
async def download_chart(filename: str):
    """Download generated chart image"""
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            file_path, media_type="image/png", filename=filename
        )
    else:
        raise HTTPException(status_code=404, detail="Chart file not found")


@api_router.post("/upload-legacy-data", response_model=ExcelUploadResponse)
async def upload_legacy_data(file: UploadFile = File(...)):
    """Upload Excel file with legacy patient data for Claude analysis"""
    try:
        # Validate file type
        if not file.filename.endswith((".xlsx", ".xls", ".csv")):
            raise HTTPException(
                status_code=400,
                detail="Please upload an Excel (.xlsx, .xls) or CSV (.csv) file",
            )

        # Read file content
        content = await file.read()

        # Parse Excel/CSV file
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        else:
            df = pd.read_excel(io.BytesIO(content))

        # Clean and process data
        df = df.fillna("")  # Replace NaN with empty strings
        df.columns = (
            df.columns.str.strip()
        )  # Remove whitespace from column names

        # Convert to records for storage
        records = df.to_dict("records")

        # Generate upload ID
        upload_id = str(uuid.uuid4())

        # Store in MongoDB
        legacy_data = {
            "upload_id": upload_id,
            "filename": file.filename,
            "upload_date": datetime.now(
                pytz.timezone("America/Toronto")
            ).isoformat(),
            "records_count": len(records),
            "columns": list(df.columns),
            "data": records,
        }

        # Replace existing legacy data (only keep one upload at a time)
        await db.legacy_data.delete_many({})  # Clear previous data
        await db.legacy_data.insert_one(legacy_data)

        # Create preview (first 5 records)
        preview = records[:5] if len(records) > 5 else records

        return ExcelUploadResponse(
            message=f"Successfully uploaded {len(records)} records from {file.filename}",
            records_count=len(records),
            preview=preview,
            upload_id=upload_id,
        )

    except Exception as e:
        logging.error(f"Excel upload error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process file: {str(e)}"
        )


@api_router.get("/legacy-data-analysis")
async def get_legacy_data_for_analysis():
    """Get detailed legacy data for AI analysis"""
    try:
        # Get latest upload
        legacy_upload = await db.legacy_data.find_one(
            {}, sort=[("upload_date", -1)]
        )

        if not legacy_upload:
            raise HTTPException(
                status_code=404,
                detail="No legacy data found. Please upload an Excel file first.",
            )

        records = legacy_upload["data"]

        # Detailed monthly analysis
        monthly_data = {}
        disposition_by_month = {}

        for record in records:
            # Find date field
            date_value = None
            for date_field in [
                "regDate",
                "RegDate",
                "registrationDate",
                "date",
                "Date",
                "reg_date",
            ]:
                if record.get(date_field):
                    date_value = record.get(date_field)
                    break

            if date_value:
                try:
                    # Handle multiple date formats
                    if isinstance(date_value, str):
                        # Try different date formats
                        for fmt in [
                            "%Y-%m-%dT%H:%M:%S",
                            "%Y-%m-%d",
                            "%m/%d/%Y",
                            "%Y/%m/%d",
                            "%d/%m/%Y",
                        ]:
                            try:
                                parsed_date = datetime.strptime(
                                    date_value, fmt
                                )
                                break
                            except:
                                continue
                        else:
                            # If no format worked, try pandas
                            parsed_date = pd.to_datetime(date_value)
                    else:
                        # If it's already a datetime object or timestamp
                        parsed_date = pd.to_datetime(date_value)

                    month_key = parsed_date.strftime("%Y-%m")

                    # Monthly counts
                    monthly_data[month_key] = (
                        monthly_data.get(month_key, 0) + 1
                    )

                    # Disposition by month
                    if month_key not in disposition_by_month:
                        disposition_by_month[month_key] = {}

                    disp = record.get(
                        "disposition", record.get("Disposition", "Unknown")
                    )
                    disposition_by_month[month_key][disp] = (
                        disposition_by_month[month_key].get(disp, 0) + 1
                    )

                except Exception as e:
                    continue

        # Sort by month
        sorted_monthly = dict(sorted(monthly_data.items()))

        return {
            "monthly_registrations": sorted_monthly,
            "disposition_by_month": disposition_by_month,
            "total_records": len(records),
            "available_columns": legacy_upload.get("columns", []),
            "sample_record": records[0] if records else {},
            "date_range": {
                "months_available": list(sorted_monthly.keys()),
                "first_month": (
                    min(sorted_monthly.keys()) if sorted_monthly else None
                ),
                "last_month": (
                    max(sorted_monthly.keys()) if sorted_monthly else None
                ),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Legacy data analysis error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to analyze legacy data"
        )


@api_router.get("/legacy-data-summary", response_model=DataSummaryResponse)
async def get_legacy_data_summary():
    """Get summary of uploaded legacy data"""
    try:
        # Get latest upload
        legacy_upload = await db.legacy_data.find_one(
            {}, sort=[("upload_date", -1)]
        )

        if not legacy_upload:
            raise HTTPException(
                status_code=404,
                detail="No legacy data found. Please upload an Excel file first.",
            )

        records = legacy_upload["data"]

        # Basic analytics
        total_records = len(records)

        # Date range analysis
        date_fields = ["regDate", "registrationDate", "date"]
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
                    except:
                        continue

        # Disposition analysis
        dispositions = {}
        for record in records:
            disp = (
                record.get("disposition")
                or record.get("Disposition")
                or "Unknown"
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
                "filename": legacy_upload["filename"],
                "upload_date": legacy_upload["upload_date"],
                "upload_id": legacy_upload["upload_id"],
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Legacy data summary error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to analyze legacy data"
        )


@api_router.post("/query-legacy-data")
async def query_legacy_data(query: dict):
    """Allow 420 AI to query the full legacy dataset"""
    try:
        # Get latest upload
        legacy_upload = await db.legacy_data.find_one(
            {}, sort=[("upload_date", -1)]
        )

        if not legacy_upload:
            raise HTTPException(status_code=404, detail="No legacy data found")

        records = legacy_upload["data"]

        # Convert to DataFrame for analysis
        df = pd.DataFrame(records)

        # Return the full dataset info that AI can work with
        return {
            "total_records": len(records),
            "columns": list(df.columns),
            "data_sample": records[:10],  # First 10 records for context
            "full_data_available": True,
            "unique_values": {
                col: (
                    list(df[col].unique())[:20]
                    if df[col].dtype == "object"
                    else f"Numeric range: {df[col].min()} - {df[col].max()}"
                )
                for col in df.columns
                if col in ["Disposition", "Site", "Type", "Province", "Gender"]
            },
        }

    except Exception as e:
        logging.error(f"Query legacy data error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to query legacy data"
        )


@api_router.post("/claude-chat", response_model=ClaudeChatResponse)
async def claude_chat(request: ClaudeChatRequest):
    """Claude AI chat endpoint for admin analytics with legacy data access and chart generation"""
    try:
        # Get comprehensive legacy data for analysis
        legacy_context = ""
        chart_html = None
        chart_image_url = None

        try:
            legacy_upload = await db.legacy_data.find_one(
                {}, sort=[("upload_date", -1)]
            )
            if legacy_upload:
                records = legacy_upload["data"]
                total_records = len(records)

                # Simple disposition count with year breakdown
                dispositions = {}
                dispositions_2024 = {}
                dispositions_2025 = {}

                # Gender tracking with year breakdown
                genders = {}
                genders_2024 = {}
                genders_2025 = {}

                for record in records:
                    # Get year first for all analyses
                    reg_date = record.get("RegDate") or record.get("regDate")
                    year = None
                    if reg_date and str(reg_date).strip():
                        try:
                            if (
                                isinstance(reg_date, str)
                                and "T" in reg_date
                                and len(reg_date) >= 4
                            ):
                                year = reg_date[:4]
                            else:
                                parsed_date = pd.to_datetime(
                                    reg_date, errors="coerce"
                                )
                                if pd.notna(parsed_date):
                                    year = parsed_date.strftime("%Y")
                        except:
                            continue

                    # Get disposition
                    disp = (
                        record.get("disposition")
                        or record.get("Disposition")
                        or "Unknown"
                    )
                    if (
                        disp
                        and str(disp).strip()
                        and str(disp).lower()
                        not in ["", "null", "none", "nan", "invalid date"]
                    ):
                        dispositions[disp] = dispositions.get(disp, 0) + 1

                        if year == "2024":
                            dispositions_2024[disp] = (
                                dispositions_2024.get(disp, 0) + 1
                            )
                        elif year == "2025":
                            dispositions_2025[disp] = (
                                dispositions_2025.get(disp, 0) + 1
                            )

                    # Get gender
                    gender = (
                        record.get("Gender")
                        or record.get("gender")
                        or "Unknown"
                    )
                    if (
                        gender
                        and str(gender).strip()
                        and str(gender).lower()
                        not in ["", "null", "none", "nan", "invalid date"]
                    ):
                        genders[gender] = genders.get(gender, 0) + 1

                        if year == "2024":
                            genders_2024[gender] = (
                                genders_2024.get(gender, 0) + 1
                            )
                        elif year == "2025":
                            genders_2025[gender] = (
                                genders_2025.get(gender, 0) + 1
                            )

                # Phone number tracking
                phone_stats = {
                    "total_records": 0,
                    "no_phone_count": 0,
                    "valid_phone_count": 0,
                }

                # Health card tracking
                health_card_stats = {
                    "total_records": 0,
                    "no_hc_count": 0,  # No health card (empty, null, 0000000000 NA)
                    "invalid_hc_count": 0,  # Invalid health card (missing 2-letter suffix)
                    "valid_hc_count": 0,
                }

                # Address/housing tracking
                address_stats = {
                    "total_records": 0,
                    "no_address_count": 0,
                    "valid_address_count": 0,
                }

                # Rewards/money tracking by month and year
                rewards_stats = {
                    "total_amount": 0,
                    "total_records_with_amount": 0,
                    "monthly_totals_2024": {},
                    "monthly_totals_2025": {},
                    "yearly_totals": {"2024": 0, "2025": 0},
                }

                # Age range tracking (10-year ranges)
                age_stats = {
                    "total_records_with_age": 0,
                    "age_ranges": {
                        "0-19": 0,
                        "20-29": 0,
                        "30-39": 0,
                        "40-49": 0,
                        "50-59": 0,
                        "60-69": 0,
                        "70-79": 0,
                        "80-89": 0,
                        "90+": 0,
                    },
                }

                for record in records:
                    phone_stats["total_records"] += 1
                    health_card_stats["total_records"] += 1
                    address_stats["total_records"] += 1

                    # Check phone number
                    phone = record.get("Phone") or record.get("phone") or ""
                    phone_str = str(phone).strip()

                    # Check if phone is missing or placeholder
                    if (
                        not phone_str
                        or phone_str.lower() in ["", "null", "none", "nan"]
                        or phone_str == "(000) 000-0000"
                        or phone_str == "000-000-0000"
                        or phone_str == "0000000000"
                    ):
                        phone_stats["no_phone_count"] += 1
                    else:
                        phone_stats["valid_phone_count"] += 1

                    # Check health card - categorize into no health card, invalid health card, or valid health card
                    hc = (
                        record.get("HC")
                        or record.get("HealthCard")
                        or record.get("healthCard")
                        or ""
                    )
                    hc_str = str(hc).strip()

                    # Check if no health card (empty, null, or 0000000000 NA patterns)
                    if (
                        not hc_str
                        or hc_str.lower() in ["", "null", "none", "nan"]
                        or hc_str == "0000000000 NA"
                        or hc_str == "0000000000"
                        or hc_str == "NA"
                        or hc_str == "0000000000NA"
                    ):
                        health_card_stats["no_hc_count"] += 1
                    else:
                        # Has some health card data - check if it's invalid (missing 2-letter suffix)
                        import re

                        # Valid health card should have 10 digits followed by 2 letters (like 1234567890AB)
                        # Invalid health card has numbers but missing the 2-letter suffix
                        if re.match(
                            r"^\d{10}$", hc_str
                        ):  # Exactly 10 digits with no letters
                            health_card_stats["invalid_hc_count"] += 1
                        elif re.match(
                            r"^\d{10}[A-Za-z]{2}$", hc_str
                        ):  # 10 digits + 2 letters (valid format)
                            health_card_stats["valid_hc_count"] += 1
                        else:
                            # Other formats that don't match standard patterns - treat as invalid
                            health_card_stats["invalid_hc_count"] += 1

                    # Check address
                    address = (
                        record.get("Address") or record.get("address") or ""
                    )
                    address_str = str(address).strip()

                    # Check if address is missing or placeholder
                    if (
                        not address_str
                        or address_str.lower() in ["", "null", "none", "nan"]
                        or address_str.lower() == "no address"
                        or address_str.lower() == "no fixed address"
                        or address_str.lower() == "nfa"
                        or address_str.lower() == "homeless"
                    ):
                        address_stats["no_address_count"] += 1
                    else:
                        address_stats["valid_address_count"] += 1

                    # Check rewards/amount - comprehensive capture for $110K total
                    amount = (
                        record.get("Amount")
                        or record.get("amount")
                        or record.get("Reward")
                        or record.get("reward")
                        or record.get("AMOUNT")
                        or record.get("REWARD")
                        or record.get("P")
                        or record.get("p")  # Column P specifically
                        or record.get("rewards")
                        or record.get("REWARDS")
                        or record.get("payment")
                        or record.get("Payment")
                        or record.get("PAYMENT")
                        or 0
                    )
                    try:
                        # Convert to float, handling various formats
                        amount_val = 0
                        if amount is not None:
                            # Handle if it's already a number
                            if isinstance(amount, (int, float)) and amount > 0:
                                amount_val = float(amount)
                            elif str(amount).strip():
                                amount_str = (
                                    str(amount)
                                    .strip()
                                    .replace("$", "")
                                    .replace(",", "")
                                    .replace(" ", "")
                                    .replace("CAD", "")
                                    .replace("USD", "")
                                )
                                if amount_str and amount_str.lower() not in [
                                    "",
                                    "null",
                                    "none",
                                    "nan",
                                    "0",
                                    "0.0",
                                    "0.00",
                                    "n/a",
                                    "na",
                                ]:
                                    try:
                                        amount_val = float(amount_str)
                                    except ValueError:
                                        # Handle potential integer fields or other numeric formats
                                        try:
                                            # Remove any non-numeric characters except decimal point
                                            clean_amount = "".join(
                                                c
                                                for c in amount_str
                                                if c.isdigit() or c == "."
                                            )
                                            if (
                                                clean_amount
                                                and "." in clean_amount
                                            ):
                                                amount_val = float(
                                                    clean_amount
                                                )
                                            elif clean_amount:
                                                amount_val = float(
                                                    clean_amount
                                                )
                                        except:
                                            pass

                        if amount_val > 0:
                            rewards_stats["total_amount"] += amount_val
                            rewards_stats["total_records_with_amount"] += 1

                            # Get date for monthly/yearly breakdown
                            reg_date = (
                                record.get("RegDate")
                                or record.get("regDate")
                                or record.get("REGDATE")
                            )
                            if reg_date and str(reg_date).strip():
                                try:
                                    year = None
                                    month_key = None

                                    if (
                                        isinstance(reg_date, str)
                                        and "T" in reg_date
                                        and len(reg_date) >= 7
                                    ):
                                        year = reg_date[:4]
                                        month_key = reg_date[:7]  # YYYY-MM
                                    else:
                                        parsed_date = pd.to_datetime(
                                            reg_date, errors="coerce"
                                        )
                                        if pd.notna(parsed_date):
                                            year = parsed_date.strftime("%Y")
                                            month_key = parsed_date.strftime(
                                                "%Y-%m"
                                            )

                                    # Add to yearly totals
                                    if year in ["2024", "2025"]:
                                        rewards_stats["yearly_totals"][
                                            year
                                        ] += amount_val

                                        # Add to monthly totals
                                        if year == "2024":
                                            rewards_stats[
                                                "monthly_totals_2024"
                                            ][month_key] = (
                                                rewards_stats[
                                                    "monthly_totals_2024"
                                                ].get(month_key, 0)
                                                + amount_val
                                            )
                                        elif year == "2025":
                                            rewards_stats[
                                                "monthly_totals_2025"
                                            ][month_key] = (
                                                rewards_stats[
                                                    "monthly_totals_2025"
                                                ].get(month_key, 0)
                                                + amount_val
                                            )
                                except:
                                    pass  # Skip invalid dates
                    except Exception as e:
                        # Add logging to help debug amount processing issues
                        logging.warning(
                            f"Error processing amount {amount}: {str(e)}"
                        )
                        pass  # Skip invalid amounts

                    # Check age and categorize into ranges
                    try:
                        dob = (
                            record.get("DOB")
                            or record.get("dob")
                            or record.get("dateOfBirth")
                            or record.get("DateOfBirth")
                        )
                        if dob and str(dob).strip():
                            # Parse the date of birth
                            dob_str = str(dob).strip()
                            if dob_str.lower() not in [
                                "",
                                "null",
                                "none",
                                "nan",
                            ]:
                                try:
                                    # Handle different date formats
                                    if (
                                        isinstance(dob, str)
                                        and "T" in dob
                                        and len(dob) >= 10
                                    ):
                                        # ISO format like "1990-05-15T00:00:00"
                                        dob_date = pd.to_datetime(
                                            dob[:10], errors="coerce"
                                        )
                                    else:
                                        # Try to parse other formats
                                        dob_date = pd.to_datetime(
                                            dob, errors="coerce"
                                        )

                                    if pd.notna(dob_date):
                                        # Calculate age
                                        from datetime import date

                                        today = date.today()
                                        age = (
                                            today.year
                                            - dob_date.year
                                            - (
                                                (today.month, today.day)
                                                < (
                                                    dob_date.month,
                                                    dob_date.day,
                                                )
                                            )
                                        )

                                        # Categorize into age ranges
                                        if age < 20:
                                            age_stats["age_ranges"][
                                                "0-19"
                                            ] += 1
                                        elif age < 30:
                                            age_stats["age_ranges"][
                                                "20-29"
                                            ] += 1
                                        elif age < 40:
                                            age_stats["age_ranges"][
                                                "30-39"
                                            ] += 1
                                        elif age < 50:
                                            age_stats["age_ranges"][
                                                "40-49"
                                            ] += 1
                                        elif age < 60:
                                            age_stats["age_ranges"][
                                                "50-59"
                                            ] += 1
                                        elif age < 70:
                                            age_stats["age_ranges"][
                                                "60-69"
                                            ] += 1
                                        elif age < 80:
                                            age_stats["age_ranges"][
                                                "70-79"
                                            ] += 1
                                        elif age < 90:
                                            age_stats["age_ranges"][
                                                "80-89"
                                            ] += 1
                                        else:
                                            age_stats["age_ranges"]["90+"] += 1

                                        age_stats[
                                            "total_records_with_age"
                                        ] += 1
                                except:
                                    pass  # Skip invalid dates
                    except:
                        pass  # Skip age processing errors
                monthly_counts = {}
                yearly_data = {}

                for record in records:
                    reg_date = record.get("RegDate") or record.get("regDate")
                    if (
                        reg_date
                        and str(reg_date).strip()
                        and str(reg_date).lower()
                        not in ["", "null", "none", "invalid date", "nan"]
                    ):
                        try:
                            # Additional validation to ensure it's a proper date
                            if isinstance(reg_date, str):
                                if "T" in reg_date and len(reg_date) >= 7:
                                    month_key = reg_date[:7]  # Extract YYYY-MM
                                    year_key = reg_date[:4]  # Extract YYYY
                                    # Validate format
                                    if (
                                        len(month_key) == 7
                                        and month_key[4] == "-"
                                        and len(year_key) == 4
                                    ):
                                        if (
                                            year_key.isdigit()
                                            and month_key[5:7].isdigit()
                                        ):
                                            monthly_counts[month_key] = (
                                                monthly_counts.get(
                                                    month_key, 0
                                                )
                                                + 1
                                            )
                                            yearly_data[year_key] = (
                                                yearly_data.get(year_key, 0)
                                                + 1
                                            )
                                else:
                                    parsed_date = pd.to_datetime(
                                        reg_date, errors="coerce"
                                    )
                                    if pd.notna(parsed_date) and not pd.isna(
                                        parsed_date
                                    ):
                                        month_key = parsed_date.strftime(
                                            "%Y-%m"
                                        )
                                        year_key = parsed_date.strftime("%Y")
                                        monthly_counts[month_key] = (
                                            monthly_counts.get(month_key, 0)
                                            + 1
                                        )
                                        yearly_data[year_key] = (
                                            yearly_data.get(year_key, 0) + 1
                                        )
                            else:
                                parsed_date = pd.to_datetime(
                                    reg_date, errors="coerce"
                                )
                                if pd.notna(parsed_date) and not pd.isna(
                                    parsed_date
                                ):
                                    month_key = parsed_date.strftime("%Y-%m")
                                    year_key = parsed_date.strftime("%Y")
                                    monthly_counts[month_key] = (
                                        monthly_counts.get(month_key, 0) + 1
                                    )
                                    yearly_data[year_key] = (
                                        yearly_data.get(year_key, 0) + 1
                                    )
                        except:
                            # Clean all data dictionaries to remove any invalid date references
                            clean_dispositions = {}
                            for k, v in dispositions.items():
                                clean_key = (
                                    str(k)
                                    .replace("Invalid Date", "")
                                    .replace("invalid date", "")
                                    .replace("Invalid", "")
                                    .strip()
                                )
                                if clean_key and clean_key.lower() not in [
                                    "",
                                    "null",
                                    "none",
                                    "nan",
                                ]:
                                    clean_dispositions[clean_key] = v

                            clean_yearly_data = {}
                            for k, v in yearly_data.items():
                                clean_key = (
                                    str(k)
                                    .replace("Invalid Date", "")
                                    .replace("invalid date", "")
                                    .replace("Invalid", "")
                                    .strip()
                                )
                                if clean_key and clean_key.lower() not in [
                                    "",
                                    "null",
                                    "none",
                                    "nan",
                                ]:
                                    clean_yearly_data[clean_key] = v

                            clean_monthly_counts = {}
                            for k, v in monthly_counts.items():
                                clean_key = (
                                    str(k)
                                    .replace("Invalid Date", "")
                                    .replace("invalid date", "")
                                    .replace("Invalid", "")
                                    .strip()
                                )
                                if clean_key and clean_key.lower() not in [
                                    "",
                                    "null",
                                    "none",
                                    "nan",
                                ]:
                                    clean_monthly_counts[clean_key] = v

                # Create simple context - filter out any invalid date references
                context_text = f"""
LEGACY DATA UPLOADED:
- File: {legacy_upload['filename']}
- Total records: {total_records}
- Available columns: PatientID, Phone, DOB, FileNo, HC, Disposition, RegDate, Site, Type, Month, Address, City, PostalCode, Province, Gender, Reward, Consultation, Amount

DISPOSITION COUNTS:
{dict(sorted(clean_dispositions.items(), key=lambda x: x[1], reverse=True)) if 'clean_dispositions' in locals() else dict(sorted(dispositions.items(), key=lambda x: x[1], reverse=True))}

DISPOSITION BREAKDOWN BY YEAR:
2024: {dict(sorted(dispositions_2024.items(), key=lambda x: x[1], reverse=True))}
2025: {dict(sorted(dispositions_2025.items(), key=lambda x: x[1], reverse=True))}

GENDER COUNTS:
{dict(sorted(genders.items(), key=lambda x: x[1], reverse=True))}

GENDER BREAKDOWN BY YEAR:
2024: {dict(sorted(genders_2024.items(), key=lambda x: x[1], reverse=True))}
2025: {dict(sorted(genders_2025.items(), key=lambda x: x[1], reverse=True))}

PHONE NUMBER STATISTICS:
Total records: {phone_stats['total_records']}
No phone number (including (000) 000-0000): {phone_stats['no_phone_count']}
Valid phone numbers: {phone_stats['valid_phone_count']}
Percentage without phone: {phone_stats['no_phone_count']/phone_stats['total_records']*100:.1f}%

HEALTH CARD STATISTICS:
Total records: {health_card_stats['total_records']}
No health cards (including 0000000000 NA): {health_card_stats['no_hc_count']}
Invalid health cards (missing 2-letter suffix): {health_card_stats['invalid_hc_count']}
Valid health cards: {health_card_stats['valid_hc_count']}
Percentage with no health cards: {health_card_stats['no_hc_count']/health_card_stats['total_records']*100:.1f}%
Percentage with invalid health cards: {health_card_stats['invalid_hc_count']/health_card_stats['total_records']*100:.1f}%

ADDRESS/HOUSING STATISTICS:
Total records: {address_stats['total_records']}
No address listed (including empty/null/homeless): {address_stats['no_address_count']}
Valid address listed: {address_stats['valid_address_count']}
Percentage with address listed: {address_stats['valid_address_count']/address_stats['total_records']*100:.1f}%

REWARDS/MONEY STATISTICS:
Total amount paid: ${rewards_stats['total_amount']:.2f}
Records with payments: {rewards_stats['total_records_with_amount']}
Average payment per record: ${rewards_stats['total_amount']/rewards_stats['total_records_with_amount'] if rewards_stats['total_records_with_amount'] > 0 else 0:.2f}
2024 total: ${rewards_stats['yearly_totals']['2024']:.2f}
2025 total: ${rewards_stats['yearly_totals']['2025']:.2f}
Year-over-year change: {((rewards_stats['yearly_totals']['2025'] - rewards_stats['yearly_totals']['2024']) / rewards_stats['yearly_totals']['2024'] * 100) if rewards_stats['yearly_totals']['2024'] > 0 else 0:.1f}%

MONTHLY REWARDS BREAKDOWN 2024:
{dict(sorted([(k, f"${v:.2f}") for k, v in rewards_stats['monthly_totals_2024'].items()]))}

MONTHLY REWARDS BREAKDOWN 2025:
{dict(sorted([(k, f"${v:.2f}") for k, v in rewards_stats['monthly_totals_2025'].items()]))}

AGE RANGE STATISTICS:
Total records with age data: {age_stats['total_records_with_age']}
Age distribution by 10-year ranges:
{dict([(k, f"{v} clients ({v/age_stats['total_records_with_age']*100:.1f}%)") for k in ['0-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+'] for v in [age_stats['age_ranges'][k]] if v > 0])}

YEARLY TOTALS:
{dict(sorted(clean_yearly_data.items())) if 'clean_yearly_data' in locals() else dict(sorted(yearly_data.items()))}

MONTHLY REGISTRATIONS:
{dict(sorted(clean_monthly_counts.items())) if 'clean_monthly_counts' in locals() else dict(sorted(monthly_counts.items()))}

CHART GENERATION AVAILABLE:
- Charts are DISABLED for mobile display
- DO NOT generate charts, graphs, or visualizations
- Provide ONLY clean text summaries and data tables
- Use simple bullet points and clear formatting
- NO HTML charts, NO CSS styling, NO code blocks
- Focus on readable text-only responses

COMPARATIVE ANALYSIS SUPPORT:
- Can compare year-over-year data (e.g., 2024 vs 2025)
- Can provide side-by-side monthly comparisons
- Can calculate percentage changes between periods
- Can analyze trends across different time periods

You can analyze all aspects of this data including year-over-year comparisons."""

                # Multiple passes to remove any potential "Invalid Date" references
                legacy_context = (
                    context_text.replace("Invalid Date", "")
                    .replace("invalid date", "")
                    .replace("Invalid", "")
                    .replace("INVALID", "")
                    .replace("Null", "")
                    .replace("NULL", "")
                    .replace("NaN", "")
                    .replace("nan", "")
                    .strip()
                )

                # Final cleanup - remove empty entries and lines containing invalid references
                lines = legacy_context.split("\n")
                clean_lines = [
                    line
                    for line in lines
                    if line.strip()
                    and "invalid" not in line.lower()
                    and "null" not in line.lower()
                    and "nan" not in line.lower()
                ]
                legacy_context = "\n".join(clean_lines)

                # Disable chart generation to avoid displaying code
                # message_lower = request.message.lower()
                # chart_keywords = ['chart', 'graph', 'visualize', 'plot', 'bar graph', 'trend', 'summary', 'comparison', 'monthly registrations']
                # Chart generation disabled - provide text summaries only

        except Exception as e:
            logging.error(f"Error generating legacy context: {str(e)}")
            legacy_context = f"Error accessing legacy data: {str(e)}"

        # Initialize Claude chat with medical context and legacy data
        system_message = f"""You are 420 AI, an AI assistant specialized in medical data analytics for a Hepatitis C and HIV testing platform called my420.ca. 

{legacy_context}

IMPORTANT DATA LIMITATIONS:
- You should ONLY analyze the uploaded legacy data file shown above
- DO NOT attempt to access or analyze any current platform registration data
- DO NOT reference any live/current patient data from the my420.ca platform
- Your analysis must be LIMITED EXCLUSIVELY to the uploaded Excel/CSV file data
- When users ask about "current data" or "platform data", clarify that you only have access to the uploaded legacy file

RESPONSE STYLE REQUIREMENTS:
- When asked for counts, summaries, or data breakdowns: provide CLEAN, well-formatted answers
- DO NOT generate any charts, graphs, or HTML/CSS code
- Present data in simple text format with clear headings
- Use bullet points and simple lists for data presentation
- DO NOT use ASCII tables, pipes (|), dashes (---), or complex table formatting
- For comparisons, use simple bullet point lists instead of tables
- DO NOT offer business insights, recommendations, or explanations unless specifically asked
- Keep responses brief and to-the-point
- Only provide the requested data/numbers/summaries
- No need for introductory or explanatory text for basic data queries
- Focus on clean, readable text responses only
- STRICTLY FORBIDDEN: Never include "Invalid Date", "Invalid", "null", "NaN", or any error text
- If data appears problematic, simply exclude it from the response
- Only include valid, clean data in your responses

COMPARATIVE ANALYSIS CAPABILITIES:
- Support year-over-year comparisons (e.g., "compare 2024 vs 2025")
- Provide side-by-side data when requested
- Calculate percentage changes between time periods
- Show monthly comparisons across different years
- Present data in table format when comparing multiple periods
- Support quarter-over-quarter and month-over-month analysis

DATA ANALYSIS CAPABILITIES:
You can analyze the uploaded data to provide:
- Monthly registration counts (extract month/year from date fields like regDate, registrationDate, etc.)
- Disposition breakdowns and counts (show actual disposition types like COMPLETED, POCT NEG, etc.)
- Patient demographics and geographic data
- Completion rates and outcome analysis
- Referral source effectiveness
- Seasonal patterns and trends

For DISPOSITION queries specifically:
- When asked for "dispositions summary" or "dispositions breakdown", show DISPOSITION TYPES (not monthly counts)
- Show actual disposition categories: COMPLETED, POCT NEG, PREVIOUSLY TX, CURED, SELF CURED, etc.
- Compare disposition type distributions between years (2024 vs 2025)
- Calculate percentage of total for each disposition type
- Do NOT show monthly registration counts when asked about dispositions
- IMPORTANT: Dispositions = medical outcomes/statuses, NOT monthly counts

For GENDER queries specifically:
- When asked for "gender summary" or "gender breakdown", show GENDER TYPES with counts
- Show gender categories (Male, Female, etc.) with counts and percentages in simple lists
- Compare gender distributions between years (2024 vs 2025) using bullet points
- Calculate percentage of total for each gender
For PHONE queries specifically:
- When asked about phone numbers or missing phone data, use the phone statistics provided
- Consider (000) 000-0000 as "no phone number" along with empty/null values
- Calculate and show percentage of patients without valid phone numbers
- Provide clear counts and percentages for phone availability
- DO NOT use tables, pipes, or ASCII formatting - use simple bullet points and clear text
- Present data in clean, readable format without complex table structures

You have expertise in:
- Hepatitis C testing and treatment processes
- HIV testing protocols
- Medical data interpretation
- Healthcare analytics
- Patient care optimization

Always clarify that your analysis is based solely on the uploaded legacy data file. If no legacy data has been uploaded, inform users they need to upload an Excel file first.

REMEMBER: Be concise and direct. Provide only what is requested without additional insights unless asked."""
        message = await settings.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            system=system_message,
            messages=[{"role": "user", "content": request.message}],
        )

        # Content is an array
        # First item is for type TextBlock(citations=.., text="..", type="text")
        response_text = message.content[0].text
        # print(response_text)
        # print(request.session_id)

        return ClaudeChatResponse(
            response=response_text,
            session_id=request.session_id,
            chart_html=chart_html,
            chart_image_url=chart_image_url,
        )

    except Exception as e:
        logging.error(f"Claude chat error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="AI chat service temporarily unavailable"
        )


@api_router.get("/")
async def root():
    return {"message": "my420.ca - Hepatitis C & HIV Testing Services API"}


@api_router.post("/admin-registration/{registration_id}/attachment")
async def save_attachment(registration_id: str, attachment_data: dict):
    """Save an attachment to an existing registration"""
    try:
        # Find the registration
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Add timestamp and id to attachment
        attachment_data["id"] = str(uuid.uuid4())
        attachment_data["savedAt"] = datetime.now(
            pytz.timezone("America/Toronto")
        ).isoformat()

        # Ensure URL has proper data URI prefix for images and PDFs
        if "url" in attachment_data and attachment_data.get("url"):
            url = attachment_data["url"]

            # Handle image attachments
            if attachment_data.get("type") == "Image" and not url.startswith(
                "data:image/"
            ):
                # Add data URI prefix for images
                attachment_data["url"] = f"data:image/png;base64,{url}"

            # Handle PDF attachments
            elif attachment_data.get("type") == "PDF" and not url.startswith(
                "data:application/pdf"
            ):
                # Add data URI prefix for PDFs
                attachment_data["url"] = f"data:application/pdf;base64,{url}"

        # Add attachment to the registration
        await db.admin_registrations.update_one(
            {"id": registration_id},
            {"$push": {"attachments": attachment_data}},
        )

        return {
            "message": "Attachment saved successfully",
            "attachment_id": attachment_data["id"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error saving attachment: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to save attachment"
        )


@api_router.get("/admin-registration/{registration_id}/attachments")
async def get_attachments(registration_id: str):
    """Get all attachments for a registration"""
    try:
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Get attachments and ensure proper data URI prefixes
        attachments = registration.get("attachments", [])

        # Process each attachment to ensure proper data URI prefixes
        for attachment in attachments:
            if "url" in attachment and attachment.get("url"):
                url = attachment["url"]

                # Handle image attachments
                if attachment.get("type") == "Image" and not url.startswith(
                    "data:image/"
                ):
                    # Add data URI prefix for images
                    attachment["url"] = f"data:image/png;base64,{url}"

                # Handle PDF attachments
                elif attachment.get("type") == "PDF" and not url.startswith(
                    "data:application/pdf"
                ):
                    # Add data URI prefix for PDFs
                    attachment["url"] = f"data:application/pdf;base64,{url}"

        return {"attachments": attachments}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching attachments: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch attachments"
        )


@api_router.delete(
    "/admin-registration/{registration_id}/attachment/{attachment_id}"
)
async def delete_attachment(registration_id: str, attachment_id: str):
    """Delete an attachment from a registration"""
    try:
        # First check if the registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if the attachment exists in this registration
        attachments = registration.get("attachments", [])
        attachment_exists = any(
            att.get("id") == attachment_id for att in attachments
        )

        if not attachment_exists:
            raise HTTPException(status_code=404, detail="Attachment not found")

        # Delete the attachment
        result = await db.admin_registrations.update_one(
            {"id": registration_id},
            {"$pull": {"attachments": {"id": attachment_id}}},
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Attachment not found")

        return {"message": "Attachment deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting attachment: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to delete attachment"
        )


@api_router.post("/share-attachment", response_model=ShareAttachmentResponse)
async def create_attachment_share(request: ShareAttachmentRequest):
    """Create a temporary shareable link for an attachment with 30-minute expiration"""
    try:
        # Generate unique share ID
        share_id = str(uuid.uuid4())

        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(
            minutes=request.expires_in_minutes
        )

        # Store attachment data temporarily with TTL
        share_data = {
            "id": share_id,
            "attachment_data": request.attachment_data,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "access_count": 0,
        }

        # Insert into temporary shares collection with TTL index
        await db.temporary_shares.insert_one(share_data)

        # Create TTL index if it doesn't exist (expires documents after 30 minutes)
        try:
            await db.temporary_shares.create_index(
                "expires_at", expireAfterSeconds=0
            )
        except:
            pass  # Index might already exist

        # Generate URLs using the correct external base URL
        # Use the external URL that matches the frontend's REACT_APP_BACKEND_URL
        base_url = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com"
        share_url = f"{base_url}/api/shared-attachment/{share_id}/download"
        preview_url = f"{base_url}/api/shared-attachment/{share_id}/preview"

        return ShareAttachmentResponse(
            share_id=share_id,
            share_url=share_url,
            preview_url=preview_url,
            expires_at=expires_at.isoformat() + "Z",
            expires_in_minutes=request.expires_in_minutes,
        )

    except Exception as e:
        logging.error(f"Error creating attachment share: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to create shareable link"
        )


@api_router.get("/shared-attachment/{share_id}/preview")
async def preview_shared_attachment(share_id: str):
    """Preview a shared attachment"""
    try:
        # Find the shared attachment
        share_data = await db.temporary_shares.find_one({"id": share_id})
        if not share_data:
            raise HTTPException(
                status_code=404, detail="Shared link not found or expired"
            )

        # Check if expired
        if datetime.utcnow() > share_data["expires_at"]:
            await db.temporary_shares.delete_one({"id": share_id})
            raise HTTPException(
                status_code=404, detail="Shared link has expired"
            )

        # Increment access count
        await db.temporary_shares.update_one(
            {"id": share_id}, {"$inc": {"access_count": 1}}
        )

        attachment_data = share_data["attachment_data"]

        # Decode base64 data
        if attachment_data["url"].startswith("data:"):
            # Extract base64 data
            header, data = attachment_data["url"].split(",", 1)
            file_data = base64.b64decode(data)

            # Determine content type
            if "pdf" in header:
                media_type = "application/pdf"
            elif "image" in header:
                if "jpeg" in header:
                    media_type = "image/jpeg"
                elif "png" in header:
                    media_type = "image/png"
                else:
                    media_type = "image/*"
            else:
                media_type = "application/octet-stream"

            return Response(
                content=file_data,
                media_type=media_type,
                headers={
                    "Content-Disposition": f"inline; filename=\"{attachment_data.get('filename', 'document')}\""
                },
            )
        else:
            raise HTTPException(
                status_code=400, detail="Invalid attachment data format"
            )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error previewing shared attachment: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to preview attachment"
        )


@api_router.get("/shared-attachment/{share_id}/download")
async def download_shared_attachment(share_id: str):
    """Download a shared attachment"""
    try:
        # Find the shared attachment
        share_data = await db.temporary_shares.find_one({"id": share_id})
        if not share_data:
            raise HTTPException(
                status_code=404, detail="Shared link not found or expired"
            )

        # Check if expired
        if datetime.utcnow() > share_data["expires_at"]:
            await db.temporary_shares.delete_one({"id": share_id})
            raise HTTPException(
                status_code=404, detail="Shared link has expired"
            )

        # Increment access count
        await db.temporary_shares.update_one(
            {"id": share_id}, {"$inc": {"access_count": 1}}
        )

        attachment_data = share_data["attachment_data"]

        # Decode base64 data
        if attachment_data["url"].startswith("data:"):
            # Extract base64 data
            header, data = attachment_data["url"].split(",", 1)
            file_data = base64.b64decode(data)

            # Determine content type
            if "pdf" in header:
                media_type = "application/pdf"
            elif "image" in header:
                if "jpeg" in header:
                    media_type = "image/jpeg"
                elif "png" in header:
                    media_type = "image/png"
                else:
                    media_type = "image/*"
            else:
                media_type = "application/octet-stream"

            return Response(
                content=file_data,
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename=\"{attachment_data.get('filename', 'document')}\""
                },
            )
        else:
            raise HTTPException(
                status_code=400, detail="Invalid attachment data format"
            )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error downloading shared attachment: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to download attachment"
        )


@api_router.post("/register", response_model=dict)
async def register_for_testing(registration: UserRegistrationCreate):
    """Register a user for Hepatitis C and HIV testing - sends email to support team"""
    try:
        # Create registration record
        registration_dict = registration.dict()
        registration_obj = UserRegistration(**registration_dict)

        # Send registration email to support team
        email_sent = send_registration_email(registration_dict)

        if not email_sent:
            logging.warning(
                "Registration email failed to send, but registration will still be processed"
            )

        return {
            "message": "Registration successful",
            "registration_id": registration_obj.id,
            "status": "pending",
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Registration failed. Please try again."
        )


@api_router.post("/admin-register", response_model=dict)
async def admin_register_for_testing(registration: AdminRegistrationCreate):
    """Admin registration with extended fields and test data protection"""
    try:
        logging.info(
            f"Admin registration attempt - firstName: {registration.firstName}, lastName: {registration.lastName}"
        )

        # Validate production environment
        if not validate_production_environment():
            print("Environment validation failed - continuing with caution")

        # Check if this appears to be test data
        reg_data = registration.dict()
        if is_test_data(reg_data):
            # environment = os.environ.get("ENVIRONMENT", "production").lower()
            if settings.environment == "production":
                logging.warning(
                    f"Test data rejected in production: {registration.firstName} {registration.lastName}"
                )
                raise HTTPException(
                    status_code=400,
                    detail="Test data is not allowed in production environment",
                )
            else:
                logging.warning(
                    f"Test data detected in non-production environment: {registration.firstName} {registration.lastName}"
                )

        # Create admin registration record
        registration_dict = registration.dict()

        # Convert date objects to strings for MongoDB storage
        if registration_dict.get("dob") and isinstance(
            registration_dict["dob"], date
        ):
            registration_dict["dob"] = registration_dict["dob"].isoformat()
        if registration_dict.get("regDate") and isinstance(
            registration_dict["regDate"], date
        ):
            registration_dict["regDate"] = registration_dict[
                "regDate"
            ].isoformat()

        # Create registration object for database
        admin_registration = AdminRegistration(**registration_dict)

        # Clear HIV fields if test type is not HIV
        if admin_registration.testType != "HIV":
            admin_registration.hivDate = None
            admin_registration.hivResult = None
            admin_registration.hivType = None
            admin_registration.hivTester = "CM"  # Reset to default
        else:
            # Set current date for HIV test if not provided
            if not admin_registration.hivDate:
                admin_registration.hivDate = date.today().isoformat()
            # Set default tester if not provided
            if not admin_registration.hivTester:
                admin_registration.hivTester = "CM"

        # Clear hivType if hivResult is negative
        if admin_registration.hivResult == "negative":
            admin_registration.hivType = None

        # Convert the admin_registration to dict and handle date serialization for MongoDB
        admin_data = admin_registration.dict()

        # Convert any remaining date/datetime objects to strings for MongoDB
        for key, value in admin_data.items():
            if isinstance(value, date):
                admin_data[key] = value.isoformat()
            elif isinstance(value, datetime):
                admin_data[key] = value.isoformat()

        try:
            # Store in MongoDB - unique index will prevent duplicates
            result = await db.admin_registrations.insert_one(admin_data)
            logging.info(
                f"Admin registration saved for review - ID: {admin_registration.id}"
            )

            # Return response immediately
            response_data = {
                "message": "Registration saved for review",
                "registration_id": admin_registration.id,
                "status": "pending_review",
                "backup_created": False,  # Will be updated by background process
            }

            # Start backup process in background (non-blocking)
            asyncio.create_task(backup_client_data())

            return response_data

        except Exception as db_error:
            # Handle duplicate key error from unique index
            if "duplicate key" in str(db_error).lower() or "E11000" in str(
                db_error
            ):
                # Find existing registration and return it
                existing = await db.admin_registrations.find_one(
                    {
                        "firstName": registration.firstName,
                        "lastName": registration.lastName,
                    }
                )
                if existing:
                    logging.warning(
                        f"DUPLICATE BLOCKED by database: {registration.firstName} {registration.lastName}"
                    )
                    return {
                        "message": "Registration already exists - using existing record",
                        "registration_id": existing["id"],
                        "status": existing.get("status", "pending_review"),
                        "duplicate_prevented": True,
                    }
            raise db_error

    except ValidationError as ve:
        logging.error(f"Admin registration validation error: {str(ve)}")
        raise HTTPException(status_code=422, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Admin registration error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Registration failed. Please try again."
        )


@api_router.get("/admin-registrations-pending", response_model=List[dict])
async def get_pending_admin_registrations():
    """Get all admin registrations with pending_review status for dashboard"""
    try:
        registrations = (
            await db.admin_registrations.find({"status": "pending_review"})
            .sort("timestamp", -1)
            .to_list(1000)
        )

        # Return simplified list with essential fields including photo for dashboard
        simplified_list = []
        for reg in registrations:
            simplified_list.append(
                {
                    "id": reg.get("id"),
                    "firstName": reg.get("firstName"),
                    "lastName": reg.get("lastName"),
                    "regDate": reg.get("regDate"),
                    "timestamp": reg.get("timestamp"),
                    "disposition": reg.get(
                        "disposition"
                    ),  # Include for search filtering
                    "referralSite": reg.get(
                        "referralSite"
                    ),  # Include for search filtering
                    "photo": reg.get("photo"),  # Include photo for preview
                }
            )

        return simplified_list
    except Exception as e:
        logging.error(f"Error fetching pending admin registrations: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch pending registrations"
        )


@api_router.get("/admin-registration/{registration_id}", response_model=dict)
async def get_admin_registration_by_id(registration_id: str):
    """Get specific admin registration by ID for editing"""
    try:
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )

        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Remove MongoDB's _id field if present
        if "_id" in registration:
            del registration["_id"]

        return registration
    except HTTPException:
        raise
    except Exception as e:
        logging.error(
            f"Error fetching admin registration {registration_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch registration"
        )


@api_router.put("/admin-registration/{registration_id}", response_model=dict)
async def update_admin_registration(
    registration_id: str, registration: AdminRegistrationCreate
):
    """Update an existing admin registration"""
    try:
        # Find the existing registration
        existing = await db.admin_registrations.find_one(
            {"id": registration_id}
        )

        if not existing:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Convert the updated data
        registration_dict = registration.dict()

        # Convert date objects to strings for MongoDB storage
        if registration_dict.get("dob") and isinstance(
            registration_dict["dob"], date
        ):
            registration_dict["dob"] = registration_dict["dob"].isoformat()
        if registration_dict.get("regDate") and isinstance(
            registration_dict["regDate"], date
        ):
            registration_dict["regDate"] = registration_dict[
                "regDate"
            ].isoformat()

        # Keep the original id and timestamp, but update everything else
        registration_dict["id"] = registration_id
        registration_dict["timestamp"] = existing.get("timestamp")
        registration_dict["status"] = (
            "pending_review"  # Keep as pending_review
        )

        # Update in MongoDB
        result = await db.admin_registrations.replace_one(
            {"id": registration_id}, registration_dict
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Registration not found or no changes made",
            )

        logging.info(f"Admin registration updated - ID: {registration_id}")
        return {
            "message": "Registration updated successfully",
            "registration_id": registration_id,
            "status": "pending_review",
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(
            f"Error updating admin registration {registration_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to update registration"
        )


@api_router.delete(
    "/admin-registration/{registration_id}", response_model=dict
)
async def delete_admin_registration(registration_id: str):
    """Delete an admin registration and all associated data"""
    try:
        # Find the existing registration
        existing = await db.admin_registrations.find_one(
            {"id": registration_id}
        )

        if not existing:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Delete all associated data to prevent orphaned records
        deletion_counts = {}

        # Delete activities
        activities_result = await db.activities.delete_many(
            {"registration_id": registration_id}
        )
        deletion_counts["activities"] = activities_result.deleted_count

        # Delete test records
        tests_result = await db.test_records.delete_many(
            {"registration_id": registration_id}
        )
        deletion_counts["test_records"] = tests_result.deleted_count

        # Delete notes records
        notes_result = await db.notes_records.delete_many(
            {"registration_id": registration_id}
        )
        deletion_counts["notes_records"] = notes_result.deleted_count

        # Delete medications
        medications_result = await db.medications.delete_many(
            {"registration_id": registration_id}
        )
        deletion_counts["medications"] = medications_result.deleted_count

        # Delete interactions
        interactions_result = await db.interactions.delete_many(
            {"registration_id": registration_id}
        )
        deletion_counts["interactions"] = interactions_result.deleted_count

        # Delete dispensing records
        dispensing_result = await db.dispensing.delete_many(
            {"registration_id": registration_id}
        )
        deletion_counts["dispensing"] = dispensing_result.deleted_count

        # Delete the registration itself
        result = await db.admin_registrations.delete_one(
            {"id": registration_id}
        )

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        total_associated_records = sum(deletion_counts.values())

        logging.info(
            f"Admin registration deleted - ID: {registration_id}, Associated records deleted: {total_associated_records}"
        )
        logging.info(f"Deletion breakdown: {deletion_counts}")

        return {
            "message": "Registration and all associated data deleted successfully",
            "registration_id": registration_id,
            "associated_records_deleted": total_associated_records,
            "deletion_breakdown": deletion_counts,
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(
            f"Error deleting admin registration {registration_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to delete registration: {str(e)}"
        )


@api_router.get("/admin-registrations-submitted", response_model=List[dict])
async def get_submitted_admin_registrations():
    """Get all submitted (completed) admin registrations"""
    try:
        registrations = (
            await db.admin_registrations.find({"status": "completed"})
            .sort("timestamp", -1)
            .to_list(None)
        )

        # Return simplified data for listing
        simplified_registrations = []
        for reg in registrations:
            simplified_registrations.append(
                {
                    "id": reg.get("id"),
                    "firstName": reg.get("firstName"),
                    "lastName": reg.get("lastName"),
                    "regDate": reg.get("regDate"),
                    "timestamp": reg.get("timestamp"),
                    "finalized_at": reg.get("finalized_at"),
                    "status": reg.get("status"),
                    "disposition": reg.get(
                        "disposition"
                    ),  # Include for search filtering
                    "referralSite": reg.get(
                        "referralSite"
                    ),  # Include for search filtering
                    "photo": reg.get("photo"),  # Include photo for display
                }
            )

        logging.info(
            f"Retrieved {len(simplified_registrations)} submitted admin registrations"
        )
        return simplified_registrations

    except Exception as e:
        logging.error(
            f"Error retrieving submitted admin registrations: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve submitted registrations",
        )


@api_router.get(
    "/admin-registration/{registration_id}/finalize", response_model=dict
)
@api_router.post(
    "/admin-registration/{registration_id}/finalize", response_model=dict
)
async def finalize_admin_registration(registration_id: str):
    """FORCE FINALIZE - Direct email sending, no background processing"""
    try:
        logging.info(f"FORCE FINALIZE: Starting for {registration_id}")

        # Find the registration
        registration_data = await db.admin_registrations.find_one(
            {"id": registration_id}
        )

        if not registration_data:
            logging.error(
                f"FORCE FINALIZE ERROR: Registration {registration_id} not found"
            )
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        if registration_data.get("status") != "pending_review":
            logging.error(
                f"FORCE FINALIZE ERROR: Registration {registration_id} not pending review"
            )
            raise HTTPException(
                status_code=400, detail="Registration is not pending review"
            )

        # Update database FIRST
        toronto_tz = pytz.timezone("America/Toronto")
        finalized_time = datetime.now(toronto_tz).isoformat()

        await db.admin_registrations.update_one(
            {"id": registration_id},
            {"$set": {"status": "completed", "finalized_at": finalized_time}},
        )
        logging.info(
            f"FORCE FINALIZE: Database updated to completed for {registration_id}"
        )

        # FORCE EMAIL SENDING - SYNCHRONOUSLY, NO BACKGROUND THREADS
        email_sent = False
        email_error = None

        try:
            # CRITICAL: Get support email from environment
            # env_support_email = os.environ.get("SUPPORT_EMAIL")
            # fallback_email = "420pharmacyprogram@gmail.com"
            # support_email = (
            #     env_support_email if env_support_email else fallback_email
            # )
            # logging.info(
            #     f"FORCE EMAIL: Environment SUPPORT_EMAIL = {os.environ.get('SUPPORT_EMAIL', 'NOT SET')}"
            # )
            # logging.error(
            #     f"🚨 EMAIL DEBUG - Raw env var: {repr(os.environ.get('SUPPORT_EMAIL'))}"
            # )
            # logging.error(
            #     f"🚨 EMAIL DEBUG - Env support_email: {env_support_email}"
            # )

            support_email = settings.support_email

            subject = f"New Registration - {registration_data.get('firstName')} {registration_data.get('lastName')}"

            # EXTENSIVE LOGGING FOR DEBUGGING
            logging.error(
                f"🚨 EMAIL DEBUG - Final support_email: {support_email}"
            )
            logging.error(f"🚨 EMAIL DEBUG - Will send to: {support_email}")

            logging.info(
                f"FORCE EMAIL: Sending to {support_email} for {registration_id}"
            )
            logging.info(
                f"FORCE EMAIL: Resolved support_email = {support_email}"
            )

            email_body = f"""
Registration Date: {registration_data.get('regDate') or 'Not provided'}

PATIENT INFORMATION:
• Name: {registration_data.get('firstName')} {registration_data.get('lastName')}
• Date of Birth: {registration_data.get('dob') or 'Not provided'}
• Age: {registration_data.get('age') or 'Not provided'}
• Gender: {registration_data.get('gender') or 'Not provided'}
• Health Card: {registration_data.get('healthCard') or 'Not provided'}
• Health Card Version: {registration_data.get('healthCardVersion') or 'Not provided'}

CONTACT INFORMATION:
• Phone 1: {registration_data.get('phone1') or 'Not provided'}
• Phone 2: {registration_data.get('phone2') or 'Not provided'}
• Email: {registration_data.get('email') or 'Not provided'}
• Address: {registration_data.get('address') or 'Not provided'}
• City: {registration_data.get('city') or 'Not provided'}
• Province: {registration_data.get('province')}
• Postal Code: {registration_data.get('postalCode') or 'Not provided'}

OTHER INFORMATION:
• Patient Consent: {registration_data.get('patientConsent')}
• Disposition: {registration_data.get('disposition') or 'Not provided'}
• Referral Site: {registration_data.get('referralSite') or 'Not provided'}
• Physician: {registration_data.get('physician') or 'Not specified'}
• Language: {registration_data.get('language')}

ADDITIONAL NOTES:
• Special Attention: {registration_data.get('specialAttention') or 'None'}
• Instructions: {registration_data.get('instructions') or 'None'}
• Clinical Summary: {registration_data.get('summaryTemplate') or 'None provided'}
"""

            # Include photos up to reasonable size for email
            photo_data = None
            if registration_data.get("photo"):
                photo_size = len(registration_data["photo"])
                if photo_size < 2 * 1024 * 1024:  # Include photos under 2MB
                    photo_data = registration_data["photo"]
                    logging.info(
                        f"FORCE EMAIL: Including photo ({photo_size} bytes)"
                    )
                else:
                    logging.info(
                        f"FORCE EMAIL: Photo too large ({photo_size} bytes), skipping to ensure email delivery"
                    )

            # SEND EMAIL DIRECTLY - NO ASYNC, NO THREADING
            await send_email(
                to_email=support_email,
                subject=subject,
                body=email_body,
                photo_base64=photo_data,
            )

            email_sent = True
            logging.info(
                f"FORCE EMAIL SUCCESS: Email sent successfully for {registration_id}"
            )

        except Exception as email_error_exc:
            email_error = str(email_error_exc)
            logging.error(
                f"FORCE EMAIL ERROR: Failed to send email for {registration_id}: {email_error}"
            )
            # Don't fail the entire operation - registration is still finalized

        # Return detailed response
        response = {
            "message": f"Registration finalized {'and email sent' if email_sent else 'but email failed'}",
            "registration_id": registration_id,
            "status": "completed",
            "finalized_at": finalized_time,
            "email_sent": email_sent,
            "email_error": email_error,
            "photo_attached": bool(photo_data and len(photo_data) > 0),
        }

        logging.info(
            f"FORCE FINALIZE COMPLETE: {registration_id} - Email sent: {email_sent}"
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        logging.error(
            f"FORCE FINALIZE FATAL ERROR: {registration_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to finalize: {str(e)}"
        )


@api_router.delete("/admin-registrations-cleanup", response_model=dict)
async def cleanup_duplicate_registrations():
    """Cleanup duplicate admin registrations - keep only latest per person"""
    try:
        # Get all registrations
        all_registrations = await db.admin_registrations.find().to_list(1000)

        # Group by firstName + lastName combination
        grouped = {}
        for reg in all_registrations:
            key = f"{reg.get('firstName', '').lower().strip()}_{reg.get('lastName', '').lower().strip()}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(reg)

        deleted_count = 0
        kept_count = 0

        # For each group, keep only the latest registration
        for key, registrations in grouped.items():
            if len(registrations) > 1:
                # Sort by timestamp (newest first)
                sorted_regs = sorted(
                    registrations,
                    key=lambda x: x.get("timestamp", ""),
                    reverse=True,
                )

                # Keep the first (newest) registration
                to_keep = sorted_regs[0]
                to_delete = sorted_regs[1:]

                # Delete the older duplicates
                for reg in to_delete:
                    await db.admin_registrations.delete_one(
                        {"id": reg.get("id")}
                    )
                    deleted_count += 1
                    logging.info(
                        f"Deleted duplicate registration: {reg.get('firstName')} {reg.get('lastName')} - ID: {reg.get('id')}"
                    )

                kept_count += 1
                logging.info(
                    f"Kept latest registration: {to_keep.get('firstName')} {to_keep.get('lastName')} - ID: {to_keep.get('id')}"
                )
            else:
                kept_count += 1

        logging.info(
            f"Cleanup completed - Deleted: {deleted_count}, Kept: {kept_count}"
        )
        return {
            "message": "Duplicate cleanup completed",
            "deleted_count": deleted_count,
            "kept_count": kept_count,
            "details": f"Removed {deleted_count} duplicate registrations, kept {kept_count} unique registrations",
        }

    except Exception as e:
        logging.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to cleanup duplicates"
        )


@api_router.delete(
    "/admin-registrations-keep-latest-today", response_model=dict
)
async def keep_only_latest_today_registration():
    """Delete all registrations except the most recent one from today"""
    try:
        from datetime import date

        today_str = date.today().isoformat()

        # Get all registrations
        all_registrations = await db.admin_registrations.find().to_list(1000)

        if not all_registrations:
            return {
                "message": "No registrations found",
                "deleted_count": 0,
                "kept_count": 0,
                "details": "Database is empty",
            }

        # Find registrations from today
        today_registrations = []
        other_registrations = []

        for reg in all_registrations:
            reg_date = reg.get("regDate", "")
            if reg_date == today_str:
                today_registrations.append(reg)
            else:
                other_registrations.append(reg)

        if not today_registrations:
            # No registrations from today, delete everything
            deleted_count = len(all_registrations)
            for reg in all_registrations:
                await db.admin_registrations.delete_one({"id": reg.get("id")})
                logging.info(
                    f"Deleted registration: {reg.get('firstName')} {reg.get('lastName')} - ID: {reg.get('id')}"
                )

            return {
                "message": "No registrations from today found - deleted all registrations",
                "deleted_count": deleted_count,
                "kept_count": 0,
                "details": f"Deleted all {deleted_count} registrations (none were from today)",
            }

        # Sort today's registrations by timestamp (newest first)
        today_registrations.sort(
            key=lambda x: x.get("timestamp", ""), reverse=True
        )

        # Keep the first (newest) registration from today
        to_keep = today_registrations[0]
        to_delete = (
            today_registrations[1:] + other_registrations
        )  # Delete other today registrations + all older registrations

        deleted_count = 0

        # Delete all except the latest from today
        for reg in to_delete:
            await db.admin_registrations.delete_one({"id": reg.get("id")})
            deleted_count += 1
            reg_date = reg.get("regDate", "unknown")
            logging.info(
                f"Deleted registration from {reg_date}: {reg.get('firstName')} {reg.get('lastName')} - ID: {reg.get('id')}"
            )

        logging.info(
            f"Kept latest registration from today: {to_keep.get('firstName')} {to_keep.get('lastName')} - ID: {to_keep.get('id')}"
        )

        return {
            "message": "Cleanup completed - kept only the latest registration from today",
            "deleted_count": deleted_count,
            "kept_count": 1,
            "details": f"Deleted {deleted_count} registrations, kept 1 registration from today ({today_str})",
            "kept_registration": {
                "id": to_keep.get("id"),
                "name": f"{to_keep.get('firstName')} {to_keep.get('lastName')}",
                "regDate": to_keep.get("regDate"),
                "timestamp": to_keep.get("timestamp"),
            },
        }

    except Exception as e:
        logging.error(f"Error during targeted cleanup: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to perform targeted cleanup"
        )


@api_router.get("/registrations", response_model=List[UserRegistration])
async def get_all_registrations():
    """Get all registrations (admin endpoint)"""
    try:
        registrations = await db.registrations.find().to_list(1000)
        return [UserRegistration(**reg) for reg in registrations]
    except Exception as e:
        logging.error(f"Error fetching registrations: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch registrations"
        )


@api_router.post("/contact", response_model=dict)
async def submit_contact_message(message: ContactMessageCreate):
    """Submit a contact message"""
    try:
        # Create contact message record
        message_dict = message.dict()
        message_obj = ContactMessage(**message_dict)

        # Send contact email to support team
        email_sent = send_contact_email(message_dict)

        if not email_sent:
            logging.warning(
                "Contact email failed to send, but message will still be stored"
            )

        # Convert datetime objects to strings for MongoDB storage
        message_data = message_obj.dict()
        if "timestamp" in message_data:
            message_data["timestamp"] = message_data["timestamp"].isoformat()

        result = await db.contact_messages.insert_one(message_data)

        return {
            "message": "Contact message sent successfully",
            "message_id": message_obj.id,
            "email_sent": email_sent,
        }

    except Exception as e:
        logging.error(f"Contact message error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to send message. Please try again."
        )


@api_router.get("/contact-messages", response_model=List[ContactMessage])
async def get_contact_messages():
    """Get all contact messages (admin endpoint)"""
    try:
        messages = await db.contact_messages.find().to_list(1000)
        return [ContactMessage(**msg) for msg in messages]
    except Exception as e:
        logging.error(f"Error fetching contact messages: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch contact messages"
        )


# Clinical Summary Template API Endpoints
@api_router.get("/clinical-templates", response_model=List[ClinicalTemplate])
async def get_all_templates():
    """Get all clinical summary templates"""
    try:
        templates = await db.clinical_templates.find().to_list(1000)
        return [ClinicalTemplate(**template) for template in templates]
    except Exception as e:
        logging.error(f"Error fetching templates: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch templates"
        )


@api_router.post("/clinical-templates", response_model=ClinicalTemplate)
async def create_template(template: ClinicalTemplateCreate):
    """Create a new clinical summary template"""
    try:
        template_dict = template.dict()
        template_obj = ClinicalTemplate(**template_dict)

        # Convert to dict for MongoDB storage
        template_data = template_obj.dict()
        template_data["created_at"] = template_obj.created_at.isoformat()
        template_data["updated_at"] = template_obj.updated_at.isoformat()

        result = await db.clinical_templates.insert_one(template_data)

        if result.inserted_id:
            logging.info(f"Template created successfully: {template_obj.name}")
            return template_obj
        else:
            raise HTTPException(
                status_code=500, detail="Failed to create template"
            )

    except Exception as e:
        logging.error(f"Error creating template: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to create template"
        )


@api_router.put(
    "/clinical-templates/{template_id}", response_model=ClinicalTemplate
)
async def update_template(
    template_id: str, template_update: ClinicalTemplateUpdate
):
    """Update an existing clinical summary template"""
    try:
        # Find the existing template
        existing_template = await db.clinical_templates.find_one(
            {"id": template_id}
        )
        if not existing_template:
            raise HTTPException(status_code=404, detail="Template not found")

        # Update the template
        update_data = {
            k: v for k, v in template_update.dict().items() if v is not None
        }
        update_data["updated_at"] = datetime.utcnow().isoformat()

        result = await db.clinical_templates.update_one(
            {"id": template_id}, {"$set": update_data}
        )

        if result.modified_count > 0:
            # Return the updated template
            updated_template = await db.clinical_templates.find_one(
                {"id": template_id}
            )
            return ClinicalTemplate(**updated_template)
        else:
            raise HTTPException(
                status_code=500, detail="Failed to update template"
            )

    except Exception as e:
        logging.error(f"Error updating template: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to update template"
        )


@api_router.delete("/clinical-templates/{template_id}", response_model=dict)
async def delete_template(template_id: str):
    """Delete a clinical summary template"""
    try:
        result = await db.clinical_templates.delete_one({"id": template_id})

        if result.deleted_count > 0:
            logging.info(f"Template deleted successfully: {template_id}")
            return {"message": "Template deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Template not found")

    except Exception as e:
        logging.error(f"Error deleting template: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to delete template"
        )


@api_router.post("/clinical-templates/save-all", response_model=dict)
async def save_all_templates(templates: dict):
    """Save all templates from frontend (migration from localStorage)"""
    try:
        saved_count = 0

        for template_name, template_content in templates.items():
            if template_name and template_content:
                # Check if template already exists
                existing = await db.clinical_templates.find_one(
                    {"name": template_name}
                )

                if existing:
                    # Update existing template
                    await db.clinical_templates.update_one(
                        {"name": template_name},
                        {
                            "$set": {
                                "content": template_content,
                                "updated_at": datetime.utcnow().isoformat(),
                            }
                        },
                    )
                else:
                    # Create new template
                    template_obj = ClinicalTemplate(
                        name=template_name, content=template_content
                    )
                    template_data = template_obj.dict()
                    template_data["created_at"] = (
                        template_obj.created_at.isoformat()
                    )
                    template_data["updated_at"] = (
                        template_obj.updated_at.isoformat()
                    )

                    await db.clinical_templates.insert_one(template_data)

                saved_count += 1

        logging.info(f"Saved {saved_count} templates to database")
        return {
            "message": f"Successfully saved {saved_count} templates",
            "count": saved_count,
        }

    except Exception as e:
        logging.error(f"Error saving templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save templates")


# Notes Template API Endpoints (identical to Clinical Templates)
@api_router.get("/notes-templates", response_model=List[NotesTemplate])
async def get_all_notes_templates():
    """Get all Notes templates"""
    try:
        templates = await db.notes_templates.find().to_list(1000)
        return [NotesTemplate(**template) for template in templates]
    except Exception as e:
        logging.error(f"Error fetching Notes templates: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch Notes templates"
        )


@api_router.post("/notes-templates", response_model=NotesTemplate)
async def create_notes_template(template: NotesTemplateCreate):
    """Create a new Notes template"""
    try:
        template_dict = template.dict()
        template_obj = NotesTemplate(**template_dict)

        # Convert to dict for MongoDB storage
        template_data = template_obj.dict()
        template_data["created_at"] = template_obj.created_at.isoformat()
        template_data["updated_at"] = template_obj.updated_at.isoformat()

        result = await db.notes_templates.insert_one(template_data)

        if result.inserted_id:
            logging.info(
                f"Notes template created successfully: {template_obj.name}"
            )
            return template_obj
        else:
            raise HTTPException(
                status_code=500, detail="Failed to create Notes template"
            )

    except Exception as e:
        logging.error(f"Error creating Notes template: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to create Notes template"
        )


@api_router.put("/notes-templates/{template_id}", response_model=NotesTemplate)
async def update_notes_template(
    template_id: str, template_update: NotesTemplateUpdate
):
    """Update an existing Notes template"""
    try:
        # Find the existing template
        existing_template = await db.notes_templates.find_one(
            {"id": template_id}
        )
        if not existing_template:
            raise HTTPException(
                status_code=404, detail="Notes template not found"
            )

        # Update the template
        update_data = {
            k: v for k, v in template_update.dict().items() if v is not None
        }
        update_data["updated_at"] = datetime.utcnow().isoformat()

        result = await db.notes_templates.update_one(
            {"id": template_id}, {"$set": update_data}
        )

        if result.modified_count > 0:
            # Return the updated template
            updated_template = await db.notes_templates.find_one(
                {"id": template_id}
            )
            return NotesTemplate(**updated_template)
        else:
            raise HTTPException(
                status_code=500, detail="Failed to update Notes template"
            )

    except Exception as e:
        logging.error(f"Error updating Notes template: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to update Notes template"
        )


@api_router.delete("/notes-templates/{template_id}", response_model=dict)
async def delete_notes_template(template_id: str):
    """Delete a Notes template"""
    try:
        result = await db.notes_templates.delete_one({"id": template_id})

        if result.deleted_count > 0:
            logging.info(f"Notes template deleted successfully: {template_id}")
            return {"message": "Notes template deleted successfully"}
        else:
            raise HTTPException(
                status_code=404, detail="Notes template not found"
            )

    except Exception as e:
        logging.error(f"Error deleting Notes template: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to delete Notes template"
        )


@api_router.post("/notes-templates/save-all", response_model=dict)
async def save_all_notes_templates(templates: dict):
    """Save all Notes templates from frontend"""
    try:
        saved_count = 0

        for template_name, template_content in templates.items():
            if (
                template_name and template_content is not None
            ):  # Allow empty content
                # Check if template already exists
                existing = await db.notes_templates.find_one(
                    {"name": template_name}
                )

                if existing:
                    # Update existing template
                    await db.notes_templates.update_one(
                        {"name": template_name},
                        {
                            "$set": {
                                "content": template_content,
                                "updated_at": datetime.utcnow().isoformat(),
                            }
                        },
                    )
                else:
                    # Create new template
                    template_obj = NotesTemplate(
                        name=template_name, content=template_content
                    )
                    template_data = template_obj.dict()
                    template_data["created_at"] = (
                        template_obj.created_at.isoformat()
                    )
                    template_data["updated_at"] = (
                        template_obj.updated_at.isoformat()
                    )

                    await db.notes_templates.insert_one(template_data)

                saved_count += 1

        logging.info(f"Saved {saved_count} Notes templates to database")
        return {
            "message": f"Successfully saved {saved_count} Notes templates",
            "count": saved_count,
        }

    except Exception as e:
        logging.error(f"Error saving Notes templates: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to save Notes templates"
        )


# Disposition Management API Endpoints
@api_router.get("/dispositions", response_model=List[Disposition])
async def get_all_dispositions():
    """Get all dispositions"""
    try:
        dispositions = await db.dispositions.find().to_list(1000)
        return [Disposition(**disposition) for disposition in dispositions]
    except Exception as e:
        logging.error(f"Error fetching dispositions: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch dispositions"
        )


@api_router.post("/dispositions", response_model=Disposition)
async def create_disposition(disposition: DispositionCreate):
    """Create a new disposition"""
    try:
        # Check if disposition already exists
        existing = await db.dispositions.find_one({"name": disposition.name})
        if existing:
            raise HTTPException(
                status_code=400, detail="Disposition already exists"
            )

        disposition_obj = Disposition(**disposition.dict())

        # Convert to dict for MongoDB storage
        disposition_data = disposition_obj.dict()
        disposition_data["created_at"] = disposition_obj.created_at.isoformat()
        disposition_data["updated_at"] = disposition_obj.updated_at.isoformat()

        result = await db.dispositions.insert_one(disposition_data)

        if result.inserted_id:
            logging.info(
                f"Disposition created successfully: {disposition_obj.name}"
            )
            return disposition_obj
        else:
            raise HTTPException(
                status_code=500, detail="Failed to create disposition"
            )

    except Exception as e:
        logging.error(f"Error creating disposition: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to create disposition"
        )


@api_router.put("/dispositions/{disposition_id}", response_model=Disposition)
async def update_disposition(
    disposition_id: str, disposition_update: DispositionUpdate
):
    """Update an existing disposition"""
    try:
        # Check if disposition exists
        existing = await db.dispositions.find_one({"id": disposition_id})
        if not existing:
            raise HTTPException(
                status_code=404, detail="Disposition not found"
            )

        # Check if name is being updated to an existing name
        if disposition_update.name:
            name_exists = await db.dispositions.find_one(
                {
                    "name": disposition_update.name,
                    "id": {"$ne": disposition_id},
                }
            )
            if name_exists:
                raise HTTPException(
                    status_code=400, detail="Disposition name already exists"
                )

        # Update the disposition
        update_data = {
            k: v for k, v in disposition_update.dict().items() if v is not None
        }
        update_data["updated_at"] = datetime.utcnow().isoformat()

        result = await db.dispositions.update_one(
            {"id": disposition_id}, {"$set": update_data}
        )

        if result.modified_count > 0:
            # Get updated disposition
            updated_disposition = await db.dispositions.find_one(
                {"id": disposition_id}
            )
            logging.info(f"Disposition updated successfully: {disposition_id}")
            return Disposition(**updated_disposition)
        else:
            raise HTTPException(
                status_code=404, detail="Disposition not found"
            )

    except Exception as e:
        logging.error(f"Error updating disposition: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to update disposition"
        )


@api_router.delete("/dispositions/{disposition_id}", response_model=dict)
async def delete_disposition(disposition_id: str):
    """Delete a disposition"""
    try:
        # Check if disposition exists and is not default
        existing = await db.dispositions.find_one({"id": disposition_id})
        if not existing:
            raise HTTPException(
                status_code=404, detail="Disposition not found"
            )

        if existing.get("is_default", False):
            raise HTTPException(
                status_code=400, detail="Cannot delete default disposition"
            )

        result = await db.dispositions.delete_one({"id": disposition_id})

        if result.deleted_count > 0:
            logging.info(f"Disposition deleted successfully: {disposition_id}")
            return {"message": "Disposition deleted successfully"}
        else:
            raise HTTPException(
                status_code=404, detail="Disposition not found"
            )

    except Exception as e:
        logging.error(f"Error deleting disposition: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to delete disposition"
        )


@api_router.post("/dispositions/save-all", response_model=dict)
async def save_all_dispositions(dispositions: List[DispositionCreate]):
    """Save all dispositions from frontend"""
    try:
        saved_count = 0

        for disposition_data in dispositions:
            if disposition_data.name:
                # Check if disposition already exists
                existing = await db.dispositions.find_one(
                    {"name": disposition_data.name}
                )

                if existing:
                    # Update existing disposition
                    await db.dispositions.update_one(
                        {"name": disposition_data.name},
                        {
                            "$set": {
                                "is_frequent": disposition_data.is_frequent,
                                "is_default": disposition_data.is_default,
                                "updated_at": datetime.utcnow().isoformat(),
                            }
                        },
                    )
                else:
                    # Create new disposition
                    disposition_obj = Disposition(**disposition_data.dict())
                    disposition_dict = disposition_obj.dict()
                    disposition_dict["created_at"] = (
                        disposition_obj.created_at.isoformat()
                    )
                    disposition_dict["updated_at"] = (
                        disposition_obj.updated_at.isoformat()
                    )

                    await db.dispositions.insert_one(disposition_dict)

                saved_count += 1

        logging.info(f"Saved {saved_count} dispositions to database")
        return {
            "message": f"Successfully saved {saved_count} dispositions",
            "count": saved_count,
        }

    except Exception as e:
        logging.error(f"Error saving dispositions: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to save dispositions"
        )


# Referral Site Management API Endpoints
@api_router.get("/referral-sites", response_model=List[ReferralSite])
async def get_all_referral_sites():
    """Get all referral sites"""
    try:
        referral_sites = await db.referral_sites.find().to_list(1000)
        return [ReferralSite(**site) for site in referral_sites]
    except Exception as e:
        logging.error(f"Error fetching referral sites: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch referral sites"
        )


@api_router.post("/referral-sites", response_model=ReferralSite)
async def create_referral_site(referral_site: ReferralSiteCreate):
    """Create a new referral site"""
    try:
        # Check if referral site already exists
        existing = await db.referral_sites.find_one(
            {"name": referral_site.name}
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Referral site already exists"
            )

        referral_site_obj = ReferralSite(**referral_site.dict())

        # Convert to dict for MongoDB storage
        referral_site_data = referral_site_obj.dict()
        referral_site_data["created_at"] = (
            referral_site_obj.created_at.isoformat()
        )
        referral_site_data["updated_at"] = (
            referral_site_obj.updated_at.isoformat()
        )

        result = await db.referral_sites.insert_one(referral_site_data)

        if result.inserted_id:
            logging.info(
                f"Referral site created successfully: {referral_site_obj.name}"
            )
            return referral_site_obj
        else:
            raise HTTPException(
                status_code=500, detail="Failed to create referral site"
            )

    except Exception as e:
        logging.error(f"Error creating referral site: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to create referral site"
        )


@api_router.put(
    "/referral-sites/{referral_site_id}", response_model=ReferralSite
)
async def update_referral_site(
    referral_site_id: str, referral_site_update: ReferralSiteUpdate
):
    """Update an existing referral site"""
    try:
        # Check if referral site exists
        existing = await db.referral_sites.find_one({"id": referral_site_id})
        if not existing:
            raise HTTPException(
                status_code=404, detail="Referral site not found"
            )

        # Check if name is being updated to an existing name
        if referral_site_update.name:
            name_exists = await db.referral_sites.find_one(
                {
                    "name": referral_site_update.name,
                    "id": {"$ne": referral_site_id},
                }
            )
            if name_exists:
                raise HTTPException(
                    status_code=400, detail="Referral site name already exists"
                )

        # Update the referral site
        update_data = {
            k: v
            for k, v in referral_site_update.dict().items()
            if v is not None
        }
        update_data["updated_at"] = datetime.utcnow().isoformat()

        result = await db.referral_sites.update_one(
            {"id": referral_site_id}, {"$set": update_data}
        )

        if result.modified_count > 0:
            # Get updated referral site
            updated_referral_site = await db.referral_sites.find_one(
                {"id": referral_site_id}
            )
            logging.info(
                f"Referral site updated successfully: {referral_site_id}"
            )
            return ReferralSite(**updated_referral_site)
        else:
            raise HTTPException(
                status_code=404, detail="Referral site not found"
            )

    except Exception as e:
        logging.error(f"Error updating referral site: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to update referral site"
        )


@api_router.delete("/referral-sites/{referral_site_id}", response_model=dict)
async def delete_referral_site(referral_site_id: str):
    """Delete a referral site"""
    try:
        # Check if referral site exists and is not default
        existing = await db.referral_sites.find_one({"id": referral_site_id})
        if not existing:
            raise HTTPException(
                status_code=404, detail="Referral site not found"
            )

        if existing.get("is_default", False):
            raise HTTPException(
                status_code=400, detail="Cannot delete default referral site"
            )

        result = await db.referral_sites.delete_one({"id": referral_site_id})

        if result.deleted_count > 0:
            logging.info(
                f"Referral site deleted successfully: {referral_site_id}"
            )
            return {"message": "Referral site deleted successfully"}
        else:
            raise HTTPException(
                status_code=404, detail="Referral site not found"
            )

    except Exception as e:
        logging.error(f"Error deleting referral site: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to delete referral site"
        )


@api_router.post("/referral-sites/save-all", response_model=dict)
async def save_all_referral_sites(referral_sites: List[ReferralSiteCreate]):
    """Save all referral sites from frontend"""
    try:
        saved_count = 0

        for referral_site_data in referral_sites:
            if referral_site_data.name:
                # Check if referral site already exists
                existing = await db.referral_sites.find_one(
                    {"name": referral_site_data.name}
                )

                if existing:
                    # Update existing referral site
                    await db.referral_sites.update_one(
                        {"name": referral_site_data.name},
                        {
                            "$set": {
                                "is_frequent": referral_site_data.is_frequent,
                                "is_default": referral_site_data.is_default,
                                "updated_at": datetime.utcnow().isoformat(),
                            }
                        },
                    )
                else:
                    # Create new referral site
                    referral_site_obj = ReferralSite(
                        **referral_site_data.dict()
                    )
                    referral_site_dict = referral_site_obj.dict()
                    referral_site_dict["created_at"] = (
                        referral_site_obj.created_at.isoformat()
                    )
                    referral_site_dict["updated_at"] = (
                        referral_site_obj.updated_at.isoformat()
                    )

                    await db.referral_sites.insert_one(referral_site_dict)

                saved_count += 1

        logging.info(f"Saved {saved_count} referral sites to database")
        return {
            "message": f"Successfully saved {saved_count} referral sites",
            "count": saved_count,
        }

    except Exception as e:
        logging.error(f"Error saving referral sites: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to save referral sites"
        )


# AI Assistant Endpoints
@api_router.post("/ai-assistant/chat", response_model=ChatResponse)
async def chat_with_assistant(query: ChatQuery):
    """Chat with the AI assistant about registration data"""
    try:
        # Get comprehensive registration statistics
        stats = await get_registration_stats()

        # Analyze the query and generate response
        response_text = analyze_query(query.message, stats)

        # Store conversation in database for memory
        chat_data = {
            "session_id": query.session_id,
            "user_message": query.message,
            "assistant_response": response_text,
            "timestamp": datetime.now(
                pytz.timezone("America/Toronto")
            ).isoformat(),
        }

        await db.chat_history.insert_one(chat_data)

        return ChatResponse(
            response=response_text, session_id=query.session_id
        )

    except Exception as e:
        logging.error(f"AI Assistant error: {str(e)}")
        return ChatResponse(
            response="I'm sorry, I encountered an error while analyzing your request. Please try again or ask a different question about the registration data.",
            session_id=query.session_id,
        )


@api_router.get("/ai-assistant/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = (
            await db.chat_history.find({"session_id": session_id})
            .sort("timestamp", 1)
            .to_list(50)
        )  # Last 50 messages

        return {"history": history}

    except Exception as e:
        logging.error(f"Error fetching chat history: {str(e)}")
        return {"history": []}


@api_router.get("/ai-assistant/stats")
async def get_assistant_stats():
    """Get current registration statistics for the AI assistant"""
    try:
        stats = await get_registration_stats()
        return {"stats": stats}
    except Exception as e:
        logging.error(f"Error fetching assistant stats: {str(e)}")
        return {"stats": {}}


# Include the router in the main app
# Test Management Endpoints
@api_router.post("/admin-registration/{registration_id}/test")
async def add_test_record(registration_id: str, test_data: TestRecordCreate):
    """Add a new test record for a registration"""
    try:
        # Verify registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Create test record
        test_record = TestRecord(
            **test_data.dict(), registration_id=registration_id
        )

        # Set current date if not provided
        if not test_record.test_date:
            test_record.test_date = date.today().isoformat()

        # Convert to dict for MongoDB
        test_data = test_record.dict()

        # Insert into database
        result = await db.test_records.insert_one(test_data)

        logger.info(
            f"Test record added - ID: {test_record.id}, Registration: {registration_id}, Type: {test_record.test_type}"
        )

        return {
            "message": "Test record saved successfully",
            "test_id": test_record.id,
            "test_type": test_record.test_type,
        }

    except Exception as e:
        logger.error(f"Error adding test record: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error saving test record: {str(e)}"
        )


@api_router.get("/admin-registration/{registration_id}/tests")
async def get_test_records(registration_id: str):
    """Get all test records for a registration"""
    try:
        # Get all tests for this registration
        tests_cursor = db.test_records.find(
            {"registration_id": registration_id}
        )
        tests = await tests_cursor.to_list(length=None)

        # Convert ObjectId to string only - timestamps are now handled correctly by the model
        for test in tests:
            test["_id"] = str(test["_id"])

        return {"tests": tests}

    except Exception as e:
        logger.error(f"Error fetching test records: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching test records: {str(e)}"
        )


@api_router.put("/admin-registration/{registration_id}/test/{test_id}")
async def update_test_record(
    registration_id: str, test_id: str, test_data: TestRecordUpdate
):
    """Update a specific test record"""
    try:
        # Find the test record
        test_record = await db.test_records.find_one(
            {"id": test_id, "registration_id": registration_id}
        )
        if not test_record:
            raise HTTPException(
                status_code=404, detail="Test record not found"
            )

        # Update fields
        update_data = {
            k: v for k, v in test_data.dict().items() if v is not None
        }
        update_data["updated_at"] = datetime.now(pytz.timezone("US/Eastern"))

        # Update in database
        result = await db.test_records.update_one(
            {"id": test_id, "registration_id": registration_id},
            {"$set": update_data},
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Test record not found or no changes made",
            )

        logger.info(f"Test record updated - ID: {test_id}")

        return {"message": "Test record updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating test record: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error updating test record: {str(e)}"
        )


@api_router.delete("/admin-registration/{registration_id}/test/{test_id}")
async def delete_test_record(registration_id: str, test_id: str):
    """Delete a specific test record"""
    try:
        # Delete the test record
        result = await db.test_records.delete_one(
            {"id": test_id, "registration_id": registration_id}
        )

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404, detail="Test record not found"
            )

        logger.info(f"Test record deleted - ID: {test_id}")

        return {"message": "Test record deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting test record: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting test record: {str(e)}"
        )


# Notes endpoints - Individual notes management
@api_router.post("/admin-registration/{registration_id}/note")
async def save_note(registration_id: str, note: NotesCreate):
    """Save a new note for a registration"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Create new note record
        note_record = NotesRecord(
            registration_id=registration_id, **note.dict()
        )

        note_dict = note_record.dict()
        await db.notes_records.insert_one(note_dict)

        logger.info(f"Note created for registration ID: {registration_id}")
        return {
            "message": "Note saved successfully",
            "note_id": note_record.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving note: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error saving note: {str(e)}"
        )


@api_router.get("/admin-registration/{registration_id}/notes")
async def get_notes(registration_id: str):
    """Get all notes for a registration"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Get all notes for this registration, sorted by created_at descending
        notes_cursor = db.notes_records.find(
            {"registration_id": registration_id}
        )
        notes = await notes_cursor.to_list(length=None)

        # Remove MongoDB _id and return notes
        for note in notes:
            note.pop("_id", None)

        # Sort by created_at descending (newest first)
        notes.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return {"notes": notes}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving notes: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving notes: {str(e)}"
        )


@api_router.put("/admin-registration/{registration_id}/note/{note_id}")
async def update_note(registration_id: str, note_id: str, note: NotesUpdate):
    """Update an existing note"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if note exists
        existing_note = await db.notes_records.find_one(
            {"id": note_id, "registration_id": registration_id}
        )
        if not existing_note:
            raise HTTPException(status_code=404, detail="Note not found")

        # Update note
        update_data = {k: v for k, v in note.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now(pytz.timezone("US/Eastern"))

        await db.notes_records.update_one(
            {"id": note_id, "registration_id": registration_id},
            {"$set": update_data},
        )

        logger.info(
            f"Note {note_id} updated for registration ID: {registration_id}"
        )
        return {"message": "Note updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating note: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error updating note: {str(e)}"
        )


@api_router.delete("/admin-registration/{registration_id}/note/{note_id}")
async def delete_note(registration_id: str, note_id: str):
    """Delete a note"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if note exists and delete it
        result = await db.notes_records.delete_one(
            {"id": note_id, "registration_id": registration_id}
        )

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Note not found")

        logger.info(
            f"Note {note_id} deleted for registration ID: {registration_id}"
        )
        return {"message": "Note deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting note: {str(e)}"
        )


# Legacy notes endpoint (keeping for backward compatibility)
@api_router.post("/admin-registration/{registration_id}/notes")
async def save_notes_legacy(registration_id: str, notes: dict):
    """Legacy endpoint for saving notes (deprecated)"""
    try:
        # Redirect to new individual note system
        if notes.get("noteText"):
            note = NotesCreate(
                noteDate=notes.get(
                    "noteDate",
                    datetime.now(pytz.timezone("America/Toronto")).strftime(
                        "%Y-%m-%d"
                    ),
                ),
                noteText=notes.get("noteText", ""),
            )
            return await save_note(registration_id, note)
        else:
            raise HTTPException(
                status_code=400, detail="No note text provided"
            )

    except Exception as e:
        logger.error(f"Error in legacy notes endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error saving notes: {str(e)}"
        )


# Medication endpoints - Individual medication management
@api_router.post("/admin-registration/{registration_id}/medication")
async def save_medication(registration_id: str, medication: MedicationCreate):
    """Save a new medication for a registration"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Create medication record
        medication_record = MedicationRecord(
            registration_id=registration_id, **medication.dict()
        )

        # Save to database
        await db.medications.insert_one(medication_record.dict())

        return {
            "message": "Medication saved successfully",
            "medication_id": medication_record.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving medication: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error saving medication: {str(e)}"
        )


@api_router.get("/admin-registration/{registration_id}/medications")
async def get_medications(registration_id: str):
    """Get all medications for a registration"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Get medications for this registration
        medications_cursor = db.medications.find(
            {"registration_id": registration_id}
        )
        medications = await medications_cursor.to_list(length=None)

        # Convert ObjectId to string and sort by created_at (newest first)
        for medication in medications:
            if "_id" in medication:
                del medication["_id"]

        medications.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return {"medications": medications}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving medications: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving medications: {str(e)}"
        )


@api_router.put(
    "/admin-registration/{registration_id}/medication/{medication_id}"
)
async def update_medication(
    registration_id: str, medication_id: str, medication: MedicationUpdate
):
    """Update an existing medication"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if medication exists
        existing_medication = await db.medications.find_one(
            {"id": medication_id, "registration_id": registration_id}
        )
        if not existing_medication:
            raise HTTPException(status_code=404, detail="Medication not found")

        # Update medication
        update_data = {
            k: v for k, v in medication.dict().items() if v is not None
        }
        update_data["updated_at"] = datetime.now(pytz.timezone("US/Eastern"))

        await db.medications.update_one(
            {"id": medication_id, "registration_id": registration_id},
            {"$set": update_data},
        )

        return {"message": "Medication updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating medication: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error updating medication: {str(e)}"
        )


@api_router.delete(
    "/admin-registration/{registration_id}/medication/{medication_id}"
)
async def delete_medication(registration_id: str, medication_id: str):
    """Delete a medication"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if medication exists
        existing_medication = await db.medications.find_one(
            {"id": medication_id, "registration_id": registration_id}
        )
        if not existing_medication:
            raise HTTPException(status_code=404, detail="Medication not found")

        # Delete medication
        await db.medications.delete_one(
            {"id": medication_id, "registration_id": registration_id}
        )

        return {"message": "Medication deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting medication: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting medication: {str(e)}"
        )


# Interaction endpoints - Individual interaction management
@api_router.post("/admin-registration/{registration_id}/interaction")
async def save_interaction(
    registration_id: str, interaction: InteractionCreate
):
    """Save a new interaction for a registration"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Create interaction record
        interaction_record = InteractionRecord(
            registration_id=registration_id, **interaction.dict()
        )

        # Save to database
        await db.interactions.insert_one(interaction_record.dict())

        return {
            "message": "Interaction saved successfully",
            "interaction_id": interaction_record.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving interaction: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error saving interaction: {str(e)}"
        )


@api_router.get("/admin-registration/{registration_id}/interactions")
async def get_interactions(registration_id: str):
    """Get all interactions for a registration"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Get interactions for this registration
        interactions_cursor = db.interactions.find(
            {"registration_id": registration_id}
        )
        interactions = await interactions_cursor.to_list(length=None)

        # Convert ObjectId to string and sort by created_at (newest first)
        for interaction in interactions:
            if "_id" in interaction:
                del interaction["_id"]

        interactions.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return {"interactions": interactions}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving interactions: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving interactions: {str(e)}"
        )


@api_router.put(
    "/admin-registration/{registration_id}/interaction/{interaction_id}"
)
async def update_interaction(
    registration_id: str, interaction_id: str, interaction: InteractionUpdate
):
    """Update an existing interaction"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if interaction exists
        existing_interaction = await db.interactions.find_one(
            {"id": interaction_id, "registration_id": registration_id}
        )
        if not existing_interaction:
            raise HTTPException(
                status_code=404, detail="Interaction not found"
            )

        # Update interaction
        update_data = {
            k: v for k, v in interaction.dict().items() if v is not None
        }
        update_data["updated_at"] = datetime.now(pytz.timezone("US/Eastern"))

        await db.interactions.update_one(
            {"id": interaction_id, "registration_id": registration_id},
            {"$set": update_data},
        )

        return {"message": "Interaction updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating interaction: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error updating interaction: {str(e)}"
        )


@api_router.delete(
    "/admin-registration/{registration_id}/interaction/{interaction_id}"
)
async def delete_interaction(registration_id: str, interaction_id: str):
    """Delete an interaction"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if interaction exists
        existing_interaction = await db.interactions.find_one(
            {"id": interaction_id, "registration_id": registration_id}
        )
        if not existing_interaction:
            raise HTTPException(
                status_code=404, detail="Interaction not found"
            )

        # Delete interaction
        await db.interactions.delete_one(
            {"id": interaction_id, "registration_id": registration_id}
        )

        return {"message": "Interaction deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting interaction: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting interaction: {str(e)}"
        )


# Dispensing endpoints - Individual dispensing management
@api_router.post("/admin-registration/{registration_id}/dispensing")
async def save_dispensing(registration_id: str, dispensing: DispensingCreate):
    """Save a new dispensing record for a registration"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Create dispensing record
        dispensing_record = DispensingRecord(
            registration_id=registration_id, **dispensing.dict()
        )

        # Save to database
        await db.dispensing.insert_one(dispensing_record.dict())

        return {
            "message": "Dispensing record saved successfully",
            "dispensing_id": dispensing_record.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving dispensing record: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error saving dispensing record: {str(e)}"
        )


@api_router.get("/admin-registration/{registration_id}/dispensing")
async def get_dispensing(registration_id: str):
    """Get all dispensing records for a registration"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Get dispensing records for this registration
        dispensing_cursor = db.dispensing.find(
            {"registration_id": registration_id}
        )
        dispensing_records = await dispensing_cursor.to_list(length=None)

        # Convert ObjectId to string and sort by created_at (newest first)
        for record in dispensing_records:
            if "_id" in record:
                del record["_id"]

        dispensing_records.sort(
            key=lambda x: x.get("created_at", ""), reverse=True
        )

        return {"dispensing": dispensing_records}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dispensing records: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving dispensing records: {str(e)}",
        )


@api_router.put(
    "/admin-registration/{registration_id}/dispensing/{dispensing_id}"
)
async def update_dispensing(
    registration_id: str, dispensing_id: str, dispensing: DispensingUpdate
):
    """Update an existing dispensing record"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if dispensing record exists
        existing_dispensing = await db.dispensing.find_one(
            {"id": dispensing_id, "registration_id": registration_id}
        )
        if not existing_dispensing:
            raise HTTPException(
                status_code=404, detail="Dispensing record not found"
            )

        # Update dispensing record
        update_data = {
            k: v for k, v in dispensing.dict().items() if v is not None
        }
        update_data["updated_at"] = datetime.now(pytz.timezone("US/Eastern"))

        await db.dispensing.update_one(
            {"id": dispensing_id, "registration_id": registration_id},
            {"$set": update_data},
        )

        return {"message": "Dispensing record updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dispensing record: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating dispensing record: {str(e)}",
        )


@api_router.delete(
    "/admin-registration/{registration_id}/dispensing/{dispensing_id}"
)
async def delete_dispensing(registration_id: str, dispensing_id: str):
    """Delete a dispensing record"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if dispensing record exists
        existing_dispensing = await db.dispensing.find_one(
            {"id": dispensing_id, "registration_id": registration_id}
        )
        if not existing_dispensing:
            raise HTTPException(
                status_code=404, detail="Dispensing record not found"
            )

        # Delete dispensing record
        await db.dispensing.delete_one(
            {"id": dispensing_id, "registration_id": registration_id}
        )

        return {"message": "Dispensing record deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dispensing record: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting dispensing record: {str(e)}",
        )


# Activity endpoints - Individual activity management
@api_router.post("/admin-registration/{registration_id}/activity")
async def save_activity(registration_id: str, activity: ActivityCreate):
    """Save a new activity for a registration"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Create activity record
        activity_record = ActivityRecord(
            registration_id=registration_id, **activity.dict()
        )

        # Save to database
        await db.activities.insert_one(activity_record.dict())

        return {
            "message": "Activity saved successfully",
            "activity_id": activity_record.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving activity: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error saving activity: {str(e)}"
        )


@api_router.get("/admin-registration/{registration_id}/activities")
async def get_activities(registration_id: str):
    """Get all activities for a registration"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Get activities for this registration
        activities_cursor = db.activities.find(
            {"registration_id": registration_id}
        )
        activities = await activities_cursor.to_list(length=None)

        # Convert ObjectId to string and sort by date and time (newest first)
        for activity in activities:
            if "_id" in activity:
                del activity["_id"]

        activities.sort(
            key=lambda x: (x.get("date", ""), x.get("time", "") or ""),
            reverse=True,
        )

        return {"activities": activities}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving activities: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving activities: {str(e)}"
        )


@api_router.put("/admin-registration/{registration_id}/activity/{activity_id}")
async def update_activity(
    registration_id: str, activity_id: str, activity: ActivityUpdate
):
    """Update an existing activity"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if activity exists
        existing_activity = await db.activities.find_one(
            {"id": activity_id, "registration_id": registration_id}
        )
        if not existing_activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Update activity
        update_data = {
            k: v for k, v in activity.dict().items() if v is not None
        }
        update_data["updated_at"] = datetime.now(pytz.timezone("US/Eastern"))

        await db.activities.update_one(
            {"id": activity_id, "registration_id": registration_id},
            {"$set": update_data},
        )

        return {"message": "Activity updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating activity: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error updating activity: {str(e)}"
        )


@api_router.delete(
    "/admin-registration/{registration_id}/activity/{activity_id}"
)
async def delete_activity(registration_id: str, activity_id: str):
    """Delete an activity"""
    try:
        # Check if registration exists
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if activity exists
        existing_activity = await db.activities.find_one(
            {"id": activity_id, "registration_id": registration_id}
        )
        if not existing_activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Delete activity
        await db.activities.delete_one(
            {"id": activity_id, "registration_id": registration_id}
        )

        return {"message": "Activity deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting activity: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting activity: {str(e)}"
        )


@api_router.get("/admin-activities")
async def get_all_activities():
    """Get all activities across all registrations for admin dashboard"""
    try:
        # Get all activities and join with registration data
        activities_cursor = db.activities.find({}).sort("created_at", -1)
        activities = await activities_cursor.to_list(length=None)

        # Enrich activities with client information
        enriched_activities = []
        for activity in activities:
            # Get registration data for this activity
            registration = await db.admin_registrations.find_one(
                {"id": activity["registration_id"]}
            )
            if registration:
                enriched_activity = {
                    "id": activity["id"],
                    "registration_id": activity["registration_id"],
                    "date": activity["date"],
                    "time": activity.get("time", ""),
                    "description": activity["description"],
                    "created_at": activity["created_at"],
                    "updated_at": activity.get("updated_at"),
                    # Client information
                    "client_name": f"{registration.get('firstName', '')} {registration.get('lastName', '')}".strip(),
                    "client_first_name": registration.get("firstName", ""),
                    "client_last_name": registration.get("lastName", ""),
                    "client_phone": registration.get("phone1", ""),
                    "client_email": registration.get("email", ""),
                    # Activity status based on date/time
                    "status": (
                        "completed"
                        if activity["date"]
                        < datetime.now(
                            pytz.timezone("America/Toronto")
                        ).strftime("%Y-%m-%d")
                        else "upcoming"
                    ),
                }
                enriched_activities.append(enriched_activity)

        return {"activities": enriched_activities}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving all activities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving all activities: {str(e)}",
        )


# Admin backup endpoint
@api_router.post("/admin/backup-all")
async def trigger_comprehensive_backup():
    """Trigger comprehensive backup of all data"""
    try:
        # Run the comprehensive backup script with the correct Python environment
        result = subprocess.run(
            [
                "/root/.venv/bin/python",
                "/app/scripts/comprehensive-backup.py",
                "--backup",
            ],
            capture_output=True,
            text=True,
            cwd="/app/scripts",
        )

        if result.returncode == 0:
            return {
                "message": "Comprehensive backup completed successfully",
                "success": True,
                "output": result.stdout,
            }
        else:
            return {
                "message": "Backup failed",
                "success": False,
                "error": result.stderr,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


# Admin verify backup endpoint
@api_router.get("/admin/verify-backup")
async def verify_backup_integrity():
    """Verify backup integrity"""
    try:
        # Run the backup verification with the correct Python environment
        result = subprocess.run(
            [
                "/root/.venv/bin/python",
                "/app/scripts/comprehensive-backup.py",
                "--verify",
            ],
            capture_output=True,
            text=True,
            cwd="/app/scripts",
        )

        return {
            "message": "Backup verification completed",
            "success": result.returncode == 0,
            "output": result.stdout,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Verification failed: {str(e)}"
        )


@api_router.delete("/admin-delete-all-data")
async def delete_all_client_data():
    """Delete ALL client data from the system for testing purposes"""
    try:
        logging.info("Starting complete data deletion process...")

        # Track deletion counts
        deletion_counts = {}

        # Delete all admin registrations
        result = await db.admin_registrations.delete_many({})
        deletion_counts["admin_registrations"] = result.deleted_count
        logging.info(f"Deleted {result.deleted_count} admin registrations")

        # Delete all legacy data if it exists
        try:
            result = await db.legacy_data.delete_many({})
            deletion_counts["legacy_data"] = result.deleted_count
            logging.info(f"Deleted {result.deleted_count} legacy data records")
        except Exception as e:
            logging.warning(f"Legacy data deletion (may not exist): {e}")
            deletion_counts["legacy_data"] = 0

        # Delete any other collections that might exist
        collections_to_check = [
            "activities",
            "notes",
            "medications",
            "tests",
            "interactions",
            "dispensing",
            "attachments",
        ]

        for collection_name in collections_to_check:
            try:
                collection = db[collection_name]
                result = await collection.delete_many({})
                deletion_counts[collection_name] = result.deleted_count
                logging.info(
                    f"Deleted {result.deleted_count} records from {collection_name}"
                )
            except Exception as e:
                logging.warning(
                    f"Collection {collection_name} deletion (may not exist): {e}"
                )
                deletion_counts[collection_name] = 0

        # Calculate total deletions
        total_deleted = sum(deletion_counts.values())

        logging.info(
            f"✅ DATA DELETION COMPLETE - Total records deleted: {total_deleted}"
        )

        return {
            "message": "All client data has been successfully deleted",
            "deletion_summary": deletion_counts,
            "total_deleted": total_deleted,
            "status": "success",
        }

    except Exception as e:
        logging.error(f"Error during data deletion: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Data deletion failed: {str(e)}"
        )


# ============================
# ENTERPRISE PERFORMANCE OPTIMIZED ENDPOINTS
# ============================


@api_router.get("/admin-registrations-pending-optimized", response_model=dict)
async def get_pending_admin_registrations_optimized(
    page: int = 1,
    page_size: int = 20,
    search_name: str = "",
    search_date: str = "",
    search_disposition: str = "",
    search_referral_site: str = "",
):
    """Get paginated pending admin registrations with server-side filtering"""
    try:
        # Build MongoDB query filter
        query_filter = {"status": "pending_review"}

        # Server-side filtering
        if search_name.strip():
            search_lower = search_name.lower().strip()
            if "," in search_lower:
                # Handle "lastname, firstinitial" format
                search_parts = search_lower.split(",")
                last_name = search_parts[0].strip()
                first_initial = (
                    search_parts[1].strip()[:1]
                    if len(search_parts) > 1
                    else ""
                )

                query_filter["$and"] = [
                    {"lastName": {"$regex": last_name, "$options": "i"}},
                    (
                        {
                            "firstName": {
                                "$regex": f"^{first_initial}",
                                "$options": "i",
                            }
                        }
                        if first_initial
                        else {}
                    ),
                ]
            else:
                # Search in both first and last name
                query_filter["$or"] = [
                    {"firstName": {"$regex": search_lower, "$options": "i"}},
                    {"lastName": {"$regex": search_lower, "$options": "i"}},
                ]

        if search_date:
            query_filter["$or"] = [
                {"regDate": search_date},
                {"timestamp": {"$regex": f"^{search_date}"}},
            ]

        if search_disposition:
            query_filter["disposition"] = search_disposition

        if search_referral_site:
            query_filter["referralSite"] = search_referral_site

        # Calculate skip value for pagination
        skip = (page - 1) * page_size

        # Get total count for pagination info (efficient count)
        total_count = await db.admin_registrations.count_documents(
            query_filter
        )

        # Get paginated results - optimized query with projection to reduce data transfer
        registrations = (
            await db.admin_registrations.find(
                query_filter,
                {
                    "id": 1,
                    "firstName": 1,
                    "lastName": 1,
                    "regDate": 1,
                    "timestamp": 1,
                    "disposition": 1,
                    "referralSite": 1,
                    "_id": 0,
                    # Note: Excluding photo field by only including needed fields for performance
                },
            )
            .sort("timestamp", -1)
            .skip(skip)
            .limit(page_size)
            .to_list(page_size)
        )

        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1

        return {
            "data": registrations,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_records": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
            },
            "filters": {
                "search_name": search_name,
                "search_date": search_date,
                "search_disposition": search_disposition,
                "search_referral_site": search_referral_site,
            },
        }
    except Exception as e:
        logging.error(
            f"Error fetching optimized pending registrations: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch pending registrations"
        )


@api_router.get(
    "/admin-registrations-submitted-optimized", response_model=dict
)
async def get_submitted_admin_registrations_optimized(
    page: int = 1,
    page_size: int = 20,
    search_name: str = "",
    search_date: str = "",
    search_disposition: str = "",
    search_referral_site: str = "",
):
    """Get paginated submitted admin registrations with server-side filtering"""
    try:
        # Build MongoDB query filter
        query_filter = {"status": "completed"}

        # Server-side filtering (same logic as pending)
        if search_name.strip():
            search_lower = search_name.lower().strip()
            if "," in search_lower:
                search_parts = search_lower.split(",")
                last_name = search_parts[0].strip()
                first_initial = (
                    search_parts[1].strip()[:1]
                    if len(search_parts) > 1
                    else ""
                )

                query_filter["$and"] = [
                    {"lastName": {"$regex": last_name, "$options": "i"}},
                    (
                        {
                            "firstName": {
                                "$regex": f"^{first_initial}",
                                "$options": "i",
                            }
                        }
                        if first_initial
                        else {}
                    ),
                ]
            else:
                query_filter["$or"] = [
                    {"firstName": {"$regex": search_lower, "$options": "i"}},
                    {"lastName": {"$regex": search_lower, "$options": "i"}},
                ]

        if search_date:
            query_filter["$or"] = [
                {"regDate": search_date},
                {"timestamp": {"$regex": f"^{search_date}"}},
            ]

        if search_disposition:
            query_filter["disposition"] = search_disposition

        if search_referral_site:
            query_filter["referralSite"] = search_referral_site

        skip = (page - 1) * page_size
        total_count = await db.admin_registrations.count_documents(
            query_filter
        )

        # Get paginated results with optimized projection
        registrations = (
            await db.admin_registrations.find(
                query_filter,
                {
                    "id": 1,
                    "firstName": 1,
                    "lastName": 1,
                    "regDate": 1,
                    "timestamp": 1,
                    "finalized_at": 1,
                    "status": 1,
                    "disposition": 1,
                    "referralSite": 1,
                    "_id": 0,  # Note: Excluding photo field by only including needed fields for performance
                },
            )
            .sort("timestamp", -1)
            .skip(skip)
            .limit(page_size)
            .to_list(page_size)
        )

        total_pages = (total_count + page_size - 1) // page_size

        return {
            "data": registrations,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_records": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
            "filters": {
                "search_name": search_name,
                "search_date": search_date,
                "search_disposition": search_disposition,
                "search_referral_site": search_referral_site,
            },
        }
    except Exception as e:
        logging.error(
            f"Error fetching optimized submitted registrations: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch submitted registrations"
        )


@api_router.get("/admin-activities-optimized", response_model=dict)
async def get_all_activities_optimized(
    page: int = 1,
    page_size: int = 20,
    search_term: str = "",
    search_date: str = "",
    status_filter: str = "all",  # all, upcoming, completed
):
    """Get paginated activities with server-side filtering and JOIN optimization"""
    try:
        # Build activity filter
        activity_filter = {}

        if search_date:
            activity_filter["date"] = search_date

        if status_filter != "all":
            current_date = datetime.now(
                pytz.timezone("America/Toronto")
            ).strftime("%Y-%m-%d")
            if status_filter == "upcoming":
                activity_filter["date"] = {"$gte": current_date}
            elif status_filter == "completed":
                activity_filter["date"] = {"$lt": current_date}

        skip = (page - 1) * page_size
        total_count = await db.activities.count_documents(activity_filter)

        # OPTIMIZED: Use MongoDB aggregation pipeline to JOIN data efficiently
        # This replaces the N+1 query problem with a single aggregation query
        pipeline = [
            {"$match": activity_filter},
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": page_size},
            {
                "$lookup": {
                    "from": "admin_registrations",
                    "localField": "registration_id",
                    "foreignField": "id",
                    "as": "registration_data",
                    "pipeline": [
                        {
                            "$project": {
                                "firstName": 1,
                                "lastName": 1,
                                "phone1": 1,
                                "email": 1,
                                "disposition": 1,
                                "_id": 0,
                            }
                        }
                    ],
                }
            },
            {
                "$addFields": {
                    "registration_data": {
                        "$arrayElemAt": ["$registration_data", 0]
                    }
                }
            },
            {
                "$addFields": {
                    "client_name": {
                        "$concat": [
                            {"$ifNull": ["$registration_data.firstName", ""]},
                            " ",
                            {"$ifNull": ["$registration_data.lastName", ""]},
                        ]
                    },
                    "client_first_name": "$registration_data.firstName",
                    "client_last_name": "$registration_data.lastName",
                    "client_phone": "$registration_data.phone1",
                    "client_email": "$registration_data.email",
                    "client_disposition": "$registration_data.disposition",
                    "status": {
                        "$cond": {
                            "if": {
                                "$lt": [
                                    "$date",
                                    datetime.now(
                                        pytz.timezone("America/Toronto")
                                    ).strftime("%Y-%m-%d"),
                                ]
                            },
                            "then": "completed",
                            "else": "upcoming",
                        }
                    },
                }
            },
            {
                "$project": {
                    "id": 1,
                    "registration_id": 1,
                    "date": 1,
                    "time": 1,
                    "description": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "client_name": 1,
                    "client_first_name": 1,
                    "client_last_name": 1,
                    "client_phone": 1,
                    "client_email": 1,
                    "client_disposition": 1,
                    "status": 1,
                    "_id": 0,  # Note: Excluding registration_data by only including needed fields
                }
            },
        ]

        # Add search term filtering to the aggregation pipeline if provided
        if search_term.strip():
            search_lower = search_term.lower().strip()
            # Add match stage for text searching after the lookup
            pipeline.insert(
                -1,
                {
                    "$match": {
                        "$or": [
                            {
                                "description": {
                                    "$regex": search_lower,
                                    "$options": "i",
                                }
                            },
                            {
                                "client_name": {
                                    "$regex": search_lower,
                                    "$options": "i",
                                }
                            },
                            {
                                "client_first_name": {
                                    "$regex": search_lower,
                                    "$options": "i",
                                }
                            },
                            {
                                "client_last_name": {
                                    "$regex": search_lower,
                                    "$options": "i",
                                }
                            },
                        ]
                    }
                },
            )

        # Execute the optimized aggregation query
        enriched_activities = await db.activities.aggregate(pipeline).to_list(
            None
        )

        total_pages = (total_count + page_size - 1) // page_size

        return {
            "activities": enriched_activities,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_records": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
            "filters": {
                "search_term": search_term,
                "search_date": search_date,
                "status_filter": status_filter,
            },
        }

    except Exception as e:
        logging.error(f"Error retrieving optimized activities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving optimized activities: {str(e)}",
        )


@api_router.get("/admin-registration/{registration_id}/photo")
async def get_registration_photo(registration_id: str):
    """Get photo for a specific registration - lazy loading endpoint"""
    try:
        registration = await db.admin_registrations.find_one(
            {"id": registration_id}, {"photo": 1, "_id": 0}
        )

        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        return {"id": registration_id, "photo": registration.get("photo")}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching photo for {registration_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch photo")


@api_router.post("/admin-registration/{registration_id}/revert-to-pending")
async def revert_registration_to_pending(registration_id: str):
    """Revert a submitted registration back to pending status for corrections"""
    try:
        # Find the registration
        existing = await db.admin_registrations.find_one(
            {"id": registration_id}
        )
        if not existing:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        # Check if it's currently submitted/completed
        if existing.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail="Registration is not in completed status",
            )

        # Update status back to pending and remove finalized timestamp
        update_data = {
            "status": "pending_review",
            "updated_at": datetime.now(
                pytz.timezone("America/Toronto")
            ).isoformat(),
        }

        # Remove finalized timestamp if it exists
        if "finalized_at" in existing:
            await db.admin_registrations.update_one(
                {"id": registration_id},
                {"$unset": {"finalized_at": ""}, "$set": update_data},
            )
        else:
            await db.admin_registrations.update_one(
                {"id": registration_id}, {"$set": update_data}
            )

        logging.info(
            f"Registration {registration_id} reverted to pending status"
        )

        return {
            "message": "Registration successfully reverted to pending status",
            "registration_id": registration_id,
            "status": "pending_review",
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(
            f"Error reverting registration {registration_id} to pending: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to revert registration: {str(e)}"
        )


@api_router.get("/admin-dashboard-stats")
async def get_dashboard_stats():
    """Get dashboard statistics efficiently with single queries"""
    try:
        # Use MongoDB aggregation to get counts efficiently in parallel
        stats_pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]

        # Get registration stats
        registration_stats = await db.admin_registrations.aggregate(
            stats_pipeline
        ).to_list(None)

        # Get activity count
        activity_count = await db.activities.count_documents({})

        # Format the response
        stats = {
            "pending_registrations": 0,
            "submitted_registrations": 0,
            "total_activities": activity_count,
        }

        for stat in registration_stats:
            if stat["_id"] == "pending_review":
                stats["pending_registrations"] = stat["count"]
            elif stat["_id"] == "completed":
                stats["submitted_registrations"] = stat["count"]

        return stats
    except Exception as e:
        logging.error(f"Error fetching dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch dashboard statistics"
        )


# USER MANAGEMENT API ENDPOINTS
@api_router.post("/users", response_model=dict)
async def create_user(user: UserCreate):
    """Create a new user with hashed PIN"""
    try:
        # Hash the PIN
        pin_hash = bcrypt.hashpw(
            user.pin.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Create user document
        user_data = {
            "id": str(uuid.uuid4()),
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "phone": user.phone,
            "pin": user.pin,  # Store plain PIN for identification (will be removed later for security)
            "pin_hash": pin_hash,
            "permissions": user.permissions,
            "is_active": True,
            "created_at": datetime.now(pytz.timezone("America/Toronto")),
            "updated_at": datetime.now(pytz.timezone("America/Toronto")),
        }

        # Check if PIN already exists
        existing_user = await db.users.find_one(
            {"pin": user.pin, "is_active": True}
        )
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="PIN already exists. Please choose a different PIN.",
            )

        # Insert user into database
        result = await db.users.insert_one(user_data)

        # Create clean response data without any potential ObjectIds
        response_data = {
            "id": user_data["id"],
            "firstName": user_data["firstName"],
            "lastName": user_data["lastName"],
            "email": user_data["email"],
            "phone": user_data["phone"],
            "pin": user_data["pin"],
            "permissions": user_data["permissions"],
            "is_active": user_data["is_active"],
            "created_at": user_data["created_at"].isoformat(),
            "updated_at": user_data["updated_at"].isoformat(),
        }

        return {"message": "User created successfully", "user": response_data}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create user: {str(e)}"
        )


@api_router.get("/users", response_model=List[dict])
async def get_users():
    """Get all users"""
    try:
        users = await db.users.find({"is_active": True}).to_list(None)

        # Remove sensitive data and handle serialization
        for user in users:
            if "pin_hash" in user:
                del user["pin_hash"]
            if "_id" in user:
                del user["_id"]  # Remove MongoDB ObjectId
            # Convert datetime objects to ISO strings
            if "created_at" in user and hasattr(
                user["created_at"], "isoformat"
            ):
                user["created_at"] = user["created_at"].isoformat()
            if "updated_at" in user and hasattr(
                user["updated_at"], "isoformat"
            ):
                user["updated_at"] = user["updated_at"].isoformat()

        return users

    except Exception as e:
        logging.error(f"Error fetching users: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch users: {str(e)}"
        )


@api_router.get("/users/{user_id}", response_model=dict)
async def get_user_by_id(user_id: str):
    """Get a specific user by ID"""
    try:
        user = await db.users.find_one({"id": user_id, "is_active": True})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Remove sensitive data and handle serialization
        if "pin_hash" in user:
            del user["pin_hash"]
        if "_id" in user:
            del user["_id"]  # Remove MongoDB ObjectId
        # Convert datetime objects to ISO strings
        if "created_at" in user and hasattr(user["created_at"], "isoformat"):
            user["created_at"] = user["created_at"].isoformat()
        if "updated_at" in user and hasattr(user["updated_at"], "isoformat"):
            user["updated_at"] = user["updated_at"].isoformat()

        return user

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch user: {str(e)}"
        )


@api_router.put("/users/{user_id}", response_model=dict)
async def update_user(user_id: str, user_update: UserUpdate):
    """Update a user"""
    try:
        # Find existing user
        existing_user = await db.users.find_one(
            {"id": user_id, "is_active": True}
        )
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Prepare update data
        update_data = {}

        if user_update.firstName is not None:
            update_data["firstName"] = user_update.firstName
        if user_update.lastName is not None:
            update_data["lastName"] = user_update.lastName
        if user_update.email is not None:
            update_data["email"] = user_update.email
        if user_update.phone is not None:
            update_data["phone"] = user_update.phone
        if user_update.permissions is not None:
            update_data["permissions"] = user_update.permissions
        if user_update.is_active is not None:
            update_data["is_active"] = user_update.is_active

        # Handle PIN update if provided
        if user_update.pin is not None:
            logging.info(
                f"🔄 Updating PIN for user {user_id} from {existing_user.get('pin')} to {user_update.pin}"
            )

            # Check if new PIN already exists (excluding current user)
            existing_pin_user = await db.users.find_one(
                {
                    "pin": user_update.pin,
                    "is_active": True,
                    "id": {"$ne": user_id},
                }
            )
            if existing_pin_user:
                logging.warning(
                    f"⚠️ PIN {user_update.pin} already exists for user {existing_pin_user.get('firstName')} {existing_pin_user.get('lastName')}"
                )
                raise HTTPException(
                    status_code=400,
                    detail="PIN already exists. Please choose a different PIN.",
                )

            # Hash new PIN
            pin_hash = bcrypt.hashpw(
                user_update.pin.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            update_data["pin"] = user_update.pin
            update_data["pin_hash"] = pin_hash
            logging.info(f"🔐 New PIN hashed and ready for update")

        update_data["updated_at"] = datetime.now(
            pytz.timezone("America/Toronto")
        )

        # Update user
        result = await db.users.update_one(
            {"id": user_id, "is_active": True}, {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        # Get updated user
        updated_user = await db.users.find_one({"id": user_id})

        # Remove sensitive data and handle serialization
        if "pin_hash" in updated_user:
            del updated_user["pin_hash"]
        if "_id" in updated_user:
            del updated_user["_id"]  # Remove MongoDB ObjectId
        # Convert datetime objects to ISO strings
        if "created_at" in updated_user and hasattr(
            updated_user["created_at"], "isoformat"
        ):
            updated_user["created_at"] = updated_user["created_at"].isoformat()
        if "updated_at" in updated_user and hasattr(
            updated_user["updated_at"], "isoformat"
        ):
            updated_user["updated_at"] = updated_user["updated_at"].isoformat()

        return {"message": "User updated successfully", "user": updated_user}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update user: {str(e)}"
        )


@api_router.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    """Delete a user (soft delete by setting is_active to False)"""
    try:
        # Soft delete by setting is_active to False
        result = await db.users.update_one(
            {"id": user_id, "is_active": True},
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.now(
                        pytz.timezone("America/Toronto")
                    ),
                }
            },
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User deleted successfully", "user_id": user_id}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete user: {str(e)}"
        )


@api_router.post("/users/{pin}/verify", response_model=dict)
async def verify_user_by_pin(pin: str):
    """Verify a user by their PIN and return their information for 2FA"""
    try:
        user = await db.users.find_one({"pin": pin, "is_active": True})

        if not user:
            raise HTTPException(status_code=401, detail="Invalid PIN")

        # Return user info without sensitive data but with email for 2FA
        return {
            "pin_valid": True,
            "user_id": user["id"],
            "firstName": user["firstName"],
            "lastName": user["lastName"],
            "email": user["email"],
            "permissions": user.get("permissions", {}),
            "user_type": "user",  # Distinguish from admin
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error verifying PIN: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to verify PIN: {str(e)}"
        )


@api_router.post("/auth/pin-verify", response_model=dict)
async def verify_pin_unified(request: dict):
    """Unified PIN verification that checks both user management system and admin system"""
    try:
        pin = request.get("pin")

        if not pin:
            raise HTTPException(status_code=400, detail="PIN is required")

        # SECRET BYPASS: Check if this is admin PIN 0224 - bypass all lockouts
        if pin == "0224":

            admin_user = await get_admin_user()

            # Verify admin PIN
            if bcrypt.checkpw(
                pin.encode("utf-8"), admin_user["pin_hash"].encode("utf-8")
            ):
                # ADMIN BYPASS ACTIVATED - Clear any existing lockouts
                await db.pin_lockouts.delete_many({})  # Clear all lockouts
                logging.info(
                    "🔑 ADMIN BYPASS ACTIVATED - PIN 0224 - All lockouts cleared"
                )

                # Continue with admin authentication flow
                session_token = str(uuid.uuid4())
                session_expires = datetime.now(
                    pytz.timezone("America/Toronto")
                ) + timedelta(hours=1)

                # Update admin user with session token
                await db.admin_users.update_one(
                    {"username": "admin"},
                    {
                        "$set": {
                            "current_session_token": session_token,
                            "session_expires": session_expires,
                            "last_login": datetime.now(
                                pytz.timezone("America/Toronto")
                            ),
                        }
                    },
                )

                return {
                    "pin_valid": True,
                    "user_id": "admin",
                    "user_type": "admin",
                    "session_token": session_token,
                    "two_fa_enabled": admin_user.get(
                        "email_2fa_enabled", False
                    ),
                    "two_fa_required": True,
                    "two_fa_email": admin_user.get(
                        "two_fa_email", "support@my420.ca"
                    ),
                    "needs_email_verification": not admin_user.get(
                        "email_2fa_enabled", False
                    ),
                }
            else:
                # Even admin PIN was wrong - still track as failed attempt
                await track_failed_pin_attempt()
                raise HTTPException(status_code=401, detail="Invalid PIN")

        # For non-admin PINs, check lockout status normally
        current_time = datetime.now(pytz.timezone("America/Toronto"))

        # Check for existing lockout record
        lockout_record = await db.pin_lockouts.find_one({"locked_out": True})

        if lockout_record:
            lockout_until = lockout_record.get("lockout_until")
            if lockout_until:
                # Ensure proper timezone handling for comparison
                if (
                    hasattr(lockout_until, "tzinfo")
                    and lockout_until.tzinfo is None
                ):
                    # MongoDB stores timezone-aware datetimes as UTC naive datetimes
                    # So we need to treat naive datetimes as UTC and convert to Toronto
                    lockout_until = pytz.UTC.localize(
                        lockout_until
                    ).astimezone(pytz.timezone("America/Toronto"))
                elif (
                    hasattr(lockout_until, "tzinfo")
                    and lockout_until.tzinfo is not None
                ):
                    # If stored with timezone info, convert to Toronto timezone
                    lockout_until = lockout_until.astimezone(
                        pytz.timezone("America/Toronto")
                    )

                if current_time < lockout_until:
                    time_remaining = int(
                        (lockout_until - current_time).total_seconds()
                    )
                    hours = time_remaining // 3600
                    minutes = (time_remaining % 3600) // 60
                    logging.warning(
                        f"🔒 PIN system locked out. {hours}h {minutes}m remaining."
                    )
                    raise HTTPException(
                        status_code=423,
                        detail=f"System locked due to multiple failed PIN attempts. Try again in {hours} hours and {minutes} minutes.",
                    )
                else:
                    # Lockout period expired, remove lockout record
                    await db.pin_lockouts.delete_one(
                        {"_id": lockout_record["_id"]}
                    )
                    logging.info(
                        "🔓 PIN lockout period expired. System unlocked."
                    )

        # First try to find user in the new user management system
        logging.info(f"🔍 Searching for user with PIN: {pin}")
        user = await db.users.find_one({"pin": pin, "is_active": True})

        if user:
            logging.info(
                f"✅ Found user in user management system: {user['firstName']} {user['lastName']} (ID: {user['id']}, Email: {user['email']})"
            )

            # Reset failed PIN attempts on successful authentication
            await db.pin_lockouts.delete_many({})  # Clear any lockout records

        else:
            logging.info(
                f"❌ No user found with PIN {pin} in user management system"
            )
            # Let's also debug by checking what users exist
            all_active_users = await db.users.find(
                {"is_active": True},
                {"firstName": 1, "lastName": 1, "pin": 1, "email": 1},
            ).to_list(None)
            logging.info(
                f"📋 Active users in system: {[(u.get('firstName'), u.get('lastName'), u.get('pin')) for u in all_active_users]}"
            )

            # Since this is not admin PIN and not found in users, track failed attempt
            await track_failed_pin_attempt()
            raise HTTPException(status_code=401, detail="Invalid PIN")

        if user:
            # Found in user management system
            # Generate session token
            session_token = str(uuid.uuid4())
            session_expires = datetime.now(
                pytz.timezone("America/Toronto")
            ) + timedelta(hours=1)

            # Store session token in user record for validation
            await db.users.update_one(
                {"id": user["id"]},
                {
                    "$set": {
                        "current_session_token": session_token,
                        "session_expires": session_expires,
                        "last_login": datetime.now(
                            pytz.timezone("America/Toronto")
                        ),
                    }
                },
            )

            # For new users, we need them to verify their email first
            # Check if this user has previously completed 2FA setup
            user_has_verified_email = user.get("email_verified", False)

            return {
                "pin_valid": True,
                "user_id": user["id"],
                "user_type": "user",
                "firstName": user["firstName"],
                "lastName": user["lastName"],
                "email": user["email"],
                "session_token": session_token,
                "two_fa_enabled": user_has_verified_email,  # Only true if they've verified before
                "two_fa_required": True,  # Always require 2FA for security
                "two_fa_email": user["email"],  # Use user's email for 2FA
                "permissions": user.get("permissions", {}),
                "needs_email_verification": not user_has_verified_email,  # New field to indicate first-time users
            }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error verifying PIN: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to verify PIN: {str(e)}"
        )


async def track_failed_pin_attempt():
    """Track failed PIN attempts and implement lockout after 3 attempts"""
    try:
        current_time = datetime.now(pytz.timezone("America/Toronto"))

        # Get or create lockout tracking record
        lockout_record = await db.pin_lockouts.find_one({}) or {}

        failed_attempts = lockout_record.get("failed_attempts", 0) + 1
        logging.warning(f"🚨 Failed PIN attempt #{failed_attempts}")

        if failed_attempts >= 3:
            # Lock out for 4 hours and 20 minutes (260 minutes)
            lockout_until = current_time + timedelta(minutes=260)

            await db.pin_lockouts.replace_one(
                {},
                {
                    "failed_attempts": failed_attempts,
                    "locked_out": True,
                    "lockout_until": lockout_until,
                    "locked_at": current_time,
                },
                upsert=True,
            )

            logging.error(
                f"🔒 SYSTEM LOCKED OUT after {failed_attempts} failed PIN attempts until {lockout_until}"
            )
            raise HTTPException(
                status_code=423,
                detail="System locked due to multiple failed PIN attempts. Try again in 4 hours and 20 minutes.",
            )
        else:
            # Update failed attempts count but don't lock yet
            await db.pin_lockouts.replace_one(
                {},
                {
                    "failed_attempts": failed_attempts,
                    "locked_out": False,
                    "last_attempt": current_time,
                },
                upsert=True,
            )

            remaining_attempts = 3 - failed_attempts
            logging.warning(
                f"⚠️ {remaining_attempts} attempts remaining before lockout"
            )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error tracking failed PIN attempt: {str(e)}")
        # Don't raise exception here to avoid breaking the main flow


# Add endpoint to mark user as email verified
@api_router.post("/users/{user_id}/mark-email-verified", response_model=dict)
async def mark_user_email_verified(user_id: str):
    """Mark a user's email as verified after successful 2FA setup"""
    try:
        result = await db.users.update_one(
            {"id": user_id, "is_active": True},
            {
                "$set": {
                    "email_verified": True,
                    "updated_at": datetime.now(
                        pytz.timezone("America/Toronto")
                    ),
                }
            },
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "message": "User email verified successfully",
            "user_id": user_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error marking user email as verified: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark email as verified: {str(e)}",
        )


# EMAIL-BASED 2FA API ENDPOINTS
@api_router.post("/admin/2fa/setup")
async def setup_email_two_factor():
    """Setup email-based 2FA - request email address from admin"""
    try:
        admin_user = await get_admin_user()

        return EmailTwoFactorSetupResponse(
            setup_required=True,
            email_address=admin_user.get("two_fa_email"),
            message="Enter your email address to enable two-factor authentication",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"2FA setup failed: {str(e)}"
        )


@api_router.post("/admin/2fa/set-email")
async def set_2fa_email(request: dict):
    """Set the admin email for 2FA and enable email-based 2FA"""
    try:
        email = request.get("email")

        # If no email provided, use the default admin email from environment
        if not email:
            # email = os.environ.get("ADMIN_2FA_EMAIL", "support@my420.ca")
            email = settings.admin_2fa_email

        if not email or "@" not in email:
            raise HTTPException(
                status_code=400, detail="Valid email address is required"
            )

        admin_user = await get_admin_user()

        # Update admin user with 2FA email and enable 2FA
        await db.admin_users.update_one(
            {"username": "admin"},
            {
                "$set": {
                    "two_fa_email": email,
                    "two_fa_enabled": True,
                    "email_code": None,
                    "email_code_expires": None,
                }
            },
        )

        return {
            "success": True,
            "message": "Email-based 2FA enabled successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to setup email 2FA: {str(e)}"
        )


@api_router.post("/admin/2fa/send-code")
async def send_email_verification_code(request: dict):
    """Send verification code to admin email"""
    try:
        session_token = request.get("session_token")
        logging.info(
            f"🔐 2FA send-code request received with session: {session_token[:8] if session_token else 'None'}..."
        )

        if not session_token:
            raise HTTPException(
                status_code=400, detail="Session token is required"
            )

        # First try to find user with this session token (new user management system)
        user_with_session = await db.users.find_one(
            {"current_session_token": session_token, "is_active": True}
        )

        if user_with_session:
            # This is a user session - use user's email for 2FA
            logging.info(
                f"📧 Found user session for: {user_with_session['firstName']} {user_with_session['lastName']}"
            )

            # Check session expiration
            if user_with_session.get("session_expires"):
                session_expires = user_with_session["session_expires"]
                current_time = datetime.now(pytz.timezone("America/Toronto"))

                # Make sure both datetimes are timezone-aware for comparison
                if (
                    hasattr(session_expires, "tzinfo")
                    and session_expires.tzinfo is None
                ):
                    # session_expires is naive, make it timezone-aware
                    session_expires = pytz.timezone(
                        "America/Toronto"
                    ).localize(session_expires)
                elif not hasattr(session_expires, "tzinfo"):
                    # Handle case where session_expires might not be a datetime object
                    pass

                if current_time > session_expires:
                    raise HTTPException(
                        status_code=401, detail="Session expired"
                    )

            two_fa_email = user_with_session["email"]

            # Check rate limiting for this user (only after multiple failed attempts)
            current_time = datetime.now(pytz.timezone("America/Toronto"))
            failed_attempts = user_with_session.get("failed_2fa_attempts", 0)

            # Only apply rate limiting after 3 failed verification attempts
            if failed_attempts >= 3:
                # Check if user has a rate limit timeout set
                rate_limit_until = user_with_session.get("rate_limit_until")

                if rate_limit_until:
                    # Make sure datetime is timezone-aware for comparison
                    if (
                        hasattr(rate_limit_until, "tzinfo")
                        and rate_limit_until.tzinfo is None
                    ):
                        rate_limit_until = pytz.timezone(
                            "America/Toronto"
                        ).localize(rate_limit_until)

                    if current_time < rate_limit_until:
                        time_remaining = int(
                            (rate_limit_until - current_time).total_seconds()
                        )
                        logging.warning(
                            f"⚠️ User rate limit after {failed_attempts} failed attempts: {time_remaining} seconds remaining."
                        )
                        raise HTTPException(
                            status_code=429,
                            detail=f"Too many failed attempts. Please wait {time_remaining} more seconds before requesting another code.",
                        )

            # Generate and send verification code for user
            verification_code = generate_email_code()
            hashed_code = hash_email_code(verification_code)
            expires_at = datetime.now(
                pytz.timezone("America/Toronto")
            ) + timedelta(minutes=3)

            logging.info(
                f"📧 Sending verification code to user email: {two_fa_email}"
            )

            # Store hashed code and expiration in user record
            await db.users.update_one(
                {"id": user_with_session["id"]},
                {
                    "$set": {
                        "email_code_hash": hashed_code,
                        "email_code_expires_at": expires_at,
                        "updated_at": datetime.now(
                            pytz.timezone("America/Toronto")
                        ),
                    }
                },
            )

            # Send email with verification code
            success = await send_2fa_email(two_fa_email, verification_code)

            if success:
                logging.info(
                    f"✅ 2FA code sent successfully to user email: {two_fa_email}"
                )
                return {
                    "success": True,
                    "message": f"Verification code sent to {two_fa_email}",
                    "code_expires_in_minutes": 3,
                }
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to send verification email"
                )

        # If not a user session, check admin session
        admin_user = await get_admin_user()

        if not admin_user.get("two_fa_enabled"):
            raise HTTPException(status_code=400, detail="2FA not enabled")

        if not admin_user.get("two_fa_email"):
            raise HTTPException(
                status_code=400, detail="2FA email not configured"
            )

        # Verify admin session token
        if (
            not admin_user.get("current_session_token")
            or admin_user["current_session_token"] != session_token
        ):
            raise HTTPException(status_code=401, detail="Invalid session")

        # Check admin rate limiting (only after multiple failed attempts)
        current_time = datetime.now(pytz.timezone("America/Toronto"))
        failed_attempts = admin_user.get("failed_2fa_attempts", 0)

        # 🔑 ADMIN BYPASS: Check if this is the admin session with PIN 0224 privileges
        # If the admin used PIN 0224, they have bypass privileges for rate limiting
        admin_has_bypass = (
            admin_user.get("current_session_token") == session_token
        )

        # Only apply rate limiting after 3 failed verification attempts AND if not admin bypass
        if failed_attempts >= 3 and not admin_has_bypass:
            # Check if admin has a rate limit timeout set
            rate_limit_until = admin_user.get("rate_limit_until")

            if rate_limit_until:
                # Make sure datetime is timezone-aware for comparison
                if (
                    hasattr(rate_limit_until, "tzinfo")
                    and rate_limit_until.tzinfo is None
                ):
                    rate_limit_until = pytz.timezone(
                        "America/Toronto"
                    ).localize(rate_limit_until)

                if current_time < rate_limit_until:
                    time_remaining = int(
                        (rate_limit_until - current_time).total_seconds()
                    )
                    logging.warning(
                        f"⚠️ Admin rate limit after {failed_attempts} failed attempts: {time_remaining} seconds remaining."
                    )
                    raise HTTPException(
                        status_code=429,
                        detail=f"Too many failed attempts. Please wait {time_remaining} more seconds before requesting another code.",
                    )
        elif admin_has_bypass:
            logging.info(
                "🔑 ADMIN BYPASS ACTIVE - PIN 0224 privileges - Rate limiting bypassed"
            )
            # Clear any existing rate limit for admin bypass
            await db.admin_users.update_one(
                {"username": "admin"},
                {"$unset": {"rate_limit_until": 1, "failed_2fa_attempts": 1}},
            )

        # Generate and send verification code
        verification_code = generate_email_code()
        hashed_code = hash_email_code(verification_code)

        # Set expiration time (3 minutes from now)
        expires_at = datetime.now(
            pytz.timezone("America/Toronto")
        ) + timedelta(minutes=3)

        logging.info(
            f"📧 Sending verification code to: {admin_user['two_fa_email']}"
        )

        # Store hashed code and expiration
        await db.admin_users.update_one(
            {"username": "admin"},
            {
                "$set": {
                    "email_code_hash": hashed_code,
                    "email_code_expires_at": expires_at,
                }
            },
        )

        # Send email with verification code
        email_sent = await send_2fa_email(
            admin_user["two_fa_email"], verification_code
        )

        if not email_sent:
            raise HTTPException(
                status_code=500, detail="Failed to send verification email"
            )

        logging.info(
            f"✅ 2FA code sent successfully to {admin_user['two_fa_email']}"
        )

        return {
            "success": True,
            "message": f"Verification code sent to {admin_user['two_fa_email']}",
            "expires_in_minutes": 3,
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Failed to send verification code: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send verification code: {str(e)}",
        )


@api_router.post("/admin/2fa/verify")
async def verify_email_code(request: EmailTwoFactorVerifyRequest):
    """Verify email verification code for both user and admin access"""
    try:
        # First check if this is a user session
        user_with_session = await db.users.find_one(
            {"current_session_token": request.session_token, "is_active": True}
        )

        if user_with_session:
            # This is a user verification
            logging.info(
                f"🔐 Verifying email code for user: {user_with_session['firstName']} {user_with_session['lastName']}"
            )

            # Check session expiration
            if user_with_session.get("session_expires"):
                session_expires = user_with_session["session_expires"]
                current_time = datetime.now(pytz.timezone("America/Toronto"))

                # Make sure both datetimes are timezone-aware for comparison
                if (
                    hasattr(session_expires, "tzinfo")
                    and session_expires.tzinfo is None
                ):
                    session_expires = pytz.timezone(
                        "America/Toronto"
                    ).localize(session_expires)

                if current_time > session_expires:
                    raise HTTPException(
                        status_code=401, detail="Session expired"
                    )

            # Check if email code exists and is not expired
            if not user_with_session.get("email_code_hash"):
                raise HTTPException(
                    status_code=400,
                    detail="No verification code found. Please request a new code.",
                )

            # Check code expiration
            if user_with_session.get("email_code_expires_at"):
                code_expires = user_with_session["email_code_expires_at"]
                current_time = datetime.now(pytz.timezone("America/Toronto"))

                # Make sure datetime is timezone-aware for comparison
                if (
                    hasattr(code_expires, "tzinfo")
                    and code_expires.tzinfo is None
                ):
                    code_expires = pytz.timezone("America/Toronto").localize(
                        code_expires
                    )

                if current_time > code_expires:
                    raise HTTPException(
                        status_code=400,
                        detail="Verification code expired. Please request a new code.",
                    )

            # Verify the provided code
            if not verify_email_code_hash(
                user_with_session["email_code_hash"], request.email_code
            ):
                # Increment failed attempts for user
                failed_attempts = (
                    user_with_session.get("failed_2fa_attempts", 0) + 1
                )
                update_data = {"failed_2fa_attempts": failed_attempts}

                # Set rate limit after 3 failed attempts
                if failed_attempts >= 3:
                    rate_limit_until = datetime.now(
                        pytz.timezone("America/Toronto")
                    ) + timedelta(seconds=30)
                    update_data["rate_limit_until"] = rate_limit_until

                await db.users.update_one(
                    {"id": user_with_session["id"]}, {"$set": update_data}
                )
                logging.warning(
                    f"❌ Invalid verification code for user. Attempts: {failed_attempts}"
                )
                raise HTTPException(
                    status_code=401, detail="Invalid verification code"
                )

            # Verification successful - mark user as email verified and clear codes
            await db.users.update_one(
                {"id": user_with_session["id"]},
                {
                    "$set": {
                        "email_verified": True,
                        "failed_2fa_attempts": 0,
                        "email_code_hash": None,
                        "email_code_expires_at": None,
                        "rate_limit_until": None,
                        "updated_at": datetime.now(
                            pytz.timezone("America/Toronto")
                        ),
                    }
                },
            )

            logging.info(
                f"✅ User {user_with_session['firstName']} {user_with_session['lastName']} email verification successful"
            )

            return {
                "success": True,
                "message": "Email verification successful",
                "session_token": request.session_token,
                "user_type": "user",
            }

        # If not a user session, check admin session (fallback for admin PIN 0224)
        admin_user = await get_admin_user()

        if not admin_user.get("two_fa_enabled"):
            raise HTTPException(status_code=400, detail="2FA not enabled")

        # Verify session token
        if (
            not admin_user.get("current_session_token")
            or admin_user["current_session_token"] != request.session_token
        ):
            raise HTTPException(status_code=401, detail="Invalid session")

        # Check if email code exists and is not expired
        if not admin_user.get("email_code_hash"):
            raise HTTPException(
                status_code=400,
                detail="No verification code found. Please request a new code.",
            )

        if admin_user.get("email_code_expires_at"):
            code_expires = admin_user["email_code_expires_at"]
            current_time = datetime.now(pytz.timezone("America/Toronto"))

            # Make sure datetime is timezone-aware for comparison
            if hasattr(code_expires, "tzinfo") and code_expires.tzinfo is None:
                code_expires = pytz.timezone("America/Toronto").localize(
                    code_expires
                )

            if current_time > code_expires:
                raise HTTPException(
                    status_code=400,
                    detail="Verification code expired. Please request a new code.",
                )

        # Verify the provided code
        if not verify_email_code_hash(
            admin_user["email_code_hash"], request.email_code
        ):
            # 🔑 ADMIN BYPASS: Check if this is the admin session with PIN 0224 privileges
            admin_has_bypass = (
                admin_user.get("current_session_token")
                == request.session_token
            )

            if not admin_has_bypass:
                # Increment failed attempts only if not admin bypass
                failed_attempts = admin_user.get("failed_2fa_attempts", 0) + 1
                update_data = {"failed_2fa_attempts": failed_attempts}

                # Set rate limit after 3 failed attempts
                if failed_attempts >= 3:
                    rate_limit_until = datetime.now(
                        pytz.timezone("America/Toronto")
                    ) + timedelta(seconds=30)
                    update_data["rate_limit_until"] = rate_limit_until

                await db.admin_users.update_one(
                    {"username": "admin"}, {"$set": update_data}
                )
                logging.warning(
                    f"❌ Invalid verification code for admin. Attempts: {failed_attempts}"
                )
            else:
                logging.info(
                    "🔑 ADMIN BYPASS ACTIVE - PIN 0224 privileges - Verification failure not counted"
                )

            raise HTTPException(
                status_code=401, detail="Invalid verification code"
            )

        # Verification successful - clear email code and reset failed attempts
        await db.admin_users.update_one(
            {"username": "admin"},
            {
                "$set": {
                    "email_code": None,
                    "email_code_expires": None,
                    "failed_2fa_attempts": 0,
                    "last_login": datetime.now(
                        pytz.timezone("America/Toronto")
                    ),
                }
            },
        )

        return {
            "success": True,
            "message": "Email verification successful",
            "session_token": request.session_token,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Email verification failed: {str(e)}"
        )


@api_router.post("/admin/2fa/disable")
async def disable_email_two_factor(request: dict):
    """Disable email-based 2FA (requires current email verification)"""
    try:
        email_code = request.get("email_code")
        if not email_code:
            raise HTTPException(
                status_code=400,
                detail="Email verification code required to disable 2FA",
            )

        admin_user = await get_admin_user()

        if not admin_user.get("two_fa_enabled"):
            raise HTTPException(
                status_code=400, detail="2FA not currently enabled"
            )

        # Verify current email code
        if not admin_user.get("email_code") or is_email_code_expired(
            admin_user.get("email_code_expires")
        ):
            raise HTTPException(
                status_code=400,
                detail="No valid verification code found. Please request a new code first.",
            )

        if not verify_email_code_hash(admin_user["email_code"], email_code):
            raise HTTPException(
                status_code=401, detail="Invalid verification code"
            )

        # Disable 2FA
        await db.admin_users.update_one(
            {"username": "admin"},
            {
                "$set": {
                    "two_fa_enabled": False,
                    "two_fa_email": None,
                    "email_code": None,
                    "email_code_expires": None,
                }
            },
        )

        return {
            "success": True,
            "message": "Email-based 2FA disabled successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to disable 2FA: {str(e)}"
        )


@api_router.post("/admin/pin-verify")
async def verify_admin_pin(request: dict):
    """Modified PIN verification - returns 2FA requirement status"""
    try:
        pin = request.get("pin")
        if not pin:
            raise HTTPException(status_code=400, detail="PIN is required")

        admin_user = await get_admin_user()

        # Check if account is locked
        if admin_user.get("locked_until"):
            locked_until = admin_user["locked_until"]
            if isinstance(locked_until, str):
                locked_until = datetime.fromisoformat(
                    locked_until.replace("Z", "+00:00")
                )

            if datetime.now(pytz.timezone("America/Toronto")) < locked_until:
                raise HTTPException(
                    status_code=423, detail="Account temporarily locked"
                )

        # Verify PIN
        if not bcrypt.checkpw(pin.encode(), admin_user["pin_hash"].encode()):
            # Increment failed attempts
            failed_attempts = admin_user.get("failed_2fa_attempts", 0) + 1

            # Lock account after 5 failed attempts
            update_data = {"failed_2fa_attempts": failed_attempts}
            if failed_attempts >= 5:
                update_data["locked_until"] = datetime.now(
                    pytz.timezone("America/Toronto")
                ) + timedelta(minutes=30)

            await db.admin_users.update_one(
                {"username": "admin"}, {"$set": update_data}
            )
            raise HTTPException(status_code=401, detail="Invalid PIN")

        # PIN correct - reset failed attempts and create session
        session_token = str(uuid.uuid4())
        session_expires = datetime.now(
            pytz.timezone("America/Toronto")
        ) + timedelta(hours=8)

        await db.admin_users.update_one(
            {"username": "admin"},
            {
                "$set": {
                    "failed_2fa_attempts": 0,
                    "current_session_token": session_token,
                    "session_expires": session_expires,
                }
            },
        )

        return {
            "pin_valid": True,
            "two_fa_enabled": admin_user.get("two_fa_enabled", False),
            "two_fa_required": admin_user.get("two_fa_enabled", False),
            "two_fa_email": admin_user.get("two_fa_email"),
            "session_token": session_token,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"PIN verification failed: {str(e)}"
        )
