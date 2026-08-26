from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api_schema import (
    ItemCreate,
    ItemRead,
    ItemReadWithDetails,
    ItemUpdate,
    M2MAssignment,
)
from database import get_session
from models import Item, Language, LanguageItem

router = APIRouter()


@router.post(
    "/items/",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Items"],
)
def create_item(item: ItemCreate, session: Session = Depends(get_session)):
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get(
    "/items/",
    response_model=List[ItemRead],
    tags=["Items"],
)
def read_items(
    offset: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    return session.exec(select(Item).offset(offset).limit(limit)).all()


@router.get(
    "/items/{item_id}",
    response_model=ItemReadWithDetails,
    tags=["Items"],
)
def read_item_by_id(item_id: int, session: Session = Depends(get_session)):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.patch(
    "/items/{item_id}",
    response_model=ItemRead,
    tags=["Items"],
)
def update_item(
    item_id: int, item_update: ItemUpdate, session: Session = Depends(get_session)
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    item_data = item_update.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)

    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Items"],
)
def delete_item(item_id: int, session: Session = Depends(get_session)):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(db_item)
    session.commit()


@router.post(
    "/items/{item_id}/languages",
    response_model=ItemReadWithDetails,
    tags=["Items"],
)
def assign_language_to_item(
    item_id: int, payload: M2MAssignment, session: Session = Depends(get_session)
):
    db_item = session.get(Item, item_id)
    db_lang = session.get(Language, payload.target_id)

    if not db_item or not db_lang:
        raise HTTPException(status_code=404, detail="Item or Language not found")

    if db_lang not in db_item.languages:
        db_item.languages.append(db_lang)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)

    return db_item


@router.delete(
    "/items/{item_id}/languages/{language_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Items"],
)
def remove_language_from_item(
    item_id: int, language_id: int, session: Session = Depends(get_session)
):
    link = session.exec(
        select(LanguageItem).where(
            LanguageItem.item_id == item_id, LanguageItem.language_id == language_id
        )
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Relationship not found")

    session.delete(link)
    session.commit()
