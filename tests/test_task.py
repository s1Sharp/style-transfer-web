import logging
import pytest
from httpx import AsyncClient


async def test_get_specific_task(ac: AsyncClient):
    response = await ac.get("/task", params={
        "task_id": 999999,
        "api_key": "test_api_key",
    })
    res_json = response.json()

    logging.info(f"res json = {res_json}")
    assert res_json['status'] == 404
