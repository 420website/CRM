# pyright: reportGeneralTypeIssues=none,reportArgumentType=none,reportOptionalMemberAccess=none,reportPossiblyUnboundVariable=none,reportAttributeAccessIssue=none,reportCallIssue=none
import io
import uuid
import pytz
import pandas as pd
from fastapi import File, APIRouter, HTTPException, UploadFile
from datetime import datetime
from app.config import settings
from app.database import mongo_db
from app.analytics.prompts import legacy_context_prompt, system_message
from app.analytics.schema import (
    ClaudeChatRequest,
    ClaudeChatResponse,
    DataSummaryResponse,
    ExcelUploadResponse,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/legacy-data-summary", response_model=DataSummaryResponse)
async def get_legacy_data_summary():
    """Get summary of uploaded legacy data"""
    try:
        # Get latest upload
        legacy_upload = await mongo_db.legacy_data.find_one(
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
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze legacy data",
        )


@router.post("/upload-legacy-data", response_model=ExcelUploadResponse)
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
        await mongo_db.legacy_data.delete_many({})  # Clear previous data
        await mongo_db.legacy_data.insert_one(legacy_data)

        # Create preview (first 5 records)
        preview = records[:5] if len(records) > 5 else records

        return ExcelUploadResponse(
            message=f"Successfully uploaded {len(records)} records from {file.filename}",
            records_count=len(records),
            preview=preview,
            upload_id=upload_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process file: {str(e)}"
        )


@router.post("/claude-chat", response_model=ClaudeChatResponse)
async def claude_chat(request: ClaudeChatRequest):
    """Claude AI chat endpoint for admin analytics with legacy data access and chart generation"""
    try:
        # Get comprehensive legacy data for analysis
        legacy_context = ""
        chart_html = None
        chart_image_url = None

        try:
            legacy_upload = await mongo_db.legacy_data.find_one(
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
                        # logging.warning(
                        #     f"Error processing amount {amount}: {str(e)}"
                        # )
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
                context_text = legacy_context_prompt(
                    legacy_upload,
                    total_records,
                    rewards_stats,
                    address_stats,
                    dispositions,
                    dispositions_2024,
                    dispositions_2025,
                    clean_dispositions,
                    genders_2024,
                    genders_2025,
                    phone_stats,
                    health_card_stats,
                    age_stats,
                    genders,
                    clean_yearly_data,
                    clean_monthly_counts,
                    monthly_counts,
                    yearly_data,
                )
                legacy_context = legacy_context(context_text)

        except Exception as e:
            # logging.error(f"Error generating legacy context: {str(e)}")
            legacy_context = f"Error accessing legacy data: {str(e)}"

        system_msg = system_message(legacy_context)

        message = await settings.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            system=system_msg,
            messages=[{"role": "user", "content": request.message}],
        )

        # Content is an array
        # First item is for type TextBlock(citations=.., text="..", type="text")
        response_text = message.content[0].text  # reportAttributeAccessIssue

        return ClaudeChatResponse(
            response=response_text,
            session_id=request.session_id,
            chart_html=chart_html,
            chart_image_url=chart_image_url,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="AI chat service temporarily unavailable"
        )
