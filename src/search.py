from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.inspection import inspect
from sqlalchemy import exc
import models, schemas
from database import SessionLocal, engine
from sqlalchemy.orm import joinedload
from sqlalchemy.inspection import inspect

def get_posts(db: Session, offset: int, limit: int, query: schemas.Search, user_id: int = None):
    search = db.query(models.Post,models.Pet,models.User).filter(models.Pet.id == models.Post.owner_id, models.User.id == models.Pet.owner_id).distinct(models.Pet.id).order_by(models.Pet.id.desc(),models.Post.time.desc())

    print(query.species)
    if query.species is not None and query.species is not "":
        search = search.filter(models.Pet.species == query.species)

    if query.sex is not None and len(query.sex) > 0:
        search = search.filter(models.Pet.sex == query.sex)

    if query.gte_date is not None and query.gte_date:
        search = search.filter(models.Pet.birth_date >= query.gte_date)

    if query.country is not None and len(query.country) > 0:
        search = search.filter(models.User.country == query.country)

    if query.city is not None and len(query.city) > 0:
        search = search.filter(models.User.city == query.city)

    if query.has_home is not None and len(query.has_home) > 0:
        search = search.filter(models.Pet.has_home == query.has_home)

    result = search.offset(offset).limit(limit).all()

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
            post['liked'] = bool(db.query(models.Like).filter(models.Like.post_id == post['id'], models.Like.owner_id == user_id).count())
        else:
            post['liked'] = False
        posts.append(post)
    return posts
