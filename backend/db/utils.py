from sqlalchemy.future import select
from sqlalchemy.orm import Session
from .models import *
from typing import Union



async def add_and_refresh_object(object: Union[User, Post, Friendship, FriendshipRequest, VotingVariant], db: Session):
    db.add(object)
    await db.commit()
    await db.refresh(object)

async def get_user_by_email(email: str, db: Session):
    result_email = await db.execute(select(User).filter(User.email == email))
    return result_email.scalars().first()

async def get_user_by_id(id: int, db: Session):
    result_db = await db.execute(select(User).filter(User.id == id))
    return result_db.scalars().first()

async def delete_object(object: Union[User, Post, Friendship, FriendshipRequest, VotingVariant], db: Session):
    await db.delete(object)
    await db.commit()



