from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Member
from ..schemas import (
    MemberCreate,
    MemberResponse,
    MemberUpdate,
)


router = APIRouter(
    prefix="/members",
    tags=["Members"],
)


@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_member(
    member: MemberCreate,
    db: Session = Depends(get_db),
):
    # Check duplicate email
    existing_member = (
        db.query(Member)
        .filter(Member.email == member.email)
        .first()
    )

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Member with email '{member.email}' already exists",
        )

    new_member = Member(
        name=member.name,
        email=member.email,
        phone=member.phone,
        membership_type=member.membership_type,
    )

    try:
        db.add(new_member)
        db.commit()
        db.refresh(new_member)

        return new_member

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Member email already exists",
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create member",
        )


@router.get(
    "",
    response_model=list[MemberResponse],
)
def get_members(
    db: Session = Depends(get_db),
):
    return (
        db.query(Member)
        .order_by(Member.id)
        .all()
    )


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
):
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

    return member


@router.put(
    "/{member_id}",
    response_model=MemberResponse,
)
def update_member(
    member_id: int,
    member_data: MemberUpdate,
    db: Session = Depends(get_db),
):
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

    update_data = member_data.model_dump(
        exclude_unset=True
    )

    # Check duplicate email
    if "email" in update_data:
        existing_member = (
            db.query(Member)
            .filter(
                Member.email == update_data["email"],
                Member.id != member_id,
            )
            .first()
        )

        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Member with email "
                    f"'{update_data['email']}' already exists"
                ),
            )

    for field, value in update_data.items():
        setattr(member, field, value)

    try:
        db.commit()
        db.refresh(member)

        return member

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Member email already exists",
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update member",
        )


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
):
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

    try:
        db.delete(member)
        db.commit()

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete member",
        )

    return None