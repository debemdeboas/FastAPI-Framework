from fastapi import Header, HTTPException, status

from src.constants import ENV_API_TOKEN_HEADER


async def verify_token_header(x_token: str = Header(..., description='Required pre-shared key for any route')):
    if x_token != ENV_API_TOKEN_HEADER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid basic token header')
