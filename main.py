import csv
import json
import os

CUSTOMER_FILE = "customers.csv"
PRODUCT_FILE = "products.json"
SALES_FILE = "sales.json"
COUPON_FILE = "coupons.json"

LOW_STOCK_LIMIT = 5
POINTS_PER_RUPEE = 1
POINTS_FOR_ONE_RUPEE = 1000

customers = []
products = []
sales = []
coupons = []

def print_separator(length=55, character="-"):
    print(character * length)

def print_header(title):

    print_separator(55, "=")
    print(title.center(55))
    print_separator(55, "=")

def safe_int_input(prompt, minimum=None):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a whole number.")
            continue
        if minimum is not None and value < minimum:
            print("Value must be at least " + str(minimum) + ".")
            continue
        return value

def safe_float_input(prompt, minimum=None):
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        if minimum is not None and value < minimum:
            print("Value must be at least " + str(minimum) + ".")
            continue
        return value

def format_money(amount):
    return "Rs. " + "{:.2f}".format(amount)

def next_id(records):
    return max((int(record["id"]) for record in records), default=0) + 1

def find_record_by_id(records, target_id):
    for record in records:
        if int(record["id"]) == target_id:
            return record
    return None

def find_customer_by_username(username):
    for customer in customers:
        if customer["username"].lower() == username.lower():
            return customer
    return None

def find_product_by_id(product_id):
    return find_record_by_id(products, product_id)

def find_coupon_by_code(coupon_code):
    for coupon in coupons:
        if coupon["code"].upper() == coupon_code.upper():
            return coupon
    return None

