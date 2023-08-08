from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Request, Form, Header
from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from typing import Optional, List

from .. import models, schemas, oauth2
from ..database import  get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

router = APIRouter(
    prefix="/vacuums",
    tags=["vacuums"],
)

templates = Jinja2Templates(directory="app/templates")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Vacuum)
def create_vacuum(vacuum: schemas.VacuumCreate, db: Session = Depends(get_db) ):

    new_vacuum = models.Vacuum( **vacuum.dict())
    db.add(new_vacuum)
    db.commit()
    db.refresh(new_vacuum)
    return {
        'message': "New test is created",
        'data': new_vacuum
    }

@router.get("/details/{inv_no}", status_code=status.HTTP_201_CREATED, response_model=schemas.Vacuum)
def get_vacuum(inv_no: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    print(current_user.email)
    vacuum = db.query(models.Vacuum).filter(models.Vacuum.inv_no == inv_no).first()
    if vacuum is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vacuum with inventory number {inv_no} is not found")
    return vacuum

@router.get("/", status_code=status.HTTP_201_CREATED, response_model=List[schemas.Vacuum])
def get_vacuums(db: Session = Depends(get_db)):
    # print(current_user)
    vacuums = db.query(models.Vacuum).all()
    return vacuums

@router.delete("/details/{inv_no}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vacuum(inv_no: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    print(current_user.email)
    vacuum_query = db.query(models.Vacuum).filter(models.Vacuum.inv_no == inv_no)
    vacuum = vacuum_query.first()
    if vacuum is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vacuum with inventory number {inv_no} is not found")

    if vacuum.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User with id number {current_user.id} is not authorized to delete this vacuum sample")

    vacuum_query.delete(synchronize_session=False)
    db.commit()
    return {
        'message': "Vacuum is deleted",
        'data': vacuum_query
    }

@router.put("/details/{inv_no}", response_model=schemas.Vacuum)
def update_vacuum(inv_no: int, updated_vacuum: schemas.VacuumCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    print(current_user.email)
    vacuum_query = db.query(models.Vacuum).filter(models.Vacuum.inv_no == inv_no)
    vacuum = vacuum_query.first()
    if vacuum is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vacuum with inventory number {inv_no} is not found")

    if vacuum.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User with id number {current_user.id} is not authorized to update this vacuum sample")

    vacuum_query.update(updated_vacuum.dict(), synchronize_session=False)
    db.commit()
    return {
        'message': "Vacuum is updated",
        'data': vacuum_query
    }


@router.get('/search-vacs/', response_model=List[schemas.VacuumBase])
async def search_vac(request: Request, db: Session = Depends(get_db), sample_tags: Optional[str] = None):


    vacs = db.query(models.Vacuum).filter((models.Vacuum.model_name.ilike(f'%{sample_tags}%')) | (models.Vacuum.brand.ilike(f'%{sample_tags}%')) | (cast(models.Vacuum.inv_no, String).ilike(f'%{sample_tags}%'))).all()

    return templates.TemplateResponse("vacuums/search-vacs.html", {"request": request, "vacs": vacs})

@router.get('/search-tester1/', response_model=List[schemas.UserOut])
async def search_user1(request: Request, db: Session = Depends(get_db), query: Optional[str] = None):


    users = db.query(models.User).filter((models.User.full_name.ilike(f'%{query}%')) | (models.User.email.ilike(f'%{query}%'))).all()

    return templates.TemplateResponse("users/search-tester1.html", {"request": request, "users": users})