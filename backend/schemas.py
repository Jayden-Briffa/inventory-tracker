from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
import re


"""
Item schemas.
"""

class ItemBase(BaseModel):
    """Schema used for item representation."""
    qrCode: str = Field(max_length=100)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    isCollection: bool

    @field_validator('qrCode', mode='after')
    @classmethod
    def isUUIDFormat(cls, qrCode: str) -> str:
        if not re.match(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", qrCode):
            raise ValueError(f"'{qrCode}' is not a valid QR code: must be in UUID format")
        return qrCode

class ItemCreate(ItemBase):
    """Schema used to create an item. All fields required."""
    pass

class ItemUpdate(BaseModel):
    # Inheriting from BaseModel instead of ItemBase since all fields are optional for updates and not every field should be updatable
    """Schema used to update an item. All fields optional."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    isCollection: Optional[bool] = None

"""
Borrow schemas.
"""

def validate_email_format(email):
    """
    Validate email format and normalize to lowercase.
    """

    if '@' not in email or '.' not in email.split('@')[-1]:
        raise ValueError('Invalid email format')
    return email.lower()

class BorrowBase(BaseModel):
    """Schema used for borrow representation."""
    itemId: int
    email: str = Field(max_length=100)
    expectedReturnDate: Optional[date] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, email):
        """Validate email using shared validation function."""
        return validate_email_format(email)

class BorrowCreate(BorrowBase):
    """Schema used to create a borrow. All fields required."""
    borrowDate: datetime = Field(default_factory=datetime.now)
    isReturned: bool = Field(default=False)
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Validate expectedReturnDate is after borrowDate."""
        if self.expectedReturnDate and self.borrowDate:
            borrow_date_only = self.borrowDate.date()
            if self.expectedReturnDate <= borrow_date_only:
                raise ValueError('expectedReturnDate must be after borrowDate')
        return self

class BorrowUpdate(BaseModel):
    # Inheriting from BaseModel instead of BorrowBase since all fields are optional for updates and not every field should be updatable
    """Schema used to update a borrow."""
    email: Optional[str] = Field(None, max_length=100)
    expectedReturnDate: Optional[date] = None
    isReturned: Optional[bool] = None
    
    # No inheritance from BorrowBase and email none check needed so redefine email field and validation here
    @field_validator('email')
    @classmethod
    def validate_email(cls, email):
        """Validate email using shared validation function."""
        if email is not None:
            return validate_email_format(email)
        return email


class BorrowResponse(BorrowBase):
    """Borrow representation returned by server."""
    borrowId: int
    borrowDate: datetime
    isReturned: bool

    
# Note: Validation for QR code uniqueness and maximum borrows per item 
# should be implemented in the CRUD layer as they require database queries


class ItemResponse(ItemBase):
    """Item representation returned by server."""
    itemId: int
    borrows: list[BorrowResponse] = Field(default_factory=list)


"""
Borrow schemas.
"""

def validate_email_format(email):
    """
    Validate email format and normalize to lowercase.
    """

    if '@' not in email or '.' not in email.split('@')[-1]:
        raise ValueError('Invalid email format')
    return email.lower()

class BorrowBase(BaseModel):
    """Schema used for borrow representation."""
    itemId: int
    email: str = Field(max_length=100)
    expectedReturnDate: Optional[date] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, email):
        """Validate email using shared validation function."""
        return validate_email_format(email)

class BorrowCreate(BorrowBase):
    """Schema used to create a borrow. All fields required."""
    borrowDate: datetime = Field(default_factory=datetime.now)
    isReturned: bool = Field(default=False)
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Validate expectedReturnDate is after borrowDate."""
        if self.expectedReturnDate and self.borrowDate:
            borrow_date_only = self.borrowDate.date()
            if self.expectedReturnDate <= borrow_date_only:
                raise ValueError('expectedReturnDate must be after borrowDate')
        return self

class BorrowUpdate(BaseModel):
    # Inheriting from BaseModel instead of BorrowBase since all fields are optional for updates and not every field should be updatable
    """Schema used to update a borrow."""
    email: Optional[str] = Field(None, max_length=100)
    expectedReturnDate: Optional[date] = None
    isReturned: Optional[bool] = None
    
    # No inheritance from BorrowBase and email none check needed so redefine email field and validation here
    @field_validator('email')
    @classmethod
    def validate_email(cls, email):
        """Validate email using shared validation function."""
        if email is not None:
            return validate_email_format(email)
        return email


class BorrowResponse(BorrowBase):
    """Borrow representation returned by server."""
    borrowId: int
    borrowDate: datetime
    isReturned: bool
    

# Note: Validation for QR code uniqueness and maximum borrows per item 
# should be implemented in the CRUD layer as they require database queries