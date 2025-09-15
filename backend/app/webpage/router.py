from asyncpg.exceptions import UniqueViolationError
from app.webpage.services import ContactService, RegisterService
from fastapi import (
    APIRouter,
    HTTPException,
    status,
)
from app.webpage.schema import (
    ContactMessageCreate,
    RegistrationMessageCreate,
)
from app.webpage.utils import send_contact_email, send_registration_email

router = APIRouter(prefix="/my420", tags=["Webpage"])


@router.post("/contact", response_model=dict)
async def submit_contact_message(message: ContactMessageCreate):

    id = await ContactService.create_contact_message(message)

    if not id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact message not created.",
        )

    # Send contact email to support team
    send_contact_email(message.model_dump())

    return {
        "message": "Contact successful sent.",
        "contact_id": id,
        "status": "pending",
    }


@router.delete("/contact/{contact_id}", response_model=dict)
async def delete_contact_message(contact_id: int):
    deleted = await ContactService.delete_contact_message(contact_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact message with id {contact_id} not found.",
        )
    return {
        "message": "Contact message deleted successfully.",
        "contact_id": contact_id,
    }


@router.post("/register", response_model=dict)
async def register_for_testing(registration: RegistrationMessageCreate):
    try:

        id = await RegisterService.create_register_message(registration)

        if not id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Register message not created.",
            )

        send_registration_email(registration.model_dump())
        return {
            "message": "Registration successful",
            "registration_id": id,
            "status": "pending",
        }
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Health card number {registration.health_card_number} already registered.",
        )
    except Exception as e:
        # Catch any other exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.delete("/register/{registration_id}", response_model=dict)
async def delete_registration_message(registration_id: int):
    deleted = await RegisterService.delete_register_message(registration_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration message with id {registration_id} not found.",
        )
    return {
        "message": "Registration message deleted successfully.",
        "registration_id": registration_id,
    }
