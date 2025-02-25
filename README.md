# Order-Processing-System

1. Create a order
    POST - /order
    payload - {
        "order_id": 5,
        "user_id": 123,
        "item_ids": [101, 102],
        "total_amount": 50.5
        }
    sample response {
        "message": "Order created successfully",
        "order_id": 5
    }

2. Order status
    GET - get_order/{order_id}
    sample response {
    "order_id": 5,
    "status": "Completed"
    }

3. Fetch Metrices
    GET - /metrices
    sample response {
    "total_orders": 5,
    "status_counts": {
        "Completed": 5
    },
    "average_processing_time": 4.012699604034424
    }

Design Decisions & Trade-offs

SQLite as Database: Chosen for simplicity and ease of integration
Background Task Processing: Orders are processed asynchronously to simulate real-world processing delays.
In-Memory Queue: A simple queue is used for task scheduling
Processing Time Simulation: Introduced artificial delays to simulate order processing times.

Assumptions

The order_id is unique and provided by the client.
Orders are processed in FIFO (First In, First Out) order.
Processing times are simulated and may not reflect real-world scenarios.
