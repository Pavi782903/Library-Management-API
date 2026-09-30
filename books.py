from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Book
from ..schemas import BookCreate, BookResponse, BookUpdate


router = APIRouter(
    prefix="/books",
    tags=["Books"],
)


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
):
    # Check duplicate ISBN before insertion
    existing_book = (
        db.query(Book)
        .filter(Book.isbn == book.isbn)
        .first()
    )

    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with ISBN '{book.isbn}' already exists",
        )

    new_book = Book(
        name=book.name,
        author=book.author,
        category=book.category,
        isbn=book.isbn,
        price=book.price,
        available_quantity=book.available_quantity,
    )

    try:
        db.add(new_book)
        db.commit()
        db.refresh(new_book)

        return new_book

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ISBN already exists",
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create book",
        )


@router.get(
    "",
    response_model=list[BookResponse],
)
def get_books(
    category: Optional[str] = Query(
        default=None,
        description="Search books by category",
    ),
    author: Optional[str] = Query(
        default=None,
        description="Search books by author",
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Book)

    if category:
        query = query.filter(
            Book.category.ilike(f"%{category}%")
        )

    if author:
        query = query.filter(
            Book.author.ilike(f"%{author}%")
        )

    return query.order_by(Book.id).all()


@router.get(
    "/{book_id}",
    response_model=BookResponse,
)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
):
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    return book


@router.put(
    "/{book_id}",
    response_model=BookResponse,
)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
):
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    update_data = book_data.model_dump(
        exclude_unset=True
    )

    # Check duplicate ISBN when ISBN is changed
    if "isbn" in update_data:
        existing_book = (
            db.query(Book)
            .filter(
                Book.isbn == update_data["isbn"],
                Book.id != book_id,
            )
            .first()
        )

        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Book with ISBN "
                    f"'{update_data['isbn']}' already exists"
                ),
            )

    for field, value in update_data.items():
        setattr(book, field, value)

    try:
        db.commit()
        db.refresh(book)

        return book

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ISBN already exists",
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update book",
        )


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
):
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    try:
        db.delete(book)
        db.commit()

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete book",
        )

    return None