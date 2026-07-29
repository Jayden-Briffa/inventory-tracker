from fastapi import FastAPI, Depends, status, HTTPException
import database
from sqlalchemy.orm import Session
import schemas
import models
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # or ["*"] for dev if you don't use cookies/auth
    allow_credentials=False,       # set False if you never send cookies/Authorization that needs credentials
    allow_methods=["*"],
    allow_headers=["*"],
)

def find_item(qr, db):
    """Helper method to get an item or raise 404."""
    item = db.query(models.Item).filter(models.Item.qrCode == qr).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with QR code '{qr}' does not exist.")
    return item


def find_borrow(borrow_id: int, db: Session):
    """Helper method to get a borrow record or raise 404."""
    borrow = db.query(models.Borrow).filter(models.Borrow.borrowId == borrow_id).first()
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Borrow with ID '{borrow_id}' does not exist.")
    return borrow

@app.get("/")
async def home():
    return "Inventory Management System API"

"""
Item endpoints.
"""

@app.post("/items", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: schemas.ItemCreate, db = Depends(database.get_db)):
    """Create a new item."""
    # Check if QR code already exists
    existing_item = db.query(models.Item).filter(models.Item.qrCode == item.qrCode).first()
    if existing_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Item with QR code '{item.qrCode}' already exists.")
    
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/items", response_model=List[schemas.ItemResponse])
async def get_items(collection: bool | None = None, db = Depends(database.get_db)):
    """Get all items. Query parameter to filter by collection status."""
    if collection is not None:
        return db.query(models.Item).filter(models.Item.isCollection == collection).all()
    return db.query(models.Item).all()


@app.get("/items/{qr}", response_model=schemas.ItemResponse)
async def get_item(qr, db = Depends(database.get_db)):
    """Get a specific item using its QR code."""
    return find_item(qr, db)


@app.patch("/items/{qr}", response_model=schemas.ItemResponse)
async def update_item(qr, item: schemas.ItemUpdate, db = Depends(database.get_db)):
    """Update an item."""
    item_to_update = find_item(qr, db)
    
    update_data = item.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update.")
    
    for key, value in update_data.items():
        setattr(item_to_update, key, value)
    
    db.commit()
    db.refresh(item_to_update)
    return item_to_update


@app.delete("/items/{qr}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(qr, db = Depends(database.get_db)):
    """Delete an item."""
    item = find_item(qr, db)
    
    # Check if item has active borrows
    active_borrows = db.query(models.Borrow).filter(
        models.Borrow.itemId == item.itemId,
        models.Borrow.isReturned == False
    ).first()
    
    if active_borrows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot delete item with active borrows."
        )
    
    db.delete(item)
    db.commit()
    return


"""
Borrow endpoints.
"""

@app.post("/borrows", response_model=schemas.BorrowResponse, status_code=status.HTTP_201_CREATED)
async def create_borrow(borrow: schemas.BorrowCreate, db = Depends(database.get_db)):
    """Create a new borrow record."""
    # Verify item exists
    item = db.query(models.Item).filter(models.Item.itemId == borrow.itemId).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {borrow.itemId} does not exist.")
    
    # Check if item is already borrowed
    # Collections can be borrowed multiple times, individual items cannot
    if not item.isCollection:
        active_borrow = db.query(models.Borrow).filter(
            models.Borrow.itemId == borrow.itemId,
            models.Borrow.isReturned == False
        ).first()
        
        if active_borrow:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Item is already borrowed and not yet returned."
            )
    
    db_borrow = models.Borrow(**borrow.model_dump())
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

@app.get("/borrows", response_model=List[schemas.BorrowResponse])
async def get_borrows(
    email: str | None = None, 
    returned: bool | None = None,
    item_id: int | None = None,
    sort_by: str = "borrowDate",
    order: str = "asc",
    db = Depends(database.get_db)
):
    """Get all borrow records. Filter by email, return status, and/or item ID. Sort by specified field."""
    borrows = db.query(models.Borrow)
    
    # Apply filters
    if email is not None:
        borrows = borrows.filter(models.Borrow.email == email.lower())
    
    if returned is not None:
        borrows = borrows.filter(models.Borrow.isReturned == returned)
    
    if item_id is not None:
        borrows = borrows.filter(models.Borrow.itemId == item_id)
    
    # Define valid sort fields
    valid_sort_fields = {
        "borrowDate": models.Borrow.borrowDate,
        "expectedReturnDate": models.Borrow.expectedReturnDate,
        "borrowId": models.Borrow.borrowId,
        "email": models.Borrow.email,
        "isReturned": models.Borrow.isReturned
    }
    
    # Validate sort field
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields.keys())}"
        )
    
    # Apply sorting
    sort_column = valid_sort_fields[sort_by]
    if order.lower() == "desc":
        borrows = borrows.order_by(sort_column.desc())
    elif order.lower() == "asc":
        borrows = borrows.order_by(sort_column.asc())
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order. Must be 'asc' or 'desc'"
        )
    
    return borrows.all()

@app.get("/borrows/{borrow_id}", response_model=schemas.BorrowResponse)
async def get_borrow(borrow_id: int, db: Session = Depends(database.get_db)):
    """Get a specific borrow record by ID."""
    return find_borrow(borrow_id, db)

@app.patch("/borrows/{borrow_id}", response_model=schemas.BorrowResponse)
async def update_borrow(borrow_id: int, borrow: schemas.BorrowUpdate, db: Session = Depends(database.get_db)):
    """Update a borrow record."""
    borrow_to_update = find_borrow(borrow_id, db)
    
    update_data = borrow.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update.")
    
    # Check if trying to set isReturned to True when already True
    if "isReturned" in update_data and update_data["isReturned"] == True and borrow_to_update.isReturned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Item has already been returned."
        )
    
    for key, value in update_data.items():
        setattr(borrow_to_update, key, value)
    
    db.commit()
    db.refresh(borrow_to_update)
    return borrow_to_update

@app.delete("/borrows/{borrow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_borrow(borrow_id: int, db: Session = Depends(database.get_db)):
    """Delete a borrow record."""
    borrow = find_borrow(borrow_id, db)
    db.delete(borrow)
    db.commit()
    return


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)