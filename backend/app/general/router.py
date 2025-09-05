# app/auth/router.py
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from app.authentication.schemas import UserRead
from app.general.services import GeneralService
from app.dependencies import get_current_user
from app.general.schemas import (
    ClinicalTemplate,
    ClinicalTemplateUpdate,
    Disposition,
    DispositionUpdate,
    NotesTemplate,
    NotesTemplateUpdate,
    ReferralSite,
    ReferralSiteUpdate,
)

router = APIRouter(prefix="/general", tags=["General"])


###############
# Note Template
###############
@router.post("/note-template")
async def create_note_template(
    data: NotesTemplate,
    user: UserRead = Depends(get_current_user),
):
    if await GeneralService.check_exists(data.name, "note_templates"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template already exists.",
        )

    if not await GeneralService.create_notes_template(data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notes template not created.",
        )

    return {"message": "Notes template created successfully."}


@router.get("/note-template", response_model=List[NotesTemplate])
async def get_note_templates(user: UserRead = Depends(get_current_user)):
    result = await GeneralService.get_note_templates()

    return result


@router.delete("/note-template/{id}")
async def delete_note_template_id(
    id: int,
    user: UserRead = Depends(get_current_user),
):
    if not await GeneralService.delete_notes_template_by_id(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notes template not found.",
        )
    return {"message": "Notes template deleted successfully."}


@router.delete("/note-template/by-name/{name}")
async def delete_note_template_name(
    name: str,
    user: UserRead = Depends(get_current_user),
):
    if not await GeneralService.delete_notes_template(name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notes template not found.",
        )
    return {"message": "Notes template deleted successfully."}


@router.patch("/note-template/{id}")
async def update_note_template(
    id: int,
    data: NotesTemplateUpdate,
    user: UserRead = Depends(get_current_user),
):

    if not await GeneralService.update_notes_template(id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notes template not found or could not be updated.",
        )

    return {"message": "Notes template updated successfully."}


##############
# Clincal Template
###############
@router.post("/clinical-template")
async def create_clinical_template(
    data: ClinicalTemplate,
    user: UserRead = Depends(get_current_user),
):

    if await GeneralService.check_exists(data.name, "clinical_templates"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template already exists.",
        )

    if not await GeneralService.create_clinical_template(data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clinical template not created.",
        )

    return {"message": "Clinical template created successfully."}


@router.get("/clinical-template", response_model=List[ClinicalTemplate])
async def get_clinical_templates(user: UserRead = Depends(get_current_user)):
    result = await GeneralService.get_clinical_templates()

    return result


@router.delete("/clinical-template/{id}")
async def delete_clinical_template_id(
    id: int,
    user: UserRead = Depends(get_current_user),
):
    if not await GeneralService.delete_clinical_template_by_id(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical template not found.",
        )
    return {"message": "Clinical template deleted successfully."}


@router.delete("/clinical-template/by-name/{name}")
async def delete_clinical_template_name(
    name: str,
    user: UserRead = Depends(get_current_user),
):
    if not await GeneralService.delete_clinical_template(name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical template not found.",
        )
    return {"message": "Clinical template deleted successfully."}


@router.patch("/clinical-template/{id}")
async def update_clinical_template(
    id: int,
    data: ClinicalTemplateUpdate,
    user: UserRead = Depends(get_current_user),
):

    if not await GeneralService.update_clinical_template(id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical template not found or could not be updated.",
        )

    return {"message": "Clinical template updated successfully."}


##############
# Disposition
###############
@router.post("/disposition")
async def create_disposition(
    data: Disposition,
    user: UserRead = Depends(get_current_user),
):

    if await GeneralService.check_exists(data.name, "dispositions"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Disposition already exists.",
        )

    if not await GeneralService.create_disposition(data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Disposition not created.",
        )
    return {"message": "Disposition created successfully."}


@router.get("/disposition", response_model=List[Disposition])
async def get_dispositions(user: UserRead = Depends(get_current_user)):
    result = await GeneralService.get_dispositions()
    return result


@router.delete("/disposition/{id}")
async def delete_disposition_id(
    id: int,
    user: UserRead = Depends(get_current_user),
):
    if not await GeneralService.delete_disposition_by_id(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disposition not found.",
        )
    return {"message": "Disposition deleted successfully."}


@router.delete("/disposition/by-name/{name}")
async def delete_disposition_name(
    name: str,
    user: UserRead = Depends(get_current_user),
):
    if not await GeneralService.delete_disposition(name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disposition not found.",
        )
    return {"message": "Disposition deleted successfully."}


@router.patch("/disposition/{id}")
async def update_disposition(
    id: int,
    data: DispositionUpdate,
    user: UserRead = Depends(get_current_user),
):
    if not await GeneralService.update_disposition(id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disposition not found or could not be updated.",
        )
    return {"message": "Disposition updated successfully."}


##############
# Referral Site
###############
@router.post("/referral-site")
async def create_referral_site(
    data: ReferralSite,
    user: UserRead = Depends(get_current_user),
):

    if await GeneralService.check_exists(data.name, "referral_sites"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Referral site already exists.",
        )

    if not await GeneralService.create_referral_site(data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Referral site not created.",
        )
    return {"message": "Referral site created successfully."}


@router.get("/referral-site", response_model=List[ReferralSite])
async def get_referral_sites(user: UserRead = Depends(get_current_user)):
    result = await GeneralService.get_referral_sites()
    return result


@router.delete("/referral-site/{id}")
async def delete_referral_site_id(
    id: int,
    user: UserRead = Depends(get_current_user),
):
    if not await GeneralService.delete_referral_site_by_id(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral site not found.",
        )
    return {"message": "Referral site deleted successfully."}


@router.delete("/referral-site/by-name/{name}")
async def delete_referral_site_name(
    name: str,
    user: UserRead = Depends(get_current_user),
):
    if not await GeneralService.delete_referral_site(name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral site not found.",
        )
    return {"message": "Referral site deleted successfully."}


@router.patch("/referral-site/{id}")
async def update_referral_site(
    id: int,
    data: ReferralSiteUpdate,
    user: UserRead = Depends(get_current_user),
):
    if not await GeneralService.update_referral_site(id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral site not found or could not be updated.",
        )
    return {"message": "Referral site updated successfully."}
