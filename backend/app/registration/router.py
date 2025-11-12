from typing import List
from asyncpg import UniqueViolationError
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from app.logger import logger
from app.authentication.schemas import UserRead
from app.email.messages import FinalizedEmailMessage
from app.email.service import EmailService
from app.config import settings
from app.objects.services import ObjectService, PhotoService
from app.registration.schemas import (
    ActivityCreate,
    ActivityRead,
    ActivityUpdate,
    DispensingCreate,
    DispensingRead,
    DispensingUpdate,
    HealthcardCheck,
    IdentityCheck,
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
    PatientCreate,
    PatientRead,
    PatientStatus,
    PatientUpdate,
    TestCreate,
    TestRead,
    TestUpdate,
)
from app.registration.services import (
    ActivityService,
    DispensingService,
    InteractionService,
    MedicationService,
    NoteService,
    PatientService,
    TestService,
)
from app.dependencies import get_current_user


router = APIRouter(prefix="/patients", tags=["Patients"])


###################
# Patients Template
###################
@router.post("")
async def create_patient(
    data: PatientCreate,
    user: UserRead = Depends(get_current_user),
):
    try:
        if not data.force_create:
            if await PatientService.get_patient_by_name_dob(
                data.first_name, data.last_name, data.dob
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Patient with that name and dob already exists.",
                )

        id = await PatientService.create_patient(data)

        if not id:
            logger.error("Failed to create patient - service returned None.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient not created.",
            )
        logger.info(f"Patient created successfully ID: {id}")
        return {"patient_id": id}

    except UniqueViolationError:
        # Example: health card must be unique
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Health card already exists.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error creating patient. Error: {str(e)}",
            exc_info=True,
        )
        # Fallback for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.post("/identity/verify")
async def check_name_dob(
    data: IdentityCheck,
    user: UserRead = Depends(get_current_user),
):
    exists = await PatientService.check_identity(data)

    if exists:
        return {"exists": True}

    return {"exists": False}


@router.post("/healthcard/verify")
async def check_healthcard(
    data: HealthcardCheck,
    user: UserRead = Depends(get_current_user),
):
    existing_user = await PatientService.check_healthcard(data)

    if existing_user:
        return {
            "exists": True,
            "user": {
                "id": existing_user.id,
                "first_name": existing_user.first_name,
                "last_name": existing_user.last_name,
            },
        }

    return {"exists": False}


@router.get("", response_model=List[PatientRead])
async def get_patients(user: UserRead = Depends(get_current_user)):
    result = await PatientService.get_patients()
    return result


@router.get("/{id}", response_model=PatientRead)
async def get_patient(id: int, user: UserRead = Depends(get_current_user)):
    result = await PatientService.get_patient_by_id(id)
    return result


@router.delete("/{id}")
async def delete_patient_by_id(
    id: int,
    user: UserRead = Depends(get_current_user),
):

    if not await PatientService.delete_patient_by_id(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # Fail quietly if objects don't exist
    for bucket in ["photos", "attachments"]:
        try:
            await ObjectService.delete_objects(bucket, str(id))
        except Exception as e:
            logger.warning(
                f"Failed to delete objects from {bucket} for patient {id}: {e}"
            )

    return {"message": "Patient deleted successfully."}


@router.delete("/by-name/{first_name}/{last_name}")
async def delete_patient_by_name(
    first_name: str,
    last_name: str,
    user: UserRead = Depends(get_current_user),
):

    if not await PatientService.delete_patient(first_name, last_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    return {"message": "Patient deleted successfully."}


@router.patch("/{id}")
async def update_patient(
    id: int,
    data: PatientUpdate,
    user: UserRead = Depends(get_current_user),
):

    try:
        if not data.force_update:
            patient = await PatientService.get_patient_by_id(id)

            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found or could not be updated.",
                )

            # Update any null values with the current values
            first_name = data.first_name or patient.first_name
            last_name = data.last_name or patient.last_name
            dob = data.dob or patient.dob

            if await PatientService.get_other_patient_name_dob(
                id,
                first_name,
                last_name,
                dob,
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Patient with that name and dob already exists.",
                )
        if not await PatientService.update_patient(id, data):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or could not be updated.",
            )
        return {"message": "Patient updated successfully."}

    except UniqueViolationError:
        # Example: health card must be unique
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Health card already exists.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error updating patient {id}: {e}", exc_info=True
        )
        # Fallback for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.patch("/{id}/status")
