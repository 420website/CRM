from typing import List, Optional
from asyncpg import UniqueViolationError
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
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
    AssessementUpdate,
    AssessmentCreate,
    AssessmentRead,
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
)
from app.registration.services import (
    ActivityService,
    AssessmentService,
    DispensingService,
    InteractionService,
    MedicationService,
    NoteService,
    PatientService,
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
    logger.info(
        f"Creating patient - Name: {data.first_name} {data.last_name}, DOB: {data.dob}, Force: {data.force_create}"
    )
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
    existing_user = await PatientService.check_identity(data)

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
    """Returns patients to the highest level of permission the user has."""
    if len(user.location_permissions) == 0:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User does not have access to any locations.",
        )
    else:
        if "All" in user.location_permissions:
            result = await PatientService.get_patients()
        else:
            result = await PatientService.get_patients_by_location(
                user.location_permissions
            )

    return result


@router.get("", response_model=List[PatientRead])
async def get_patients_by_location(
    locations: Optional[List[str]] = Query(None),
    user: UserRead = Depends(get_current_user),
):
    """Returns patients to the highest level of permission the user has."""
    if not locations or len(locations) == 0:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Atleast one location is required",
        )

    if len(user.location_permissions) == 0:
        logger.info(
            f"User {user.id} tried to access records without proper permissions."
        )
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User does not have access to any locations.",
        )
    else:
        if "All" in locations:
            if "All" not in user.location_permissions:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="User does not have access to all locations.",
                )
            else:
                result = await PatientService.get_patients()
        else:
            if "All" in user.location_permissions or all(
                l in user.location_permissions for l in locations
            ):
                result = await PatientService.get_patients_by_location(
                    locations=locations
                )
            else:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="User does not have access to all locations requested.",
                )

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
    logger.info(f"Deleting patient - ID: {id}")

    if not await PatientService.delete_patient_by_id(id):
        logger.info(f"Deleting patient Failed  ID {id}")

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
    logger.info(f"Deleting patient - Name: {first_name} {last_name}")

    if not await PatientService.delete_patient(first_name, last_name):
        logger.info(
            f"Deleting patient Failed - Name: {first_name} {last_name}"
        )

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
    logger.info(f"Updating patient - ID {id}")

    try:
        if not data.force_update:
            patient = await PatientService.get_patient_by_id(id)

            if not patient:
                logger.error(
                    "Failed to update patient - service returned None."
                )

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

        logger.info(f"Patient updated successfully ID: {id}")

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
    logger.info(f"Updating patient status: ID: {id} Status: {status}")

    patient = await PatientService.get_patient_by_id(id)
    if not patient:
        logger.error(f"Updating patient status failed: {id} patient not found")
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
        logger.error(f"Updating patient status failed: {id}")

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
            logger.info("Finalized patient email sent.")
        except Exception as e:
            logger.error(
                f"Failed to send finalization email for patient {id}: {e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error sending registration email.",
            )

    logger.info("Patient status updated successfully")

    return {"message": "Patient updated successfully."}


###############
# Assessements
###############
@router.post("/{patient_id}/assessment/")
async def create_assessment(
    patient_id: int,
    data: AssessmentCreate,
    user: UserRead = Depends(get_current_user),
):
    logger.info(f"Creating assessment for patient {patient_id}")
    try:
        # Ensure the patient_id in the URL matches the data
        if not await AssessmentService.create_assessment(patient_id, data):
            logger.error(
                f"Failed to create assessment for patient {patient_id}."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment not created.",
            )

        logger.info(
            f"Successfully created assessment for patient {patient_id}"
        )

        return {"message": "Assessment created successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error creating assessment. Error: {str(e)}",
            exc_info=True,
        )
        # Fallback for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assessment not created: {str(e)}",
        )


@router.get("/{patient_id}/assessments/", response_model=List[AssessmentRead])
async def get_assessments_by_patient(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await AssessmentService.get_assessment_by_patient(patient_id)
    return result


@router.get(
    "/{patient_id}/assessment/{assessment_id}",
    response_model=AssessmentRead,
)
async def get_assessment_by_id(
    patient_id: int,
    assessment_id: int,
    user: UserRead = Depends(get_current_user),
):
    result = await AssessmentService.get_assessment_by_id(assessment_id)

    if not result or result.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )
    return result


