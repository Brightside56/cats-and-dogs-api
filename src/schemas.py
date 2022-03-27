from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class Auth(BaseModel):
    username: str
    password: str

class PetBase(BaseModel):
    name: str
    description: str | None = None
    sex: str
    species: str
    birth_date: date
    image: str | None = None
    has_home: bool

class PetCreate(PetBase):
    pass

class Pet(PetBase):
    id: int
    name: str
    description: str | None = None
    sex: str
    species: str
    birth_date: date
    image: str | None = None
    has_home: bool
    owner_id: int
    country: str | None = None
    city: str | None = None

    class Config:
        orm_mode = True

class PetUpdate(PetBase):
    name: Optional[str]
    description: Optional[str]
    sex: Optional[str]
    species: Optional[str]
    birth_date: Optional[date]
    image: Optional[str]
    has_home: Optional[bool]

class UserBase(BaseModel):
    pass

class UserCreate(UserBase):
    username: str
    email: str
    password: str

class UserUpdate(UserBase):
    email: Optional[str]
    country: Optional[str]
    city: Optional[str]
    address: Optional[str]
    phone: Optional[str]

class User(UserBase):
    id: int
    username: str
    email: str
    country: Optional[str]
    city: Optional[str]
    address: Optional[str]
    phone: Optional[str]

    # is_active: bool
    pets: list[Pet] = []
    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    owner_id: int
    post_id: int

class Comment(CommentBase):
    id: int
    text: str
    time: datetime
    owner_id: int
    post_id: int

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    text: Optional[str]
    images: List[str] | None = None

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    text: Optional[str]
    images: List[str] | None = None
    time: datetime
    owner_id: int
    avatar: Optional[str]
    name: str
    
    comments: list[Comment] = []
    class Config:
        orm_mode = True


class LikeBase(BaseModel):
    owner_id: int
    post_id: int

class LikeCreate(LikeBase):
    pass

class Like(LikeBase):
    id: int
    owner_id: int
    post_id: int

    class Config:
        orm_mode = True
