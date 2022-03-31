from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.inspection import inspect
from sqlalchemy import exc
import models, schemas
from database import SessionLocal, engine

from sqlalchemy.inspection import inspect

def get_posts(db: Session, offset: int, limit: int, query: schemas.Search, user_id: int = None):
    # with engine.connect() as con:

    #     rs = con.execute('SELECT images as images FROM posts')

    #     for row in rs:
    #         print(row)
    result = db.query(models.Post,models.Pet,models.User).filter(models.Pet.id == models.Post.owner_id, models.User.id == models.Pet.owner_id).all()
    posts = []
    for item in result:
        post = {}
        post['text'] = item[0].text
        post['images'] = item[0].images
        post['id'] = item[0].id
        post['time'] = item[0].time
        post['owner_id'] = item[0].owner_id
        post['avatar'] = item[1].image 
        post['name'] = item[1].name
        post['country'] = item[2].country
        post['city'] = item[2].city
        post['comments_count'] = len(item[0].comments)
        post['likes_count'] = db.query(models.Like).filter(models.Like.post_id == post['id']).count()
        if user_id is not None:
            print(db.query(models.Like).filter(models.Like.post_id == post['id'], models.Like.owner_id == user_id).count())
            post['liked'] = bool(db.query(models.Like).filter(models.Like.post_id == post['id'], models.Like.owner_id == user_id).count())
        else:
            post['liked'] = False
        posts.append(post)
    return posts
