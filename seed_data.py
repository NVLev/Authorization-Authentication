"""
Скрипт для заполнения БД тестовыми данными.
Запуск: python seed_data.py
"""
import asyncio
from core.db_helper import db_helper
from core.models import Role, BusinessElement, AccessRule, User, UserRole
from services.auth_service import AuthService


async def seed_database():
    """Заполняет БД тестовыми ролями, элементами, правилами и пользователями"""
    async with db_helper.session_factory() as session:
        print("Seeding database...")

        # 1. Создаём роли
        admin_role = Role(name="admin", description="Полный доступ ко всем ресурсам")
        manager_role = Role(name="manager", description="Управление проектами")
        user_role = Role(name="user", description="Базовый доступ")

        session.add_all([admin_role, manager_role, user_role])
        await session.commit()
        await session.refresh(admin_role)
        await session.refresh(manager_role)
        await session.refresh(user_role)
        print("Roles created: admin, manager, user")

        # 2. Создаём бизнес-элементы (ресурсы)
        projects_el = BusinessElement(name="projects", description="Проекты")
        users_el = BusinessElement(name="users", description="Пользователи")
        rules_el = BusinessElement(name="access_rules", description="Правила доступа")

        session.add_all([projects_el, users_el, rules_el])
        await session.commit()
        await session.refresh(projects_el)
        await session.refresh(users_el)
        await session.refresh(rules_el)
        print("Business elements created: projects, users, access_rules")

        # 3. Правила для админа (полный доступ ко всему)
        admin_rules = []
        for element in [projects_el, users_el, rules_el]:
            rule = AccessRule(
                role_id=admin_role.id,
                element_id=element.id,
                read_all_permission=True,
                create_permission=True,
                update_all_permission=True,
                delete_all_permission=True
            )
            admin_rules.append(rule)
        session.add_all(admin_rules)

        # 4. Правила для менеджера (проекты - все читать, свои редактировать)
        manager_projects_rule = AccessRule(
            role_id=manager_role.id,
            element_id=projects_el.id,
            read_all_permission=True,
            create_permission=True,
            update_permission=True,
            delete_permission=True,
        )
        session.add(manager_projects_rule)

        # 5. Правила для user (только свои проекты)
        user_projects_rule = AccessRule(
            role_id=user_role.id,
            element_id=projects_el.id,
            read_permission=True,
            create_permission=True,
            update_permission=True,
            delete_permission=True,
        )
        session.add(user_projects_rule)

        await session.commit()
        print("Access rules created (admin: full, manager: read all + edit own, user: own only)")

        # 6. Создаём тестовых пользователей
        admin_user = User(
            email="admin@test.com",
            pass_hash=AuthService.get_password_hash("admin123"),
            is_active=True,
        )
        session.add(admin_user)
        await session.flush()
        admin_user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        session.add(admin_user_role)


        manager_user = User(
            email="manager@test.com",
            pass_hash=AuthService.get_password_hash("manager123"),
            is_active=True,
        )
        session.add(manager_user)
        await session.flush()

        manager_user_role = UserRole(user_id=manager_user.id, role_id=manager_role.id)
        session.add(manager_user_role)

        regular_user = User(
            email="user@test.com",
            pass_hash=AuthService.get_password_hash("user123"),
            is_active=True,
        )
        session.add(regular_user)
        await session.flush()

        regular_user_role = UserRole(user_id=regular_user.id, role_id=user_role.id)
        session.add(regular_user_role)

        await session.commit()
        print("Test users created")

        print("\n" + "=" * 60)
        print("Database seeded successfully!")
        print("=" * 60)
        print("\nTest accounts:")
        print(f"  Admin:   admin@test.com / admin123    (full access)")
        print(f"  Manager: manager@test.com / manager123 (read all, edit own)")
        print(f"  User:    user@test.com / user123       (own only)")
        print("\n💡 Tip: Use these credentials to test the API\n")


async def clear_database():
    """Очищает все данные из таблиц (для пересоздания)"""
    async with db_helper.session_factory() as session:
        from sqlalchemy import text

        print("🧹 Clearing database...")

        # Удаляем данные в правильном порядке (из-за внешних ключей)
        await session.execute(text("DELETE FROM access_rules"))
        await session.execute(text("DELETE FROM user_roles"))
        await session.execute(text("DELETE FROM refresh_tokens"))
        await session.execute(text("DELETE FROM projects"))
        await session.execute(text("DELETE FROM users"))
        await session.execute(text("DELETE FROM business_elements"))
        await session.execute(text("DELETE FROM roles"))

        await session.commit()
        print("✅ Database cleared")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        asyncio.run(clear_database())
    else:
        asyncio.run(seed_database())