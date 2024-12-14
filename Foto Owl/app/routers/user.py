from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.database import get_db
from app.auth import get_current_user

router = APIRouter()

@router.get("/books", response_model=List[schemas.BookResponse])
def get_books(db: Session = Depends(get_db)):
    """
    Retrieve a list of all books available in the library.
    
    Parameter:
        db: Database session dependency.

    Returns:
        List of books in the library.
    """
    # Fetch and return all books from the database
    return crud.get_books(db)


@router.get("/borrow_history")
def view_borrow_history(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    View the borrowing history of the currently authenticated user.
    
    Parameter:
        db: Database session dependency.
        current_user: The currently authenticated user.

    Returns:
        List of borrow requests made by the user.
    """
    # Fetch and return all borrow requests for the logged-in user
    return db.query(models.BorrowRequest).filter(models.BorrowRequest.user_id == current_user.id).all()


@router.post("/borrow_request")
def borrow_request(
    request: schemas.BorrowRequestCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new borrow request for a book.
    Ensures the requested book exists and is not already borrowed during the requested period.
    
    Parameter:
        request: Details of the borrow request, including book ID, start date, and end date.
        current_user: The currently authenticated user.
        db: Database session dependency.

    Returns:
        The created borrow request.

    Raises:
        HTTPException: If the book does not exist or if the book is already borrowed during the requested period.
    """
    # Step 1: Check if the requested book exists
    book = db.query(models.Book).filter(models.Book.id == request.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Step 2: Ensure there are no overlapping borrow periods for the requested book
    overlapping_request = db.query(models.BorrowRequest).filter(
        models.BorrowRequest.book_id == request.book_id,
        models.BorrowRequest.status == "approved",  # Check only approved requests
        models.BorrowRequest.end_date > request.start_date,  # Overlapping condition
        models.BorrowRequest.start_date < request.end_date   # Overlapping condition
    ).first()

    if overlapping_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This book is already borrowed during the requested period"
        )

    # Step 3: Create a new borrow request with "pending" status
    borrow_request = models.BorrowRequest(
        user_id=current_user.id,
        book_id=request.book_id,
        start_date=request.start_date,
        end_date=request.end_date,
        status="pending"
    )
    # Add the borrow request to the database and save changes
    db.add(borrow_request)
    db.commit()
    db.refresh(borrow_request)  # Refresh to get the updated state of the object

    # Return the newly created borrow request
    return borrow_request
