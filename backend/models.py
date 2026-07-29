from datetime import datetime, date
from typing import List
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()

class Item(Base):
    """Model used for item representation."""
    __tablename__ = "items"
    
    itemId: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    qrCode: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    isCollection: Mapped[bool] = mapped_column(default=False, index=True, nullable=False)
    
    borrows: Mapped[List["Borrow"]] = relationship(back_populates="item", cascade="all, delete-orphan") #Delete/cascade all borrows if item is deleted - an error is thrown if trying to delete an item with active borrows so this is just to ensure there are no orphaned borrows

class Borrow(Base):
    """Model used for borrow representation."""
    __tablename__ = "borrows"
    
    borrowId: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    itemId: Mapped[int] = mapped_column(ForeignKey("items.itemId", ondelete="CASCADE"), index=True, nullable=False) 
    email: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    borrowDate: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    expectedReturnDate: Mapped[date] = mapped_column(nullable=False)
    isReturned: Mapped[bool] = mapped_column(default=False, index=True, nullable=False)
    
    item: Mapped["Item"] = relationship(back_populates="borrows")
