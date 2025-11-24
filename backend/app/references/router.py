# app/auth/router.py
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from app.authentication.schemas import UserRead
from app.dependencies import get_current_user
from app.references.schemas import (
    ReferenceOption,
    ReferenceOptionUpdate,
    ReferenceTemplate,
    ReferenceTemplateUpdate,
)
from app.references.services import (
    ReferenceOptionService,
    ReferenceTemplateService,
)

router = APIRouter(prefix="/reference-data", tags=["References"])


####################
# Options
####################
@router.post("/option")
async def create_option_type(
    data: ReferenceOption,
    user: UserRead = Depends(get_current_user),
):

    if await ReferenceOptionService.check_exists(data.name, data.type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Option already exists.",
        )

    if not await ReferenceOptionService.create_option(data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Option not created.",
        )
    return {"message": "Option created successfully."}


@router.get("/option/{option_type}", response_model=List[ReferenceOption])
async def get_option_type(
    option_type: str,
    user: UserRead = Depends(get_current_user),
):
    result = await ReferenceOptionService.get_options(option_type)
    return result


@router.delete("/option/{id}")
async def delete_option_id(
    id: int,
    user: UserRead = Depends(get_current_user),
):
    if not await ReferenceOptionService.delete_option_by_id(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option not found.",
        )

    return {"message": "Option deleted successfully."}


@router.delete("/option/{option_type}/{name}")
async def delete_option_name(
    option_type: str,
    name: str,
    user: UserRead = Depends(get_current_user),
):
    if not await ReferenceOptionService.delete_option(name, option_type):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option not found.",
        )
    return {"message": "Option deleted successfully."}


@router.patch("/option/{id}")
async def update_option(
    id: int,
    data: ReferenceOptionUpdate,
    user: UserRead = Depends(get_current_user),
):
    if not await ReferenceOptionService.update_option(id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option not found or could not be updated.",
        )

    return {"message": "Option updated successfully."}


###############
# Templates
###############
@router.post("/template")
async def create_template(
    data: ReferenceTemplate,
    user: UserRead = Depends(get_current_user),
):

    if await ReferenceTemplateService.check_exists(data.name, data.type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template already exists.",
        )

    if not await ReferenceTemplateService.create_template(data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template not created.",
        )

    return {"message": "Template created successfully."}


@router.get(
    "/template/{template_type}", response_model=List[ReferenceTemplate]
)
async def get_templates(
    template_type: str,
    user: UserRead = Depends(get_current_user),
):
    result = await ReferenceTemplateService.get_templates(template_type)

    return result


@router.delete("/template/{id}")
async def delete_template_id(
    id: int,
    user: UserRead = Depends(get_current_user),
):
    if not await ReferenceTemplateService.delete_template_by_id(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found.",
        )

    return {"message": "Template deleted successfully."}


@router.delete("/template/{template_type}/{name}")
async def delete_template_name(
    template_type: str,
    name: str,
    user: UserRead = Depends(get_current_user),
):
    if not await ReferenceTemplateService.delete_template(name, template_type):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found.",
        )

    return {"message": "Template deleted successfully."}


@router.patch("/template/{id}")
async def update_template(
    id: int,
    data: ReferenceTemplateUpdate,
    user: UserRead = Depends(get_current_user),
):

    if not await ReferenceTemplateService.update_template(id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or could not be updated.",
        )

    return {"message": "Template updated successfully."}
