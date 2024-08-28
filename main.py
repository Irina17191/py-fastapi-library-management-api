from fastapi import (
    FastAPI,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

import crud
import schemas
from database import SessionLocal
from models import Author


app = FastAPI()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root() -> dict:
    return {"message": "Hello World"}


@app.get("/authors/", response_model=list[schemas.AuthorList])
def read_all_authors(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db)
) -> list[Author]:
    return crud.get_all_authors(db=db, skip=skip, limit=limit)


@app.post("/authors/", response_model=schemas.AuthorDetail)
def create_author(
        author: schemas.AuthorCreate,
        db: Session = Depends(get_db),
) -> Author:
    db_author = crud.get_author_by_name(db=db, name=author.name)
    if db_author:
        raise HTTPException(
            status_code=400,
            detail="Author with such name already exists",
        )

    return crud.create_author(db=db, author=author)


@app.get("/authors/{author_id}", response_model=schemas.AuthorDetail)
def read_author(
        author_id: int,
        db: Session = Depends(get_db)
) -> Author:
    author = crud.get_author(db=db, author_id=author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@app.get("/books/", response_model=list[schemas.Book])
def read_all_books(
        db: Session = Depends(get_db),
        author_id: int | None = None,
        skip: int = 0,
        limit: int = 10,
) -> list[schemas.Book]:
    return crud.get_book_list(
        db=db, author_id=author_id, skip=skip, limit=limit
    )


@app.get("/books/{book_id}", response_model=schemas.Book)
def read_book(
        book_id: int,
        db: Session = Depends(get_db)
) -> schemas.Book:
    db_book = crud.get_book(db=db, book_id=book_id)

    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return db_book


@app.post("/books/", response_model=schemas.Book)
def create_book(
        book: schemas.BookCreate,
        db: Session = Depends(get_db),
) -> schemas.Book:
    return crud.create_book(db=db, book=book)