async def update_patient_status(
    id: int,
    data: PatientStatus,
    user: UserRead = Depends(get_current_user),
):
    patient = await PatientService.get_patient_by_id(id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found."
        )

    if patient.status == data.status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient status already {data.status}.",
        )

    if not await PatientService.update_patient_status(
        id, data.status, patient.finalized_at is None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient could not be updated.",
        )

    if data.status == "finalized":
        try:
            subject = (
                f"New Registration - {patient.first_name} {patient.last_name}"
            )

            email = (
                EmailService()
                .recipient(settings.support_email)
                .subject(subject)
                .body(FinalizedEmailMessage(patient.model_dump()))
            )

            photo_key = await PhotoService.get_patient_photo_key(id)
            if photo_key:
                await email.attach("photos", photo_key)

            email.send()
        except Exception as e:
            logger.error(
                f"Failed to send finalization email for patient {id}: {e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error sending registration email.",
            )
    return {"message": "Patient updated successfully."}


###############
# Test
###############
@router.post("/{patient_id}/tests/")
async def create_test(
    patient_id: int,
    data: TestCreate,
    user: UserRead = Depends(get_current_user),
):
    # Ensure the patient_id in the URL matches the data
    if not await TestService.create_test(patient_id, data):
        logger.error(f"Failed to create test for patient {patient_id}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test not created.",
        )

    return {"message": "Test created successfully."}


@router.get("/{patient_id}/tests/", response_model=List[TestRead])
async def get_tests_by_patient(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await TestService.get_tests_by_patient(patient_id)
    return result


@router.get("/{patient_id}/tests/{test_id}", response_model=TestRead)
async def get_test_by_id(
    patient_id: int,
    test_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await TestService.get_test_by_id(test_id)

    if not result or result.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found.",
        )
    return result


@router.delete("/{patient_id}/tests/{test_id}")
async def delete_test_by_id(
    patient_id: int,
    test_id: int,
    user: UserRead = Depends(get_current_user),
):
    # Verify the test belongs to the patient before deleting
    test = await TestService.get_test_by_id(test_id)
    if not test or test.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found.",
        )

    if not await TestService.delete_test_by_id(test_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found.",
        )
    return {"message": "Test deleted successfully."}


@router.patch("/{patient_id}/tests/{test_id}")
async def update_test(
    patient_id: int,
    test_id: int,
    data: TestUpdate,
    user: UserRead = Depends(get_current_user),
):
    # Verify the test belongs to the patient before updating
    test = await TestService.get_test_by_id(test_id)
    if not test or test.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found.",
        )

    if not await TestService.update_test(test_id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found or could not be updated.",
        )
    return {"message": "Test updated successfully."}


###############
# Note
###############
@router.post("/{patient_id}/notes/")
async def create_note(
    patient_id: int,
    data: NoteCreate,
    user: UserRead = Depends(get_current_user),
):

    if not await NoteService.create_note(patient_id, data):
        logger.error(f"Failed to create note for patient {patient_id}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note not created.",
        )
    return {"message": "Note created successfully."}


@router.get("/{patient_id}/notes/", response_model=List[NoteRead])
async def get_notes_by_patient(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await NoteService.get_notes_by_patient(patient_id)
    return result


@router.get("/{patient_id}/notes/{note_id}", response_model=NoteRead)
async def get_note_by_id(
    patient_id: int,
    note_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await NoteService.get_note_by_id(note_id)
    if not result or result.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )
    return result


@router.delete("/{patient_id}/notes/{note_id}")
async def delete_note_by_id(
    patient_id: int,
    note_id: int,
    user: UserRead = Depends(get_current_user),
):
    # Verify the note belongs to the patient before deleting
    note = await NoteService.get_note_by_id(note_id)
    if not note or note.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )
    if not await NoteService.delete_note_by_id(note_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )
    return {"message": "Note deleted successfully."}


