from fastapi import Depends
from sqlmodel import Session, select

from database import engine
from models import Item
from tools import embedder


def index_item_embeddings():
    with Session(engine) as session:
        items = session.exec(select(Item).where(Item.embedding == None)).all()
        for item in items:
            # Combine contextual text for embedding
            content_to_embed = f"{item.title}. Insights: {item.quick_insights}. Remarks: {item.remarks}"
            item.embedding = embedder.encode(content_to_embed).tolist()
            session.add(item)
        session.commit()


if __name__ == "__main__":
    index_item_embeddings()
