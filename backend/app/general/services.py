from typing import List, Optional, Union
from app.general.schemas import (
    ClinicalTemplate,
    ClinicalTemplateUpdate,
    Disposition,
    DispositionUpdate,
    DocumentType,
    DocumentTypeUpdate,
    General,
    GeneralUpdate,
    Medication,
    MedicationOutcome,
    MedicationOutcomeUpdate,
    MedicationUpdate,
    NotesTemplate,
    NotesTemplateUpdate,
    ReferralSite,
    ReferralSiteUpdate,
)
from app.database import database


class GeneralService:
    @staticmethod
    async def check_exists(name: str, table: str) -> bool:
        query = f"""
            SELECT id 
            FROM {table} 
            WHERE name=$1; 
            """

        async with database.get_connection() as conn:
            row = await conn.fetch(query, name)

            return True if row else False

    # NoteTemplate
    @staticmethod
    async def create_notes_template(template: NotesTemplate) -> Optional[int]:
        query = """
        INSERT INTO note_templates (name, content, is_default)
        VALUES ($1, $2, $3)
        RETURNING id;
        """

        # Insert user and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                template.name,
                template.content,
                template.is_default,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def get_note_template(name: str) -> Union[NotesTemplate, None]:
        query = """
        SELECT * 
        FROM note_templates 
        WHERE name=$1; 
        """

        async with database.get_connection() as conn:
            row = await conn.fetch(query, name)

            if row:
                return NotesTemplate(**dict(row)) if row else None

    @staticmethod
    async def get_note_templates() -> List[NotesTemplate]:
        query = """
        SELECT * FROM note_templates; 
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(NotesTemplate(**dict(row)))

        return result

    @staticmethod
    async def delete_notes_template(name: str) -> bool:
        query = """DELETE FROM note_templates WHERE name=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, name)
            return bool(row)

    @staticmethod
    async def delete_notes_template_by_id(id: int) -> bool:
        query = """DELETE FROM note_templates WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_notes_template(
        temp_id: int, temp_updates: NotesTemplateUpdate
    ) -> bool:
        updates = temp_updates.model_dump(exclude_unset=True)

        if not updates:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(updates.keys())
        ]
        query = f"UPDATE note_templates SET {', '.join(set_clauses)} WHERE id = ${len(updates)+1} RETURNING id;"
        values = list(updates.values()) + [temp_id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)

    # Clinical Template
    @staticmethod
    async def create_clinical_template(
        template: ClinicalTemplate,
    ) -> Optional[int]:
        query = """
        INSERT INTO clinical_templates (name, content, is_default)
        VALUES ($1, $2, $3)
        RETURNING id;
        """

        # Insert user and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                template.name,
                template.content,
                template.is_default,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def get_clinical_template(
        name: str,
    ) -> Union[ClinicalTemplate, None]:
        query = """
        SELECT * 
        FROM clinical_templates 
        WHERE name=$1; 
        """

        async with database.get_connection() as conn:
            row = await conn.fetch(query, name)

            if row:
                return ClinicalTemplate(**dict(row)) if row else None

    @staticmethod
    async def get_clinical_templates() -> List[ClinicalTemplate]:
        query = """
        SELECT * FROM clinical_templates; 
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(ClinicalTemplate(**dict(row)))

        return result

    @staticmethod
    async def delete_clinical_template(name: str) -> bool:
        query = (
            """DELETE FROM clinical_templates WHERE name=$1 RETURNING id;"""
        )

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, name)
            return bool(row)

    @staticmethod
    async def delete_clinical_template_by_id(id: int) -> bool:
        query = """DELETE FROM clinical_templates WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_clinical_template(
        temp_id: int,
        temp_updates: ClinicalTemplateUpdate,
    ) -> bool:
        updates = temp_updates.model_dump(exclude_unset=True)

        if not updates:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(updates.keys())
        ]
        query = f"UPDATE clinical_templates SET {', '.join(set_clauses)} WHERE id = ${len(updates)+1} RETURNING id;"
        values = list(updates.values()) + [temp_id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)

    # Dispositions
    @staticmethod
    async def create_disposition(disposition: Disposition) -> Optional[str]:
        query = """
        INSERT INTO dispositions (name, is_frequent, is_default)
        VALUES ($1, $2, $3)
        RETURNING id;
        """

        # Insert user and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                disposition.name,
                disposition.is_frequent,
                disposition.is_default,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def get_dispositions() -> List[Disposition]:
        query = """
        SELECT * FROM dispositions;
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(Disposition(**dict(row)))

        return result

    @staticmethod
    async def delete_disposition(name: str) -> bool:
        query = """DELETE FROM dispositions WHERE name=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, name)
            return bool(row)

    @staticmethod
    async def delete_disposition_by_id(id: int) -> bool:
        query = """DELETE FROM dispositions WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_disposition(
        id: int,
        updates: DispositionUpdate,
    ) -> bool:
        update = updates.model_dump(exclude_unset=True)

        if not update:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(update.keys())
        ]
        query = f"UPDATE dispositions SET {', '.join(set_clauses)} WHERE id = ${len(update)+1} RETURNING id;"
        values = list(update.values()) + [id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)

    # Dcoument type
    @staticmethod
    async def create_document_type(
        document_type: DocumentType,
    ) -> Optional[str]:
        query = """
        INSERT INTO document_types (name, is_frequent, is_default)
        VALUES ($1, $2, $3)
        RETURNING id;
        """

        # Insert user and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                document_type.name,
                document_type.is_frequent,
                document_type.is_default,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def get_document_types() -> List[Disposition]:
        query = """
        SELECT * FROM document_types;
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(DocumentType(**dict(row)))

        return result

    @staticmethod
    async def delete_document_type(name: str) -> bool:
        query = """DELETE FROM document_types WHERE name=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, name)
            return bool(row)

    @staticmethod
    async def delete_document_type_by_id(id: int) -> bool:
        query = """DELETE FROM document_types WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_document_type(
        id: int,
        updates: DocumentTypeUpdate,
    ) -> bool:
        update = updates.model_dump(exclude_unset=True)

        if not update:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(update.keys())
        ]
        query = f"UPDATE document_types SET {', '.join(set_clauses)} WHERE id = ${len(update)+1} RETURNING id;"
        values = list(update.values()) + [id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)

    # Referral Sites
    @staticmethod
    async def create_referral_site(
        referral_site: ReferralSite,
    ) -> Optional[int]:
        query = """
        INSERT INTO referral_sites (name, is_frequent, is_default)
        VALUES ($1, $2, $3)
        RETURNING id;
        """

        # Insert referral site and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                referral_site.name,
                referral_site.is_frequent,
                referral_site.is_default,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def get_referral_sites() -> List[ReferralSite]:
        query = """
        SELECT * FROM referral_sites;
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(ReferralSite(**dict(row)))

        return result

    @staticmethod
    async def delete_referral_site(name: str) -> bool:
        query = """DELETE FROM referral_sites WHERE name=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, name)
            return bool(row)

    @staticmethod
    async def delete_referral_site_by_id(id: int) -> bool:
        query = """DELETE FROM referral_sites WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_referral_site(
        id: int,
        updates: ReferralSiteUpdate,
    ) -> bool:
        update = updates.model_dump(exclude_unset=True)

        if not update:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(update.keys())
        ]
        query = f"UPDATE referral_sites SET {', '.join(set_clauses)} WHERE id = ${len(update)+1} RETURNING id;"
        values = list(update.values()) + [id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)

    # Medication
    @staticmethod
    async def create_medication(
        medication: Medication,
    ) -> Optional[int]:
        query = """
        INSERT INTO medication_templates (name, is_frequent, is_default)
        VALUES ($1, $2, $3)
        RETURNING id;
        """

        # Insert referral site and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                medication.name,
                medication.is_frequent,
                medication.is_default,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def get_medications() -> List[ReferralSite]:
        query = """
        SELECT * FROM medication_templates
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(Medication(**dict(row)))

        return result

    @staticmethod
    async def delete_medication(name: str) -> bool:
        query = (
            """DELETE FROM medication_templates WHERE name=$1 RETURNING id;"""
        )

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, name)
            return bool(row)

    @staticmethod
    async def delete_medication_by_id(id: int) -> bool:
        query = (
            """DELETE FROM medication_templates WHERE id=$1 RETURNING id;"""
        )

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_medication(
        id: int,
        updates: MedicationUpdate,
    ) -> bool:
        update = updates.model_dump(exclude_unset=True)

        if not update:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(update.keys())
        ]
        query = f"UPDATE medication_templates SET {', '.join(set_clauses)} WHERE id = ${len(update)+1} RETURNING id;"
        values = list(update.values()) + [id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)

    # Medication Outcome
    @staticmethod
    async def create_medication_outcome(
        medication: MedicationOutcome,
    ) -> Optional[int]:
        query = """
        INSERT INTO medication_outcomes (name, is_frequent, is_default)
        VALUES ($1, $2, $3)
        RETURNING id;
        """

        # Insert referral site and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                medication.name,
                medication.is_frequent,
                medication.is_default,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def get_medication_outcomes() -> List[ReferralSite]:
        query = """
        SELECT * FROM medication_outcomes;
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        if rows:
            for row in rows:
                result.append(MedicationOutcome(**dict(row)))

        return result

    @staticmethod
    async def delete_medication_outcome(name: str) -> bool:
        query = (
            """DELETE FROM medication_outcomes WHERE name=$1 RETURNING id;"""
        )

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, name)
            return bool(row)

    @staticmethod
    async def delete_medication_outcome_by_id(id: int) -> bool:
        query = """DELETE FROM medication_outcomes WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_medication_outcome(
        id: int,
        updates: MedicationOutcomeUpdate,
    ) -> bool:
        update = updates.model_dump(exclude_unset=True)

        if not update:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(update.keys())
        ]
        query = f"UPDATE medication_outcomes SET {', '.join(set_clauses)} WHERE id = ${len(update)+1} RETURNING id;"
        values = list(update.values()) + [id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)

    # general
    @staticmethod
    async def create_general_type(data: General) -> Optional[int]:
        query = """
        INSERT INTO general (name, is_frequent, is_default, type)
        VALUES ($1, $2, $3, $4)
        RETURNING id;
        """

        # Insert referral site and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                data.name,
                data.is_frequent,
                data.is_default,
                data.type,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def get_general(general_type: str) -> List[General]:
        query = """
        SELECT * 
        FROM general 
        WHERE type=$1;
        """

        async with database.get_connection() as conn:
            rows = await conn.fetch(query, general_type)

        result = []
        if rows:
            for row in rows:
                result.append(General(**dict(row)))

        return result

    @staticmethod
    async def delete_general(name: str, general_type: str) -> bool:
        query = """
            DELETE FROM general 
            WHERE name=$1
            AND type=$2
            RETURNING id;
            """

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, name, general_type)
            return bool(row)

    @staticmethod
    async def delete_general_by_id(id: int) -> bool:
        query = """
            DELETE FROM general 
            WHERE id=$1 
            RETURNING id;
            """

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)

    @staticmethod
    async def update_general(id: int, updates: GeneralUpdate) -> bool:
        update = updates.model_dump(exclude_unset=True)

        if not update:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(update.keys())
        ]
        query = f"UPDATE general SET {', '.join(set_clauses)} WHERE id = ${len(update)+1} RETURNING id;"
        values = list(update.values()) + [id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)
