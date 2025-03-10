from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from .models import *
from typing import Union



async def add_and_refresh_object(object: Union[User, Post, Friendship, FriendshipRequest, VotingVariant, Like, Message], db: Session):
    db.add(object)
    await db.commit()
    await db.refresh(object)

async def get_user_by_email(email: str, db: Session):
    result_email = await db.execute(select(User).filter(User.email == email))
    return result_email.scalars().first()

async def get_user_by_id(id: int, db: Session):
    result_db = await db.execute(select(User).filter(User.id == id))
    return result_db.scalars().first()

async def delete_object(object: Union[User, Post, Friendship, FriendshipRequest, VotingVariant, Like], db: Session):
    await db.delete(object)
    await db.commit()

async def get_post_by_id(id: int, db: Session):
    result_db = await db.execute(select(Post).filter(Post.id == id))
    return result_db.scalars().first()

async def get_like_on_post_from_user(post_id: int, user_id: int, db: Session):
    result_db = await db.execute(select(Like).filter( and_(
        Like.post_id==post_id,
        Like.author_id==user_id
    ) ))
    return result_db.scalars().first()



