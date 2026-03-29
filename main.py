from fastapi import FastAPI #importing fastAPI library where we can use all fuinctions and tools in the library
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI() #creating the server application

def get_db():
    conn = psycopg2.connect(
        dbname="lumina_db",
        user="aneeshgajula",
        password="",
        host="localhost"
    )
    return conn

@app.get("/health") # this is making the function below get called when client makes a GET request from the URL
def health_check(): #A normal Python function. FastAPI calls this automatically when a request hits /health. You don't call it yourself — the framework does.
    return {"status": "ok", "service": "lumina"} # the return type is a python dictionary, FastAPI automatically converts this to JSON-
#which is the universal language for talking to databases and passing data around

#JSON is just a dictionary. Python dict → FastAPI → JSON. That's the whole magic.

@app.get("/plans")
def get_plans():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM plans")
    plans = cursor.fetchall()
    cursor.close()
    conn.close()
    return plans
VALID_TRANSITIONS = {"TRIALING": ["ACTIVE", "CANCELED"], "ACTIVE" : ["PAST_DUE", "CANCELED"], "PAST_DUE" : ["ACTIVE", "CANCELED"], "CANCELED" : []}

def can_transition(current_status, new_status):
    return new_status in VALID_TRANSITIONS[current_status]

@app.post("/subscriptions")

def create_subscription(user_id: int, plan_id: int):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Step 1: check the plan exists
    cursor.execute("SELECT * FROM plans WHERE id = %s", (plan_id,))
    plan = cursor.fetchone()
    if not plan:
        return {"error": "Plan not found"}
    
    # Step 2: check user doesn't already have active subscription  
    cursor.execute(
    "SELECT user_id FROM subscriptions WHERE user_id = %s AND status = 'ACTIVE'",
    (user_id,)
    )
    existing = cursor.fetchone()
    if existing:
        return {"error": "User already has an active subscription"}
    # Step 3: create subscription + invoice atomically
    try:

        #calculate when their billing period ends (1 month from now)

        from datetime import datetime, timedelta
        period_end = datetime.now() + timedelta(days = 30)

        cursor.execute(
            """INSERT INTO subscriptions (user_id, plan_id, status, current_period_end)
           VALUES (%s, %s, 'ACTIVE', %s) RETURNING *""",
            (user_id, plan_id, period_end)
        )
        subscription = cursor.fetchone()
        # insert the invoice atomically
        cursor.execute(
        """INSERT INTO invoices (subscription_id, user_id, amount_cents, due_date)
           VALUES (%s, %s, %s, %s)""",
        (subscription['id'], user_id, plan['price_cents'], period_end)
        )
        conn.commit()
        return {"message": "Subscription created", "subscription": subscription}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

@app.patch("/subscriptions/{subscription_id}/status")
def update_status(subscription_id: int, new_status: str):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # fetch current subscription
    cursor.execute("SELECT * FROM subscriptions WHERE id = %s", (subscription_id,))
    subscription = cursor.fetchone()
    
    if not subscription:
        return {"error": "Subscription not found"}
    
    # check if transition is valid
    if not can_transition(subscription['status'], new_status):
        return {"error": f"Cannot transition from {subscription['status']} to {new_status}"}
    
    # update the status
    cursor.execute(
        "UPDATE subscriptions SET status = %s WHERE id = %s RETURNING *",
        (new_status, subscription_id)
    )
    updated = cursor.fetchone()
    conn.commit()
    return updated    
        
    # Step 4: return confirmation