"""Seed 1,000 sample books in batches of 10.

Run with: uv run python seed.py
"""

import random
from datetime import datetime, timedelta

from sqlalchemy import column, table
from sqlmodel import Session, select

from src.common.database import engine
from src.common.models import (
    Author,
    Category,
    Item,
    ItemType,
    Language,
    Location,
    User,
    create_database,
)

TOTAL_BOOKS = 1_000
BATCH_SIZE = 10
PUBLICATION_YEAR = 2026

CATEGORY_NAMES = [
    "General & Reference",
    "Literature (Novels, Story Books, Poetry, Drama)",
    "Religion & Philosophy",
    "Social Sciences (Politics, Law, Economics, Education)",
    "History & Biography",
    "Science & Mathematics",
    "Technology (Health, Agriculture, Engineering, Business, ICT)",
    "Arts, Culture & Recreation",
    "Environment & Geography",
    "Language",
]
LANGUAGE_NAMES = ["English", "Sinhala", "Tamil", "Arabic"]
BOOK_TOPICS = [
    "Sri Lankan Literature",
    "World History",
    "Ecology and Conservation",
    "Mathematical Thinking",
    "Community Health",
    "Agricultural Practice",
    "Digital Technology",
    "Cultural Heritage",
    "Comparative Religion",
    "Language Learning",
]
APPROACHES = [
    "Exploring",
    "Understanding",
    "Studies in",
    "Perspectives on",
    "An Introduction to",
    "A Reader in",
    "Research on",
    "Discovering",
    "The Practice of",
    "Collected Essays on",
]
BOOK_FORMATS = [
    "Foundations and Case Studies",
    "People, Places, and Ideas",
    "A Historical Overview",
    "Methods and Applications",
    "Selected Readings",
    "Principles for Today",
    "A Guide for Students",
    "Stories and Perspectives",
    "Questions and Debates",
    "An Illustrated Survey",
]
AUTHOR_NAMES = [
    ("Amara", "Perera"),
    ("Nimal", "Fernando"),
    ("Sahana", "Jayasinghe"),
    ("Ravi", "Silva"),
    ("Maya", "Wickramasinghe"),
    ("Ishan", "Senanayake"),
    ("Leela", "Gunawardena"),
    ("Arun", "Bandara"),
    ("Nadeesha", "Dissanayake"),
    ("Kavindu", "Wijesinghe"),
    ("Farah", "Hassan"),
    ("Daniel", "Peris"),
    ("Anjali", "de Silva"),
    ("Tharindu", "Karunaratne"),
    ("Ruwani", "Abeysekara"),
    ("Imran", "Rauf"),
    ("Dinuka", "Herath"),
    ("Shalini", "Rajapaksa"),
    ("Malik", "Ameen"),
    ("Chathuri", "Ekanayake"),
]


def get_or_create(session: Session, model, key: str, value: str, **defaults):
    record = session.exec(select(model).where(getattr(model, key) == value)).first()
    if record is None:
        record = model(**{key: value, **defaults})
        session.add(record)
        session.flush()
    return record


def book_title(sequence: int) -> str:
    title_index = sequence - 1
    topic = BOOK_TOPICS[title_index % len(BOOK_TOPICS)]
    approach = APPROACHES[(title_index // len(BOOK_TOPICS)) % len(APPROACHES)]
    book_format = BOOK_FORMATS[
        (title_index // (len(BOOK_TOPICS) * len(APPROACHES))) % len(BOOK_FORMATS)
    ]
    volume = title_index // (len(BOOK_TOPICS) * len(APPROACHES) * len(BOOK_FORMATS)) + 1
    return f"{approach} {topic}: {book_format} (Volume {volume})"


def seed_books() -> None:
    engine.echo = False
    create_database()

    with Session(engine) as session:
        locations = {
            name: get_or_create(session, Location, "name", name)
            for name in ("Library", "Store")
        }
        item_type = get_or_create(session, ItemType, "type", "Book")
        categories = [
            get_or_create(session, Category, "name", name) for name in CATEGORY_NAMES
        ]
        languages = [
            get_or_create(session, Language, "name", name) for name in LANGUAGE_NAMES
        ]
        sender = get_or_create(
            session,
            User,
            "email",
            "seed.sender@example.invalid",
            first_name="Sample",
            last_name="Sender",
        )
        approver = get_or_create(
            session,
            User,
            "email",
            "seed.approver@example.invalid",
            first_name="Sample",
            last_name="Approver",
        )
        authors = [
            get_or_create(
                session,
                Author,
                "email",
                f"seed.author.{index:02d}@example.invalid",
                first_name=first_name,
                last_name=last_name,
            )
            for index, (first_name, last_name) in enumerate(AUTHOR_NAMES, start=1)
        ]
        session.commit()

        sequences = range(1, TOTAL_BOOKS + 1)
        item_codes = [
            f"PVT-{PUBLICATION_YEAR % 100:02d}M{(sequence - 1) % len(categories) + 1}-{sequence:04d}"
            for sequence in sequences
        ]
        item_code_prefix = f"PVT-{PUBLICATION_YEAR % 100:02d}M"
        item_table = table("item", column("item_code"))
        existing_codes: set[str] = set(
            session.exec(
                select(item_table.c.item_code).where(
                    item_table.c.item_code.like(f"{item_code_prefix}%")
                )
            ).all()
        )
        existing_codes.intersection_update(item_codes)
        pending = []
        dms_suffixes = iter(
            random.Random(PUBLICATION_YEAR).sample(
                range(100_000, 1_000_000), TOTAL_BOOKS
            )
        )

        for sequence, item_code in enumerate(item_codes, start=1):
            if item_code in existing_codes:
                next(dms_suffixes)
                continue

            category_index = (sequence - 1) % len(categories)
            language_index = (sequence - 1) % len(languages)
            received_at = datetime(2025, 1, 1) + timedelta(days=(sequence - 1) % 600)
            dms_number = f"PMO/{received_at:%Y/%m/%d}/{next(dms_suffixes):06d}"
            pending.append(
                (
                    Item(
                        dms_number=dms_number,
                        item_code=item_code,
                        title=book_title(sequence),
                        sender_id=sender.id,
                        received_at=received_at,
                        acknowledgement_sent=received_at + timedelta(days=1),
                        location_id=locations[
                            "Library" if sequence % 2 else "Store"
                        ].id,
                        approved_by_id=approver.id,
                        approved_at=received_at + timedelta(days=2),
                        remarks=f"Seeded sample book #{sequence:04d}",
                        quick_insights=(
                            f"A sample book about "
                            f"{BOOK_TOPICS[(sequence - 1) % len(BOOK_TOPICS)]}."
                        ),
                        type_id=item_type.id,
                        author_id=authors[(sequence - 1) % len(authors)].id,
                    ),
                    categories[category_index],
                    languages[language_index],
                )
            )

        for offset in range(0, len(pending), BATCH_SIZE):
            batch = pending[offset : offset + BATCH_SIZE]
            session.add_all([item for item, _, _ in batch])
            for item, category, language in batch:
                item.categories.append(category)
                item.languages.append(language)
            session.commit()

        print(
            f"Seed complete: inserted {len(pending)} books in batches of {BATCH_SIZE}; "
            f"{len(existing_codes)} already existed."
        )


if __name__ == "__main__":
    seed_books()
