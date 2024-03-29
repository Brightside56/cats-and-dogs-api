from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, ARRAY, Date, DateTime, Index
from sqlalchemy import UniqueConstraint
# from sqlalchemy.types import Date
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy import Table
from typing import Dict, Any
from sqlalchemy.dialects.postgresql import ENUM
import schemas

class Custom:
    """Some custom logic here!"""

    __table__: Table  # def for mypy

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        return cls.__name__  # pylint: disable= no-member

    def to_dict(self) -> Dict[str, Any]:
        """Serializes only column data."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Base = declarative_base(cls=Custom)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    address = Column(String)
    pets = relationship("Pet", back_populates="owner")

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    sex = Column(String, index=True)
    species = Column(String, index=True)
    birth_date = Column(Date, index=True) 
    image = Column(String)
    has_home = Column(Boolean, server_default='t', default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))    
    owner = relationship("User", back_populates="pets")
    posts = relationship("Post", backref="pets", cascade="all, delete")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("pets.id"))
    images = Column(ARRAY(String()))
    time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    comments = relationship("Comment", back_populates="post", cascade="all, delete")
    likes = relationship("Like", backref="posts", cascade="all, delete")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    post = relationship("Post", back_populates="comments")

class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("post_id", "owner_id", name="post_owner_key"),
    )

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

class Transfer(Base):
    __tablename__ = "transfers"
    # __table_args__ = (
    #     Index(
    #         'pet_unique_transfer',  # Index name
    #         'pet_id', 'status',  # Columns which are part of the index
    #         unique=True,
    #         postgresql_where=Column(f'status={schemas.TransferStatusEnum}')),  # The condition
    #     Index(
    #         'ix_unique_primary_content',  # Index name
    #         'pet_id', 'status',  # Columns which are part of the index
    #         unique=True,
    #         postgresql_where=Column('is_primary')),  # The condition

    # )

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), unique=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    applicant_id = Column(Integer, ForeignKey("users.id"))
    time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(ENUM(schemas.TransferStatusEnum), default=schemas.TransferStatusEnum.waiting, nullable=False)

class Shelter(Base):
    __tablename__ = "shelters"
    # __table_args__ = (
    #     UniqueConstraint("user_id", "pet_id", name="shelter_owner_key"),
    # )
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    pet_id = Column(Integer, ForeignKey("pets.id"))

