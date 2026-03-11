from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from enum import Enum

app = FastAPI()

# ═════════════════════════════════════
# ENUM (for Swagger dropdown)
# ═════════════════════════════════════

class Category(str, Enum):
    Electronics = "Electronics"
    Stationery = "Stationery"


# ═════════════════════════════════════
# PYDANTIC MODEL
# ═════════════════════════════════════

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)


# ═════════════════════════════════════
# DATA
# ═════════════════════════════════════

products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},
]

orders = []
order_counter = 1


# ═════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════

def find_product(product_id: int):
    for p in products:
        if p['id'] == product_id:
            return p
    return None


def calculate_total(product: dict, quantity: int):
    return product['price'] * quantity


def filter_products_logic(category=None, min_price=None, max_price=None, in_stock=None):

    result = products

    if category is not None:
        result = [p for p in result if p['category'] == category]

    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]

    if max_price is not None:
        result = [p for p in result if p['price'] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]

    return result


def getcomment():
    comments=[]
    c=input("comment (optional)")
    comments.append(c)
    return c 






# ═════════════════════════════════════
# ENDPOINTS
# ═════════════════════════════════════

@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}


# ─────────────────────────────────────

@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}


# ─────────────────────────────────────
# FILTER PRODUCTS
# ─────────────────────────────────────

@app.get("/products/filter")
def filter_products(
    category: Category = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None),
    in_stock: bool = Query(None)
):

    result = filter_products_logic(category, min_price, max_price, in_stock)

    return {
        "filtered_products": result,
        "count": len(result)
    }



@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}

# ─────────────────────────────────────
# COMPARE PRODUCTS
# ─────────────────────────────────────

@app.get("/products/compare")
def compare_products(
    product_id_1: int = Query(...),
    product_id_2: int = Query(...)
):

    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)

    if not p1:
        return {"error": f"Product {product_id_1} not found"}

    if not p2:
        return {"error": f"Product {product_id_2} not found"}

    cheaper = p1 if p1["price"] < p2["price"] else p2

    return {
        "product_1": p1,
        "product_2": p2,
        "better_value": cheaper["name"],
        "price_diff": abs(p1["price"] - p2["price"])
    }

#------SUMMARY------------------------
@app.get('/products/summary')
def summary():
  tot=len(products)
  inst=len([p for p in products if p["in_stock"]==True])  
  outst=tot-inst
  maxi=products[0]
  mini=products[0]
  for p in products:
    if p['price']>maxi['price']:
        maxi=p
    if p['price']<mini['price']:
        mini=p

  cat=list({p["category"] for p in products})
  return{"total_products":tot,
  "in_stock_count":inst,
  "out_of_stock_count":outst,
  "most_expensive":{"name":maxi["name"],  "price":maxi["price"]},
  "cheapest":{"name":mini['name'], "price":mini['price']},
  "categories":cat}

  #---------BULK ORDER----------------
from typing import List  # add to imports at top

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity:   int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name:  str           = Field(..., min_length=2)
    contact_email: str           = Field(..., min_length=5)
    items:         List[OrderItem] = Field(..., min_items=1)

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
    return {"company": order.company_name, "confirmed": confirmed,
            "failed": failed, "grand_total": grand_total}








# ─────────────────────────────────────
# GET PRODUCT BY ID
# ─────────────────────────────────────

@app.get("/products/{product_id}")
def get_product(product_id: int):

    product = find_product(product_id)

    if not product:
        return {"error": "Product not found"}

    return {"name":product["name"],'price':product["price"]}


# ─────────────────────────────────────
# PLACE ORDER
# ─────────────────────────────────────



# ─────────────────────────────────────
# GET ALL ORDERS
# ─────────────────────────────────────



#--------GET RATING----------------
@app.get("/feedback/{rating}")
def feedback(rating: int, comment: str = Query(None)):

    if rating < 1 or rating > 5:
        return {"error": "Rating must be between 1 and 5"}

    return {
        "rating": rating,
        "comment": comment
    }


orders = []

@app.post("/orders")
def place_order(order: OrderRequest):

    product = next((p for p in products if p["id"] == order.product_id), None)

    if not product:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"error": "Product out of stock"}

    new_order = {
        "order_id": len(orders) + 1,
        "customer_name": order.customer_name,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "delivery_address": order.delivery_address,
        "status": "pending"
    }

    orders.append(new_order)

    return {
        "message": "Order placed successfully",
        "order": new_order
    }


@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:

        if order["order_id"] == order_id:

            if order["status"] == "confirmed":
                return {"message": "Order already confirmed"}

            order["status"] = "confirmed"

            return {
                "message": "Order confirmed successfully",
                "order": order
            }

    return {"error": "Order not found"}
