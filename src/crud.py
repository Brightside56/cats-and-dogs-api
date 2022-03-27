from sqlalchemy.orm import Session
from sqlalchemy import desc

import models, schemas


def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user.to_dict()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    users = db.query(models.User).offset(skip).limit(limit).all()
    filtered_users = []
    for user in users:
        filtered_users.append(user.to_dict())
    return filtered_users


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, username=user.username, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user.to_dict()

def update_user(db: Session, user: schemas.UserUpdate, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user.to_dict()


def get_pet(db: Session, pet_id: int):
    pet = db.query(models.Pet,models.User.country.label('country'),models.User.city.label('city')).join(models.User).filter(models.Pet.owner_id == models.User.id, models.Pet.id == pet_id).first()
    if pet:
        pet_dict = pet[0].to_dict()
        pet_dict['country'] = pet[1]
        pet_dict['city'] = pet[2]
        return pet_dict
    else:
        return []

def get_pets(db: Session, offset: int = 0, limit: int = 100):
    pets = db.query(models.Pet,models.User.country.label('country'),models.User.city.label('city')).join(models.User).filter(models.Pet.owner_id == models.User.id).offset(offset).limit(limit).all()
    pets_filtered = []
    for pet in pets:
        pet_dict = pet[0].to_dict()
        pet_dict['country'] = pet[1]
        pet_dict['city'] = pet[2]
        pets_filtered.append(pet_dict)
        
    return pets_filtered

def create_pet(db: Session, pet: schemas.PetCreate, user_id: int):
    db_pet = models.Pet(**pet.dict(), owner_id=user_id)
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet.to_dict()

def update_pet(db: Session, pet: schemas.PetUpdate, pet_id: int):
    db_pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    for key, value in pet.dict(exclude_unset=True).items():
        setattr(db_pet, key, value)
    db.commit()
    db.refresh(db_pet) #refresh the attribute of the given instan
    return db_pet.to_dict()


def get_post(db: Session, post_id: int):
    post = db.query(models.Post, models.Pet.name.label('name'), models.Pet.image.label('avatar')).join(models.Pet).filter(models.Post.id == post_id, models.Pet.id == models.Post.owner_id).first()
    if post:
        post_dict = post[0].to_dict()
        post_dict['name'] = post[1]
        post_dict['avatar'] = post[2]
        return post_dict
    else:
        return []

def get_posts(db: Session, offset: int = 0, limit: int = 100, pet_id: int = None):
    if pet_id is not None:
        posts = db.query(models.Post, models.Pet.name.label('name'), models.Pet.image.label('avatar')).join(models.Pet).filter(models.Post.owner_id==pet_id, models.Post.owner_id == models.Pet.id).order_by(desc(models.Post.time)).offset(offset).limit(limit).all()
    else:
        posts = db.query(models.Post, models.Pet.name.label('name'), models.Pet.image.label('avatar')).join(models.Pet).filter(models.Post.owner_id == models.Pet.id).order_by(desc(models.Post.time)).offset(offset).limit(limit).all()
    
    filtered_posts = []
    for post in posts:
        post_dict = post[0].to_dict()
        post_dict['name'] = post[1]
        post_dict['avatar'] = post[2]
        filtered_posts.append(post_dict)
    return filtered_posts

def create_post(db: Session, post: schemas.PostCreate, owner_id: int):
    db_post = models.Post(**post.dict(), owner_id=owner_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    created_post = db_post.to_dict()
    pet = db.query(models.Pet).filter(models.Pet.id == owner_id).first()
    created_post['name'] = pet.name
    created_post['avatar'] = pet.image
    
    return created_post

def update_post(db: Session, post: schemas.PostCreate, post_id: int):
    db_post = get_post(db=db, post_id=post_id)
    for key, value in post.items():
        if value is not None:
            setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return post


def get_comment(db: Session, comment_id: int):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    return comment.to_dict()

def get_comments(db: Session, offset: int = 0, limit: int = 100, post_id: int = None):
    if post_id is not None:
        comments = db.query(models.Comment).filter(models.Comment.post_id==post_id).order_by(desc(models.Comment.time)).offset(offset).limit(limit).all()
    else:
        comments = db.query(models.Comment).order_by(desc(models.Comment.time)).offset(offset).limit(limit).all()
    
    filtered_comments = []
    for comment in comments:
        filtered_comments.append(comment.to_dict())
    return filtered_comments

def create_comment(db: Session, comment: schemas.CommentCreate):
    db_comment = models.Comment(**comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment.to_dict()

def update_comment(db: Session, comment: schemas.CommentBase, comment_id: int):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    for key, value in comment:
        setattr(db_comment, key, value)
    db.commit()
    db.refresh(db_comment) 
    return db_comment.to_dict()

def delete_comment(db: Session, comment_id: int):
    db.execute(models.Comment.delete().where(models.Comment.id == comment_id))
    db.commit()
    return comment_id

def get_likes(db: Session, post_id: int):
    likes = db.query(models.Like).filter(models.Comment.post_id==post_id).order_by(desc(models.Comment.time)).offset(offset).limit(limit).all()
    return len(likes)

def create_like(db: Session, comment: schemas.LikeCreate):
    db_like = models.Like(**like.dict())
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like.to_dict()

def delete_like(db: Session, comment: schemas.LikeCreate, like_id: int):
    db.execute(models.Like.delete().where(models.Like.id == like_id))
    db.commit()
    return like_id