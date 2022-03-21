from pydantic import BaseModel
from typing import Optional
from datetime import date

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
    pets: list[Pet] = []

    class Config:
        orm_mode = True



# class PetCreate(PetBase):
#     id: int
#     sex: 

# class Pet(PetBase):
