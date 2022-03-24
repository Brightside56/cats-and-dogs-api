from sqlalchemy.orm import Session
from sqlalchemy import desc

import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, username=user.username, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: schemas.UserUpdate, user_id: int):
    db_user = get_user(db=db, user_id=user_id)
    for key, value in user.dict().items():
        if value is not None:
            setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user) #refresh the attribute of the given instan
    return user


def get_pet(db: Session, pet_id: int):
    # return db.query(*models.Pet.__table__.columns,models.User.country,models.User.city).join(models.User).filter(models.Pet.id == models.User.id, models.Pet.id == pet_id, ).first()
    pet = db.query(models.Pet,models.User.country.label('country'),models.User.city.label('city')).join(models.User).filter(models.Pet.owner_id == models.User.id, models.Pet.id == pet_id).first()
    
    pet[0].country = pet[1]
    pet[0].city = pet[2]
    
    
    return pet[0]

def get_pets(db: Session, offset: int = 0, limit: int = 100):
    pets = db.query(models.Pet,models.User.country.label('country'),models.User.city.label('city')).join(models.User).filter(models.Pet.owner_id == models.User.id).offset(offset).limit(limit).all()
    pets_filtered = []
    for pet in pets:
        pet[0].country = pet[1]
        pet[0].city = pet[2]
        pets_filtered.append(pet[0])
        
    return pets_filtered

def create_pet(db: Session, pet: schemas.PetCreate, user_id: int):
    db_pet = models.Pet(**pet.dict(), owner_id=user_id)
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

def update_pet(db: Session, user: schemas.Pet):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def get_posts(db: Session, offset: int = 0, limit: int = 100, pet_id: int = None):
    if pet_id is not None:
        return db.query(models.Post).filter(models.Post.owner_id==pet_id).order_by(desc(models.Post.time)).offset(offset).limit(limit).all()
    else:
        return db.query(models.Post).order_by(desc(models.Post.time)).offset(offset).limit(limit).all()

def create_post(db: Session, post: schemas.PostCreate):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def get_comments(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Comment).offset(offset).limit(limit).all()

def create_comment(db: Session, comment: schemas.PostCreate, user_id: int):
    db_comment = models.Comment(**comment.dict(), owner_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def get_comments(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Comment).offset(offset).limit(limit).all()

def create_comment(db: Session, comment: schemas.PostCreate, user_id: int):
    db_comment = models.Comment(**comment.dict(), owner_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment



# def get_like(db: Session, offset: int = 0, limit: int = 100, post_id: int, owner_id: int):
#     return db.query(models.Like).offset(offset).limit(limit).all()

# def get_likes(db: Session, offset: int = 0, limit: int = 100, post_id: int):
#     return db.query(models.Like).offset(offset).limit(limit).all()

# def create_like(db: Session, comment: schemas.LikeCreate, post_id: int, user_id: int):
#     db_like = models.Like(**comment.dict(), post_id=post_id, owner_id=user_id)
#     db.add(db_like)
#     db.commit()
#     db.refresh(db_like)
#     return db_like

# def delete_like(db: Session, comment_id: int):
#     return db.query(models.Comment).filter(models.Comment.id == comment_id).first()
