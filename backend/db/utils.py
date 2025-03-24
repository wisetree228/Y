"""
Импорты всякой необходимой шняги
"""
from typing import Union, Type, List
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from .models import ( User, Post, Friendship, FriendshipRequest,
    VotingVariant, Like, Message, Vote, MediaInPost, Comment,
    MediaInMessage
)


async def add_and_refresh_object(
        object: Union[User, Post, Friendship, FriendshipRequest,
        VotingVariant, Like, Message, Vote, MediaInPost, Comment,
        MediaInMessage],
        db: Session
) -> None:
    """
    Добавляет обьект в бд и перезагружает его (получает автоматически созданные
    параметры обьекта, такие как id и created_at)
    Args:
        object (Union[User, Post, Friendship, FriendshipRequest, VotingVariant, Like, Message, Vote, MediaInPost]): обьект
        db (Session): Сессия базы данных.
    Returns:
        None
    """
    db.add(object)
    await db.commit()
    await db.refresh(object)


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Получает пользователя по email из бд
    Args:
        email (str): email
        db (Session): Сессия базы данных.
    Returns:
        User: Объект пользователя или None.
    """
    result_email = await db.execute(select(User).filter(User.email == email))
    return result_email.scalars().first()


async def get_user_by_username(username: str, db: Session) -> User:
    """
    Получает пользователя по username пользователя.

    Args:
        username (str): Имя пользователя.
        db (Session): Сессия базы данных.
    Returns:
        User: Объект пользователя или None.
    """
    result_email = await db.execute(select(User).filter(User.username == username))
    return result_email.scalars().first()


async def delete_object(
    object: Union[User, Post, Friendship, FriendshipRequest,
    VotingVariant, Like, Message, Vote, Comment, MediaInPost,
    MediaInMessage],
    db: Session
) -> None:
    """
    Удаляет обьект из бд
    Args:
        object (Union[User, Post, Friendship, FriendshipRequest, VotingVariant, Like, Message, Vote, MediaInPost]): обьект
        db (Session): Сессия базы данных.
    Returns:
        None
    """
    await db.delete(object)
    await db.commit()


async def get_like_on_post_from_user(post_id: int, user_id: int, db: Session) -> Like:
    """
    Возвращает лайк пользователя на посте
    Args:
        post_id (int): id поста
        post_id (int): id юзера
    Returns:
        обьект Like или None
    """
    result_db = await db.execute(select(Like).filter( and_(
        Like.post_id==post_id,
        Like.author_id==user_id
    ) ))
    return result_db.scalars().first()


async def get_likes_count(post_id: int, db: Session) -> int:
    """
    Возвращает количество лайков на посте
    Args:
        post_id (int): id поста
    Returns:
        int количество лайков
    """
    count_query = await db.execute(select(
        func.count()
    ).select_from(Like).filter(
        Like.post_id==post_id)
    )
    count = count_query.scalar()
    return count


async def get_user_vote(var_id: int, user_id: int, db: Session) -> Vote:
    """
    Возвращает голос юзера на варианте голосования
    Args:
        var_id (int): id варианта
        user_id (int): id юзера
        db (Session): сессия бд
    Returns:
        обьект Vote или None
    """
    result_db = await db.execute(
        select(Vote).filter(and_(
        Vote.user_id == user_id,
        Vote.variant_id == var_id
    )))
    return result_db.scalars().first()


async def get_existing_friendship_request(
        author_id: int, getter_id: int, db: Session
) -> FriendshipRequest:
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


async def get_existing_friendship(
        first_friend_id: int, second_friend_id: int, db: Session
) -> Friendship:
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
            and_(
                Friendship.first_friend_id == first_friend_id,
                Friendship.second_friend_id == second_friend_id
            ),
            and_(
                Friendship.first_friend_id == second_friend_id,
                Friendship.second_friend_id == first_friend_id
            )
        )
    ))
    return result.scalars().first()


async def get_comments_count(post_id: int, db: Session) -> int:
    """
    Получает количество комментариев на посте
    Args:
        post_id (int): id поста
        db (Session): сессия бд
    Returns:
        int количество комментариев
    """
    count_query = await db.execute(select(
        func.count()
    ).select_from(Comment).filter(
        Comment.post_id==post_id
    ))
    count = count_query.scalar()
    return count


async def get_all_from_table(
        object_type: Union[Type[User], Type[Post], Type[Friendship], Type[FriendshipRequest],
        Type[VotingVariant], Type[Like], Type[Message], Type[Vote], Type[MediaInPost],
        Type[MediaInMessage], Type[Comment]],
        db: Session, limit=None
) -> list:
    """
    Получает все обьекты из таблицы бд
    Args:
        object_type: Модель, связанная с таблицей
        db (Session): сессия бд
        limit: ограничение на количество получаемых обьектов, по умолчанию None
    Returns:
        список обьектов
    """
    if limit:
        result = await db.execute(select(object_type).order_by(desc(object_type.id)).limit(5))
        return result.scalars().all()
    result = await db.execute(select(object_type))
    return result.scalars().all()


async def get_post_voting_variants(post_id: int, db: Session) -> list:
    """
    Получает варианты голосования поста
    Args:
        post_id (int): id поста
        db (Session): сессия бд
    Returns:
        список обьектов VotingVariant
    """
    result_db = await db.execute(select(VotingVariant).filter(VotingVariant.post_id==post_id))
    return result_db.scalars().all()


async def get_like_status(user_id: int, post_id: int, db: Session) -> bool:
    """
    Определяет, лайкнул ли пользователь пост
    Args:
        post_id (int): id поста
        user_id (int): id юзера
        db (Session): сессия бд
    Returns:
        True или False
    """
    result_db = await db.execute(select(Like).filter(
        and_(Like.post_id==post_id, Like.author_id==user_id)
    ))
    if result_db.scalars().first():
        return True
    return False


async def get_images_id_for_post(post_id: int, db: Session) -> List[int]:
    """
    Получает список id картинок в бд, прикреплённых к посту
    Args:
        post_id (int): id поста
        db (Session): сессия бд
    Returns:
        list[int]
    """
    id_list=[]
    result_db = await db.execute(select(MediaInPost).filter(MediaInPost.post_id==post_id))
    for img in result_db.scalars().all():
        id_list.append(img.id)
    return id_list


async def get_object_by_id(
        object_type: Union[Type[User], Type[Post], Type[Friendship], Type[FriendshipRequest],
        Type[VotingVariant], Type[Like], Type[Message], Type[Vote], Type[MediaInPost],
        Type[MediaInMessage], Type[Comment]],
        id: int, db: Session
):
    """
    Получает обьект из бд по id
    Args:
        object_type: модель обьекта
        id (int): id обьекта
        db (Session): сессия бд
    Returns:
        обьект
    """
    result = await db.execute(select(object_type).filter(object_type.id==id))
    return result.scalars().first()


async def get_post_comments(post_id: int, db: Session) -> list:
    """
    Возвращает список комментариев к посту
    Args:
        post_id (int): id поста
        db (Session): сессия бд
    Returns:
        list - список обьектов Comment
    """
    result_db = await db.execute(select(Comment).filter(Comment.post_id==post_id))
    return result_db.scalars().all()
