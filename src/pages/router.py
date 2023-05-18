import json

from fastapi import APIRouter, Request, Response, Depends
from fastapi.templating import Jinja2Templates
from fastapi_cache.decorator import cache

from task.router import get_task_status

router = APIRouter(
    prefix="/pages",
    tags=["Pages"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/base")
def get_base_page(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@router.get("/task")
def get_search_page(request: Request, response: Response):
    return templates.TemplateResponse("search.html", {"request": request, "tasks": []})

@cache(expire=60*60)
@router.get("/task/{task_id}")
def get_search_page(request: Request, response: Response, api_key:str, task=Depends(get_task_status)):
    return templates.TemplateResponse("search.html", {"request": request, "tasks": [(task["data"]["task_status"], task["data"]["task_link"])] })
