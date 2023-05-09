
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from fastapi_cache.decorator import cache

from starlette import status
from auth.base_config import current_user


router = APIRouter(
    prefix="/user",
    tags=["Users"]
)


@router.get("/get_api_key")
@cache(expire=60)
def get_api_key(user=Depends(current_user)):
    return ORJSONResponse([{"api_key": user.api_key}])