@router.patch("/{patient_id}/notes/{note_id}")
async def update_note(
    patient_id: int,
    note_id: int,
    data: NoteUpdate,
    user: UserRead = Depends(get_current_user),
):
    # Verify the note belongs to the patient before updating
    note = await NoteService.get_note_by_id(note_id)

    if not note or note.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )
    if not await NoteService.update_note(note_id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or could not be updated.",
        )
    return {"message": "Note updated successfully."}


###############
# Activity
###############
@router.post("/{patient_id}/activities/")
async def create_activity(
    patient_id: int,
    data: ActivityCreate,
    user: UserRead = Depends(get_current_user),
):
    if not await ActivityService.create_activity(patient_id, data):
        logger.error(f"Failed to create activity for patient {patient_id}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activity not created.",
        )
    return {"message": "Activity created successfully."}


@router.get("/{patient_id}/activities/", response_model=List[ActivityRead])
async def get_activities_by_patient(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await ActivityService.get_activities_by_patient(patient_id)
    return result


@router.get("/activities/", response_model=List[PatientActivity])
async def get_activities(
    user: UserRead = Depends(get_current_user),
):
    result = await ActivityService.get_patient_activities()
    return result


@router.get(
    "/{patient_id}/activities/{activity_id}", response_model=ActivityRead
)
async def get_activity_by_id(
    patient_id: int,
    activity_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await ActivityService.get_activities_by_id(activity_id)
    if not result or result.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )
    return result


@router.delete("/{patient_id}/activities/{activity_id}")
async def delete_activity_by_id(
    patient_id: int,
    activity_id: int,
    user: UserRead = Depends(get_current_user),
):
    # Verify the activity belongs to the patient before deleting
    activity = await ActivityService.get_activities_by_id(activity_id)
    if not activity or activity.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )
    if not await ActivityService.delete_activity_by_id(activity_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )
    return {"message": "Activity deleted successfully."}


@router.patch("/{patient_id}/activities/{activity_id}")
async def update_activity(
    patient_id: int,
    activity_id: int,
    data: ActivityUpdate,
    user: UserRead = Depends(get_current_user),
):
    # Verify the activity belongs to the patient before updating
    activity = await ActivityService.get_activities_by_id(activity_id)

    if not activity or activity.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )
    if not await ActivityService.update_activity(activity_id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found or could not be updated.",
        )
    return {"message": "Activity updated successfully."}


###############
# Dispensing
###############
@router.post("/{patient_id}/dispensings/")
async def create_dispensing(
    patient_id: int,
    data: DispensingCreate,
    user: UserRead = Depends(get_current_user),
):
    if not await DispensingService.check_medication(
        patient_id, data.medication
    ):
        logger.error(f"Failed to create dispensing for patient {patient_id}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medication none existant for client please create medication and retry.",
        )

    if not await DispensingService.create_dispensing(patient_id, data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispensing not created.",
        )

    return {"message": "Dispensing created successfully."}


@router.get("/{patient_id}/dispensings/", response_model=List[DispensingRead])
async def get_dispensings_by_patient(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await DispensingService.get_dispensing_by_patient(patient_id)
    return result


@router.get(
    "/{patient_id}/dispensings/{dispensing_id}", response_model=DispensingRead
)
async def get_dispensing_by_id(
    patient_id: int,
    dispensing_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await DispensingService.get_dispensing_by_id(dispensing_id)
    if not result or result.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispensing not found.",
        )
    return result


@router.delete("/{patient_id}/dispensings/{dispensing_id}")
async def delete_dispensing_by_id(
    patient_id: int,
    dispensing_id: int,
    user: UserRead = Depends(get_current_user),
):
    # Verify the dispensing belongs to the patient before deleting
    dispensing = await DispensingService.get_dispensing_by_id(dispensing_id)
    if not dispensing or dispensing.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispensing not found.",
        )
    if not await DispensingService.delete_dispensing_by_id(dispensing_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispensing not found.",
        )
    return {"message": "Dispensing deleted successfully."}


