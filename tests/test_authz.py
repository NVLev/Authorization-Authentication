import pytest


class TestAuthorizationServiceViaAPI:
    """Тесты AuthorizationService через API"""

    async def test_admin_has_full_access(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}

        resp = await client.post(
            "/projects/",
            json={"title": "Admin Project", "description": "Full access"},
            headers=headers
        )
        assert resp.status_code == 200
        project = resp.json()
        project_id = project["id"]

        resp_get = await client.get(f"/projects/{project_id}", headers=headers)
        assert resp_get.status_code == 200
        assert resp_get.json()["title"] == "Admin Project"

        resp_patch = await client.patch(
            f"/projects/{project_id}",
            json={"title": "Updated Admin Project"},
            headers=headers
        )
        assert resp_patch.status_code == 200
        assert resp_patch.json()["title"] == "Updated Admin Project"

        resp_delete = await client.delete(f"/projects/{project_id}", headers=headers)
        assert resp_delete.status_code == 200
        assert resp_delete.json()["message"] == "Project deleted"

    async def test_manager_can_read_all(self, client, manager_token):
        headers = {"Authorization": f"Bearer {manager_token}"}
        resp = await client.get("/projects/", headers=headers)
        assert resp.status_code == 200

    async def test_manager_can_update_own_only(self, client, manager_token, admin_token):
        headers_manager = {"Authorization": f"Bearer {manager_token}"}
        headers_admin = {"Authorization": f"Bearer {admin_token}"}

        resp_own = await client.post(
            "/projects/",
            json={"title": "Manager Project", "description": "Own only"},
            headers=headers_manager
        )
        assert resp_own.status_code == 200
        own_project_id = resp_own.json()["id"]

        resp_other = await client.post(
            "/projects/",
            json={"title": "Admin Project", "description": "Owned by admin"},
            headers=headers_admin
        )
        other_project_id = resp_other.json()["id"]

        resp_patch_own = await client.patch(
            f"/projects/{own_project_id}",
            json={"title": "Updated Manager Project"},
            headers=headers_manager
        )
        assert resp_patch_own.status_code == 200

        resp_patch_other = await client.patch(
            f"/projects/{other_project_id}",
            json={"title": "Hack attempt"},
            headers=headers_manager
        )
        assert resp_patch_other.status_code == 403

    async def test_user_own_only(self, client, user_token, admin_token):
        headers_user = {"Authorization": f"Bearer {user_token}"}
        headers_admin = {"Authorization": f"Bearer {admin_token}"}

        resp_own = await client.post(
            "/projects/",
            json={"title": "User Project", "description": "Own only"},
            headers=headers_user
        )
        assert resp_own.status_code == 200
        own_project_id = resp_own.json()["id"]

        resp_other = await client.post(
            "/projects/",
            json={"title": "Admin Project", "description": "Owned by admin"},
            headers=headers_admin
        )
        other_project_id = resp_other.json()["id"]

        resp_get_own = await client.get(f"/projects/{own_project_id}", headers=headers_user)
        assert resp_get_own.status_code == 200

        # Чтение чужого проекта → 403
        resp_get_other = await client.get(f"/projects/{other_project_id}", headers=headers_user)
        assert resp_get_other.status_code == 403

    async def test_get_user_permissions_via_api(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = await client.get("/auth/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "roles" in data
        assert "admin" in data["roles"]
