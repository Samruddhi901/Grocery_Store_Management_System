class Product:
    def __init__(self,product_id,name,category,price,stock):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock
import sqlite3
class DatabaseManager:
    def __init__(self,db_name="Grocery_store.db"):
        #1. connect to DatabaseFile(create if it is not exist)
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_tables()
    def setup_tables(self):
        #2 Tell the data base to create a table for our products
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products(
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT UNIQUE,
                           category TEXT NOT NULL,
                           price REAL NOT NULL,
                           stock INTEGER NOT NULL
                           )
                           ''')
        self.conn.commit() #to save the change
class Inventory:
    def __init__ (self,db_manager):
        #we pass our database manager here so this class can use it
        self.db = db_manager
    def add_products(self,name,category,price,stock):
        #1 The SQL command to insert data
        if price <= 0:
            print("Invalid price.")
            return
        if stock <= 0:
            print("Invalid stock.")
            return
        query = "INSERT INTO products(name,category,price,stock) VALUES(?,?,?,?)"
        #2 Run the command using data base cursor
        try:
            self.db.cursor.execute(query,(name,category,price,stock))
            self.db.conn.commit()       #Save the change to the file
            print(f"{name} added to the store successfully!")
        except Exception as e:
            print(e)

    def view_all_products(self):
        #1. Ask data base to look up all items
        query = "SELECT * FROM products"
        self.db.cursor.execute(query)
        #2 Grab all the results found by the cursor
        all_items = self.db.cursor.fetchall()
        #3 Print them neatly on screen
        print("\n--CURRENT STORE INVENTORY--")
        print(f"{'ID':<5} {'Name':<15} {'Category':<12} {'Price':<8} {'Stock':<6}")
        print("-" * 50)
        for item in all_items:
            print(f"{item[0]:<5} {item[1]:<15} {item[2]:<12} ${item[3]:<7.2f} {item[4]:<6}")
        print()
class CheckoutSystem:
    def __init__(self,db_manager,inventory):
      self.db = db_manager
      self.inventory = inventory
      self.cart = {}  #startes totally empty
    def add_to_cart(self,product_id,quantity):
        #1. Check if the product is exists in the store
        if quantity <= 0:
            print("Invalid quantity")
            return
        query = "SELECT stock FROM products WHERE id = ?"
        self.db.cursor.execute(query,(product_id,))
        result = self.db.cursor.fetchone() #We only need ONE item stock
        if not result:
            print("Error:That product id doesn't exist!")
            return
        current_stock = result[0]
        #2. Check if we have enough on the shelves
        if quantity > current_stock:
            print("Error:Not enough stock.We only have {current_stock} left.")
            return
        #3 Add it to our temporery dictionary cart
        self.cart[product_id] = self.cart.get(product_id,0) + quantity
        print("Added to cart!")

    def generate_bill(self):
        if not self.cart:
            print("your cart is empty")
            return
        print("\n===================================")
        print("\n       MY GROCCERY STORE RECEIPT    ")
        print("\n===================================")

        grand_total = 0

        #Loop for everthing inside our temporary cart dictionary
        for product_id ,quantity in self.cart.items():
            #1.Curremt details from data base
            self.db.cursor.execute("SELECT name,price,stock FROM products WHERE id = ?",(product_id,))
            product = self.db.cursor.fetchone()
            if product is None:
                print("product is not found")
                continue

            name,price,current_stock = product[0], product[1], product[2]
            item_total = price * quantity
            grand_total += item_total
            print(f"{name:<15} x{quantity:<4} ${price:<6.2f} Total: ${item_total:.2f}")

            #2 Substract stock:Calculate new stock level
            new_stock = current_stock - quantity

            #3 Update Database : tell then data base to update the shelf quantity
            self.db.cursor.execute("UPDATE products SET stock = ? WHERE id = ? ",(new_stock,product_id))

            #4. Save all the changes permanently and empty the cart
        self.db.conn.commit()
        self.cart.clear()
        self.db.conn.close()

        print("\n=================================================")
        print(f"GRAND TOTAL TO PAY:           ${grand_total:.2f}")       
        print("\n=================================================")

'''
db = DatabaseManager()
inventory = INVENTORY(db)

#inventory.add_products("Rice","Food",50,10)
#inventory.add_products("Milk","Dairy",30,20)

inventory.view_all_products()

product_id = int(input("Enter Product ID: "))
quantity = int(input("Enter Quantity: "))
checkout = CheckoutSystem(db, inventory)
checkout.add_to_cart(product_id,quantity)
checkout.generate_bill()
'''

db = DatabaseManager()
inventory = Inventory(db)
checkout = CheckoutSystem(db,inventory)
print("\n----Add users product list in store----")
new_name = input("Enter the product name: ")
new_category = input("Enter the product category: ")
new_price = float(input("Enter the product price: "))
new_stock = int(input("Enter Initial stock quantity: "))

inventory.add_products(new_name,new_category,new_price,new_stock)
print("\n")
inventory.view_all_products()
print("\n----Customer Checkout---")
product_id = int(input("Enter Product ID to buy: "))
quantity = int(input("Enter Quantity: "))
checkout.add_to_cart(product_id,quantity)
checkout.generate_bill()
                
