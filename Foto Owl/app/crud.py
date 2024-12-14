from sqlalchemy.orm import Session
from . import models, schemas

def create_user(db: Session, user: schemas.UserCreate, is_admin: bool = True):
    """
    Create a new user in the database.

    Parameter:
        db: The database session dependency.
        user: The details of the user to be created.
        is_admin: Whether the user being created is an admin. Defaults to True.

    Returns:
        The created user object.
    """
    # Create a new user object with the provided details
    db_user = models.User(email=user.email, password=user.password, is_admin=is_admin)
    
    # Add the user to the database and commit the transaction
    db.add(db_user)
    db.commit()
    
    # Refresh the user object to reflect the latest state
    db.refresh(db_user)
    
    # Return the created user
    return db_user

def get_books(db: Session):
    """
    Retrieve a list of all books in the library.

    Parameter:
        db: The database session dependency.

    Returns:
        List of all books in the library.
    """
    # Query the database for all books and return the result
    return db.query(models.Book).all()

def get_user_borrow_history(db: Session, user_id: int):
    """
    Retrieve the borrow history for a specific user.

    Parameter:
        db: The database session dependency.
        user_id: The ID of the user whose borrow history is to be fetched.

    Returns:
        List of borrow requests made by the user.
    """
    # Query the database for borrow requests associated with the given user ID
    return db.query(models.BorrowRequest).filter(models.BorrowRequest.user_id == user_id).all()
