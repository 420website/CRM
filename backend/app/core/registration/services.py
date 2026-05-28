import json
from datetime import datetime, timezone
from typing import List, Optional, Union
import datetime as dt
from app.core.registration.schemas import (
    ActivityCreate,
    ActivityRead,
    ActivityUpdate,
    AssessementUpdate,
    AssessmentCreate,
    AssessmentRead,
    DispensingCreate,
    DispensingRead,
    DispensingUpdate,
    HealthcardCheck,
    HealthcardUser,
    IdentityCheck,
    IdentityUser,
    InteractionCreate,
    InteractionRead,
    InteractionUpdate,
    MedicationCreate,
    MedicationRead,
    MedicationUpdate,
    NoteCreate,
    NoteRead,
    NoteUpdate,
    PatientActivity,
    PatientBase,
    PatientCreate,
    PatientRead,
    PatientUpdate,
)
from app.common.storage.postgres import database

AGE_QUERY = "DATE_PART('year', AGE(dob))::INT AS age"


class PatientService:
    # Patient
    @staticmethod
    async def create_patient(patient: PatientCreate) -> Optional[int]:
        query = """
        INSERT INTO patients (
            first_name, last_name, dob, gender, aka, address, unit_number, 
            city, province, postal_code, phone1, phone2, email, language, health_card, 
            health_card_version, coverage_type, disposition, physician, 
            patient_consent, leave_message, voicemail, text, preferred_time,
            rna_available, rna_result, rna_sample_date, referral_site, referral_person, 
            reg_date, special_attention, instructions, selected_template, 
            summary_template, limited
        )
        VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15,
            $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28,
            $29, $30, $31, $32, $33, $34, $35
        )
        RETURNING id;
        """
        # Insert patient and get the generated ID
        try:
            async with database.get_transaction() as conn:
                row = await conn.fetchrow(
                    query,
                    patient.first_name,
                    patient.last_name,
                    patient.dob,
                    patient.gender,
                    patient.aka,
                    patient.address,
                    patient.unit_number,
                    patient.city,
                    patient.province,
                    patient.postal_code,
                    patient.phone1,
                    patient.phone2,
                    patient.email,
                    patient.language,
                    patient.health_card,
                    patient.health_card_version,
                    patient.coverage_type,
                    patient.disposition,
                    patient.physician,
                    patient.patient_consent,
                    patient.leave_message,
                    patient.voicemail,
                    patient.text,
                    patient.preferred_time,
                    patient.rna_available,
                    patient.rna_result,
                    patient.rna_sample_date,
                    patient.referral_site,
                    patient.referral_person,
                    patient.reg_date,
                    patient.special_attention,
                    patient.instructions,
                    patient.selected_template,
                    patient.summary_template,
                    patient.limited,
                )
                if row and "id" in row:
                    return row["id"]
                return None
        except Exception as e:
            raise e

    @staticmethod
    async def get_patients() -> List[PatientBase]:
        query = f"""
        SELECT *, {AGE_QUERY} FROM patients;
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(PatientRead(**dict(row)))
        return result

    @staticmethod
    async def get_patients_by_location(
        locations: List[str],
    ) -> List[PatientBase]:
        if len(locations) == 0:
            return []

        query = f"""
        SELECT *, {AGE_QUERY}        
        FROM patients
        WHERE province= ANY($1); 
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query, locations)

        result = []
        if rows:
            for row in rows:
                result.append(PatientRead(**dict(row)))
        return result

    @staticmethod
    async def get_patient_by_id(id: int) -> Union[PatientRead, None]:
        query = f"""
        SELECT *, {AGE_QUERY}    
        FROM patients
        WHERE id=$1; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, id)

        if row:
            return PatientRead(**dict(row)) if row else None

    @staticmethod
    async def check_identity(data: IdentityCheck) -> Union[IdentityUser, None]:
        if data.id is None:
            query = """
                SELECT id, first_name, last_name 
                FROM patients 
                WHERE first_name=$1 
                    AND last_name=$2 
                    AND dob=$3
            """
            params = [data.first_name, data.last_name, data.dob]
        else:
            query = """
                SELECT id, first_name, last_name 
                FROM patients 
                WHERE first_name=$1 
                    AND last_name=$2 
                    AND dob=$3 
                    AND id!=$4
            """
            params = [data.first_name, data.last_name, data.dob, data.id]

        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, *params)

        if row:
            return IdentityUser(**dict(row)) if row else None

    @staticmethod
    async def check_healthcard(
        data: HealthcardCheck,
    ) -> Union[HealthcardUser, None]:
        if data.id is None:
            query = """
                SELECT id, first_name, last_name 
                FROM patients 
                WHERE health_card=$1
            """
            params = [data.health_card]
        else:
            query = """
                SELECT id, first_name, last_name 
                FROM patients 
                WHERE health_card=$1
                    AND id!=$2
            """
            params = [data.health_card, data.id]

        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, *params)

        if row:
            return HealthcardUser(**dict(row)) if row else None

    @staticmethod
    async def get_patient_by_name_dob(
        first_name: str,
        last_name: str,
        dob: dt.date,
    ) -> Union[int, None]:
        query = """
        SELECT id 
        FROM patients
        WHERE first_name=$1 
          AND last_name=$2 
          AND dob=$3; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, first_name, last_name, dob)

        if row and "id" in row:
            return row["id"]

        return None

    @staticmethod
    async def get_other_patient_name_dob(
        id: int,
        first_name: str,
        last_name: str,
        dob: dt.date,
    ) -> Union[int, None]:
        query = """
        SELECT id 
        FROM patients
        WHERE first_name=$1 
          AND last_name=$2 
          AND dob=$3
          AND id !=$4; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, first_name, last_name, dob, id)

        if row and "id" in row:
            return row["id"]

        return None

    @staticmethod
    async def get_patient_status(id: int) -> Union[str, None]:
        query = """
        SELECT status  
        FROM patients
        WHERE id=$1; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, id)

        if row:
            return row if row else None

    @staticmethod
    async def delete_patient(first_name: str, last_name: str) -> bool:
        query = """
            DELETE FROM patients 
            WHERE first_name=$1 
            AND last_name=$2 
            RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, first_name, last_name)
            return bool(row)

    @staticmethod
    async def delete_patient_by_id(id: int) -> bool:
        query = """DELETE FROM patients WHERE id=$1 RETURNING id;"""
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_patient(
        patient_id: int,
        patient_updates: PatientUpdate,
    ) -> bool:
        try:
            updates = patient_updates.model_dump(
                exclude_unset=True,
                exclude={"force_update"},
            )

            if not updates:
                return False

            set_clauses = [
                f"{field} = ${i+1}" for i, field in enumerate(updates.keys())
            ]
            query = f"UPDATE patients SET {', '.join(set_clauses)} WHERE id = ${len(updates)+1} RETURNING id;"
            values = list(updates.values()) + [patient_id]
            async with database.get_transaction() as conn:
                row = await conn.fetchrow(query, *values)
                return bool(row)
        except Exception as e:
            raise e

    @staticmethod
    async def update_patient_status(
        patient_id: int, status: str, is_first_finalize: bool
    ) -> bool:
        if status != "pending" and is_first_finalize:
            finalized_at = datetime.now(timezone.utc)

            query = """
                UPDATE patients
                SET status = $1, finalized_at=$2, updated_at = NOW()
                WHERE id = $3
                RETURNING id;
            """
            params = [status, finalized_at, patient_id]
        else:
            query = """
                UPDATE patients
                SET status = $1, updated_at = NOW()
                WHERE id = $2
                RETURNING id;
            """
            params = [status, patient_id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *params)
            return bool(row)


class AssessmentService:
    # Test
    @staticmethod
    async def create_assessment(
        patient_id: int, data: AssessmentCreate
    ) -> bool:
        query = """
        INSERT INTO assessments (patient_id, type, date, result, tester, data)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id;
        """
        # Convert data dict to JSON string if present
        json_data = json.dumps(data.data) if data.data else None

        # Insert test and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                patient_id,
                data.type,
                data.date,
                data.result,
                data.tester,
                json_data,
            )
            return bool(row)

    @staticmethod
    async def get_assessments() -> List[AssessmentRead]:
        query = """
        SELECT * FROM assessments; 
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

            # Parse JSON string back to dict
            assessments = []
            for row in rows:
                row_dict = dict(row)
                # Parse the JSON string in the 'data' field
                if row_dict.get("data"):
                    row_dict["data"] = json.loads(row_dict["data"])
                assessments.append(AssessmentRead(**row_dict))

            return assessments

    @staticmethod
    async def get_assessment_by_patient(
        patient_id: int,
    ) -> List[AssessmentRead]:
        query = """
        SELECT * 
        FROM assessments 
        WHERE patient_id = $1 
        ORDER BY date DESC;
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query, patient_id)

            # Parse JSON string back to dict
            assessments = []
            for row in rows:
                row_dict = dict(row)
                # Parse the JSON string in the 'data' field
                if row_dict.get("data"):
                    row_dict["data"] = json.loads(row_dict["data"])
                assessments.append(AssessmentRead(**row_dict))

            return assessments

    @staticmethod
    async def get_assessment_by_id(
        assessment_id: int,
    ) -> Union[AssessmentRead, None]:
        query = """
        SELECT * 
        FROM assessments 
        WHERE id = $1; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, assessment_id)

        if not row:
            return None

        row_dict = dict(row)

        # Parse the JSON string in the 'data' field
        if row_dict.get("data"):
            row_dict["data"] = json.loads(row_dict["data"])

        return AssessmentRead(**dict(row_dict))

    @staticmethod
    async def delete_assessment_by_id(id: int) -> bool:
        query = """DELETE FROM assessments WHERE id=$1 RETURNING id;"""
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_assessment(
        assessment_id: int,
        assessment_updates: AssessementUpdate,
    ) -> bool:
        updates = assessment_updates.model_dump(exclude_unset=True)

        # Convert data dict to JSON string if present
        if "data" in updates and updates["data"] is not None:
            updates["data"] = json.dumps(updates["data"])

        if not updates:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(updates.keys())
        ]
        query = f"UPDATE assessments SET {', '.join(set_clauses)} WHERE id = ${len(updates)+1} RETURNING id;"
        values = list(updates.values()) + [assessment_id]
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)


