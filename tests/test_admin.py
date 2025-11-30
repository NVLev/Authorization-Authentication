import pytest


class TestAdminRoles:
    """Тесты управления ролями"""

    async def test_list_roles_as_admin(self, client, admin_token):
        """Админ может просматривать роли"""
        response = await client.get(
            "/admin/roles",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        assert response.status_code == 200
        roles = response.json()
        assert len(roles) >= 3  # admin, manager, user
        role_names = [r["name"] for r in roles]
        assert "admin" in role_names
        assert "manager" in role_names

    async def test_list_roles_as_user_forbidden(self, client, user_token):
        """Обычный пользователь не может просматривать роли"""
        response = await client.get(
            "/admin/roles",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403


class TestAdminResources:
    """Тесты управления ресурсами"""

    async def test_list_resources_as_admin(self, client, admin_token):
        """Админ может просматривать ресурсы"""
        response = await client.get(
            "/admin/resources",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        resources = response.json()
        assert len(resources) >= 1  # projects
        resource_names = [r["name"] for r in resources]
        assert "projects" in resource_names


class TestAdminAccessRules:
    """Тесты управления правилами доступа"""

    async def test_list_rules_as_admin(self, client, admin_token):
        """Админ может просматривать правила доступа"""
        response = await client.get(
            "/admin/rules",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        rules = response.json()
        assert len(rules) > 0

        # Проверяем структуру
        first_rule = rules[0]
        assert "id" in first_rule
        assert "role_name" in first_rule
        assert "element_name" in first_rule

    async def test_list_rules_as_manager_forbidden(self, client, manager_token):
        """Менеджер не может просматривать правила"""
        response = await client.get(
            "/admin/rules",
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 403