import io
from typing import Any, Dict, Tuple
import pandas as pd
from fastapi import UploadFile
from app.analytics.schema import (
    AnalyticsStats,
    DataSummaryResponse,
    LegacyData,
)
import re


async def read_legacy_data_file(file: UploadFile) -> pd.DataFrame:
    # Read file content
    content = await file.read()

    # Parse Excel/CSV file
    if file.filename.endswith(".csv"):
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    else:
        df = pd.read_excel(io.BytesIO(content))

    df = df.fillna("")
    df.columns = df.columns.str.strip()

    return df


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


class LegacyDataAnalyzer:
    """Handles analysis of legacy patient data"""

    @staticmethod
    def extract_year_from_date(date_value: Any) -> str | None:
        """Extract year from various date formats"""
        if not date_value or str(date_value).strip() == "":
            return None

        try:
            date_str = str(date_value).strip()
            if date_str.lower() in ["", "null", "none", "nan", "invalid date"]:
                return None

            # Handle ISO format
            if (
                isinstance(date_value, str)
                and "T" in date_value
                and len(date_value) >= 4
            ):
                return date_value[:4]

            # Parse other formats
            parsed_date = pd.to_datetime(date_value, errors="coerce")
            if pd.notna(parsed_date):
                return parsed_date.strftime("%Y")

        except Exception:
            pass
        return None

    @staticmethod
    def extract_month_year_from_date(
        date_value: Any,
    ) -> Tuple[str | None, str | None]:
        """Extract both month-year (YYYY-MM) and year from date"""
        if not date_value or str(date_value).strip() == "":
            return None, None

        try:
            date_str = str(date_value).strip()
            if date_str.lower() in ["", "null", "none", "nan", "invalid date"]:
                return None, None

            # Handle ISO format
            if (
                isinstance(date_value, str)
                and "T" in date_value
                and len(date_value) >= 7
            ):
                year = date_value[:4]
                month_year = date_value[:7]  # YYYY-MM
                # Validate format
                if (
                    len(month_year) == 7
                    and month_year[4] == "-"
                    and year.isdigit()
                    and month_year[5:7].isdigit()
                ):
                    return month_year, year

            # Parse other formats
            parsed_date = pd.to_datetime(date_value, errors="coerce")
            if pd.notna(parsed_date):
                return parsed_date.strftime("%Y-%m"), parsed_date.strftime(
                    "%Y"
                )

        except Exception:
            pass
        return None, None

    @staticmethod
    def process_disposition_and_gender(record: Dict, stats: AnalyticsStats):
        """Process disposition and gender data with year breakdown"""
        year = LegacyDataAnalyzer.extract_year_from_date(
            record.get("RegDate") or record.get("regDate")
        )

        # Process disposition
        disp = (
            record.get("disposition") or record.get("Disposition") or "Unknown"
        )
        if (
            disp
            and str(disp).strip()
            and str(disp).lower()
            not in ["", "null", "none", "nan", "invalid date"]
        ):
            stats.dispositions[disp] = stats.dispositions.get(disp, 0) + 1

            if year == "2024":
                stats.dispositions_2024[disp] = (
                    stats.dispositions_2024.get(disp, 0) + 1
                )
            elif year == "2025":
                stats.dispositions_2025[disp] = (
                    stats.dispositions_2025.get(disp, 0) + 1
                )

        # Process gender
        gender = record.get("Gender") or record.get("gender") or "Unknown"
        if (
            gender
            and str(gender).strip()
            and str(gender).lower()
            not in ["", "null", "none", "nan", "invalid date"]
        ):
            stats.genders[gender] = stats.genders.get(gender, 0) + 1

            if year == "2024":
                stats.genders_2024[gender] = (
                    stats.genders_2024.get(gender, 0) + 1
                )
            elif year == "2025":
                stats.genders_2025[gender] = (
                    stats.genders_2025.get(gender, 0) + 1
                )

    @staticmethod
    def process_phone_number(record: Dict, stats: AnalyticsStats):
        """Process phone number validation"""
        stats.phone_stats["total_records"] += 1

        phone = record.get("Phone") or record.get("phone") or ""
        phone_str = str(phone).strip()

        invalid_phones = [
            "",
            "null",
            "none",
            "nan",
            "(000) 000-0000",
            "000-000-0000",
            "0000000000",
        ]

        if not phone_str or phone_str.lower() in invalid_phones:
            stats.phone_stats["no_phone_count"] += 1
        else:
            stats.phone_stats["valid_phone_count"] += 1

    @staticmethod
    def process_health_card(record: Dict, stats: AnalyticsStats):
        """Process health card validation"""
        stats.health_card_stats["total_records"] += 1

        hc = (
            record.get("HC")
            or record.get("HealthCard")
            or record.get("healthCard")
            or ""
        )
        hc_str = str(hc).strip()

        # No health card patterns
        no_hc_patterns = [
            "",
            "null",
            "none",
            "nan",
            "0000000000 NA",
            "0000000000",
            "NA",
            "0000000000NA",
        ]

        if not hc_str or hc_str.lower() in no_hc_patterns:
            stats.health_card_stats["no_hc_count"] += 1
        elif re.match(r"^\d{10}$", hc_str):  # 10 digits only (invalid)
            stats.health_card_stats["invalid_hc_count"] += 1
        elif re.match(
            r"^\d{10}[A-Za-z]{2}$", hc_str
        ):  # 10 digits + 2 letters (valid)
            stats.health_card_stats["valid_hc_count"] += 1
        else:
            stats.health_card_stats["invalid_hc_count"] += 1

    @staticmethod
    def process_address(record: Dict, stats: AnalyticsStats):
        """Process address validation"""
        stats.address_stats["total_records"] += 1

        address = record.get("Address") or record.get("address") or ""
        address_str = str(address).strip().lower()

        invalid_addresses = [
            "",
            "null",
            "none",
            "nan",
            "no address",
            "no fixed address",
            "nfa",
            "homeless",
        ]

        if not address_str or address_str in invalid_addresses:
            stats.address_stats["no_address_count"] += 1
        else:
            stats.address_stats["valid_address_count"] += 1

    @staticmethod
    def process_rewards(record: Dict, stats: AnalyticsStats):
        """Process rewards/payment amounts"""
        # Try multiple possible field names for amount
        amount_fields = [
            "Amount",
            "amount",
            "Reward",
            "reward",
            "AMOUNT",
            "REWARD",
            "P",
            "p",
            "rewards",
            "REWARDS",
            "payment",
            "Payment",
            "PAYMENT",
        ]

        amount = None
        for field in amount_fields:
            if field in record and record[field] is not None:
                amount = record[field]
                break

        if amount is None:
            return

        try:
            amount_val = LegacyDataAnalyzer.parse_amount(amount)
            if amount_val > 0:
                stats.rewards_stats["total_amount"] += amount_val
                stats.rewards_stats["total_records_with_amount"] += 1

                # Process date for monthly/yearly breakdown
                month_year, year = (
                    LegacyDataAnalyzer.extract_month_year_from_date(
                        record.get("RegDate")
                        or record.get("regDate")
                        or record.get("REGDATE")
                    )
                )

                if year in ["2024", "2025"]:
                    stats.rewards_stats["yearly_totals"][year] += amount_val

                    if year == "2024" and month_year:
                        stats.rewards_stats["monthly_totals_2024"][
                            month_year
                        ] = (
                            stats.rewards_stats["monthly_totals_2024"].get(
                                month_year, 0
                            )
                            + amount_val
                        )
                    elif year == "2025" and month_year:
                        stats.rewards_stats["monthly_totals_2025"][
                            month_year
                        ] = (
                            stats.rewards_stats["monthly_totals_2025"].get(
                                month_year, 0
                            )
                            + amount_val
                        )

        except Exception:
            pass  # Skip invalid amounts

    @staticmethod
    def parse_amount(amount: Any) -> float:
        """Parse amount from various formats"""
        if isinstance(amount, (int, float)) and amount > 0:
            return float(amount)

        if not str(amount).strip():
            return 0

        amount_str = (
            str(amount)
            .strip()
            .replace("$", "")
            .replace(",", "")
            .replace(" ", "")
            .replace("CAD", "")
            .replace("USD", "")
        )

        invalid_amounts = [
            "",
            "null",
            "none",
            "nan",
            "0",
            "0.0",
            "0.00",
            "n/a",
            "na",
        ]
        if amount_str.lower() in invalid_amounts:
            return 0

        try:
            return float(amount_str)
        except ValueError:
            # Try cleaning non-numeric characters
            clean_amount = "".join(
                c for c in amount_str if c.isdigit() or c == "."
            )
            return float(clean_amount) if clean_amount else 0

    @staticmethod
    def process_age(record: Dict, stats: AnalyticsStats):
        """Process age and categorize into ranges"""
        dob_fields = ["DOB", "dob", "dateOfBirth", "DateOfBirth"]
        dob = None

        for field in dob_fields:
            if field in record and record[field]:
                dob = record[field]
                break

        if not dob or str(dob).strip().lower() in ["", "null", "none", "nan"]:
            return

        try:
            # Parse date of birth
            if isinstance(dob, str) and "T" in dob and len(dob) >= 10:
                dob_date = pd.to_datetime(dob[:10], errors="coerce")
            else:
                dob_date = pd.to_datetime(dob, errors="coerce")

            if pd.notna(dob_date):
                # Calculate age
                today = date.today()
                age = (
                    today.year
                    - dob_date.year
                    - (
                        (today.month, today.day)
                        < (dob_date.month, dob_date.day)
                    )
                )

                # Categorize into age ranges
                if age < 20:
                    stats.age_stats["age_ranges"]["0-19"] += 1
                elif age < 30:
                    stats.age_stats["age_ranges"]["20-29"] += 1
                elif age < 40:
                    stats.age_stats["age_ranges"]["30-39"] += 1
                elif age < 50:
                    stats.age_stats["age_ranges"]["40-49"] += 1
                elif age < 60:
                    stats.age_stats["age_ranges"]["50-59"] += 1
                elif age < 70:
                    stats.age_stats["age_ranges"]["60-69"] += 1
                elif age < 80:
                    stats.age_stats["age_ranges"]["70-79"] += 1
                elif age < 90:
                    stats.age_stats["age_ranges"]["80-89"] += 1
                else:
                    stats.age_stats["age_ranges"]["90+"] += 1

                stats.age_stats["total_records_with_age"] += 1

        except Exception:
            pass

    @staticmethod
    def process_registration_dates(record: Dict, stats: AnalyticsStats):
        """Process registration dates for monthly/yearly counts"""
        month_year, year = LegacyDataAnalyzer.extract_month_year_from_date(
            record.get("RegDate") or record.get("regDate")
        )

        if month_year and year:
            stats.monthly_counts[month_year] = (
                stats.monthly_counts.get(month_year, 0) + 1
            )
            stats.yearly_data[year] = stats.yearly_data.get(year, 0) + 1

    @staticmethod
    def analyze_legacy_data(legacy_upload: dict) -> AnalyticsStats:
        """Main analysis function - processes all legacy data"""
        if not legacy_upload or len(legacy_upload["data"]) == 0:
            raise ValueError("No legacy data available")

        records = legacy_upload["data"]
        stats = AnalyticsStats()
        stats.total_records = len(records)

        # Process each record
        for record in records:
            LegacyDataAnalyzer.process_disposition_and_gender(record, stats)
            LegacyDataAnalyzer.process_phone_number(record, stats)
            LegacyDataAnalyzer.process_health_card(record, stats)
            LegacyDataAnalyzer.process_address(record, stats)
            LegacyDataAnalyzer.process_rewards(record, stats)
            LegacyDataAnalyzer.process_age(record, stats)
            LegacyDataAnalyzer.process_registration_dates(record, stats)

        return stats
