"""
Импорты всякой необходимой шняги
"""
from typing import Union, Type, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_, func, desc
from .models import ( User, Post, Friendship, FriendshipRequest,
    VotingVariant, Like, Message, Vote, MediaInPost, Comment,
    MediaInMessage
)


async def add_and_refresh_object(
        object: Union[User, Post, Friendship, FriendshipRequest,
        VotingVariant, Like, Message, Vote, MediaInPost, Comment,
        MediaInMessage],
        db: AsyncSession
) -> None:
    """
    Добавляет обьект в бд и перезагружает его (получает автоматически созданные
    параметры обьекта, такие как id и created_at)
    Args:
        object (Union[User, Post, Friendship, FriendshipRequest, VotingVariant, Like, Message, Vote, MediaInPost]): обьект
        db (AsyncSession): Сессия базы данных.
    Returns:
        None
    """
    db.add(object)
    await db.commit()
    await db.refresh(object)


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """
    Получает пользователя по email из бд
    Args:
        email (str): email
        db (AsyncSession): Сессия базы данных.
    Returns:
        User: Объект пользователя или None.
    """
    result_email = await db.execute(select(User).filter(User.email == email))
    return result_email.scalars().first()


async def get_user_by_username(username: str, db: AsyncSession) -> User:
    """
    Получает пользователя по username пользователя.

    Args:
        username (str): Имя пользователя.
        db (AsyncSession): Сессия базы данных.
    Returns:
        User: Объект пользователя или None.
    """
    result_email = await db.execute(select(User).filter(User.username == username))
    return result_email.scalars().first()


async def delete_object(
    object: Union[User, Post, Friendship, FriendshipRequest,
    VotingVariant, Like, Message, Vote, Comment, MediaInPost,
    MediaInMessage],
    db: AsyncSession
) -> None:
    """
    Удаляет обьект из бд
    Args:
        object (Union[User, Post, Friendship, FriendshipRequest, VotingVariant, Like, Message, Vote, MediaInPost]): обьект
        db (AsyncSession): Сессия базы данных.
    Returns:
        None
    """
    await db.delete(object)
    await db.commit()


async def get_like_on_post_from_user(post_id: int, user_id: int, db: AsyncSession) -> Like:
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


async def get_likes_count(post_id: int, db: AsyncSession) -> int:
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


async def get_user_vote(var_id: int, user_id: int, db: AsyncSession) -> Vote:
    """
    Возвращает голос юзера на варианте голосования
    Args:
        var_id (int): id варианта
        user_id (int): id юзера
        db (AsyncSession): сессия бд
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
        author_id: int, getter_id: int, db: AsyncSession
) -> FriendshipRequest:
    """
    Получает существующий запрос на дружбу.

    Args:
        author_id (int): ID автора запроса.
        getter_id (int): ID получателя запроса.
        db (AsyncSession): Сессия базы данных.
    Returns:
        FriendshipRequest: Объект запроса на дружбу или None.
    """
    result = await db.execute(select(FriendshipRequest).filter(
        and_(FriendshipRequest.author_id == author_id, FriendshipRequest.getter_id == getter_id)
    ))
    return result.scalars().first()


async def get_existing_friendship(
        first_friend_id: int, second_friend_id: int, db: AsyncSession
) -> Friendship:
    """
    Получает существующую дружбу.

    Args:
        first_friend_id (int): ID первого друга.
        second_friend_id (int): ID второго друга.
        db (AsyncSession): Сессия базы данных.
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


async def get_all_from_table(
        object_type: Union[Type[User], Type[Post], Type[Friendship], Type[FriendshipRequest],
        Type[VotingVariant], Type[Like], Type[Message], Type[Vote], Type[MediaInPost],
        Type[MediaInMessage], Type[Comment]],
        db: AsyncSession, limit=None, skip=0
) -> list:
    """
    Получает все обьекты из таблицы бд
    (Если используете эту функцию с limit, то также укажите skip)
    Args:
        object_type: Модель, связанная с таблицей
        db (AsyncSession): сессия бд
        limit: ограничение на количество получаемых обьектов, по умолчанию None
        skip: сколько обьектов пропустить
    Returns:
        список обьектов
    """
    if limit:
        result = await db.execute(select(object_type).offset(skip).limit(limit))
        return result.scalars().all()
    result = await db.execute(select(object_type))
    return result.scalars().all()


