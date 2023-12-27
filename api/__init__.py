from fastapi import APIRouter
from api.endpoints import router as main_router

router = APIRouter()
router.include_router(main_router, prefix='')