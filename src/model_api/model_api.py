import os
import pickle
import uvicorn
import time
import jwt
from fastapi import Request, HTTPException, Body, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from fastapi import FastAPI
from passlib.context import CryptContext


# JWT settings
JWT_SECRET = "secret"
JWT_ALGORITHM = "HS256"

# Admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

MODEL_PATH = "../../models/model.pkl"

pwd_context = CryptContext(
    schemes=["bcrypt"], bcrypt__default_rounds=12, deprecated="auto"
)

# In-memory users database
users_db = {
    "testuser": {"username": "testuser", "password": pwd_context.hash("testpassword")}
}

def load_model():
    filehandler = open(MODEL_PATH, "rb")
    model = pickle.load(filehandler)
    filehandler.close()
    return model

loaded_model = load_model()

# Pydantic model for user schema
class UserSchema(BaseModel):
    username: str
    password: str

# hashes a string password using bcrypt
def hash_password(password: str):
    return pwd_context.hash(password)


# verifies if string password matches the hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# his function constructs a JSON response with an access token
def token_response(token: str):
    return {"access_token": token}


# signing a JWT token using the provided payload and secret key
# the token expires after 100 minutes
def sign_jwt(user_id: str):
    payload = {
        "user_id": user_id,
        "expires": time.time() + 6000,
    }  # Token expires within 100 minutes
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


# this function decodes a JWT token to retrieve the payload
# if the 10 minutes have not yet expired
def decode_jwt(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception:
        return {}


def check_user(data: UserSchema):
    for user in users_db:
        if user.username == data.username and user.password == data.password:
            return True
    return False


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str):
        isTokenValid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except Exception:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid


api = FastAPI()

@api.get("/health")
async def get_health():
    return {"message": "Up and running!"}

# endpoint for user signup that registers new users and checks if user already exists
@api.post("/user/signup")
async def create_user(user: UserSchema = Body(...)):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = hash_password(user.password)
    users_db[user.username] = {"username": user.username, "password": hashed_password}
    return sign_jwt(user.username)


# endpoint for user login that authenticates by checking if users are admin or signed up in the user database,
# veryfiys username and password and returns a JWT token
@api.post("/user/login")
async def user_login(user: UserSchema = Body(...)):
    if ADMIN_USERNAME is None or ADMIN_PASSWORD is None:
        raise HTTPException(
            status_code=500,
            detail=f"The OS env. variables `ADMIN_USERNAME` and `ADMIN_PASSWORD` have not been set!",
        )

    if user.username in users_db and verify_password(
        user.password, users_db[user.username]["password"]
    ):
        return sign_jwt(user.username)
    elif user.username == ADMIN_USERNAME and user.password == ADMIN_PASSWORD:
        return sign_jwt(user.username)
    raise HTTPException(status_code=401, detail="Invalid username or password")

#TODO: Prediction endpoint
"""
@api.post("/predict", dependencies=[Depends(JWTBearer())])
def predict_model(user_id: int):
    users = "" #read UsersMatrix from DB
    user = users[users["userId"].isin([user_id])]
    user = user.drop("userId", axis=1)
    _, indices = model.kneighbors(user)
    # read movie titels from indices?
    prediction = "List of movie titles?"
    return {"prediction": prediction}
"""

@api.get("/reload_model", dependencies=[Depends(JWTBearer())])
def reload_model():
    global loaded_model
    # Reload the model
    loaded_model = load_model()
    return {"message": "The Model was updated!"}


if __name__ == "__main__":

    uvicorn.run(api, host="0.0.0.0", port=8000)