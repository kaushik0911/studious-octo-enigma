from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from api_schema import NamedEntityCreate, NamedEntityRead
from database import get_session
from models import Category

router = APIRouter()


@router.get(
    "/categories/",
    response_model=list[NamedEntityRead],
    tags=["Categories"],
)
def read_categories(session: Session = Depends(get_session)):
    categories = session.query(Category).all()
    return categories


@router.post(
    "/categories/",
    response_model=NamedEntityRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Categories"],
)
def create_category(cat: NamedEntityCreate, session: Session = Depends(get_session)):
    db_cat = Category.model_validate(cat)
    session.add(db_cat)
    session.commit()
    session.refresh(db_cat)
    return db_cat
