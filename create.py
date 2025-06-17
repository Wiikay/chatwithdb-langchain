import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker
import string

# Initialize Faker for generating realistic data
fake = Faker()

def create_database():
    """Create SQLite database and tables"""
    conn = sqlite3.connect('telecom_data.db')
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone_number TEXT UNIQUE NOT NULL,
            email TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            plan_type TEXT,
            monthly_fee REAL,
            registration_date DATE,
            status TEXT
        )
    ''')
    
    # Create call_records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS call_records (
            call_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            receiver_number TEXT,
            call_duration INTEGER,
            call_type TEXT,
            call_date DATETIME,
            cost REAL,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    # Create data_usage table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_usage (
            usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            usage_date DATE,
            data_used_mb REAL,
            data_type TEXT,
            cost REAL,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    # Create billing table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS billing (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            bill_date DATE,
            due_date DATE,
            amount REAL,
            payment_status TEXT,
            payment_date DATE,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    return conn, cursor

def generate_phone_number():
    """Generate a realistic phone number"""
    area_codes = ['201', '202', '203', '205', '206', '207', '208', '209', '210']
    area_code = random.choice(area_codes)
    number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{area_code}-{number[:3]}-{number[3:]}"

def generate_customers(cursor, num_customers=1000):
    """Generate customer data"""
    plan_types = ['Basic', 'Premium', 'Family', 'Business', 'Student']
    statuses = ['Active', 'Suspended', 'Inactive']
    
    customers_data = []
    
    for i in range(num_customers):
        plan_type = random.choice(plan_types)
        
        # Set monthly fee based on plan type
        fee_mapping = {
            'Basic': random.uniform(25, 35),
            'Premium': random.uniform(60, 80),
            'Family': random.uniform(90, 120),
            'Business': random.uniform(150, 200),
            'Student': random.uniform(15, 25)
        }
        
        customer = (
            fake.first_name(),
            fake.last_name(),
            generate_phone_number(),
            fake.email(),
            fake.street_address(),
            fake.city(),
            fake.state_abbr(),
            fake.zipcode(),
            plan_type,
            round(fee_mapping[plan_type], 2),
            fake.date_between(start_date='-3y', end_date='today'),
            random.choice(statuses)
        )
        customers_data.append(customer)
    
    cursor.executemany('''
        INSERT INTO customers (first_name, last_name, phone_number, email, address, 
                             city, state, zip_code, plan_type, monthly_fee, 
                             registration_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', customers_data)
    
    print(f"Generated {num_customers} customers")

def generate_call_records(cursor, num_calls=1000):
    """Generate call records data"""
    # Get customer IDs
    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    call_types = ['Local', 'Long Distance', 'International', 'Mobile']
    calls_data = []
    
    for i in range(num_calls):
        customer_id = random.choice(customer_ids)
        call_type = random.choice(call_types)
        
        # Generate duration in seconds (30 seconds to 2 hours)
        duration = random.randint(30, 7200)
        
        # Calculate cost based on call type and duration
        cost_per_minute = {
            'Local': 0.05,
            'Long Distance': 0.15,
            'International': 0.50,
            'Mobile': 0.10
        }
        
        cost = round((duration / 60) * cost_per_minute[call_type], 2)
        
        call = (
            customer_id,
            generate_phone_number(),
            duration,
            call_type,
            fake.date_time_between(start_date='-1y', end_date='now'),
            cost
        )
        calls_data.append(call)
    
    cursor.executemany('''
        INSERT INTO call_records (customer_id, receiver_number, call_duration, 
                                call_type, call_date, cost)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', calls_data)
    
    print(f"Generated {num_calls} call records")

def generate_data_usage(cursor, num_records=500):
    """Generate data usage records"""
    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    data_types = ['4G', '5G', 'WiFi', 'Roaming']
    usage_data = []
    
    for i in range(num_records):
        customer_id = random.choice(customer_ids)
        data_type = random.choice(data_types)
        
        # Generate data usage in MB (10MB to 50GB)
        data_used = round(random.uniform(10, 50000), 2)
        
        # Calculate cost based on data type
        cost_per_mb = {
            '4G': 0.01,
            '5G': 0.015,
            'WiFi': 0.005,
            'Roaming': 0.05
        }
        
        cost = round(data_used * cost_per_mb[data_type], 2)
        
        usage = (
            customer_id,
            fake.date_between(start_date='-1y', end_date='today'),
            data_used,
            data_type,
            cost
        )
        usage_data.append(usage)
    
    cursor.executemany('''
        INSERT INTO data_usage (customer_id, usage_date, data_used_mb, data_type, cost)
        VALUES (?, ?, ?, ?, ?)
    ''', usage_data)
    
    print(f"Generated {num_records} data usage records")

def generate_billing(cursor, num_bills=500):
    """Generate billing records"""
    cursor.execute("SELECT customer_id, monthly_fee FROM customers")
    customers = cursor.fetchall()
    
    payment_statuses = ['Paid', 'Pending', 'Overdue', 'Failed']
    bills_data = []
    
    for i in range(num_bills):
        customer_id, monthly_fee = random.choice(customers)
        
        # Add some variation to the bill amount
        amount = round(monthly_fee + random.uniform(-10, 50), 2)
        
        bill_date = fake.date_between(start_date='-1y', end_date='today')
        due_date = bill_date + timedelta(days=30)
        
        payment_status = random.choice(payment_statuses)
        payment_date = None
        
        if payment_status == 'Paid':
            payment_date = fake.date_between(start_date=bill_date, end_date=due_date)
        
        bill = (
            customer_id,
            bill_date,
            due_date,
            amount,
            payment_status,
            payment_date
        )
        bills_data.append(bill)
    
    cursor.executemany('''
        INSERT INTO billing (customer_id, bill_date, due_date, amount, 
                           payment_status, payment_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', bills_data)
    
    print(f"Generated {num_bills} billing records")

def generate_sample_queries(cursor):
    """Generate some sample queries to test the database"""
    print("\n=== Sample Queries ===")
    
    # Total customers by plan type
    print("\n1. Customers by Plan Type:")
    cursor.execute('''
        SELECT plan_type, COUNT(*) as count, AVG(monthly_fee) as avg_fee
        FROM customers 
        GROUP BY plan_type
        ORDER BY count DESC
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} customers, Avg Fee: ${row[2]:.2f}")
    
    # Top 5 customers by total call costs
    print("\n2. Top 5 Customers by Call Costs:")
    cursor.execute('''
        SELECT c.first_name, c.last_name, SUM(cr.cost) as total_cost
        FROM customers c
        JOIN call_records cr ON c.customer_id = cr.customer_id
        GROUP BY c.customer_id
        ORDER BY total_cost DESC
        LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} {row[1]}: ${row[2]:.2f}")
    
    # Data usage statistics
    print("\n3. Data Usage by Type:")
    cursor.execute('''
        SELECT data_type, COUNT(*) as records, 
               AVG(data_used_mb) as avg_usage,
               SUM(cost) as total_cost
        FROM data_usage 
        GROUP BY data_type
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} records, Avg: {row[2]:.2f}MB, Total Cost: ${row[3]:.2f}")

def main():
    """Main function to create database and generate data"""
    print("Creating telecom database with synthetic data...")
    
    # Create database and tables
    conn, cursor = create_database()
    
    try:
        # Generate data (totaling 3000 rows across all tables)
        generate_customers(cursor, 1000)      # 1000 customers
        generate_call_records(cursor, 1200)   # 1200 call records
        generate_data_usage(cursor, 500)      # 500 data usage records
        generate_billing(cursor, 300)         # 300 billing records
        
        # Commit changes
        conn.commit()
        
        # Display some statistics
        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM call_records")
        call_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM data_usage")
        usage_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM billing")
        billing_count = cursor.fetchone()[0]
        
        total_records = customer_count + call_count + usage_count + billing_count
        
        print(f"\n=== Database Statistics ===")
        print(f"Total records created: {total_records}")
        print(f"  - Customers: {customer_count}")
        print(f"  - Call Records: {call_count}")
        print(f"  - Data Usage: {usage_count}")
        print(f"  - Billing: {billing_count}")
        
        # Run sample queries
        generate_sample_queries(cursor)
        
        print(f"\nDatabase 'telecom_data.db' created successfully!")
        print("You can now connect to it using any SQLite client or Python script.")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()