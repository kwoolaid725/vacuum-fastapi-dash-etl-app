from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Request, Form, Header, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from .. import models, schemas, oauth2
from ..database import  get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from dataclasses import dataclass

router = APIRouter(
    prefix="/users",
    tags=["users"],
)
templates = Jinja2Templates(directory="app/templates")
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hashed_password = utils.hash(user.password)
    # user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        'message': "New data is entered",
        'data': new_user,
        'status': status.HTTP_201_CREATED
    }
@router.get("/", status_code=status.HTTP_201_CREATED, response_model=List[schemas.UserOut])
def get_users(db: Session = Depends(get_db)):

    # print(current_user)
    users = db.query(models.User).all()
    return users

@router.get('/details/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id number {id} is not found")
    return user
#



@router.get('/search-tester1/', response_model=List[schemas.UserOut])
async def search_user1(request: Request, db: Session = Depends(get_db), query: Optional[str] = None):


    users = db.query(models.User).filter((models.User.full_name.ilike(f'%{query}%')) | (models.User.email.ilike(f'%{query}%'))).all()

    return templates.TemplateResponse("users/search-tester1.html", {"request": request, "users": users})

@router.get('/search-tester2/', response_model=List[schemas.UserOut])
async def search_user2(request: Request, db: Session = Depends(get_db), query: Optional[str] = None):


    users = db.query(models.User).filter((models.User.full_name.ilike(f'%{query}%')) | (models.User.email.ilike(f'%{query}%'))).all()

    return templates.TemplateResponse("users/search-tester2.html", {"request": request, "users": users})




@router.post('/search/', response_class=HTMLResponse)
async def search_user(request: Request, result: str):
    return templates.TemplateResponse("users/search.html",{"request":request, "result": result})


@router.get('/search/', response_class=HTMLResponse)
async def search_user(request: Request):

    return templates.TemplateResponse("users/search.html",{"request":request})


