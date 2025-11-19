"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Food app schemas

class MenuItem(BaseModel):
    """
    Menu items offered in the food app
    Collection name: "menuitem"
    """
    name: str = Field(..., description="Dish name")
    description: Optional[str] = Field(None, description="Dish description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Category like 'Pizza', 'Drinks', 'Desserts'")
    image_url: Optional[str] = Field(None, description="Image URL for the dish")
    is_available: bool = Field(True, description="Whether item is available")

class OrderItem(BaseModel):
    menu_item_id: str = Field(..., description="Referenced menu item id as string")
    quantity: int = Field(..., ge=1, description="Quantity ordered")

class Order(BaseModel):
    """
    Orders placed by users
    Collection name: "order"
    """
    customer_name: str = Field(..., description="Customer full name")
    customer_phone: str = Field(..., description="Contact phone")
    customer_address: str = Field(..., description="Delivery address")
    items: List[OrderItem] = Field(..., description="List of items in the order")
    notes: Optional[str] = Field(None, description="Special instructions")
    status: str = Field("pending", description="Order status: pending, confirmed, delivered, cancelled")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
