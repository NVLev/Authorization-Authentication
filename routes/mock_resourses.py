from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from core.models import Project
from core.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from middleware.permissions import get_current_user
from services.authz_service import AuthorizationService

router = APIRouter(prefix="/projects", tags=["Projects (Mock Resources)"])


@router.get("/", response_model=list[ProjectRead])
async def list_projects(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    # Проверяем право read_all
    allowed = await AuthorizationService.check_permission(
        user=user,
        element_name="projects",
        action="read",
        session=session,
        resource_owner_id=None,  # неважно
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to read projects",
        )

    result = await session.execute(select(Project))
    return result.scalars().all()


@router.post("/", response_model=ProjectRead)
async def create_project(
    data: ProjectCreate,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    allowed = await AuthorizationService.check_permission(
        user=user, element_name="projects", action="create", session=session
    )

    if not allowed:
        raise HTTPException(
            status_code=403, detail="You do not have permission to create projects"
        )

    project = Project(title=data.title, description=data.description, owner_id=user.id)

    session.add(project)
    await session.commit()
    await session.refresh(project)

    return project


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    allowed = await AuthorizationService.check_permission(
        user=user,
        element_name="projects",
        action="read",
        resource_owner_id=project.owner_id,
        session=session,
    )

    if not allowed:
        raise HTTPException(403, "No permission to read this project")

    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    allowed = await AuthorizationService.check_permission(
        user=user,
        element_name="projects",
        action="update",
        resource_owner_id=project.owner_id,
        session=session,
    )

    if not allowed:
        raise HTTPException(403, "No permission to update this project")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    await session.commit()
    await session.refresh(project)

    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    allowed = await AuthorizationService.check_permission(
        user=user,
        element_name="projects",
        action="delete",
        resource_owner_id=project.owner_id,
        session=session,
    )

    if not allowed:
        raise HTTPException(403, "No permission to delete this project")

    await session.delete(project)
    await session.commit()

    return {"message": "Project deleted"}
