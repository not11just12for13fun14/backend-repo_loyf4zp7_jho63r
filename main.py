import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

from database import db, create_document, get_documents
from schemas import MenuItem, Order, User, Product

app = FastAPI(title="Food App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utils

def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    # Convert nested ObjectIds if any appear
    for k, v in list(d.items()):
        try:
            # handle ObjectId-like values by casting to str
            from bson import ObjectId  # type: ignore
            if isinstance(v, ObjectId):
                d[k] = str(v)
        except Exception:
            pass
    return d


@app.get("/")
def read_root():
    return {"message": "Food App API is running"}


@app.get("/schema")
def get_schema():
    """Expose Pydantic schemas so UI/tools can introspect collections."""
    return {
        "schemas": {
            "user": User.model_json_schema(),
            "product": Product.model_json_schema(),
            "menuitem": MenuItem.model_json_schema(),
            "order": Order.model_json_schema(),
        }
    }


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, "name", "✅ Connected")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# -------------- MENU ENDPOINTS --------------

@app.get("/menu")
def list_menu():
    """Return available menu items. Auto-seed a few if empty."""
    items = get_documents("menuitem")
    if not items:
        seed_items = [
            MenuItem(name="Margherita Pizza", description="Classic with tomatoes, mozzarella & basil", price=10.99, category="Pizza", image_url="https://images.unsplash.com/photo-1548365328-9f547fb09530?q=80&w=1200&auto=format&fit=crop", is_available=True),
            MenuItem(name="Spaghetti Carbonara", description="Creamy sauce with pancetta & parmesan", price=12.5, category="Pasta", image_url="https://images.unsplash.com/photo-1523986371872-9d3ba2e2f642?q=80&w=1200&auto=format&fit=crop", is_available=True),
            MenuItem(name="Caesar Salad", description="Romaine, croutons, parmesan & Caesar dressing", price=8.75, category="Salad", image_url="https://images.unsplash.com/photo-1551892374-ecf8754cf8c0?q=80&w=1200&auto=format&fit=crop", is_available=True),
            MenuItem(name="Iced Lemon Tea", description="Refreshing home-brewed lemon tea", price=3.5, category="Drinks", image_url="https://images.unsplash.com/photo-1497534446932-c925b458314e?q=80&w=1200&auto=format&fit=crop", is_available=True),
        ]
        for si in seed_items:
            create_document("menuitem", si)
        items = get_documents("menuitem")
    return [serialize_doc(x) for x in items]


@app.post("/menu")
def create_menu_item(item: MenuItem):
    new_id = create_document("menuitem", item)
    return {"id": new_id}


# -------------- ORDER ENDPOINTS --------------

class OrderResponse(BaseModel):
    id: str
    total: float
    status: str


@app.post("/orders", response_model=OrderResponse)
def create_order(order: Order):
    # Compute total server-side
    id_to_price: Dict[str, float] = {}
    menu_docs = get_documents("menuitem")
    for m in menu_docs:
        _id = str(m.get("_id"))
        id_to_price[_id] = float(m.get("price", 0))

    total = 0.0
    for it in order.items:
        if it.menu_item_id not in id_to_price:
            raise HTTPException(status_code=400, detail=f"Menu item not found: {it.menu_item_id}")
        total += id_to_price[it.menu_item_id] * it.quantity

    order_dict = order.model_dump()
    order_dict["total"] = round(total, 2)

    new_id = create_document("order", order_dict)
    return OrderResponse(id=new_id, total=round(total, 2), status=order.status)


@app.get("/orders")
def list_orders(limit: Optional[int] = 20):
    docs = get_documents("order", limit=limit)
    return [serialize_doc(x) for x in docs]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
