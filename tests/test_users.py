def get_token(client):
    response = client.post(
        "/users/User_login/login",
        json={
            "email":"mani@example.com",
            "password":"mani369"
        }
    )
    return response.get_json()["access_token"]


def test_get_users_authorized(client):
    token = get_token(client)

    response = client.get(
        "/users/Get_ALL_Users",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

def test_get_users_unauthorized(client):
    response = client.get("/users/Get_ALL_Users")
    assert response.status_code == 401

def test_admin_only_api(client):
    res = client.post(
        "/users/User_login/login",
        json={
            "email": "raju@example.com",
            "password": "123456"
        }
    )

    token = res.get_json()["access_token"]

    response = client.get(
        "/users/Get_ALL_Users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403

# import pytest
# from services.user_service import UserService
# from utils.errors import  AppError
# service = UserService()

# def test_login_success(mocker):
#     mocker.patch(
#         "repository.user_repo.get_user_by_email",
#         return_value=FakeUser(password="hashed")
#     )
#     mocker.patch(
#         "utils.security.check_password",
#         return_value=True
#     )

#     result = service.login("a@test.com", "123")

#     assert result["message"] == "Login success"


# def test_login_invalid_user(mocker):
#     mocker.patch(
#         "repository.user_repo.get_user_by_email",
#         return_value=None
#     )

#     with pytest.raises(AppError):
#         service.login("x@test.com", "123")

# def test_admin_only_access():
#     with pytest.raises(AppError):
#         if g.role != "admin":
#             raise AppError("Admin access required", 403)
