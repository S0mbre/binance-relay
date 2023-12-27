from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from api import router

app = FastAPI(
    title='Binance Relay',
    redoc_url=None,
    root_path='',
    openapi_url='/openapi.json',
    default_response_class=ORJSONResponse
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(router)