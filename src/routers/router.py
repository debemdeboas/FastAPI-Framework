from fastapi.routing import APIRouter
from fastapi import Depends, Request

from src.constants import *
from src.routers.dependencies import *
from src.utils.logger import get_logger


async def log_request(request: Request):
    logger.info(f'Request received: {request.method} {request.url}')


logger = get_logger(__name__)
logger.info('Create')
router = APIRouter(
    prefix=f'/{API_VERSION}/services',
    dependencies=[Depends(verify_token_header),
                  Depends(log_request)]
)