class NoteService:
    # Notes
    @staticmethod
    async def create_note(patient_id: int, note: NoteCreate) -> bool:
        query = """
        INSERT INTO notes (
            patient_id, note_date, note_text, template_type
        )
        VALUES (
            $1, $2, $3, $4
        )
        RETURNING id;
        """
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                patient_id,
                note.note_date,
                note.note_text,
                note.template_type,
            )
            return bool(row)

    @staticmethod
    async def get_notes() -> List[NoteRead]:
        query = """
        SELECT * 
        FROM notes 
        ORDER BY note_date DESC, updated_at DESC; 
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(NoteRead(**dict(row)))
        return result

    @staticmethod
    async def get_notes_by_patient(patient_id: int) -> List[NoteRead]:
        query = """
        SELECT * 
        FROM notes 
        WHERE patient_id = $1 
        ORDER BY note_date DESC, updated_at DESC;
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query, patient_id)

        result = []
        if rows:
            for row in rows:
                result.append(NoteRead(**dict(row)))
        return result

    @staticmethod
    async def get_note_by_id(note_id: int) -> Union[NoteRead, None]:
        query = """
        SELECT * 
        FROM notes 
        WHERE id = $1; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, note_id)

        if row:
            return NoteRead(**dict(row)) if row else None

    @staticmethod
    async def delete_note_by_id(id: int) -> bool:
        query = """DELETE FROM notes WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_note(
        note_id: int,
        note_updates: NoteUpdate,
    ) -> bool:
        updates = note_updates.model_dump(exclude_unset=True)

        if not updates:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(updates.keys())
        ]
        query = f"UPDATE notes SET {', '.join(set_clauses)} WHERE id = ${len(updates)+1} RETURNING id;"
        values = list(updates.values()) + [note_id]
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)


