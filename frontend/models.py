"""
SQLAlchemy models for the Restaurant Review System frontend.

Database: PostgreSQL
ORM:      SQLAlchemy (declarative base)

Relationships:
  - Restaurant --< MenuItem   (one-to-many; cascade delete)
  - Restaurant --< Review     (one-to-many; cascade delete)
  - User       --< Review     (one-to-many; cascade delete)
"""

import enum

from sqlalchemy import (
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all models."""
    pass


# ============================================================
# ENUM
# ============================================================

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


# ============================================================
# USER
# ============================================================

class User(Base):
    """Application user with role-based access control."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        Index("idx_users_username", "username"),
    )

    id       = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role     = Column(Enum(UserRole), nullable=False, default=UserRole.USER)

    # Reviews written by this user; removed when the user is deleted
    reviews = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role}>"


# ============================================================
# RESTAURANT
# ============================================================

class Restaurant(Base):
    """A restaurant listing."""

    __tablename__ = "restaurants"
    __table_args__ = (
        Index("idx_restaurants_cuisine", "cuisine"),
    )

    id           = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String(100), nullable=False)
    cuisine      = Column(String(50), nullable=False)
    # Comma-separated dietary tags, e.g. "vegan,gluten-free"
    dietary_tags = Column(String(255))
    description  = Column(Text)
    location     = Column(String(255), nullable=False)

    # Menu items for this restaurant; removed when restaurant is deleted
    menu_items = relationship(
        "MenuItem",
        back_populates="restaurant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Reviews for this restaurant; removed when restaurant is deleted
    reviews = relationship(
        "Review",
        back_populates="restaurant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Restaurant id={self.id} name={self.name!r} cuisine={self.cuisine!r}>"


# ============================================================
# MENU ITEM
# ============================================================

class MenuItem(Base):
    """A single item on a restaurant's menu."""

    __tablename__ = "menus"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_menus_price_non_negative"),
        Index("idx_menus_restaurant_id", "restaurant_id"),
    )

    id            = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
    )
    item_name   = Column(String(100), nullable=False)
    price       = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)

    # The restaurant this item belongs to
    restaurant = relationship("Restaurant", back_populates="menu_items")

    def __repr__(self) -> str:
        return (
            f"<MenuItem id={self.id} item_name={self.item_name!r} "
            f"price={self.price} restaurant_id={self.restaurant_id}>"
        )


# ============================================================
# REVIEW
# ============================================================

class Review(Base):
    """A user's review of a restaurant."""

    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_range"),
        Index("idx_reviews_restaurant_id", "restaurant_id"),
        Index("idx_reviews_user_id", "user_id"),
    )

    id            = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating    = Column(SmallInteger, nullable=False)
    comment   = Column(Text)
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # The user who wrote this review
    user = relationship("User", back_populates="reviews")

    # The restaurant being reviewed
    restaurant = relationship("Restaurant", back_populates="reviews")

    def __repr__(self) -> str:
        return (
            f"<Review id={self.id} user_id={self.user_id} "
            f"restaurant_id={self.restaurant_id} rating={self.rating}>"
        )
