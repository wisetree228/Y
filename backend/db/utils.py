from sqlalchemy.orm import Session
from .models import *
from typing import Union



async def add_and_refresh_object(object: Union[User, Post, Friendship, FriendshipRequest, VotingVariant], db: Session):
    db.add(object)
    await db.commit()
    await db.refresh(object)




