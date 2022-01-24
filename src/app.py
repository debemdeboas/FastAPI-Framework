from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.constants import *
from src.mongo import MongoDatabase
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info('Create')
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    contact=API_CONTACT,
)

db = MongoDatabase()


@app.get('/')
async def homepage():
    return RedirectResponse('/docs')
