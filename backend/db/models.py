from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, LargeBinary
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # hash
    name = Column(String)
    surname = Column(String)
    avatar = Column(LargeBinary)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    # complaints_about_comments = relationship("ComplaintAboutComment", back_populates="author", cascade="all, delete-orphan")
    # complaints_about_posts = relationship("ComplaintAboutPost", back_populates="author", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")
    friendship_requests_sent = relationship("FriendshipRequest", foreign_keys="FriendshipRequest.author_id", back_populates="author", cascade="all, delete-orphan")
    friendship_requests_received = relationship("FriendshipRequest", foreign_keys="FriendshipRequest.getter_id", back_populates="getter", cascade="all, delete-orphan")
    messages_sent = relationship("Message", foreign_keys="Message.author_id", back_populates="author", cascade="all, delete-orphan")
    messages_received = relationship("Message", foreign_keys="Message.getter_id", back_populates="getter", cascade="all, delete-orphan")
    # subscriptions = relationship("Subscribe", foreign_keys="Subscribe.subscriber_id", back_populates="subscriber", cascade="all, delete-orphan")
    # subscribers = relationship("Subscribe", foreign_keys="Subscribe.contentmaker_id", back_populates="contentmaker", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="author", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    # complaints = relationship("ComplaintAboutComment", back_populates="comment", cascade="all, delete-orphan")


# class ComplaintAboutComment(Base):
#     __tablename__ = 'complaints_about_comment'
#     id = Column(Integer, primary_key=True)
#     author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     comment_id = Column(Integer, ForeignKey('comments.id'), nullable=False)
#     created_at = Column(DateTime, default=datetime.now)
#
#     author = relationship("User", back_populates="complaints_about_comments")
#     comment = relationship("Comment", back_populates="complaints")
#
# class ComplaintAboutPost(Base):
#     __tablename__ = 'complaints_about_post'
#     id = Column(Integer, primary_key=True)
#     author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
#     created_at = Column(DateTime, default=datetime.now)
#
#     author = relationship("User", back_populates="complaints_about_posts")
#     post = relationship("Post", back_populates="complaints")


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    # complaints = relationship("ComplaintAboutPost", back_populates="post", cascade="all, delete-orphan")
    voting_variants = relationship("VotingVariant", back_populates="post", cascade="all, delete-orphan")
    media = relationship("MediaInPost", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")


class VotingVariant(Base):
    __tablename__ = 'voting_variants'
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    post = relationship("Post", back_populates="voting_variants")
    votes = relationship("Vote", back_populates="variant", cascade="all, delete-orphan")


class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('voting_variants.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="votes")
    variant = relationship("VotingVariant", back_populates="votes")


class Friendship(Base):
    __tablename__ = 'friendship'
    id = Column(Integer, primary_key=True)
    first_friend_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    second_friend_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    first_friend = relationship("User", foreign_keys=[first_friend_id])
    second_friend = relationship("User", foreign_keys=[second_friend_id])


class FriendshipRequest(Base):
    __tablename__ = 'friendship_requests'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    getter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    author = relationship("User", foreign_keys=[author_id], back_populates="friendship_requests_sent")
    getter = relationship("User", foreign_keys=[getter_id], back_populates="friendship_requests_received")


# class Subscribe(Base):
#     __tablename__ = 'subscribe'
#     id = Column(Integer, primary_key=True)
#     subscriber_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     contentmaker_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     created_at = Column(DateTime, default=datetime.now)
#
#     subscriber = relationship("User", foreign_keys=[subscriber_id], back_populates="subscriptions")
#     contentmaker = relationship("User", foreign_keys=[contentmaker_id], back_populates="subscribers")


class MediaInPost(Base):
    __tablename__ = 'media_in_post'
    id = Column(Integer, primary_key=True)
    image = Column(LargeBinary)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    post = relationship("Post", back_populates="media")


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    getter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    author = relationship("User", foreign_keys=[author_id], back_populates="messages_sent")
    getter = relationship("User", foreign_keys=[getter_id], back_populates="messages_received")
    media = relationship("MediaInMessage", back_populates="message", cascade="all, delete-orphan")


class MediaInMessage(Base):
     __tablename__ = 'media_in_message'
     id = Column(Integer, primary_key=True)
     message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
     image = Column(LargeBinary)
     created_at = Column(DateTime, default=datetime.now)

     message = relationship("Message", back_populates="media")


class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)

    author = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")


# async def create_database():
#     async with engine.begin() as conn:
#         # Используем run_sync для создания таблиц
#         await conn.run_sync(Base.metadata.create_all)

