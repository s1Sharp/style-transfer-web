import logging
import pytest
from sqlalchemy import insert, select

from auth.models import User
from conftest import client, async_session_maker


async def test_add_user():
    async with async_session_maker() as session:
        stmt = insert(User).values({'email':"test@mail.com", 'hashed_password':"testhash"}).returning(User.id)
        id = await session.scalars(stmt)
        await session.commit()

        user = await session.get(User, id)
        assert user.email == "test@mail.com"
        assert user.hashed_password == "testhash"
 

def test_register():
    response = client.post("/auth/register", json={
    "email": "stubemail@mail.com",
    "password": "testpassword",
    "username": "testuser",
    "tg_id": 555555,
    })

    assert response.status_code == 201
