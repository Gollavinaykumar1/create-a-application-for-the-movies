import jwt
import asyncio
from datetime import datetime, timedelta

secret_key = "my_secret_key"
algorithm = "HS256"
access_token_expires = timedelta(minutes=30)

async def create_access_token(data: dict):
    payload = {
        "exp": datetime.utcnow() + access_token_expires,
        "iat": datetime.utcnow(),
        "sub": data["user_id"],
    }
    access_token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return access_token

async def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def rate_limit_exceeded(ip_address: str):
    # implement rate limiting logic here
    # for example, using a database to store request counts
    # this is a simplified example and may not be suitable for production use
    max_requests = 100
    request_count = await get_request_count(ip_address)
    if request_count > max_requests:
        return True
    return False

async def get_request_count(ip_address: str):
    # implement logic to get request count from database
    # this is a simplified example and may not be suitable for production use
    return 0

async def validate_input(data: dict):
    # implement input validation logic here
    # for example, using a schema to validate user input
    # this is a simplified example and may not be suitable for production use
    required_fields = ["username", "password"]
    for field in required_fields:
        if field not in data:
            return False
    return True