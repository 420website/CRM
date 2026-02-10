# app/auth/router.py
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from app.core.authentication.schemas import UserRead
from app.common.dependencies import get_current_user
from app.common.exceptions import DuplicateError, NotFoundError
from app.core.references.schemas import (
    ReferenceOption,
    ReferenceOptionUpdate,
    ReferenceTemplate,
    ReferenceTemplateUpdate,
)
from app.core.references.services import (
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
    _: UserRead = Depends(get_current_user),
):

    try:
        if await ReferenceOptionService.check_exists(
            data.name, data.type, data.custom_fields
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Option already exists.",
            )
        if not await ReferenceOptionService.create_option(data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Option not created.",
            )
        return {"message": "Option created successfully."}
    except HTTPException:
        raise
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/option/{option_type}", response_model=List[ReferenceOption])
async def get_option_type(
    option_type: str,
    _: UserRead = Depends(get_current_user),
):
    result = await ReferenceOptionService.get_options(option_type)
    return result


@router.delete("/option/{id}")
async def delete_option_id(
    id: int,
    _: UserRead = Depends(get_current_user),
):
    if not await ReferenceOptionService.delete_option_by_id(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option not found.",
        )

    return {"message": "Option deleted successfully."}


@router.patch("/option/{id}")
async def update_option(
    id: int,
    data: ReferenceOptionUpdate,
    _: UserRead = Depends(get_current_user),
):
    try:
        await ReferenceOptionService.update_option(id, data)
        return {"message": "Option updated successfully."}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


###############
# Templates
###############
@router.post("/template")
async def create_template(
    data: ReferenceTemplate,
    _: UserRead = Depends(get_current_user),
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
    _: UserRead = Depends(get_current_user),
):
    result = await ReferenceTemplateService.get_templates(template_type)

    return result


@router.delete("/template/{id}")
async def delete_template_id(
    id: int,
    _: UserRead = Depends(get_current_user),
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
    _: UserRead = Depends(get_current_user),
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
    _: UserRead = Depends(get_current_user),
):

    if not await ReferenceTemplateService.update_template(id, data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or could not be updated.",
        )

    return {"message": "Template updated successfully."}
