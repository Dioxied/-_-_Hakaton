import jwt
from datetime import datetime, timedelta

JWT_SECRET = "super-secret-key"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600

def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["user_id"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
