import re
import inspect
import uuid
import os
import aiofiles
from datetime import date
from fastapi import FastAPI, HTTPException, Depends, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import crud, models, schemas, helpers
from database import SessionLocal, engine
from typing import List, Optional


IMAGES_PET_AVATARS = 'static/pet_avatars/'
IMAGES_POST_IMAGES = 'static/post_images/'
IMAGES_PUBLIC_URL = 'https://api2.adoptpets.click'

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"

@AuthJWT.load_config
def get_config():
    return Settings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.post('/auth/login')
def auth_login(auth: schemas.Auth, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    user_id = helpers.check_auth(db, auth)
    if not user_id:
        raise HTTPException(status_code=401,detail="Bad username or password")
    else:
        access_token = Authorize.create_access_token(subject=user_id)
        refresh_token = Authorize.create_refresh_token(subject=user_id)
    return {"access": access_token, "refresh": refresh_token}

@app.post('/auth/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    """
    The jwt_refresh_token_required() function insures a valid refresh
    token is present in the request before running any code below that function.
    we can use the get_jwt_subject() function to get the subject of the refresh
    token, and use the create_access_token() function again to make a new access token
    """
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {"access": new_access_token}

@app.post('/users', response_model=schemas.User)
def user_add(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.get('/users/me', response_model=schemas.User)
def user_me(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    user = helpers.get_user_by_id(db, Authorize.get_jwt_subject())
    if user is not None and 'pets' in user:
        for i in range(len(user['pets'])):
            if user['pets'][i]['image'] is not None:
                user['pets'][i]['image'] = IMAGES_PUBLIC_URL + user['pets'][i]['image']
    return user

@app.put("/users/me", response_model=schemas.UserUpdate)
def user_me_update(user: schemas.UserUpdate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    updated_user = crud.update_user(db=db, user=user, user_id=Authorize.get_jwt_subject())
    return updated_user

@app.post('/pets', response_model=schemas.Pet)
async def pets_add(name: str = Form(...), description: str = Form(...), sex: str = Form(...), species: str = Form(...), birth_date: date = Form(...), has_home: bool = Form(...), image: UploadFile | None = None, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    file = image
    if not file:
        avatar = None
        pass
    else:
        if file.content_type not in ['image/jpeg', 'image/png']:
            raise HTTPException(status_code=406, detail="Only .jpeg or .png  files allowed")
        _, ext = os.path.splitext(file.filename)
        file_name = f'{uuid.uuid4().hex}{ext}'
        async with aiofiles.open(IMAGES_PET_AVATARS + file_name, 'wb') as f:
            while content := await file.read(1024):  # async read chunk
                await f.write(content)  # async write chunk        
        
        avatar = '/' + IMAGES_PET_AVATARS + file_name
    
    pet = schemas.PetCreate(name=name, description=description, sex=sex, species=species, birth_date=birth_date, has_home=has_home, image=avatar)
    created_pet = crud.create_pet(db=db, pet=pet, user_id=Authorize.get_jwt_subject())
    if created_pet['image'] is not None:
        created_pet['image'] = IMAGES_PUBLIC_URL + created_pet['image']
    return created_pet

@app.get('/pets', response_model=list[schemas.Pet])
def pets_get(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pets = crud.get_pets(db=db, offset=offset, limit=limit)
    for i in range(len(pets)):
        if pets[i]['image'] is not None:
            pets[i]['image'] = IMAGES_PUBLIC_URL + pets[i]['image']
    return pets

@app.get('/pets/{pet_id}', response_model=schemas.Pet)
def pet_get(pet_id: int, db: Session = Depends(get_db)):
    pet = crud.get_pet(db=db, pet_id=pet_id)
    if pet is not None:
        if 'image' in pet:
            pet['image'] = IMAGES_PUBLIC_URL + pet['image']
        return pet
    else:
        raise HTTPException(status_code=404, detail="Pet with such id not found")


@app.put("/pet/{pet_id}", response_model=schemas.Pet)
def pet_update(pet_id: int, pet: schemas.PetUpdate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    pet_by_id = crud.get_pet(db=db, pet_id=pet_id)
    if pet_by_id['owner_id'] == Authorize.get_jwt_subject():
        updated_pet = crud.update_pet(db=db, pet=pet, pet_id=pet_id)
    else:
        raise HTTPException(status_code=422, detail="Wrong owner of pet")   

    if updated_pet is not None:
        if updated_pet['image'] is not None:
            updated_pet['image'] = IMAGES_PUBLIC_URL + updated_pet['image']
        return updated_pet
    else:
        raise HTTPException(status_code=404, detail="Pet with such id not found")
     



@app.post('/pets/{pet_id}/posts', response_model=schemas.Post)
async def pet_posts_add(pet_id: int, text: Optional[str] = Form(None), image_files: List[UploadFile] = File(...), Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    images = []
    if image_files is None:
        raise HTTPException(status_code=422, detail="You cannot create post without images")
    else:
        for image_file in image_files:
            if image_file.content_type not in ['image/jpeg', 'image/png']:
                pass
            else:
                _, ext = os.path.splitext(image_file.filename)
                file_name = f'{uuid.uuid4().hex}{ext}'
                async with aiofiles.open(IMAGES_POST_IMAGES + file_name, 'wb') as f:
                    while content := await image_file.read(1024):  # async read chunk
                        await f.write(content)  # async write chunk        
                
                images.append('/' + IMAGES_POST_IMAGES + file_name)
    
    # check if pet is owned by user
    pet_by_id = pet_get(pet_id, db)

    if 'owner_id' in pet_by_id and pet_by_id['owner_id'] == Authorize.get_jwt_subject():
        post = schemas.PostCreate(text=text, images=images)
        created_post = crud.create_post(db=db, post=post, owner_id=Authorize.get_jwt_subject())
        if 'images' in created_post:
            for i in range(len(created_post['images'])):
                created_post['images'][i] = IMAGES_PUBLIC_URL + created_post['images'][i]
        if 'avatar' in created_post:
            created_post['avatar'] = IMAGES_PUBLIC_URL + created_post['avatar']
        return created_post
    else:
        raise HTTPException(status_code=422, detail="Wrong owner of pet")

@app.get('/pets/{pet_id}/posts', response_model=List[schemas.Post])
def pet_posts_get(pet_id: int, db: Session = Depends(get_db)):
    posts = crud.get_posts(db=db, pet_id=pet_id)
    if posts:
        for p in range(len(posts)):
            for i in range(len(posts[p]['images'])):
                posts[p]['images'][i] = IMAGES_PUBLIC_URL + posts[p]['images'][i]
            if 'avatar' in posts[p]:
                posts[p]['avatar'] = IMAGES_PUBLIC_URL + posts[p]['avatar']
    return posts

@app.get('/posts', response_model=List[schemas.Post])
def posts_get(db: Session = Depends(get_db)):
    posts = crud.get_posts(db=db)
    if posts:
        for p in range(len(posts)):
            for i in range(len(posts[p]['images'])):
                posts[p]['images'][i] = IMAGES_PUBLIC_URL + posts[p]['images'][i]
            if 'avatar' in posts[p]:
                posts[p]['avatar'] = IMAGES_PUBLIC_URL + posts[p]['avatar']
    return posts

@app.get('/posts/{post_id}', response_model=schemas.Post)
def posts_get(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db=db, post_id=post_id)
    if post:
        for i in range(len(post['images'])):
            post['images'][i] = IMAGES_PUBLIC_URL + post['images'][i]
        if 'avatar' in post:
            post['avatar'] = IMAGES_PUBLIC_URL + post['avatar']
        return post
    else:
        raise HTTPException(status_code=404, detail="Post not found")

@app.get('/posts/{post_id}/likes', response_model=int)
def posts_get(post_id: int, db: Session = Depends(get_db)):
    return crud.get_likes(db=db, post_id=post_id)

@app.post('/posts/{post_id}/like', response_model=int)
def posts_get(post_id: int, db: Session = Depends(get_db)):
    return crud.create_like(db=db, post_id=post_id)

@app.delete('/posts/{post_id}/like', response_model=int)
def posts_get(post_id: int, db: Session = Depends(get_db)):
    return crud.get_likes(db=db, post_id=post_id)

@app.get('/comments', response_model=List[schemas.Comment])
def comments_get(db: Session = Depends(get_db)):
    return crud.get_comments(db=db)

@app.post('/comments', response_model=schemas.Comment)
async def comments_add(comment: schemas.CommentCreate, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    comment.owner_id = Authorize.get_jwt_subject()
    return crud.create_comment(db=db, comment=comment)

@app.get('/comments/{comment_id}', response_model=schemas.Comment)
def comment_get(comment_id: int, db: Session = Depends(get_db)):
    return crud.get_comment(db=db, comment_id=comment_id)

@app.put('/comments/{comment_id}', response_model=schemas.Comment)
async def comments_update(comment_id: int, comment: schemas.CommentBase, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    comment_source = crud.get_comment(comment_id=comment_id, db=db)
    if comment_source['owner_id'] == Authorize.get_jwt_subject():
        return crud.update_comment(db=db, comment=comment, comment_id=comment_id)

@app.delete('/comments/{comment_id}', response_model=int)
async def comments_delete(comment_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    comment_source = crud.get_comment(comment_id=comment_id, db=db)
    if comment_source['owner_id'] == Authorize.get_jwt_subject():
        return crud.delete_comment(db=db, comment_id=comment_id)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title = "My Auth API",
        version = "1.0",
        description = "An API with an Authorize Button",
        routes = app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }

    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route,"endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            # access_token
            if (
                re.search("jwt_required", inspect.getsource(endpoint)) or
                re.search("fresh_jwt_required", inspect.getsource(endpoint)) or
                re.search("jwt_optional", inspect.getsource(endpoint))
            ):
                openapi_schema["paths"][path][method]["security"] = [
                    {
                        "Bearer Auth": []
                    }
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi