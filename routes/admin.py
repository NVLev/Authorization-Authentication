from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from core.models import AccessRule, BusinessElement, Role
from core.schemas import (
    AccessRuleCreate,
    AccessRuleRead,
    AccessRuleUpdate,
    BusinessElementCreate,
    BusinessElementRead,
    RoleCreate,
    RoleRead,
)
from middleware.permissions import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/roles", response_model=RoleRead)
async def create_role(
    data: RoleCreate,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    existing = await session.execute(select(Role).where(Role.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(400, detail="Role already exists")

    role = Role(name=data.name, description=data.description)
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role


@router.get("/roles", response_model=list[RoleRead])
async def list_roles(
    admin=Depends(require_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await session.execute(select(Role))
    return result.scalars().all()


@router.post("/resources", response_model=BusinessElementRead)
async def create_resource(
    data: BusinessElementCreate,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    existing = await session.execute(
        select(BusinessElement).where(BusinessElement.name == data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, detail="Resource already exists")

    element = BusinessElement(name=data.name, description=data.description)
    session.add(element)
    await session.commit()
    await session.refresh(element)
    return element


@router.get("/resources", response_model=list[BusinessElementRead])
async def list_resources(
    admin=Depends(require_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await session.execute(select(BusinessElement))
    return result.scalars().all()


@router.post("/rules", response_model=AccessRuleRead)
async def create_rule(
    data: AccessRuleCreate,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):

    role = await session.get(Role, data.role_id)
    if not role:
        raise HTTPException(404, detail="Role not found")

    element = await session.get(BusinessElement, data.element_id)
    if not element:
        raise HTTPException(404, detail="Resource not found")

    existing = await session.execute(
        select(AccessRule).where(
            AccessRule.role_id == data.role_id, AccessRule.element_id == data.element_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, detail="Rule already exists")

    rule = AccessRule(**data.model_dump())
    session.add(rule)
    await session.commit()
    await session.refresh(rule)

    return AccessRuleRead(
        **data.model_dump(), id=rule.id, role_name=role.name, element_name=element.name
    )


@router.get("/rules", response_model=list[AccessRuleRead])
async def list_rules(
    admin=Depends(require_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await session.execute(
        select(AccessRule, Role, BusinessElement)
        .join(Role, AccessRule.role_id == Role.id)
        .join(BusinessElement, AccessRule.element_id == BusinessElement.id)
    )

    items = []
    for rule, role, element in result.all():
        items.append(
            AccessRuleRead(
                id=rule.id,
                role_id=rule.role_id,
                element_id=rule.element_id,
                read_permission=rule.read_permission,
                read_all_permission=rule.read_all_permission,
                create_permission=rule.create_permission,
                update_permission=rule.update_permission,
                update_all_permission=rule.update_all_permission,
                delete_permission=rule.delete_permission,
                delete_all_permission=rule.delete_all_permission,
                role_name=role.name,
                element_name=element.name,
            )
        )
    return items


@router.patch("/rules/{rule_id}", response_model=AccessRuleRead)
async def update_rule(
    rule_id: int,
    data: AccessRuleUpdate,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    rule = await session.get(AccessRule, rule_id)
    if not rule:
        raise HTTPException(404, detail="Rule not found")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(rule, key, value)

    await session.commit()
    await session.refresh(rule)

    role = await session.get(Role, rule.role_id)
    element = await session.get(BusinessElement, rule.element_id)

    return AccessRuleRead(
        id=rule.id,
        role_id=rule.role_id,
        element_id=rule.element_id,
        read_permission=rule.read_permission,
        read_all_permission=rule.read_all_permission,
        create_permission=rule.create_permission,
        update_permission=rule.update_permission,
        update_all_permission=rule.update_all_permission,
        delete_permission=rule.delete_permission,
        delete_all_permission=rule.delete_all_permission,
        role_name=role.name,
        element_name=element.name,
    )