@router.patch("/{patient_id}/dispensings/{dispensing_id}")
async def update_dispensing(
    patient_id: int,
    dispensing_id: int,
    data: DispensingUpdate,
    user: UserRead = Depends(get_current_user),
):
    # Verify the dispensing belongs to the patient before updating
    dispensing = await DispensingService.get_dispensing_by_id(dispensing_id)
    if not dispensing or dispensing.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispensing not found.",
        )
    if not await DispensingService.update_dispensing(dispensing_id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispensing not found or could not be updated.",
        )
    return {"message": "Dispensing updated successfully."}


###############
# Medication
###############
@router.post("/{patient_id}/medications/")
async def create_medication(
    patient_id: int,
    data: MedicationCreate,
    user: UserRead = Depends(get_current_user),
):
    if not await MedicationService.create_medication(patient_id, data):
        logger.error(f"Failed to create medication for patient {patient_id}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medication not created.",
        )

    return {"message": "Medication created successfully."}


@router.get("/{patient_id}/medications/", response_model=List[MedicationRead])
async def get_medications_by_patient(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await MedicationService.get_medications_by_patient(patient_id)
    return result


@router.get(
    "/{patient_id}/medications/{medication_id}", response_model=MedicationRead
)
async def get_medication_by_id(
    patient_id: int,
    medication_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await MedicationService.get_medications_by_id(medication_id)
    if not result or result.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found.",
        )
    return result


@router.delete("/{patient_id}/medications/{medication_id}")
async def delete_medication_by_id(
    patient_id: int,
    medication_id: int,
    user: UserRead = Depends(get_current_user),
):
    # Verify the medication belongs to the patient before deleting
    medication = await MedicationService.get_medications_by_id(medication_id)

    if not medication or medication.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found.",
        )
    if not await MedicationService.delete_medication_by_id(medication_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found.",
        )
    return {"message": "Medication deleted successfully."}


@router.patch("/{patient_id}/medications/{medication_id}")
async def update_medication(
    patient_id: int,
    medication_id: int,
    data: MedicationUpdate,
    user: UserRead = Depends(get_current_user),
):
    # Verify the medication belongs to the patient before updating
    medication = await MedicationService.get_medications_by_id(medication_id)
    if not medication or medication.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found.",
        )
    if not await MedicationService.update_medication(medication_id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found or could not be updated.",
        )
    return {"message": "Medication updated successfully."}


###############
# Interaction
###############
@router.post("/{patient_id}/interactions/")
async def create_interaction(
    patient_id: int,
    data: InteractionCreate,
    user: UserRead = Depends(get_current_user),
):
    if not await InteractionService.create_interaction(patient_id, data):
        logger.error(f"Failed to create interaction for patient {patient_id}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interaction not created.",
        )

    return {"message": "Interaction created successfully."}


@router.get(
    "/{patient_id}/interactions/", response_model=List[InteractionRead]
)
async def get_interactions_by_patient(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await InteractionService.get_interactions_by_patient(patient_id)
    return result


@router.get(
    "/{patient_id}/interactions/{interaction_id}",
    response_model=InteractionRead,
)
async def get_interaction_by_id(
    patient_id: int,
    interaction_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await InteractionService.get_interactions_by_id(interaction_id)
    if not result or result.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found.",
        )
    return result


@router.delete("/{patient_id}/interactions/{interaction_id}")
async def delete_interaction_by_id(
    patient_id: int,
    interaction_id: int,
    user: UserRead = Depends(get_current_user),
):
    # Verify the interaction belongs to the patient before deleting
    interaction = await InteractionService.get_interactions_by_id(
        interaction_id
    )
    if not interaction or interaction.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found.",
        )
    if not await InteractionService.delete_interaction_by_id(interaction_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found.",
        )
    return {"message": "Interaction deleted successfully."}


@router.patch("/{patient_id}/interactions/{interaction_id}")
async def update_interaction(
    patient_id: int,
    interaction_id: int,
    data: InteractionUpdate,
    user: UserRead = Depends(get_current_user),
):
    # Verify the interaction belongs to the patient before updating
    interaction = await InteractionService.get_interactions_by_id(
        interaction_id
    )
    if not interaction or interaction.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found.",
        )
    if not await InteractionService.update_interaction(interaction_id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found or could not be updated.",
        )
    return {"message": "Interaction updated successfully."}
