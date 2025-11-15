from datetime import datetime, timezone
from typing import List, Optional, Union
import datetime as dt
from app.registration.schemas import (
    ActivityCreate,
    ActivityRead,
    ActivityUpdate,
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
    TestCreate,
    TestRead,
    TestUpdate,
)
from app.database import database


class PatientService:
    # Patient
    @staticmethod
    async def create_patient(patient: PatientCreate) -> Optional[int]:
        query = """
        INSERT INTO patients (
            first_name, last_name, dob, age, gender, aka, address, unit_number, 
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
            $29, $30, $31, $32, $33, $34, $35, $36
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
                    patient.age,
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
        query = """
        SELECT * FROM patients; 
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(PatientRead(**dict(row)))
        return result

    @staticmethod
    async def get_patient_by_id(id: int) -> Union[PatientRead, None]:
        query = """
        SELECT * 
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


class TestService:
    # Test
    @staticmethod
    async def create_test(patient_id: int, test: TestCreate) -> bool:
        query = """
        INSERT INTO tests (
            patient_id, test_type, test_date, hiv_result, hiv_type, hiv_tester,
            hcv_result, hcv_tester, bloodwork_type, bloodwork_circles, 
            bloodwork_result, bloodwork_date_submitted, bloodwork_tester
        )
        VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
        )
        RETURNING id;
        """
        # Insert test and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                patient_id,
                test.test_type,
                test.test_date,
                test.hiv_result,
                test.hiv_type,
                test.hiv_tester,
                test.hcv_result,
                test.hcv_tester,
                test.bloodwork_type,
                test.bloodwork_circles,
                test.bloodwork_result,
                test.bloodwork_date_submitted,
                test.bloodwork_tester,
            )
            return bool(row)

    @staticmethod
    async def get_tests() -> List[TestRead]:
        query = """
        SELECT * FROM tests; 
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query)
        result = []
        if rows:
            for row in rows:
                result.append(TestRead(**dict(row)))
        return result

    @staticmethod
    async def get_tests_by_patient(patient_id: int) -> List[TestRead]:
        query = """
        SELECT * 
        FROM tests 
        WHERE patient_id = $1 
        ORDER BY test_date DESC;
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query, patient_id)
        result = []
        if rows:
            for row in rows:
                result.append(TestRead(**dict(row)))
        return result

    @staticmethod
    async def get_test_by_id(test_id: int) -> Union[TestRead, None]:
        query = """
        SELECT * 
        FROM tests 
        WHERE id = $1; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, test_id)

        if row:
            return TestRead(**dict(row)) if row else None

    @staticmethod
    async def delete_test_by_id(id: int) -> bool:
        query = """DELETE FROM tests WHERE id=$1 RETURNING id;"""
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_test(
        test_id: int,
        test_updates: TestUpdate,
    ) -> bool:
        updates = test_updates.model_dump(exclude_unset=True)

        if not updates:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(updates.keys())
        ]
        query = f"UPDATE tests SET {', '.join(set_clauses)} WHERE id = ${len(updates)+1} RETURNING id;"
        values = list(updates.values()) + [test_id]
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
        INSERT INTO activities (
            patient_id, date, time, description
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
                activity.date,
                activity.time,
                activity.description,
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
            p.disposition,
            p.referral_site
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
        id: int,
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