@router.delete("/{patient_id}/assessment/{assessment_id}")
async def delete_assessment_by_id(
    patient_id: int,
    assessment_id: int,
    user: UserRead = Depends(get_current_user),
):
    logger.info(
        f"Deleting assessment {assessment_id} for patient {patient_id}"
    )

    # Verify the test belongs to the patient before deleting
    test = await AssessmentService.get_assessment_by_id(assessment_id)
    if not test or test.patient_id != patient_id:
        logger.warning(
            f"Assessment {assessment_id} not found for patient {patient_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )

    if not await AssessmentService.delete_assessment_by_id(assessment_id):
        logger.error(f"Failed to delete assessment {assessment_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )

    logger.info(f"Assessment {assessment_id} deleted for patient {patient_id}")

    return {"message": "Assessment deleted successfully."}


@router.patch("/{patient_id}/assessment/{assessment_id}")
async def update_assessment(
    patient_id: int,
    assessment_id: int,
    data: AssessementUpdate,
    user: UserRead = Depends(get_current_user),
):
    logger.info(
        f"Updating assessment {assessment_id} for patient {patient_id}"
    )

    # Verify the test belongs to the patient before updating
    test = await AssessmentService.get_assessment_by_id(assessment_id)
    if not test or test.patient_id != patient_id:
        logger.warning(
            f"Assessment {assessment_id} not found for patient {patient_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )

    if not await AssessmentService.update_assessment(assessment_id, data):
        logger.error(f"Failed to update assessment {assessment_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found or could not be updated.",
        )

    logger.info(f"Assessment {assessment_id} update for patient {patient_id}")

    return {"message": "Assessment updated successfully."}


###############
# Note
###############
@router.post("/{patient_id}/notes/")
async def create_note(
    patient_id: int,
    data: NoteCreate,
    user: UserRead = Depends(get_current_user),
):
    logger.info(f"Creating note for patient {patient_id}")

    if not await NoteService.create_note(patient_id, data):
        logger.error(f"Failed to create note for patient {patient_id}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note not created.",
        )

    logger.info(f"Successfully created note for patient {patient_id}")

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
    logger.info(f"Deleting note {note_id} for patient {patient_id}")

    # Verify the note belongs to the patient before deleting
    note = await NoteService.get_note_by_id(note_id)
    if not note or note.patient_id != patient_id:
        logger.warning(f"Note {note_id} not found for patient {patient_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )

    if not await NoteService.delete_note_by_id(note_id):
        logger.error(f"Failed to delete note {note_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )

    logger.info(f"Note {note_id} deleted for patient {patient_id}")

    return {"message": "Note deleted successfully."}


@router.patch("/{patient_id}/notes/{note_id}")
async def update_note(
    patient_id: int,
    note_id: int,
    data: NoteUpdate,
    user: UserRead = Depends(get_current_user),
):
    logger.info(f"Updating note {note_id} for patient {patient_id}")

    # Verify the note belongs to the patient before updating
    note = await NoteService.get_note_by_id(note_id)

    if not note or note.patient_id != patient_id:
        logger.warning(f"Note {note_id} not found for patient {patient_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )

    if not await NoteService.update_note(note_id, data):
        logger.error(f"Failed to update note {note_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or could not be updated.",
        )

    logger.info(f"Note {note_id} update for patient {patient_id}")

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
    logger.info(f"Creating activity for patient {patient_id}")

    if not await ActivityService.create_activity(patient_id, data):
        logger.error(f"Failed to create activity for patient {patient_id}.")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activity not created.",
        )

    logger.info(f"Successfully created activity for patient {patient_id}")

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
    logger.info(f"Deleting activity {activity_id} for patient {patient_id}")

    # Verify the activity belongs to the patient before deleting
    activity = await ActivityService.get_activities_by_id(activity_id)
    if not activity or activity.patient_id != patient_id:
        logger.warning(
            f"Activity {activity_id} not found for patient {patient_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    if not await ActivityService.delete_activity_by_id(activity_id):
        logger.error(f"Failed to delete activity {activity_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    logger.info(f"Activity {activity_id} deleted for patient {patient_id}")

    return {"message": "Activity deleted successfully."}


@router.patch("/{patient_id}/activities/{activity_id}")
async def update_activity(
    patient_id: int,
    activity_id: int,
    data: ActivityUpdate,
    user: UserRead = Depends(get_current_user),
):
    logger.info(f"Updating activity {activity_id} for patient {patient_id}")

    # Verify the activity belongs to the patient before updating
    activity = await ActivityService.get_activities_by_id(activity_id)

    if not activity or activity.patient_id != patient_id:
        logger.warning(
            f"Activity {activity_id} not found for patient {patient_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    if not await ActivityService.update_activity(activity_id, data):
        logger.error(f"Failed to update activity {activity_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found or could not be updated.",
        )

    logger.info(f"Activity {activity_id} update for patient {patient_id}")

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
    logger.info(f"Creating dispensing for patient {patient_id}")

    if not await DispensingService.check_medication(
        patient_id, data.medication
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medication none existant for client please create medication and retry.",
        )

    if not await DispensingService.create_dispensing(patient_id, data):
        logger.error(f"Failed to create dispensing for patient {patient_id}.")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispensing not created.",
        )

    logger.info(f"Successfully created dispensing for patient {patient_id}")

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
    logger.info(
        f"Deleting dispensing {dispensing_id} for patient {patient_id}"
    )

    # Verify the dispensing belongs to the patient before deleting
    dispensing = await DispensingService.get_dispensing_by_id(dispensing_id)
    if not dispensing or dispensing.patient_id != patient_id:
        logger.warning(
            f"Dispensing {dispensing_id} not found for patient {patient_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispensing not found.",
        )
    if not await DispensingService.delete_dispensing_by_id(dispensing_id):
        logger.error(f"Failed to delete dispensing {dispensing_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispensing not found.",
        )

    logger.info(f"Dispensing {dispensing_id} deleted for patient {patient_id}")

    return {"message": "Dispensing deleted successfully."}


@router.patch("/{patient_id}/dispensings/{dispensing_id}")
async def update_dispensing(
    patient_id: int,
    dispensing_id: int,
    data: DispensingUpdate,
    user: UserRead = Depends(get_current_user),
):
    logger.info(
        f"Updating dispensing {dispensing_id} for patient {patient_id}"
    )

    if not await DispensingService.check_medication(
        patient_id, data.medication
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medication none existant for client please create medication and retry.",
        )

    # Verify the dispensing belongs to the patient before updating
    dispensing = await DispensingService.get_dispensing_by_id(dispensing_id)
    if not dispensing or dispensing.patient_id != patient_id:
        logger.warning(
            f"Dispensingt {dispensing_id} not found for patient {patient_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispensing not found.",
        )

    if not await DispensingService.update_dispensing(dispensing_id, data):
        logger.error(f"Failed to update dispensing {dispensing_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispensing not found or could not be updated.",
        )

    logger.info(f"Dispensing {dispensing_id} update for patient {patient_id}")

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
    logger.info(f"Creating medication for patient {patient_id}")

    if not await MedicationService.create_medication(patient_id, data):
        logger.error(f"Failed to create medication for patient {patient_id}.")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medication not created.",
        )

    logger.info(f"Successfully created medication for patient {patient_id}")

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

    logger.info(
        f"Deleting medication {medication_id} for patient {patient_id}"
    )

    # Verify the medication belongs to the patient before deleting
    medication = await MedicationService.get_medications_by_id(medication_id)

    if not medication or medication.patient_id != patient_id:
        logger.warning(
            f"Medication {medication_id} not found for patient {patient_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found.",
        )

    if not await MedicationService.delete_medication_by_id(medication_id):
        logger.error(f"Failed to delete medication {medication_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found.",
        )

    logger.info(
        f"Medicationt {medication_id} deleted for patient {patient_id}"
    )

    return {"message": "Medication deleted successfully."}


@router.patch("/{patient_id}/medications/{medication_id}")
async def update_medication(
    patient_id: int,
    medication_id: int,
    data: MedicationUpdate,
    user: UserRead = Depends(get_current_user),
):
    logger.info(
        f"Updating medication {medication_id} for patient {patient_id}"
    )

    # Verify the medication belongs to the patient before updating
    medication = await MedicationService.get_medications_by_id(medication_id)
    if not medication or medication.patient_id != patient_id:
        logger.warning(
            f"Medication {medication_id} not found for patient {patient_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found.",
        )

    if not await MedicationService.update_medication(medication_id, data):
        logger.error(f"Failed to update medication {medication_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found or could not be updated.",
        )

    logger.info(f"Medication {medication_id} update for patient {patient_id}")

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
    logger.info(f"Creating interaction for patient {patient_id}")

    if not await InteractionService.create_interaction(patient_id, data):
        logger.error(f"Failed to create interaction for patient {patient_id}.")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interaction not created.",
        )

    logger.info(f"Successfully created interaction for patient {patient_id}")

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
    logger.info(
        f"Deleting interaction {interaction_id} for patient {patient_id}"
    )

    # Verify the interaction belongs to the patient before deleting
    interaction = await InteractionService.get_interactions_by_id(
        interaction_id
    )
    if not interaction or interaction.patient_id != patient_id:
        logger.warning(
            f"Interaction {interaction_id} not found for patient {patient_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found.",
        )

    if not await InteractionService.delete_interaction_by_id(interaction_id):
        logger.error(f"Failed to delete interaction {interaction_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found.",
        )

    logger.info(
        f"Interaction {interaction_id} deleted for patient {patient_id}"
    )

    return {"message": "Interaction deleted successfully."}


@router.patch("/{patient_id}/interactions/{interaction_id}")
async def update_interaction(
    patient_id: int,
    interaction_id: int,
    data: InteractionUpdate,
    user: UserRead = Depends(get_current_user),
):
    logger.info(
        f"Updating interaction {interaction_id} for patient {patient_id}"
    )

    # Verify the interaction belongs to the patient before updating
    interaction = await InteractionService.get_interactions_by_id(
        interaction_id
    )
    if not interaction or interaction.patient_id != patient_id:
        logger.warning(
            f"Interaction {interaction_id} not found for patient {patient_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found.",
        )

    if not await InteractionService.update_interaction(interaction_id, data):
        logger.error(f"Failed to update interaction {interaction_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found or could not be updated.",
        )

    logger.info(
        f"Interaction {interaction_id} update for patient {patient_id}"
    )

    return {"message": "Interaction updated successfully."}
