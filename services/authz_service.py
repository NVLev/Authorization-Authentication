from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import User, AccessRule, BusinessElement


class AuthorizationService:
    """Сервис для проверки прав доступа к ресурсам"""

    @staticmethod
    async def check_permission(
            user: User,
            element_name: str,
            action: str,
            resource_owner_id: Optional[int] = None,
            session: AsyncSession = None
    ) -> bool:
        """
        Проверяет, может ли пользователь выполнить действие над ресурсом.

        Args:
            user: Пользователь с загруженными roles
            element_name: Название ресурса ("projects", "users", и т.д.)
            action: Действие ("read", "create", "update", "delete")
            resource_owner_id: ID владельца ресурса (для проверки "только свои")
            session: Сессия БД

        Returns:
            bool: True если доступ разрешён, иначе False
        """
        if not session:
            raise ValueError("Session is required")

        # Получаем бизнес-элемент
        stmt = select(BusinessElement).where(BusinessElement.name == element_name)
        result = await session.execute(stmt)
        element = result.scalar_one_or_none()

        if not element:
            return False  # Ресурс не существует

        # Получаем ID ролей пользователя
        user_role_ids = [role.id for role in user.roles]

        if not user_role_ids:
            return False

        # Получаем правила доступа для ролей пользователя
        stmt = select(AccessRule).where(
            AccessRule.role_id.in_(user_role_ids),
            AccessRule.element_id == element.id
        )
        result = await session.execute(stmt)
        rules = result.scalars().all()

        if not rules:
            return False

        # Проверяем права по каждому правилу
        for rule in rules:
            if action == "read" and rule.read_all_permission:
                return True
            if action == "update" and rule.update_all_permission:
                return True
            if action == "delete" and rule.delete_all_permission:
                return True
            if action == "create" and rule.create_permission:
                return True


            if resource_owner_id is not None and resource_owner_id == user.id:
                if action == "read" and rule.read_permission:
                    return True
                if action == "update" and rule.update_permission:
                    return True
                if action == "delete" and rule.delete_permission:
                    return True

        return False

    @staticmethod
    async def get_user_permissions(
            user: User,
            session: AsyncSession
    ) -> dict:
        """
        Возвращает все права пользователя в структурированном виде.

        Args:
            user: Пользователь с загруженными roles
            session: Сессия БД

        Returns:
            dict: {
                "projects": {
                    "read": True,
                    "read_all": True,
                    "create": True,
                    ...
                },
                ...
            }
        """
        user_role_ids = [role.id for role in user.roles]

        if not user_role_ids:
            return {}

        # Получаем все правила для ролей пользователя с загрузкой элементов
        stmt = (
            select(AccessRule)
            .options(selectinload(AccessRule.element))
            .where(AccessRule.role_id.in_(user_role_ids))
        )
        result = await session.execute(stmt)
        rules = result.scalars().all()

        # Группируем по элементам
        permissions = {}

        for rule in rules:
            element_name = rule.element.name

            if element_name not in permissions:
                permissions[element_name] = {
                    "read": False,
                    "read_all": False,
                    "create": False,
                    "update": False,
                    "update_all": False,
                    "delete": False,
                    "delete_all": False,
                }

            # Объединяем права (если хотя бы одна роль разрешает - разрешено)
            permissions[element_name]["read"] |= rule.read_permission
            permissions[element_name]["read_all"] |= rule.read_all_permission
            permissions[element_name]["create"] |= rule.create_permission
            permissions[element_name]["update"] |= rule.update_permission
            permissions[element_name]["update_all"] |= rule.update_all_permission
            permissions[element_name]["delete"] |= rule.delete_permission
            permissions[element_name]["delete_all"] |= rule.delete_all_permission

        return permissions