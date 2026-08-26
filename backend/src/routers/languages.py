from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from api_schema import NamedEntityCreate, NamedEntityRead
from database import get_session
from models import Language

router = APIRouter()


@router.get(
    "/languages/",
    response_model=list[NamedEntityRead],
    tags=["Languages"],
)
def read_languages(session: Session = Depends(get_session)):
    languages = session.query(Language).all()
    return languages


@router.post(
    "/languages/",
    response_model=NamedEntityRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Languages"],
)
def create_language(lang: NamedEntityCreate, session: Session = Depends(get_session)):
    db_lang = Language.model_validate(lang)
    session.add(db_lang)
    session.commit()
    session.refresh(db_lang)
    return db_lang
