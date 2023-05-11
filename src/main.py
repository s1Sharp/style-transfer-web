from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead

from auth.router import router as router_user
from task.router import router as router_tasks
from pages.router import router as router_pages
from healthz.router import router as router_healthz

from redis import asyncio as aioredis
from config import REDIS_URL, DOMEN_URL


app = FastAPI(
    title="Transfer style app"
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(router_tasks)
app.include_router(router_pages)
app.include_router(router_user)
app.include_router(router_healthz)


origins = [
    DOMEN_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)