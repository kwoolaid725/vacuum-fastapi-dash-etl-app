from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Request, Form, Header
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from typing import Optional, List

from .. import models, schemas, oauth2
from ..database import  get_db

from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates




router = APIRouter(
    prefix="/tests",
    tags=["tests"],
)

templates = Jinja2Templates(directory="app/templates")

# @router.get("/", status_code=status.HTTP_201_CREATED, response_model=List[schemas.Test])
# def get_tests(db: Session = Depends(get_db)):
#
#     # print(current_user)
#     tests = db.query(models.Test).all()
#     return tests

@router.get("/", status_code=status.HTTP_201_CREATED, response_class=HTMLResponse, response_model=schemas.Test)
def get_tests(request: Request, db: Session = Depends(get_db), hx_request: Optional[str] = Header(None), category: Optional[str] = None):

    tests = db.query(models.Test).join(models.test_vacuums).join(models.Vacuum).join(models.User).order_by(desc(models.Test.id))\
        .filter(models.test_vacuums.c.test_id == models.Test.id,
                models.test_vacuums.c.vacuum_inv_no == models.Vacuum.inv_no).all()
    test_category = db.query(models.TestCategory.name).distinct().order_by(models.TestCategory.name).all()

    cat_vac = db.query(models.TestCategory.name, models.VacType.vactype).join(models.VacType).filter(
        (models.TestCategory.name.ilike(f'%{category}%'))).all()

    print(test_category)
    print(cat_vac)
    context = {"request": request,
               "tests": tests,
                "test_category": test_category,
                "cat_vac": cat_vac}

    return templates.TemplateResponse("tests/tests.html", context)



@router.post("/add", status_code=status.HTTP_201_CREATED, response_class=HTMLResponse, response_model=schemas.Test)
async def add_test(request: Request, test: schemas.TestCreate = Depends(schemas.TestCreate.as_form), db: Session = Depends(get_db)):
    data = models.Test(**test.dict())
    test_category = db.query(models.TestCategory).all()
    # new_test to json
    new_test = jsonable_encoder(data)
    db.add(data)
    db.commit()
    db.refresh(data)
    # response = templates.TemplateResponse("tests/tests.html", {"request": request})
    # response.headers['HX-Redirect'] = "http://localhost:8000/tests/"

    # return JSONResponse(content=new_test, response= status_code=status.HTTP_201_CREATED)
    redirect_url = request.url_for('get_tests')
    # return templates.TemplateResponse("tests/tests.html", {"request": request})
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)




@router.get("/details/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.Test)
def get_test(id: int, db: Session = Depends(get_db)):

    test = db.query(models.Test).filter(models.Test.id == id).first()
    if test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Test with id number {id} is not found")
    return test



@router.delete("/details/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test(id: int, db: Session = Depends(get_db)):

    test_query = db.query(models.Test).filter(models.Test.id == id)
    test = test_query.first()
    if test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Test with id number {id} is not found")

    # if test.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                         detail=f"User with id number {current_user.id} is not authorized to delete this test")

    test_query.delete(synchronize_session=False)
    db.commit()
    return {
        'message': "Test is deleted",
        'data': test_query
    }

@router.put("/details/{id}", response_model=schemas.Test)
def update_test(id: int, updated_test: schemas.TestCreate, db: Session = Depends(get_db)):

    test_query = db.query(models.Test).filter(models.Test.id == id)
    test = test_query.first()
    if test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Test with id number {id} is not found")

    # if test.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"User with id number {current_user.id} is not authorized to update this test")

    test_query.update(updated_test.dict(), synchronize_session=False)
    updated = jsonable_encoder(models.Test(**updated_test.dict()))
    db.commit()
    return JSONResponse(content=updated)


@router.get("/categories/", status_code=status.HTTP_201_CREATED)
def get_test_categories(request: Request, db: Session = Depends(get_db), category: Optional[str] = None ):
    # categories = db.query(models.TestCategory.name).filter(func.lower(models.TestCategory.name) == func.lower(name)).distinct().order_by(models.TestCategory.name).all()

    cat_vac = db.query(models.TestCategory.name, models.VacType.vactype).join(models.VacType).filter(
        (models.TestCategory.name.ilike(f'%{category}%'))).all()

    print(cat_vac)

    context = {"request": request,
               "cat_vac": cat_vac}

    return templates.TemplateResponse("tests/categories.html", context)



@router.get("/categories/{name}", status_code=status.HTTP_201_CREATED, response_model=schemas.TestCategory)
def get_test_categories(name: str, request: Request, db: Session = Depends(get_db)):

    # categories = db.query(models.TestCategory.name).filter(func.lower(models.TestCategory.name) == func.lower(name)).distinct().order_by(models.TestCategory.name).all()
    categories = db.query(models.TestCategory.name).filter(func.lower(models.TestCategory.name) == func.lower(name)).first()
    print(categories)



    context = {"request": request,
               "categories": categories}

    return templates.TemplateResponse("tests/categories.html", context)


@router.get("/categories/{name}/vac-types", status_code=status.HTTP_201_CREATED)
def get_test_categories(name: str, request: Request, db: Session = Depends(get_db)):


    # vactypes = db.query(models.VacType.vactype).join(models.TestCategory).filter(func.lower(models.TestCategory.name) == func.lower(name)).all()
    vactypes = db.query(models.TestCatgegory.name, models.VacType.vactype).join(models.VacType).filter(func.lower(models.TestCategory.name) == func.lower(name)).all()
    print(vactypes)
    print(name)


    context = {"request": request,
               "data": vactypes}

    return templates.TemplateResponse("tests/partials/category-vactypes.html", context)

# @router.get("/categories/vac_types", status_code=status.HTTP_201_CREATED, response_class=HTMLResponse)
# def get_vac_types(request: Request, db: Session = Depends(get_db)):
#
#
#     context = {"request": request,
#                "data": data}
#
#     return templates.TemplateResponse("vacuums/vac_types.html", context)