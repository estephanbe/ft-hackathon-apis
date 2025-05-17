from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from DB.mongodb import get_mongo_db, close_mongo_db
from config import settings
from routers import network, auth
from routers import me as me_router

load_dotenv()  # This loads the environment variables from .env
APP_VERSION = 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await get_mongo_db()
    yield
    # Shutdown logic
    await close_mongo_db()


app = FastAPI(
    lifespan=lifespan,
    prefix=settings.API_V1_STR,
    title='The Kingdom Network',
    description='The Kingdom Network API',
    version=str(APP_VERSION),
    openapi_url=settings.API_V1_STR + '/openapi.json',
    docs_url=settings.API_V1_STR + '/docs',
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {
        "status": "up",
        "version": APP_VERSION
    }


app.include_router(network.router, prefix=settings.API_V1_STR + "/network")
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(me_router.router, prefix=settings.API_V1_STR)
