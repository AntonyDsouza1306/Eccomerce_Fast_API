# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 13:05:14 2023

@author: desou
"""

from fastapi import FastAPI, File, UploadFile
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
from random import randint
from bson import ObjectId
from pymongo import MongoClient

app = FastAPI()

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['orders_db']
orders = db['orders']

# Pydantic models
class Product(BaseModel):
    product_name: str
    price: int
    quantity: int
    product_img: str

class Order(BaseModel):
    order_id: str = Field(default_factory=lambda: 'O_' + str(randint(1000000000, 9999999999)))
    user_id: str = Field(default_factory=lambda: 'U_' + str(randint(100000, 999999)))
    product_details: List[Product]
    status: str = 'placed'
    order_date_time: datetime = Field(default_factory=datetime.now)

class OrderUpdate(BaseModel):
    order_id: str
    status: str
    updated_order_date_time: datetime = Field(default_factory=datetime.now)

# API endpoints
@app.post('/api/v1/order-create')
async def create_order(order: Order, file: UploadFile = File(...)):
    # Save uploaded image to local folder
    img_path = f'Uploads/profile/{file.filename}'
    with open(img_path, 'wb') as f:
        f.write(await file.read())
    order.product_details[0].product_img = img_path

    # Validate order_id and user_id
    assert len(order.order_id) == 10, 'Order ID must be 10 digits long.'
    assert len(order.user_id) == 6, 'User ID must be 6 digits long.'
    
    # Save order to MongoDB
    orders.insert_one(order.dict(by_alias=True))
    
    return {'message': 'Order created successfully.'}

@app.get('/api/v1/order')
async def get_all_orders():
    # Fetch all orders from MongoDB
    cursor = orders.find({})
    results = []
    for doc in cursor:
        result = {}
        result['UserID'] = doc['user_id']
        result['Order_id'] = doc['order_id']
        result['Product_details'] = []
        for product in doc['product_details']:
            result['Product_details'].append({
                'Product_name': product['product_name'],
                'Price': product['price'],
                'quantity': product['quantity'],
                'product_img': product['product_img']
            })
        result['Total_ammount'] = sum([product['price']*product['quantity'] for product in doc['product_details']])
        result['Status'] = doc['status']
        result['Order_date_time'] = doc['order_date_time'].strftime('%d-%m-%Y %I:%M %p')
        results.append(result)
    return results

@app.put('/api/v1/order-update')
async def update_order(order_update: OrderUpdate):
    # Validate order_id
    assert len(order_update.order_id) == 10, 'Order ID must be 10 digits long.'
    
    # Update order status in MongoDB
    result = orders.update_one({'order_id': order_update.order_id}, {'$set': {'status': order_update.status, 'order_date_time': order_update.updated_order_date_time}})
    if result.modified_count == 1:
        # If order status is confirmed, print bill
        if order_update.status == 'confirmed':
            order = orders.find_one({'order_id': order_update.order_id})
