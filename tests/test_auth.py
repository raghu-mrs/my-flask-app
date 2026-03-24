def test_login_success(client):
    response = client.post(
        "/users/User_login/login",
        json={
            "email":"mani@example.com",
            "password":"mani369"
        }
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
