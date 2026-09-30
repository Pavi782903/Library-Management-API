from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Book, BorrowRecord, Member
from ..schemas import BorrowResponse, ReturnResponse


router = APIRouter(
    prefix="/members",
    tags=["Borrowing & Returning"],
)


@router.post(
    "/{member_id}/books/{book_id}/borrow",
    response_model=BorrowResponse,
    status_code=status.HTTP_200_OK,
)
def borrow_book(
    member_id: int,
    book_id: int,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # Check member
    # ---------------------------------------------------------

    member = (
        db.query(Member)
        .filter(Member.id == member_id)
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found",
        )

    # ---------------------------------------------------------
    # Check book
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Check quantity
    # ---------------------------------------------------------

    if book.available_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Book '{book.name}' is currently unavailable. "
                "Available quantity is 0."
            ),
        )

    # ---------------------------------------------------------
    # Check if same member already has this book
    # ---------------------------------------------------------

    active_borrow = (
        db.query(BorrowRecord)
        .filter(
            BorrowRecord.member_id == member_id,
            BorrowRecord.book_id == book_id,
            BorrowRecord.returned_at.is_(None),
        )
        .first()
    )

    if active_borrow:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Member {member_id} has already borrowed "
                f"book {book_id} and has not returned it yet"
            ),
        )

    # ---------------------------------------------------------
    # Create borrow record
    # ---------------------------------------------------------

    borrow_record = BorrowRecord(
        member_id=member_id,
        book_id=book_id,
        borrowed_at=datetime.utcnow(),
    )

    # Reduce available quantity
    book.available_quantity -= 1

    try:
        db.add(borrow_record)
        db.commit()
        db.refresh(borrow_record)

        return BorrowResponse(
            message="Book borrowed successfully",
            member_id=member_id,
            book_id=book_id,
            book_name=book.name,
            available_quantity=book.available_quantity,
            borrowed_at=borrow_record.borrowed_at,
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to borrow book",
        )


@router.post(
    "/{member_id}/books/{book_id}/return",
    response_model=ReturnResponse,
    status_code=status.HTTP_200_OK,
)
def return_book(
    member_id: int,
    book_id: int,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # Check member
    # ---------------------------------------------------------

    member = (
        db.query(Member)
        .filter(Member.id == member_id)
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found",
        )

    # ---------------------------------------------------------
    # Check book
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Find active borrow
    # ---------------------------------------------------------

    borrow_record = (
        db.query(BorrowRecord)
        .filter(
            BorrowRecord.member_id == member_id,
            BorrowRecord.book_id == book_id,
            BorrowRecord.returned_at.is_(None),
        )
        .first()
    )

    if not borrow_record:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Member {member_id} has not borrowed "
                f"book {book_id}"
            ),
        )

    # ---------------------------------------------------------
    # Mark as returned
    # ---------------------------------------------------------

    returned_time = datetime.utcnow()

    borrow_record.returned_at = returned_time

    # Increase available quantity
    book.available_quantity += 1

    try:
        db.commit()
        db.refresh(borrow_record)

        return ReturnResponse(
            message="Book returned successfully",
            member_id=member_id,
            book_id=book_id,
            book_name=book.name,
            available_quantity=book.available_quantity,
            returned_at=returned_time,
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to return book",
        )