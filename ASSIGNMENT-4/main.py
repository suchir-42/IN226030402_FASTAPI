from fastapi import FastAPI,Query,Response,status, HTTPException
from pydantic import BaseModel,Field

app=FastAPI()

#-----Products database-----------------
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook',       'price':  99, 'category': 'Stationery',  'in_stock': True},
    {'id': 3, 'name': 'USB Hub',        'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',        'price':  49, 'category': 'Stationery',  'in_stock': True}
]

#-------------Helper functions-----------------------
def find_product(product_id :int):
    for p in products:
        if p['id']==product_id:
            return p 
    return None


def calculateTotal(product : dict,quantity:int):
    return product['price']*quantity


class CheckOut(BaseModel):
    customer_name :str = Field(...,min_length=2)
    customer_address :str =Field(...,min_length=3)

orders=[]
cart=[]
orderCounter=1

        


#-------For checking the existing products-------------
@app.get("/products")
def get_products():
    return products


#-------------Home--------------------------------------
@app.get('/')
def home():
    return{"Fast api is working"}


#-------------Adding the product to the cart--------------
@app.post('/cart/add')
def add_product(
    product_id : int=Query(...,description="Product ID"),
    quantity :int =Query(...,description="Quantity")):
    product=find_product(product_id)

    if not product:
        raise HTTPException(status_code=404,detail='Product not found')
    if quantity <1:
        raise HTTPException(status_code=400,detail='Quantity must be atleast 1')
    if not product['in_stock']:
        raise HTTPException(status_code=400,detail=f"{product['name']} is out of stock ")  

    for item in cart:
        if item['product_id']==product_id:
            item['quantity'] += quantity
            item['sub_total'] = item['quantity'] * item['product_price']
            return {
                'message':'Cart Updated',
                'cart_item': item
            }

    cart_item={
        'product_id' : product_id,
        'quantity'   : quantity,
        'product_name': product['name'],
        'product_price':product['price'],
        'sub_total' :calculateTotal(product,quantity)
    }

    cart.append(cart_item)
    return {
        'message':'Added to cart',
        'Item'   :cart_item
    }


#----------------Retriving the cart details---------------
@app.get('/cart')
def cartDetails():
    if not cart:
        return {'meassge':'cart is empty','items':[],'grand total':0}

    grand_total=sum(item['sub_total'] for item in cart)
    return{
        'Items':cart,
        'Total Number of Items':len(cart),
        'Grand Total':grand_total
    }


#-----------------Check Out--------------------------------
@app.post('/cart/checkout')
def checkOutCart(checking : CheckOut,response :Response):
    placed_orders=[]
    global orderCounter
    if not cart:
        raise HTTPException(status_code=400,detail='Cart is empty add items first')

    grand_total=0
    for item in cart:
        order={
            'order_id' : orderCounter,
            'customerName':checking.customer_name,
            'customerAdd':checking.customer_address,
            'product':item['product_name'],
            'Quantity':item['quantity'],
            'TotalPrice':item['sub_total'],
            'status':'Confirmed'

        }

        orders.append(order)
        placed_orders.append(order)

        grand_total+=item['sub_total']
        orderCounter+=1

    cart.clear()
    return{
        'message':'Check out Successful',
        'Orders placed':placed_orders,
        'grand_total':grand_total
    }


#---------Deleting the item from the cart-------------------
@app.delete('/cart/delete')
def deleteItem(productId :int,response :Response):
    for item in cart:
        if item['product_id']==productId:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    response.status_code=status.HTTP_404_NOT_FOUND
    return{"Error":"Product not in cart"}

#-------------Returning Orders--------------------------------
@app.get('/orders')
def getOrders():
    return{
        "Orders":orders,
        "Totol Orders":len(orders)
    }
