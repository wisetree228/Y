from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from .models import *
from typing import Union


async def add_and_refresh_object(object: Union[User, Post, Friendship, FriendshipRequest, VotingVariant, Like, Message, Vote, MediaInPost], db: Session):
    db.add(object)
    await db.commit()
    await db.refresh(object)


async def get_user_by_email(email: str, db: Session):
    result_email = await db.execute(select(User).filter(User.email == email))
    return result_email.scalars().first()


async def get_user_by_username(username: str, db: Session):
    """
    Получает пользователя по имени пользователя.

    Args:
        username (str): Имя пользователя.
        db (Session): Сессия базы данных.

    Returns:
        User: Объект пользователя или None.
    """
    result_email = await db.execute(select(User).filter(User.username == username))
    return result_email.scalars().first()


async def get_user_by_id(id: int, db: Session):
    result_db = await db.execute(select(User).filter(User.id == id))
    return result_db.scalars().first()


async def delete_object(object: Union[User, Post, Friendship, FriendshipRequest, VotingVariant, Like, Message, Vote], db: Session):
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


async def get_likes_count(post_id: int, db: Session):
    count_query = await db.execute(select(func.count()).select_from(Like).filter(Like.post_id==post_id))
    count = count_query.scalar()
    return count


async def get_variant_by_id(var_id: int, db: Session):
    result_db = await db.execute(select(VotingVariant).filter(VotingVariant.id == var_id))
    return result_db.scalars().first()


async def get_user_vote(var_id: int, user_id: int, db: Session):
    result_db = await db.execute(select(Vote).filter(and_(
        Vote.user_id == user_id,
        Vote.variant_id == var_id
    )))
    return result_db.scalars().first()


async def get_existing_friendship_request(author_id: int, getter_id: int, db: Session) -> FriendshipRequest:
    """
    Получает существующий запрос на дружбу.

    Args:
        author_id (int): ID автора запроса.
        getter_id (int): ID получателя запроса.
        db (Session): Сессия базы данных.

    Returns:
        FriendshipRequest: Объект запроса на дружбу или None.
    """
    result = await db.execute(select(FriendshipRequest).filter(
        and_(FriendshipRequest.author_id == author_id, FriendshipRequest.getter_id == getter_id)
    ))
    return result.scalars().first()


async def get_existing_friendship(first_friend_id: int, second_friend_id: int, db: Session) -> Friendship:
    """
    Получает существующую дружбу.

    Args:
        first_friend_id (int): ID первого друга.
        second_friend_id (int): ID второго друга.
        db (Session): Сессия базы данных.

    Returns:
        Friendship: Объект дружбы или None.
    """
    result = await db.execute(select(Friendship).filter(
        or_(
            and_(Friendship.first_friend_id == first_friend_id, Friendship.second_friend_id == second_friend_id),
            and_(Friendship.first_friend_id == second_friend_id, Friendship.second_friend_id == first_friend_id)
        )
    ))
    return result.scalars().first()


