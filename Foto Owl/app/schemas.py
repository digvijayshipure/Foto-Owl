# Pydantic models


from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str
    is_admin: bool

class BookCreate(BaseModel):
    title: str
    author: str
    copies: int

class BorrowRequestCreate(BaseModel):
    book_id: int
    start_date: datetime
    end_date: datetime

class BorrowRequestResponse(BaseModel):
    id: int
    book_id: int
    start_date: datetime
    end_date: datetime
    status: str

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: bool

    class Config:
        orm_mode = True

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    copies: int

    class Config:
        orm_mode = True