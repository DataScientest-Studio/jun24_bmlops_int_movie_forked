from fastapi.testclient import TestClient
from fastapi import status
from model_api import api, users_db, ADMIN_USERNAME, ADMIN_PASSWORD

client = TestClient(api)

UNKNOWN_USER = ("unknown", "user")
NON_ADMIN_USER = list(users_db.items())[0]
ADMIN_USER = (ADMIN_USERNAME, {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})


def test_health():
    """Testing if the health endpoint works"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK

def test_unauthorized_login():
    """Testing if secured endpoint doesnt work because it has no auth."""
    response = client.get("/secured")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_unknown_user_login():
    """Testing the secured endpoint doesnt work because of unknown user."""
    response = client.get("/secured", auth=UNKNOWN_USER)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_login_with_known_user():
    """Testing the userlogin endpoint works with non admin."""
    response = client.post(
        "/user/login", json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == status.HTTP_200_OK

def test_login_as_admin():
    """Testing the secured endpoint works with admin user."""
    response = client.post(
        "/user/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == status.HTTP_200_OK

    login_data = response.json()
    assert "access_token" in login_data

    access_token = login_data["access_token"]

    # Access the secured endpoint with the access token
    secured_response = client.get(
        "/secured", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert secured_response.status_code == status.HTTP_200_OK

#TODO: Write test for prediction endpoint
#function to test the prediction
def test_prediction():

    login_response = client.post("/user/login",json= {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert login_response.status_code == status.HTTP_200_OK

    #checking if we get an access token and saving it in the variable access token
    login_data = login_response.json()
    assert "access_token" in login_data
    access_token = login_data["access_token"]

    #this is the test User id
    user_id = 1

    #defining the header with the previously created access token
    headers = {"Authorization": f"Bearer {access_token}"}
    prediction_response = client.get(f"/predict/{user_id}", headers=headers)

    # Assert the response status code to be 200
    assert prediction_response.status_code == status.HTTP_200_OK

    # Optionally, you can check the response content
    prediction_response_json =  prediction_response.json()
    assert "prediction" in  prediction_response_json
