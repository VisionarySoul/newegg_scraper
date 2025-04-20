import sqlite3
import csv
import os

# Database configuration
db_name = 'newegg_products.db'
table_name = 'products'

# Connect to SQLite database (creates it if it doesn't exist)
try:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Drop the existing table if it exists
    cursor.execute('DROP TABLE IF EXISTS products')
    
    # Create table with proper schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        bullet_description TEXT,
        price DECIMAL(10,2),
        rating DECIMAL(3,1),
        seller TEXT,
        product_number TEXT
    )
    ''')
    
    conn.commit()
    print("Database and table created successfully")
    
except Exception as e:
    print(f"Error creating database: {str(e)}")
    exit(1)

# Find the latest CSV file
csv_files = [f for f in os.listdir('.') if f.startswith('newegg_products_') and f.endswith('.csv')]

if not csv_files:
    print("Error: No newegg_products_*.csv files found in current directory!")
    print("Current directory contents:")
    print(os.listdir('.'))
    exit(1)

latest_csv = max(csv_files, key=os.path.getctime)
print(f"Found CSV file: {latest_csv}")

# Import data from CSV
products_added = 0

try:
    print(f"Opening CSV file: {latest_csv}")
    with open(latest_csv, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        print(f"CSV headers: {csvreader.fieldnames}")
        
        for row in csvreader:
            try:
                # Clean up the price
                price = row['price'].replace('$', '').replace(',', '').strip()
                
                # Prepare data
                product_data = (
                    row['title'],
                    row['description'],
                    row['bullet_description'],
                    float(price) if price else 0,
                    float(row['rating']) if row['rating'] else 0,
                    row['seller'],
                    row['product_number']
                )
                
                # Insert into database
                cursor.execute('''
                INSERT INTO products 
                (title, description, bullet_description, price, rating, seller, product_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', product_data)
                
                products_added += 1
                if products_added % 10 == 0:
                    print(f"Added {products_added} products...")
                
            except Exception as e:
                print(f"Error processing row {products_added + 1}:")
                print(f"Row data: {row}")
                print(f"Error message: {str(e)}")
                continue
        
        conn.commit()
        print(f"Successfully added {products_added} products to the database")

except Exception as e:
    print(f"Error reading CSV file: {str(e)}")
    exit(1)

# View sample products
try:
    # Get total count
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    print(f"\nTotal products in database: {count}")
    
    # Get first 5 products
    cursor.execute('''
    SELECT id, title, price, rating, seller, bullet_description 
    FROM products 
    LIMIT 5
    ''')
    
    products = cursor.fetchall()
    if products:
        print("\nSample Products:")
        for product in products:
            print(f"\n{product[0]} {product[1]}")
            print(f"   Price: ${product[2]}")
            print(f"   Rating: {product[3]}")
            print(f"   Seller: {product[4]}")
            if product[5]:  # bullet_description
                print(f"   Bullet Description: {product[5]}")
    else:
        print("No products found in database!")

except Exception as e:
    print(f"Error viewing products: {str(e)}")

finally:
    conn.close()