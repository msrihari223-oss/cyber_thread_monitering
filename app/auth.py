from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "cyber_secret"

def create_token(data: dict):

    expire = datetime.utcnow() + timedelta(hours=2)

    data.update({"exp": expire})

    return jwt.encode(
        data,
        SECRET_KEY,
        algorithm="HS256"
    )