class InteractionService:
    # Interactions
    @staticmethod
    async def create_interaction(
        patient_id: int, interaction: InteractionCreate
    ) -> bool:
        query = """
        INSERT INTO interactions (
            patient_id, date, description, referral_id, amount, payment_type, issued
        )
        VALUES (
            $1, $2, $3, $4, $5, $6, $7
        )
        RETURNING id;
        """
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                patient_id,
                interaction.date,
                interaction.description,
                interaction.referral_id,
                interaction.amount,
                interaction.payment_type,
                interaction.issued,
            )
            return bool(row)

    @staticmethod
    async def get_interactions() -> List[InteractionRead]:
        query = """
        SELECT * 
        FROM interactions 
        ORDER BY date DESC; 
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query)
        result = []
        if rows:
            for row in rows:
                result.append(InteractionRead(**dict(row)))
        return result

    @staticmethod
    async def get_interactions_by_patient(
        patient_id: int,
    ) -> List[InteractionRead]:
        query = """
        SELECT * 
        FROM interactions 
        WHERE patient_id = $1 
        ORDER BY date DESC;
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query, patient_id)
        result = []
        if rows:
            for row in rows:
                result.append(InteractionRead(**dict(row)))
        return result

    @staticmethod
    async def get_interactions_by_id(id: int) -> Union[InteractionRead, None]:
        query = """
        SELECT * 
        FROM interactions 
        WHERE id = $1; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, id)

        if row:
            return InteractionRead(**dict(row)) if row else None

    @staticmethod
    async def delete_interaction_by_id(id: int) -> bool:
        query = """DELETE FROM interactions WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_interaction(
        interaction_id: int,
        interaction_updates: InteractionUpdate,
    ) -> bool:
        updates = interaction_updates.model_dump(exclude_unset=True)

        if not updates:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(updates.keys())
        ]
        query = f"UPDATE interactions SET {', '.join(set_clauses)} WHERE id = ${len(updates)+1} RETURNING id;"
        values = list(updates.values()) + [interaction_id]
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)


