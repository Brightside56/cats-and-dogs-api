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


IMAGES_PET_AVATARS = 'static/pet_avatars/'
IMAGES_PUBLIC_URL = 'https://api.adoptpets.click'

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
    return user

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
    if created_pet.image is not None:
        created_pet.image = IMAGES_PUBLIC_URL + created_pet.image

    return created_pet

@app.get('/pets', response_model=list[schemas.Pet])
def pets_get(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pets = crud.get_pets(db=db, offset=offset, limit=limit)

    for i in range(len(pets)):
        if pets[i].image is not None:
            pets[i].image = IMAGES_PUBLIC_URL + pets[i].image
    return pets

@app.get('/pets/{pet_id}', response_model=schemas.Pet)
def pet_get(pet_id: int, db: Session = Depends(get_db)):
    pet = crud.get_pet(db=db, pet_id=pet_id)
    if pet is not None:
        if pet.image is not None:
            pet.image = IMAGES_PUBLIC_URL + pet.image
        return pet
    else:
        raise HTTPException(status_code=404, detail="Pet with such id not found")

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