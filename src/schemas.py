from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class TransferStatusEnum(str,Enum):
  waiting = 'Waiting'
  rejected = 'Rejected'
  cancelled = "Cancelled"
  approved = "Approved"
  finished = "Finished"

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
    state: str | None = None
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
    state: Optional[str]
    city: Optional[str]
    address: Optional[str]
    phone: Optional[str]

class User(UserBase):
    id: int
    username: str
    email: str
    country: Optional[str]
    state: Optional[str]
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
    username: str | None = None    

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
    country: str | None = None
    state: str | None = None
    city: str | None = None    
    likes_count: int
    liked: Optional[bool] = False
    comments_count: int

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

class TransferBase(BaseModel):
    pet_id: int
    applicant_id: int

class TransferUpdate(TransferBase):
    status: TransferStatusEnum

class Transfer(TransferBase):
    id: int
    pet_id: int
    owner_id: int
    applicant_id: int
    status: TransferStatusEnum
    time: datetime

    class Config:
        orm_mode = True

class Shelter(BaseModel):
    user_id: int
    pet_id: int

    class Config:
        orm_mode = True

# class Shelter(ShelterBase):
#     id: int
#     owner_id: int
#     post_id: int

#     user_id = Column(Integer, unique=True, ForeignKey("users.id"))
#     pet_id = Column(Integer, ForeignKey("pets.id"))


#     class Config:
#         orm_mode = True


class Search(BaseModel):
    species: Optional[str]
    gte_date: Optional[date] | None = None
    sex: Optional[str]
    country: Optional[str]
    city: Optional[str]
    has_home: Optional[bool]