class MedicationService:
    # Medications
    @staticmethod
    async def create_medication(
        patient_id: int, medication: MedicationCreate
    ) -> bool:
        query = """
        INSERT INTO medications (
            patient_id, medication, start_date, end_date, outcome
        )
        VALUES (
            $1, $2, $3, $4, $5
        )
        RETURNING id;
        """
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                patient_id,
                medication.medication,
                medication.start_date,
                medication.end_date,
                medication.outcome,
            )
            return bool(row)

    @staticmethod
    async def get_medications() -> List[MedicationRead]:
        query = """
        SELECT * FROM medications ORDER BY start_date DESC; 
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query)
        result = []
        if rows:
            for row in rows:
                result.append(MedicationRead(**dict(row)))
        return result

    @staticmethod
    async def get_medications_by_patient(
        patient_id: int,
    ) -> List[MedicationRead]:
        query = """
        SELECT * 
        FROM medications 
        WHERE patient_id = $1 
        ORDER BY start_date DESC;
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query, patient_id)
        result = []
        if rows:
            for row in rows:
                result.append(MedicationRead(**dict(row)))
        return result

    @staticmethod
    async def get_medications_by_id(id: int) -> Union[MedicationRead, None]:
        query = """
        SELECT * 
        FROM medications 
        WHERE id = $1; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, id)

        if row:
            return MedicationRead(**dict(row)) if row else None

    @staticmethod
    async def delete_medication_by_id(id: int) -> bool:
        query = """DELETE FROM medications WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_medication(
        medication_id: int,
        medication_updates: MedicationUpdate,
    ) -> bool:
        updates = medication_updates.model_dump(exclude_unset=True)

        if not updates:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(updates.keys())
        ]
        query = f"UPDATE medications SET {', '.join(set_clauses)} WHERE id = ${len(updates)+1} RETURNING id;"
        values = list(updates.values()) + [medication_id]
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)


