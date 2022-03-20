from pydantic import BaseModel
from typing import Optional

class Auth(BaseModel):
    username: str
    password: str

class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    username: str
    email: str
    password: str

class User(UserBase):
    id: int
    username: str
    email: str
    country: Optional[str]
    city: Optional[str]
    # is_active: bool
    # items: list[Item] = []

    class Config:
        orm_mode = True