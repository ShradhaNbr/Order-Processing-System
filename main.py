from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import sqlite3  
import queue
from typing import List
import time
import json

app = FastAPI()

order_queue = queue.Queue() 

conn = sqlite3.connect("orders.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
               order_id integer primary key,
               user_id integer,
               items_id integer,
               total_amount float,
               status text,
               created_at timestamp default current_timestamp,
               updated_at timestamp default current_timestamp)
               """)
conn.commit()


class Order(BaseModel):
    order_id:int
    user_id:int
    item_ids:List[int]
    total_amount : float

class OrderStatusResponse(BaseModel):
    order_id:int
    status:str
  
@app.get("/")
def read_root():
    return {"message": "Welcome to Order Processing API"}


@app.post('/order')
def create_order(order: Order, background_tasks: BackgroundTasks):
    items_id = json.dumps(order.item_ids)
    cursor.execute("INSERT INTO orders (order_id, user_id, items_id, total_amount, status) VALUES (?, ?, ?, ?, ?)",
                   (order.order_id, order.user_id, items_id, order.total_amount, "Pending"))
    conn.commit()
    order_queue.put(order.order_id)
    background_tasks.add_task(process_order, order.order_id)
    return {"message": "Order created successfully","order_id": order.order_id}

def process_order(order_id):
    start_time = time.time()
    time.sleep(2)
    cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", ('Processing',order_id))
    conn.commit()
    time.sleep(2)
    cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", ('Completed', order_id))
    conn.commit()
    end_time = time.time()
    processing_time = end_time - start_time
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_metrics (
            order_id INTEGER PRIMARY KEY,
            processing_time REAL
        )
    """)
    conn.commit()
    
    cursor.execute("INSERT INTO order_metrics (order_id, processing_time) VALUES (?, ?)", (order_id, processing_time))
    conn.commit()

@app.get('/get_order/{order_id}',response_model=OrderStatusResponse)
def get_order_status(order_id: int):
    cursor.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,))
    status = cursor.fetchone()
    if not status:
        raise HTTPException(status_code=404, detail="Order not found")
    else:
        return {"order_id": order_id, "status": status[0]}#returns in tuple the first value
    
@app.get('/metrices')
def get_metrices():
    cursor.execute("SELECT count(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    cursor.execute("SELECT status, count(*) FROM orders GROUP by status")
    status_counts = {status:count for status, count in cursor.fetchall()}
    cursor.execute("SELECT AVG(processing_time) FROM order_metrics")
    avg_processing_time = cursor.fetchone()[0] or 0.0
    return {"total_orders": total_orders, 
            "status_counts": status_counts,
            "average_processing_time": avg_processing_time}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=8000)