class DispensingService:
    @staticmethod
    async def check_medication(patient_id: int, medication: str) -> bool:
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM medications
                WHERE patient_id = $1
                AND medication =$2
            );
        """
        async with database.get_transaction() as conn:
            return await conn.fetchval(query, patient_id, medication)

    @staticmethod
    async def create_dispensing(
        patient_id: int, dispensing: DispensingCreate
    ) -> bool:
        query = """
        INSERT INTO dispensing (
            patient_id, medication, rx, quantity, lot, product_type, expiry_date
        )
        VALUES (
            $1, $2, $3, $4, $5, $6, $7
        )
        RETURNING id;
        """
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                patient_id,
                dispensing.medication,
                dispensing.rx,
                dispensing.quantity,
                dispensing.lot,
                dispensing.product_type,
                dispensing.expiry_date,
            )
            return bool(row)

    @staticmethod
    async def get_dispensing() -> List[DispensingRead]:
        query = """
        SELECT * FROM dispensing ORDER BY created_at DESC; 
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(DispensingRead(**dict(row)))
        return result

    @staticmethod
    async def get_dispensing_by_patient(
        patient_id: int,
    ) -> List[DispensingRead]:
        query = """
        SELECT * 
        FROM dispensing 
        WHERE patient_id = $1 
        ORDER BY created_at DESC;
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query, patient_id)

        result = []
        if rows:
            for row in rows:
                result.append(DispensingRead(**dict(row)))
        return result

    @staticmethod
    async def get_dispensing_by_id(id: int) -> Union[DispensingRead, None]:
        query = """
        SELECT * 
        FROM dispensing 
        WHERE id = $1; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, id)

        if row:
            return DispensingRead(**dict(row)) if row else None

    @staticmethod
    async def delete_dispensing_by_id(id: int) -> bool:
        query = """DELETE FROM dispensing WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_dispensing(
        dispensing_id: int,
        dispensing_updates: DispensingUpdate,
    ) -> bool:
        updates = dispensing_updates.model_dump(exclude_unset=True)

        if not updates:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(updates.keys())
        ]
        query = f"UPDATE dispensing SET {', '.join(set_clauses)} WHERE id = ${len(updates)+1} RETURNING id;"
        values = list(updates.values()) + [dispensing_id]
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)


class ActivityService:
    # Activities
    @staticmethod
    async def create_activity(
        patient_id: int, activity: ActivityCreate
    ) -> bool:
        query = """
        INSERT INTO activities (patient_id, date, time, description, name)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id;
        """
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                patient_id,
                activity.date,
                activity.time,
                activity.description,
                activity.name,
            )
            return bool(row)

    @staticmethod
    async def get_patient_activities() -> List[PatientActivity]:
        query = """
        SELECT 
            a.*, 
            p.first_name, 
            p.last_name, 
            p.phone1,
            p.province,
            p.disposition,
            p.referral_site,
            p.finalized_at, 
            p.status,
            p.reg_date, 
            p.file_id,
            p.created_at AS submitted_date
        FROM activities a
        JOIN patients p ON a.patient_id = p.id
        ORDER BY a.date DESC, a.time DESC;
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(PatientActivity(**dict(row)))
        return result

    @staticmethod
    async def get_activites_by_location(
        locations: List[str],
    ) -> List[PatientActivity]:
        if len(locations) == 0:
            return []

        query = """
        WITH location_patients AS (
            SELECT 
                id,
                first_name, 
                last_name, 
                province,
                phone1,
                disposition,
                referral_site,
                finalized_at, 
                status,
                reg_date, 
                file_id,
                created_at
            FROM patients
            WHERE province= ANY($1)
        )
        SELECT 
            a.*, 
            lp.first_name, 
            lp.last_name, 
            lp.province,
            lp.phone1,
            lp.disposition,
            lp.referral_site,
            lp.finalized_at, 
            lp.status,
            lp.reg_date, 
            lp.file_id,
            lp.created_at AS submitted_date
        FROM activities a
        JOIN location_patients lp ON a.patient_id = lp.id
        ORDER BY a.date DESC, a.time DESC;
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query, locations)

        result = []
        if rows:
            for row in rows:
                result.append(PatientActivity(**dict(row)))
        return result

    @staticmethod
    async def get_activities() -> List[ActivityRead]:
        query = """
        SELECT * FROM activities ORDER BY date DESC, time DESC; 
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(ActivityRead(**dict(row)))
        return result

    @staticmethod
    async def get_activities_by_patient(patient_id: int) -> List[ActivityRead]:
        query = """
        SELECT * 
        FROM activities 
        WHERE patient_id = $1 
        ORDER BY date DESC, time DESC;
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query, patient_id)

        result = []
        if rows:
            for row in rows:
                result.append(ActivityRead(**dict(row)))
        return result

    @staticmethod
    async def get_activities_by_id(id: int) -> Union[ActivityRead, None]:
        query = """
        SELECT * 
        FROM activities 
        WHERE id = $1; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, id)

        if row:
            return ActivityRead(**dict(row)) if row else None

    @staticmethod
    async def delete_activity_by_id(id: int) -> bool:
        query = """DELETE FROM activities WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_activity(
        activity_id: int,
        activity_updates: ActivityUpdate,
    ) -> bool:
        updates = activity_updates.model_dump(exclude_unset=True)

        if not updates:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(updates.keys())
        ]
        query = f"UPDATE activities SET {', '.join(set_clauses)} WHERE id = ${len(updates)+1} RETURNING id;"
        values = list(updates.values()) + [activity_id]
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)

    @staticmethod
    async def update_activity_status(
        id: int,  # id
        status: bool,
    ) -> bool:
        query = """
            UPDATE activities
            SET completed = $1, updated_at = NOW()
            WHERE id = $3
            RETURNING id;
        """
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, status)
            return bool(row)
