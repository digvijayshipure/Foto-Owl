from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.database import get_db
from app.auth import authenticate_user, create_access_token, get_current_user

router = APIRouter()


@router.post("/token")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/create_admin_user", response_model=schemas.UserResponse)
def create_admin_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create the first admin user for the system.
    Only one admin user is allowed.
    
    Parameter:
        user: The user details for creating the admin.
        db: Database session dependency.

    Returns:
        The created admin user details.

    Raises:
        HTTPException: If an admin already exists.
    """
    # Check if an admin already exists in the database
    existing_admin = db.query(models.User).filter(models.User.is_admin == True).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="An admin already exists.")
    
    # Create and return the new admin user
    return crud.create_user(db, user=user, is_admin=True)

@router.post("/create_user", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Create a regular user. Only admins are authorized to perform this action.
    
    Parameter:
        user: The user details for creating the user.
        db: Database session dependency.
        current_user: The currently authenticated user.

    Returns:
        The created user details.

    Raises:
        HTTPException: If the current user is not authorized.
    """
    # Ensure the current user has admin privileges
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.create_user(db, user=user)

@router.get("/borrow_requests")
def view_borrow_requests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Retrieve all borrow requests. Only admins can view these requests.
    
    Parameter:
        db: Database session dependency.
        current_user: The currently authenticated user.

    Returns:
        List of all borrow requests.

    Raises:
        HTTPException: If the current user is not authorized.
    """
    # Ensure only admins can access borrow requests
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    # Fetch and return all borrow requests
    return db.query(models.BorrowRequest).all()

@router.post("/approve_request/{request_id}")
def approve_request(request_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Approve a borrow request by its ID. Only admins are authorized to approve requests.
    
    Parameter:
        request_id: The ID of the borrow request to approve.
        db: Database session dependency.
        current_user: The currently authenticated user.

    Returns:
        The updated borrow request with approved status.

    Raises:
        HTTPException: If the request is not found or the current user is not authorized.
    """
    # Ensure only admins can approve requests
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    # Find the borrow request by ID
    borrow_request = db.query(models.BorrowRequest).filter(models.BorrowRequest.id == request_id).first()
    if not borrow_request:
        raise HTTPException(status_code=404, detail="Request not found")
    # Update the request status to 'approved' and commit changes
    borrow_request.status = "approved"
    db.commit()
    return borrow_request

@router.get("/user/{user_id}/borrow_history", response_model=List[schemas.BorrowRequestResponse])
def view_user_borrow_history(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    View the borrow history of a specific user. Only admins can access this information.
    
    Parameter:
        user_id: The ID of the user whose borrow history is requested.
        db: Database session dependency.
        current_user: The currently authenticated user.

    Returns:
        The borrow history of the specified user.

    Raises:
        HTTPException: If no borrow history is found or the current user is not authorized.
    """
    # Ensure only admins can access user borrow history
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    # Retrieve the borrow history of the specified user
    borrow_history = crud.get_user_borrow_history(db, user_id)
    if not borrow_history:
        raise HTTPException(status_code=404, detail="No borrow history found for this user")
    return borrow_history

@router.post("/add_book")
def add_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Add a new book to the library collection. Only admins can add books.
    
    Parameter:
        book: The details of the book to be added.
        db: Database session dependency.
        current_user: The currently authenticated user.

    Returns:
        The created book details.

    Raises:
        HTTPException: If the current user is not authorized.
    """
    # Ensure only admins can add new books
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    # Create and add the new book to the database
    db_book = models.Book(title=book.title, author=book.author, copies=book.copies)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book