async def get_post_voting_variants(post_id: int, db: AsyncSession) -> list:
    """
    Получает варианты голосования поста
    Args:
        post_id (int): id поста
        db (AsyncSession): сессия бд
    Returns:
        список обьектов VotingVariant
    """
    result_db = await db.execute(select(VotingVariant).filter(VotingVariant.post_id==post_id))
    return result_db.scalars().all()


async def get_object_by_id(
        object_type: Union[Type[User], Type[Post], Type[Friendship], Type[FriendshipRequest],
        Type[VotingVariant], Type[Like], Type[Message], Type[Vote], Type[MediaInPost],
        Type[MediaInMessage], Type[Comment]],
        id: int, db: AsyncSession
):
    """
    Получает обьект из бд по id
    Args:
        object_type: модель обьекта
        id (int): id обьекта
        db (AsyncSession): сессия бд
    Returns:
        обьект
    """
    result = await db.execute(select(object_type).filter(object_type.id==id))
    return result.scalars().first()


async def get_messages_between_two_users(first_user_id: int, second_user_id: int, db: AsyncSession) -> list:
    """
    Возвращает список сообщений между двумя пользователями
    Args:
        first_user_id (int): id первого пользователя
        second_user_id (int): id второго пользователя
        db (AsyncSession): сессия бд
    Returns:
        list - список обьектов Message
    """
    result_db = await db.execute(select(Message).filter(
        or_(
            and_(
                Message.author_id == first_user_id,
                Message.getter_id == second_user_id
            ),
            and_(
                Message.author_id == second_user_id,
                Message.getter_id == first_user_id
            )
        )
    ))
    return result_db.scalars().all()


async def get_images_id_for_message(message_id: int, db: AsyncSession) -> List[int]:
    """
    Получает список id картинок в бд, прикреплённых к сообщению
    Args:
        message_id (int): id поста
        db (AsyncSession): сессия бд
    Returns:
        list[int]
    """
    id_list=[]
    result_db = await db.execute(select(MediaInMessage).filter(MediaInMessage.message_id==message_id))
    for img in result_db.scalars().all():
        id_list.append(img.id)
    return id_list


async def get_votes_on_voting_variant(variant_id: int, db: AsyncSession) -> List[Vote]:
    """
    Возвращает голоса на варианте голосования с жадной загрузкой пользователей
    Args:
        variant_id (int): id варианта голосования
        db (AsyncSession): сессия бд
    Returns:
        List[Vote] - список голосов с подгруженными пользователями
    """
    result = await db.execute(
        select(Vote)
        .options(joinedload(Vote.user))  # Жадная загрузка пользователя
        .filter(Vote.variant_id == variant_id)
    )
    return result.scalars().all()

async def get_user_posts(user_id: int, db: AsyncSession) -> list:
    """
    Возвращает посты пользователя
    Args:
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        list
    """
    result_db = await db.execute(select(Post).filter(Post.author_id == user_id))
    return result_db.scalars().all()


async def get_user_friends(user_id: int, db: AsyncSession):
    """
    Возвращает список друзей пользователя
    Args:
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        list
    """
    result_db = await db.execute(select(Friendship).filter(
        or_(
            Friendship.first_friend_id==user_id,
            Friendship.second_friend_id==user_id
        )
    ).options(
        joinedload(Friendship.first_friend),
        joinedload(Friendship.second_friend)
    ))
    friends_list = []
    for friendship in result_db.scalars().all():
        if friendship.first_friend_id==user_id:
            friends_list.append(friendship.second_friend)
        else:
            friends_list.append(friendship.first_friend)
    return friends_list


async def get_friendship_requests_for_user(user_id: int, db: AsyncSession):
    """
    Возвращает запросы дружбы отправленные пользователю, с
    информацией об отправителе
    Args:
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        массив обьектов
    """
    result_db = await db.execute(select(FriendshipRequest).filter(
        FriendshipRequest.getter_id==user_id
    ).options(
        joinedload(FriendshipRequest.author)
    ))
    return result_db


