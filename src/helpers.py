from sqlalchemy.orm import Session

import models, schemas

def check_auth(db: Session, auth: schemas.Auth):
    user = db.query(models.User).filter(models.User.username == auth.username).first()
    if user is not None:
        if user.hashed_password == auth.password + "notreallyhashed":
            return user.id

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()
    