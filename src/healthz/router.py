from fastapi import APIRouter, Request, Response

router = APIRouter(
    prefix="/healthz",
    tags=["Service is alive"]
)

@router.get("", status_code=200)
def healthz():
    return  {"message": "Service is alive"}
