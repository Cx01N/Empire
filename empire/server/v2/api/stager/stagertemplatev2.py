from fastapi import HTTPException, Depends

from empire.server.server import main
from empire.server.v2.api.EmpireApiRouter import APIRouter
from empire.server.v2.api.jwt_auth import get_current_active_user
from empire.server.v2.api.stager.stager_dto import domain_to_dto_template, StagerTemplate, StagerTemplates

stager_template_service = main.stagertemplatesv2

router = APIRouter(
    prefix="/api/v2beta/stager-templates",
    tags=["stager-templates"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=StagerTemplates, dependencies=[Depends(get_current_active_user)])
async def get_stager_templates():
    templates = list(map(lambda x: domain_to_dto_template(x[1], x[0]),
                         stager_template_service.loaded_stagers.items()))

    return {'records': templates}


@router.get("/{uid}", response_model=StagerTemplate, dependencies=[Depends(get_current_active_user)])
async def get_stager_template(uid: str):
    template = stager_template_service.loaded_stagers.get(uid)

    if not template:
        raise HTTPException(status_code=404, detail="Stager template not found")

    return domain_to_dto_template(template, uid)