def save_customers():
    field_names = [
        "id", "username", "password", "role", "loyalty_points"
    ]
    with open(CUSTOMER_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        for customer in customers:
            writer.writerow(customer)

def load_customers():
    global customers
    customers = []
    if os.path.exists(CUSTOMER_FILE):
        try:
            with open(CUSTOMER_FILE, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if not row.get("id") or not row.get("username"):
                        continue
                    customer = {
                        "id": int(row["id"]),
                        "username": row["username"],
                        "password": row.get("password", ""),
                        "role": row.get("role", "customer"),
                        "loyalty_points": int(row.get("loyalty_points", 0) or 0)
                    }
                    customers.append(customer)
        except (ValueError, csv.Error):
            print("Warning: customers.csv could not be read correctly.")

    admin = find_customer_by_username("admin")
    if admin is None:
        customers.append({
            "id": next_id(customers),
            "username": "admin",
            "password": "admin123",
            "role": "admin",
            "loyalty_points": 0
        })
        save_customers()

def save_json_file(file_name, records):
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

def load_json_file(file_name):
    if not os.path.exists(file_name):
        return []
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
        print("Warning: " + file_name + " should contain a list. Starting with an empty list.")
        return []
    except (json.JSONDecodeError, OSError):
        print("Warning: could not read " + file_name + ". Starting with an empty list.")
        return []

def load_all_data():
    global products, sales, coupons
    load_customers()
    products = load_json_file(PRODUCT_FILE)
    sales = load_json_file(SALES_FILE)
    coupons = load_json_file(COUPON_FILE)

def save_all_data():
    save_customers()
    save_json_file(PRODUCT_FILE, products)
    save_json_file(SALES_FILE, sales)
    save_json_file(COUPON_FILE, coupons)

def register_customer():
    print_header("CUSTOMER REGISTRATION")
    username = input("Choose a username: ").strip()
    if username == "":
        print("Username cannot be empty.")
        return
    if find_customer_by_username(username) is not None:
        print("That username is already registered. Choose another one.")
        return
    password = input("Choose a password: ").strip()
    if password == "":
        print("Password cannot be empty.")
        return
    new_customer = {
        "id": next_id(customers),
        "username": username,
        "password": password,
        "role": "customer",
        "loyalty_points": 0
    }
    customers.append(new_customer)
    save_customers()

    print("Registration completed successfully.")
    print("Welcome, " + username + "!")

def login_user():
    print_header("LOGIN")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    customer = find_customer_by_username(username)
    if customer is not None and customer["password"] == password:
        print("Login successful. Welcome, " + customer["username"] + "!")
        return customer
    print("Invalid username or password.")
    return None

def choose_category():
    categories = [
        "Fruits and Vegetables",
        "Staples and Grains",
        "Dairy and Bakery",
        "Snacks and Beverages",
        "Household",
        "Personal Care",
        "Other"
    ]
    print("Choose a product category:")
    for number, category in enumerate(categories, 1):
        print(str(number) + ". " + category)
    category_choice = safe_int_input("Category number: ", minimum=1)
    while category_choice > len(categories):
        print("Please choose a category from the list.")
        category_choice = safe_int_input("Category number: ", minimum=1)
    return categories[category_choice - 1]

def add_product():
    print_header("ADD PRODUCT")
    name = input("Product name: ").strip()
    if name == "":
        print("Product name cannot be empty.")
        return

    category = choose_category()
    selling_price = safe_float_input("Selling price (Rs.): ", minimum=0.01)
    cost_price = safe_float_input("Purchase cost per unit (Rs.): ", minimum=0)
    quantity = safe_int_input("Initial stock quantity: ", minimum=0)
    if cost_price > selling_price:
        print("Note: the purchase cost is higher than the selling price. This product may create a loss.")
    product = {
        "id": next_id(products),
        "name": name,
        "category": category,
        "price": selling_price,
        "cost_price": cost_price,
        "quantity": quantity
    }
    products.append(product)
    save_json_file(PRODUCT_FILE, products)
    print("Product added successfully.")

def view_products():
    print_header("PRODUCT LIST")

    if len(products) == 0:
        print("No products have been added yet.")
        return
    for product in products:
        print("ID: " + str(product["id"]))
        print("Name: " + product["name"])
        print("Category: " + product.get("category", "Other"))
        print("Selling price: " + format_money(float(product["price"])))
        print("Available stock: " + str(product["quantity"]))
        print_separator(55)

def search_products():
    print_header("SEARCH PRODUCTS")
    search_text = input("Enter a product name or category: ").strip().lower()
    found = False
    for product in products:
        product_name = product["name"].lower()
        product_category = product.get("category", "Other").lower()
        if search_text in product_name or search_text in product_category:
            print(
                str(product["id"]) + ". " + product["name"] +
                " | " + product_category.title() +
                " | " + format_money(float(product["price"])) +
                " | Stock: " + str(product["quantity"])
            )
            found = True
    if not found:
        print("No matching products were found.")

def update_product():
    print_header("UPDATE PRODUCT")
    view_products()
    if len(products) == 0:
        return
    product_id = safe_int_input("Enter product ID to update: ", minimum=1)
    product = find_product_by_id(product_id)

    if product is None:
        print("Product ID not found.")
        return
    print("1. Change name")
    print("2. Change category")
    print("3. Change selling price")
    print("4. Change purchase cost")
    print("5. Add stock")
    print("6. Set stock quantity")
    choice = safe_int_input("Choose what to update: ", minimum=1)
    if choice == 1:
        new_name = input("New product name: ").strip()
        if new_name != "":
            product["name"] = new_name
            print("Product name updated.")
        else:
            print("Name cannot be empty.")
    elif choice == 2:
        product["category"] = choose_category()
        print("Product category updated.")
    elif choice == 3:
        product["price"] = safe_float_input("New selling price: ", minimum=0.01)
        print("Selling price updated.")
    elif choice == 4:
        product["cost_price"] = safe_float_input("New purchase cost: ", minimum=0)
        print("Purchase cost updated.")
    elif choice == 5:
        extra_stock = safe_int_input("Quantity to add: ", minimum=1)
        product["quantity"] = int(product["quantity"]) + extra_stock
        print("Stock added.")
    elif choice == 6:
        product["quantity"] = safe_int_input("New total stock quantity: ", minimum=0)
        print("Stock quantity updated.")
    else:
        print("Invalid update choice.")
        return
    save_json_file(PRODUCT_FILE, products)

def remove_product():
    print_header("REMOVE PRODUCT")
    view_products()
    if len(products) == 0:
        return
    product_id = safe_int_input("Enter product ID to remove: ", minimum=1)
    product = find_product_by_id(product_id)
    if product is None:
        print("Product ID not found.")
        return
    confirmation = input("Remove " + product["name"] + "? Type YES to confirm: ").strip()

    if confirmation == "YES":
        products.remove(product)
        save_json_file(PRODUCT_FILE, products)
        print("Product removed.")
    else:
        print("Removal cancelled.")

def check_low_stock():
    print_header("LOW STOCK REPORT")
    found = False
    for product in products:
        if int(product["quantity"]) <= LOW_STOCK_LIMIT:
            print(
                product["name"] + " | Stock remaining: " +
                str(product["quantity"]) + " | Category: " +
                product.get("category", "Other")
            )
            found = True
    if not found:
        print("All products have stock above the low-stock limit.")

def add_coupon():
    print_header("CREATE COUPON")
    code = input("Coupon code (example: SAVE10): ").strip().upper()
    if code == "":
        print("Coupon code cannot be empty.")
        return
    if find_coupon_by_code(code) is not None:
        print("A coupon with this code already exists.")
        return
    print("1. Percentage discount")
    print("2. Fixed amount discount")
    discount_choice = safe_int_input("Discount type: ", minimum=1)
    while discount_choice not in [1, 2]:
        print("Choose 1 or 2.")
        discount_choice = safe_int_input("Discount type: ", minimum=1)
    if discount_choice == 1:
        discount_type = "percentage"
        discount_value = safe_float_input("Discount percentage (1 to 100): ", minimum=1)
        while discount_value > 100:
            print("Percentage cannot be more than 100.")
            discount_value = safe_float_input("Discount percentage (1 to 100): ", minimum=1)
    else:
        discount_type = "fixed"
        discount_value = safe_float_input("Discount amount in Rs.: ", minimum=0.01)
    minimum_amount = safe_float_input("Minimum cart subtotal (Rs.): ", minimum=0)
    maximum_uses = safe_int_input("Maximum total uses (0 means unlimited): ", minimum=0)
    new_coupon = {
        "id": next_id(coupons),
        "code": code,
        "discount_type": discount_type,
        "discount_value": discount_value,
        "minimum_amount": minimum_amount,
        "maximum_uses": maximum_uses,
        "usage_count": 0,
        "used_by": [],
        "active": True
    }
    coupons.append(new_coupon)
    save_json_file(COUPON_FILE, coupons)
    print("Coupon created successfully.")

def view_coupons():
    print_header("COUPON LIST")
    if len(coupons) == 0:
        print("No coupons are available.")
        return
    for coupon in coupons:
        if coupon.get("discount_type") == "percentage":
            discount_text = str(coupon["discount_value"]) + "% off"
        else:
            discount_text = format_money(float(coupon["discount_value"])) + " off"
        if coupon.get("active", True):
            status = "Active"
        else:
            status = "Inactive"
        print("Code: " + coupon["code"])
        print("Discount: " + discount_text)
        print("Minimum bill: " + format_money(float(coupon["minimum_amount"])))
        print("Uses: " + str(coupon.get("usage_count", 0)) + "/" + str(coupon.get("maximum_uses", 0) or "Unlimited"))
        print("Status: " + status)
        print_separator(55)

def deactivate_coupon():
    view_coupons()
    if len(coupons) == 0:
        return
    code = input("Enter coupon code to deactivate: ").strip().upper()
    coupon = find_coupon_by_code(code)
    if coupon is None:
        print("Coupon not found.")
        return
    coupon["active"] = False
    save_json_file(COUPON_FILE, coupons)
    print("Coupon deactivated.")

def validate_coupon(code, customer, subtotal):
    coupon = find_coupon_by_code(code)
    if coupon is None:
        print("Coupon code does not exist.")
        return None, 0.0
    if not coupon.get("active", True):
        print("This coupon is inactive.")
        return None, 0.0

    minimum_amount = float(coupon["minimum_amount"])
    if subtotal < minimum_amount:
        print("Minimum purchase for this coupon is " + format_money(minimum_amount) + ".")
        return None, 0.0
    maximum_uses = int(coupon.get("maximum_uses", 0))
    usage_count = int(coupon.get("usage_count", 0))
    if maximum_uses > 0 and usage_count >= maximum_uses:
        print("This coupon has reached its usage limit.")
        return None, 0.0
    if customer["username"] in coupon.get("used_by", []):
        print("You have already used this coupon.")
        return None, 0.0
    if coupon["discount_type"] == "percentage":
        discount = subtotal * float(coupon["discount_value"]) / 100
    else:
        discount = float(coupon["discount_value"])
    if discount > subtotal:
        discount = subtotal
    return coupon, discount

def calculate_cart_subtotal(cart):
    return sum(float(item["price"]) * int(item["quantity"]) for item in cart)

def view_cart(cart):
    print_header("YOUR SHOPPING CART")
    if len(cart) == 0:
        print("Your cart is empty.")
        return
    for item in cart:
        item_total = float(item["price"]) * int(item["quantity"])
        print(
            item["name"] + " x " + str(item["quantity"]) +
            " | Unit price: " + format_money(float(item["price"])) +
            " | Item total: " + format_money(item_total)
        )
    print("Subtotal: " + format_money(calculate_cart_subtotal(cart)))

def add_to_cart(cart):
    view_products()
    if len(products) == 0:
        return
    product_id = safe_int_input("Enter product ID to add: ", minimum=1)
    product = find_product_by_id(product_id)
    if product is None:
        print("Product not found.")
        return
    quantity = safe_int_input("Quantity to add: ", minimum=1)
    existing_item = next((item for item in cart if int(item["id"]) == product_id), None)
    already_in_cart = int(existing_item["quantity"]) if existing_item else 0
    if already_in_cart + quantity > int(product["quantity"]):
        print("Not enough stock. Available quantity: " + str(product["quantity"]))
        return
    if existing_item is not None:
        existing_item["quantity"] = int(existing_item["quantity"]) + quantity
    else:
        cart.append({
            "id": int(product["id"]),
            "name": product["name"],
            "category": product.get("category", "Other"),
            "price": float(product["price"]),
            "cost_price": float(product.get("cost_price", 0)),
            "quantity": quantity
        })
    print("Product added to cart.")

def update_cart_quantity(cart):
    view_cart(cart)
    if len(cart) == 0:
        return
    product_id = safe_int_input("Enter product ID to change quantity: ", minimum=1)
    cart_item = None
    for item in cart:
        if int(item["id"]) == product_id:
            cart_item = item
            break
    if cart_item is None:
        print("That product is not in your cart.")
        return
    new_quantity = safe_int_input("Enter new quantity (0 to remove item): ", minimum=0)
    product = find_product_by_id(product_id)
    if new_quantity == 0:
        cart.remove(cart_item)
        print("Item removed from cart.")
    elif product is None:
        print("This product is no longer available.")
        cart.remove(cart_item)
    elif new_quantity > int(product["quantity"]):
        print("Not enough stock. Available quantity: " + str(product["quantity"]))
    else:
        cart_item["quantity"] = new_quantity
        print("Cart quantity updated.")

def show_customer_history(customer):
    print_header("YOUR PURCHASE HISTORY")
    found = False

    for sale in sales:
        if sale.get("customer_username", "").lower() == customer["username"].lower():
            found = True
            print("Transaction ID: " + str(sale["id"]))
            print("Items: ")
            for item in sale["items"]:
                print("  " + item["name"] + " x " + str(item["quantity"]))
            print("Subtotal: " + format_money(float(sale["subtotal"])))
            print("Coupon discount: " + format_money(float(sale["coupon_discount"])))
            print("Loyalty discount: " + format_money(float(sale["loyalty_discount"])))
            print("Amount paid: " + format_money(float(sale["final_total"])))
            print_separator(55)
    if not found:
        print("You do not have any saved purchases yet.")

def checkout(customer, cart):
    print_header("CHECKOUT")
    if len(cart) == 0:
        print("Your cart is empty.")
        return
    for item in cart:
        product = find_product_by_id(int(item["id"]))
        if product is None or int(item["quantity"]) > int(product["quantity"]):
            print("Stock changed for " + item["name"] + ". Please update your cart first.")
            return
    subtotal = calculate_cart_subtotal(cart)
    print("Cart subtotal: " + format_money(subtotal))
    applied_coupon = None
    coupon_discount = 0.0
    use_coupon = input("Do you have a coupon? (yes/no): ").strip().lower()
    if use_coupon == "yes":
        coupon_code = input("Enter coupon code: ").strip().upper()
        applied_coupon, coupon_discount = validate_coupon(coupon_code, customer, subtotal)
        if applied_coupon is not None:
            print("Coupon discount: " + format_money(coupon_discount))

    amount_after_coupon = subtotal - coupon_discount
    loyalty_discount = 0.0
    points_to_redeem = 0
    available_points = int(customer.get("loyalty_points", 0))
    print("Your loyalty points: " + str(available_points))
    print("Redemption rate: " + str(POINTS_FOR_ONE_RUPEE) + " points = Rs. 1")
    use_points = input("Would you like to redeem points? (yes/no): ").strip().lower()
    if use_points == "yes":
        maximum_redeemable_points = (available_points // POINTS_FOR_ONE_RUPEE) * POINTS_FOR_ONE_RUPEE
        maximum_discount = maximum_redeemable_points / POINTS_FOR_ONE_RUPEE
        print("Maximum available loyalty discount: " + format_money(maximum_discount))
        if maximum_redeemable_points > 0 and amount_after_coupon > 0:
            points_to_redeem = safe_int_input(
                "Enter points to redeem (multiples of 1000): ", minimum=1000
            )
            while points_to_redeem % POINTS_FOR_ONE_RUPEE != 0 or points_to_redeem > maximum_redeemable_points:
                print("Enter a valid multiple of 1000 within your available points.")
                points_to_redeem = safe_int_input(
                    "Enter points to redeem (multiples of 1000): ", minimum=1000
                )
            loyalty_discount = points_to_redeem / POINTS_FOR_ONE_RUPEE
            if loyalty_discount > amount_after_coupon:
                loyalty_discount = amount_after_coupon
                points_to_redeem = int(loyalty_discount * POINTS_FOR_ONE_RUPEE)
                points_to_redeem = (points_to_redeem // POINTS_FOR_ONE_RUPEE) * POINTS_FOR_ONE_RUPEE
                loyalty_discount = points_to_redeem / POINTS_FOR_ONE_RUPEE
        elif available_points < POINTS_FOR_ONE_RUPEE:
            print("You need at least 1000 points to redeem a discount.")
    final_total = subtotal - coupon_discount - loyalty_discount
    if final_total < 0:
        final_total = 0.0
    print_separator(55)
    print("Subtotal: " + format_money(subtotal))
    print("Coupon discount: " + format_money(coupon_discount))
    print("Loyalty discount: " + format_money(loyalty_discount))
    print("FINAL AMOUNT: " + format_money(final_total))
    confirmation = input("Confirm purchase? (yes/no): ").strip().lower()
    if confirmation != "yes":
        print("Checkout cancelled. Your cart has not been changed.")
        return
    transaction_items = []
    for item in cart:
        product = find_product_by_id(int(item["id"]))
        product["quantity"] = int(product["quantity"]) - int(item["quantity"])
        transaction_items.append({
            "id": int(item["id"]),
            "name": item["name"],
            "category": item.get("category", "Other"),
            "price": float(item["price"]),
            "cost_price": float(item.get("cost_price", 0)),
            "quantity": int(item["quantity"])
        })
    points_earned = int(final_total) * POINTS_PER_RUPEE
    customer["loyalty_points"] = available_points - points_to_redeem + points_earned
    if applied_coupon is not None:
        applied_coupon["usage_count"] = int(applied_coupon.get("usage_count", 0)) + 1
        if customer["username"] not in applied_coupon.get("used_by", []):
            applied_coupon.setdefault("used_by", []).append(customer["username"])
    transaction = {
        "id": next_id(sales),
        "customer_id": int(customer["id"]),
        "customer_username": customer["username"],
        "items": transaction_items,
        "subtotal": round(subtotal, 2),
        "coupon_code": applied_coupon["code"] if applied_coupon is not None else "",
        "coupon_discount": round(coupon_discount, 2),
        "loyalty_points_redeemed": points_to_redeem,
        "loyalty_discount": round(loyalty_discount, 2),
        "loyalty_points_earned": points_earned,
        "final_total": round(final_total, 2)
    }
    sales.append(transaction)
    save_all_data()
    print_separator(55, "=")
    print("                 GROCERY STORE BILL")
    print_separator(55, "=")
    print("Transaction ID: " + str(transaction["id"]))
    print("Customer: " + customer["username"])
    print_separator(55)
    for item in transaction_items:
        item_total = float(item["price"]) * int(item["quantity"])
        print(item["name"] + " x " + str(item["quantity"]) + " = " + format_money(item_total))
    print_separator(55)
    print("Subtotal: " + format_money(subtotal))
    print("Coupon discount: " + format_money(coupon_discount))
    print("Loyalty discount: " + format_money(loyalty_discount))
    print("Amount paid: " + format_money(final_total))
    print("Points redeemed: " + str(points_to_redeem))
    print("Points earned: " + str(points_earned))
    print("Available points: " + str(customer["loyalty_points"]))
    print_separator(55, "=")
    print("Thank you for shopping with us, " + customer["username"] + "!")
    cart.clear()

def analytics_summary():
    print_header("STORE ANALYTICS SUMMARY")
    total_revenue = 0.0
    total_cost = 0.0
    total_units_sold = 0
    total_transactions = len(sales)
    total_discounts = 0.0
    for sale in sales:
        total_revenue += float(sale["final_total"])
        total_discounts += float(sale.get("coupon_discount", 0)) + float(sale.get("loyalty_discount", 0))
        for item in sale["items"]:
            total_units_sold += int(item["quantity"])
            total_cost += float(item.get("cost_price", 0)) * int(item["quantity"])

    gross_profit = total_revenue - total_cost
    stock_units = 0
    stock_cost_value = 0.0
    stock_selling_value = 0.0
    for product in products:
        quantity = int(product["quantity"])
        stock_units += quantity
        stock_cost_value += float(product.get("cost_price", 0)) * quantity
        stock_selling_value += float(product["price"]) * quantity
    print("Total sales transactions: " + str(total_transactions))
    print("Total units sold: " + str(total_units_sold))
    print("Revenue collected after discounts: " + format_money(total_revenue))
    print("Recorded discounts: " + format_money(total_discounts))
    print("Estimated gross profit: " + format_money(gross_profit))
    print("Units currently in stock: " + str(stock_units))
    print("Current inventory value at cost: " + format_money(stock_cost_value))
    print("Current inventory value at selling price: " + format_money(stock_selling_value))
    registered_customer_count = sum(1 for customer in customers if customer.get("role") == "customer")
    print("Registered customers: " + str(registered_customer_count))

def category_wise_analytics():
    print_header("CATEGORY-WISE SALES ANALYTICS")
    category_totals = {}
    for sale in sales:
        sale_subtotal = float(sale.get("subtotal", 0))
        sale_final_total = float(sale.get("final_total", 0))
        for item in sale["items"]:
            category = item.get("category", "Other")
            if category not in category_totals:
                category_totals[category] = {
                    "units": 0,
                    "sales_value": 0.0,
                    "cost_value": 0.0
                }
            item_quantity = int(item["quantity"])
            item_sales_before_discount = float(item["price"]) * item_quantity
            if sale_subtotal > 0:
                item_sales_after_discount = item_sales_before_discount * sale_final_total / sale_subtotal
            else:
                item_sales_after_discount = 0.0
            category_totals[category]["units"] += item_quantity
            category_totals[category]["sales_value"] += item_sales_after_discount
            category_totals[category]["cost_value"] += float(item.get("cost_price", 0)) * item_quantity

    if len(category_totals) == 0:
        print("There are no sales to analyze yet.")
        return
    for category, values in category_totals.items():
        gross_profit = values["sales_value"] - values["cost_value"]
        print("Category: " + category)
        print("Units sold: " + str(values["units"]))
        print("Sales revenue after allocated discounts: " + format_money(values["sales_value"]))
        print("Estimated gross profit before store expenses: " + format_money(gross_profit))
        print_separator(55)

def product_wise_analytics():
    print_header("PRODUCT-WISE VOLUME AND PROFIT")
    product_totals = {}
    for sale in sales:
        sale_subtotal = float(sale.get("subtotal", 0))
        sale_final_total = float(sale.get("final_total", 0))
        for item in sale["items"]:
            product_id = str(item["id"])
            if product_id not in product_totals:
                product_totals[product_id] = {
                    "name": item["name"],
                    "category": item.get("category", "Other"),
                    "units": 0,
                    "sales_value": 0.0,
                    "cost_value": 0.0
                }
            item_quantity = int(item["quantity"])
            item_sales_before_discount = float(item["price"]) * item_quantity
            if sale_subtotal > 0:
                item_sales_after_discount = item_sales_before_discount * sale_final_total / sale_subtotal
            else:
                item_sales_after_discount = 0.0
            product_totals[product_id]["units"] += item_quantity
            product_totals[product_id]["sales_value"] += item_sales_after_discount
            product_totals[product_id]["cost_value"] += float(item.get("cost_price", 0)) * item_quantity
    if len(product_totals) == 0:
        print("There are no sales to analyze yet.")
        return

    ranked_products = list(product_totals.values())
    ranked_products.sort(key=lambda product: product["units"], reverse=True)
    print("Products ranked by quantity sold:")
    for product in ranked_products:
        profit = product["sales_value"] - product["cost_value"]
        print(
            product["name"] + " | Category: " + product["category"] +
            " | Units sold: " + str(product["units"]) +
            " | Revenue after discounts: " + format_money(product["sales_value"]) +
            " | Gross profit estimate: " + format_money(profit)
        )
    print("\nTop-selling product: " + ranked_products[0]["name"])
    most_profitable_product = ranked_products[0]
    for product in ranked_products:
        product_profit = product["sales_value"] - product["cost_value"]
        best_profit = most_profitable_product["sales_value"] - most_profitable_product["cost_value"]
        if product_profit > best_profit:
            most_profitable_product = product
    print("Most profitable product by recorded gross profit: " + most_profitable_product["name"])

def sales_summary_report():
    print_header("SALES SUMMARY REPORT")
    total_transactions = len(sales)
    total_revenue = 0.0
    total_units_sold = 0
    for sale in sales:
        total_revenue += float(sale.get("final_total", 0))
        for item in sale.get("items", []):
            total_units_sold += int(item.get("quantity", 0))

    if total_transactions == 0:
        print("There are no sales records yet.")
        return
    print("Total transactions: " + str(total_transactions))
    print("Total units sold: " + str(total_units_sold))
    print("Total revenue collected: " + format_money(total_revenue))
    print("Average transaction value: " + format_money(total_revenue / total_transactions))

def customer_analytics():
    print_header("CUSTOMER ANALYTICS")
    customer_totals = {}
    for customer in customers:
        if customer.get("role") == "customer":
            customer_totals[customer["username"]] = {
                "orders": 0,
                "spending": 0.0,
                "points": int(customer.get("loyalty_points", 0))
            }
    for sale in sales:
        username = sale["customer_username"]
        if username not in customer_totals:
            customer_totals[username] = {"orders": 0, "spending": 0.0, "points": 0}
        customer_totals[username]["orders"] += 1
        customer_totals[username]["spending"] += float(sale["final_total"])
    if len(customer_totals) == 0:
        print("No customer data is available.")
        return
    for username, values in customer_totals.items():
        print("Customer: " + username)
        print("Orders placed: " + str(values["orders"]))
        print("Total amount spent: " + format_money(values["spending"]))
        print("Current loyalty points: " + str(values["points"]))
        print_separator(55)

    customer_names = list(customer_totals.keys())
    most_orders_username = customer_names[0]
    most_spending_username = customer_names[0]
    for username in customer_names:
        if customer_totals[username]["orders"] > customer_totals[most_orders_username]["orders"]:
            most_orders_username = username
        if customer_totals[username]["spending"] > customer_totals[most_spending_username]["spending"]:
            most_spending_username = username
    print("Most repeat orders: " + most_orders_username)
    print("Highest total spending: " + most_spending_username)

def export_sales_to_csv():
    print_header("EXPORT SALES REPORT")
    report_file = "sales_report.csv"
    field_names = [
        "transaction_id", "customer_username", "items_summary",
        "subtotal", "coupon_code", "coupon_discount", "loyalty_discount",
        "final_total", "loyalty_points_earned", "loyalty_points_redeemed"
    ]

    with open(report_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        for sale in sales:
            item_names = [item["name"] + " x " + str(item["quantity"]) for item in sale["items"]]
            writer.writerow({
                "transaction_id": sale["id"],
                "customer_username": sale["customer_username"],
                "items_summary": "; ".join(item_names),
                "subtotal": sale["subtotal"],
                "coupon_code": sale["coupon_code"],
                "coupon_discount": sale["coupon_discount"],
                "loyalty_discount": sale["loyalty_discount"],
                "final_total": sale["final_total"],
                "loyalty_points_earned": sale["loyalty_points_earned"],
                "loyalty_points_redeemed": sale["loyalty_points_redeemed"]
            })
    print("Sales report exported to " + report_file + ".")

def admin_analytics_menu():
    while True:
        print_header("ANALYTICS DASHBOARD")
        print("1. Overall store summary")
        print("2. Category-wise analytics")
        print("3. Product-wise volume and profit")
        print("4. Sales summary report")
        print("5. Customer analytics")
        print("6. Export sales report to CSV")
        print("7. Return to admin menu")

        choice = safe_int_input("Choose an option: ", minimum=1)
        if choice == 1:
            analytics_summary()
        elif choice == 2:
            category_wise_analytics()
        elif choice == 3:
            product_wise_analytics()
        elif choice == 4:
            sales_summary_report()
        elif choice == 5:
            customer_analytics()
        elif choice == 6:
            export_sales_to_csv()
        elif choice == 7:
            break
        else:
            print("Invalid choice. Please choose from 1 to 7.")

def admin_coupon_menu():
    while True:
        print_header("COUPON MANAGEMENT")
        print("1. Create coupon")
        print("2. View coupons")
        print("3. Deactivate coupon")
        print("4. Return to admin menu")
        choice = safe_int_input("Choose an option: ", minimum=1)
        if choice == 1:
            add_coupon()
        elif choice == 2:
            view_coupons()
        elif choice == 3:
            deactivate_coupon()
        elif choice == 4:
            break
        else:
            print("Invalid choice. Please choose from 1 to 4.")

def admin_menu():
    while True:
        print_header("ADMIN MENU")
        print("1. View products")
        print("2. Add product")
        print("3. Update product or stock")
        print("4. Remove product")
        print("5. Low-stock report")
        print("6. Analytics dashboard")
        print("7. Coupon management")
        print("8. View all sales history")
        print("9. Log out")
        choice = safe_int_input("Choose an option: ", minimum=1)
        if choice == 1:
            view_products()
        elif choice == 2:
            add_product()
        elif choice == 3:
            update_product()
        elif choice == 4:
            remove_product()
        elif choice == 5:
            check_low_stock()
        elif choice == 6:
            admin_analytics_menu()
        elif choice == 7:
            admin_coupon_menu()
        elif choice == 8:
            print_header("ALL SALES HISTORY")
            if len(sales) == 0:
                print("No sales have been recorded.")
            else:
                for sale in sales:
                    print(
                        "Transaction " + str(sale["id"]) +
                        " | Customer: " + sale["customer_username"] + " | Total: " +
                        format_money(float(sale["final_total"]))
                    )
        elif choice == 9:
            break
        else:
            print("Invalid choice. Please choose from 1 to 9.")

def customer_menu(customer):
    cart = []
    while True:
        print_header("CUSTOMER MENU - " + customer["username"])
        print("1. View products")
        print("2. Search products")
        print("3. Add product to cart")
        print("4. View cart")
        print("5. Update cart quantity / remove item")
        print("6. Checkout")
        print("7. View loyalty points")
        print("8. View purchase history")
        print("9. Log out")
        choice = safe_int_input("Choose an option: ", minimum=1)
        if choice == 1:
            view_products()
        elif choice == 2:
            search_products()
        elif choice == 3:
            add_to_cart(cart)
        elif choice == 4:
            view_cart(cart)
        elif choice == 5:
            update_cart_quantity(cart)
        elif choice == 6:
            checkout(customer, cart)
        elif choice == 7:
            print_header("LOYALTY ACCOUNT")
            points = int(customer.get("loyalty_points", 0))
            print("Available loyalty points: " + str(points))
            print("Redemption value: " + format_money(points / POINTS_FOR_ONE_RUPEE))
            print("Points are earned at " + str(POINTS_PER_RUPEE) + " point per whole rupee paid.")
        elif choice == 8:
            show_customer_history(customer)
        elif choice == 9:
            break
        else:
            print("Invalid choice. Please choose from 1 to 9.")

def main():

    load_all_data()
    while True:
        print_header("GROCERY MANAGEMENT SYSTEM")
        print("1. Login")
        print("2. Register as a customer")
        print("3. Exit")
        choice = safe_int_input("Choose an option: ", minimum=1)
        if choice == 1:
            logged_in_customer = login_user()
            if logged_in_customer is not None:
                if logged_in_customer["role"] == "admin":
                    admin_menu()
                else:
                    customer_menu(logged_in_customer)
        elif choice == 2:
            register_customer()
        elif choice == 3:
            save_all_data()
            print("Your data has been saved. Goodbye!")
            break
        else:
            print("Invalid choice. Please choose from 1 to 3.")

if __name__ == "__main__":
    main()
