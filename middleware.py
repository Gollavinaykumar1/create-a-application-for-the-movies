import asyncio
from security import rate_limit_exceeded, verify_access_token
from auth import authenticate_user

async def rate_limit_middleware(request):
    ip_address = request.ip
    if await rate_limit_exceeded(ip_address):
        return {"error": "Rate limit exceeded"}
    return None

async def auth_middleware(request):
    token = request.headers.get("Authorization")
    if token is None:
        return {"error": "Unauthorized"}
    user_data = await authenticate_user(token)
    if user_data is None:
        return {"error": "Invalid token"}
    request.user = user_data
    return None