from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from api_schema import UserCreate, UserRead
from database import get_session
from models import User

router = APIRouter()


@router.post(
    "/users/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/users/", response_model=List[UserRead], tags=["Users"])
def read_users(
    offset: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    return session.exec(select(User).offset(offset).limit(limit)).all()
