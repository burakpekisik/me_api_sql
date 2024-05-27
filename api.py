from flask import Flask, jsonify, Response, json, request
from flask_restful import Resource, Api
from GetOrderData import getOrderData
from GetCustomerData import getCustomerData
# import pandas as pd
import mysql.connector
from datetime import datetime
import city_ids
import userInfo

app = Flask("ExcelAPI")
api = Api(app)

# Establish connection to MySQL database
db_connection = mysql.connector.connect(
    host=userInfo.db_host,
    user=userInfo.db_username,
    password=userInfo.db_password,
    database=userInfo.db_database
)

def prepare_word(word):
    turkish_chars = "çğıöşüÇĞİÖŞÜ"
    english_chars = "cgiosuCGIOSU"
    translation_table = str.maketrans(turkish_chars, english_chars)
    word = word.translate(translation_table)
    word = word.lower()
    word = word.replace(" ", "")
    return word

def get_phone_number(phone_number):
    if phone_number.startswith("0"):
        phone_number = phone_number[1:]
    elif phone_number.startswith("+90"):
        phone_number = phone_number.replace("+90", "")
    elif phone_number.startswith("+"):
        phone_number = phone_number.replace("+", "00")
    phone_number = phone_number.replace(" ", "")
    phone_number = phone_number.replace("(", "")
    phone_number = phone_number.replace(")", "")
    phone_number = phone_number.replace("-", "")

    return phone_number

def get_customer_id(customer_name):
    db_cursor = db_connection.cursor()

    # Prepare customer name
    customer_name = prepare_word(customer_name)

    # Find customer ID
    select_query = "SELECT customer_id FROM customer_list WHERE LOWER(REPLACE(customer_name, ' ', '')) = %s"
    db_cursor.execute(select_query, (customer_name,))
    result = db_cursor.fetchall()

    if result:
        customer_id = result[0][0]
    else:
        customer_id = None
    #     # If customer doesn't exist, insert new customer and get its ID
    #     insert_query = "INSERT INTO customer_list (customer_name) VALUES (%s)"
    #     db_cursor.execute(insert_query, (customer_name,))
    #     db_connection.commit()
    #     customer_id = db_cursor.lastrowid

    return customer_id

class OrderData(Resource):
    def get(self, customer_name):
        data = getOrderData()
        customerDatas = getCustomerData()
        email_mapping = {prepare_word(customerData['customer_name']): customerData['email'] for customerData in customerDatas}

        if customer_name == "all":
            for row in data:
                row["email"] = email_mapping.get(prepare_word(row['customer_name']), "")
            return Response(json.dumps(data, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')
        
        elif customer_name == "last":
            last_orders = data[:50]  # Get the last 50 orders
            for row in last_orders:
                row["email"] = email_mapping.get(prepare_word(row['customer_name']), "")
            return Response(json.dumps(last_orders, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')

        elif str(customer_name).isalpha():
            found_orders = [row for row in data if prepare_word(row['customer_name']) == prepare_word(customer_name)]
            for row in found_orders:
                row["email"] = email_mapping.get(prepare_word(row['customer_name']), "")
            if found_orders:
                return Response(json.dumps(found_orders, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')
            else:
                return Response(json.dumps({"error": "Order not found."}, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')
        
        elif str(customer_name).isdigit():
            found_order = next((row for row in data if str(row['order_id']) == str(customer_name)), None)
            if found_order:
                found_order["email"] = email_mapping.get(prepare_word(found_order['customer_name']), "")
                return Response(json.dumps(found_order, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')
            else:
                return Response(json.dumps({"error": "Order not found."}, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')

class CustomerData(Resource):
    def get(self, customer_name):
        data = getCustomerData()
        found_customers = [row for row in data if prepare_word(row['customer_name']) == prepare_word(customer_name)]
        
        if customer_name == "all":
            return Response(json.dumps(data, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')
        elif found_customers:
            return Response(json.dumps(found_customers, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')
        else:
            return Response(json.dumps({"error": "Customer not found."}, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')

class ImportTrackID(Resource):
    def post(self, order_id, track_id):
        try:
            order_details = self.updateTrackID(order_id, track_id)
            return Response(json.dumps(order_details, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')
        except Exception as e:
            return Response(json.dumps({"error": str(e)}, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')

    def updateTrackID(self, order_id, track_id):
        
        db_cursor = db_connection.cursor()

        # Update track_id for the specified order_id
        try:
            if str(order_id).startswith("WP_"):
                table_name = "whatsapp_orders"
            else:
                table_name = "website_orders"

            update_query = f"UPDATE {table_name} SET track_id = %s WHERE order_id = %s"
            db_cursor.execute(update_query, (track_id, order_id))
            db_connection.commit()

            # Retrieve updated order details
            select_query = f"SELECT * FROM {table_name} WHERE order_id = %s"
            db_cursor.execute(select_query, (order_id,))
            order_details = db_cursor.fetchone()

            if str(order_id).startswith("WP_"):
                return {
                    "customer_id": "0",
                    "customer_name": order_details[1],
                    "date_for_transport": order_details[7],
                    "letter_name": order_details[4],
                    "order_date": order_details[6],
                    "order_id": order_details[0],
                    "order_price": order_details[5],
                    "phone_number": order_details[2],
                    "track_id": track_id
                }
            else:
                return {
                    "customer_id": order_details[6],
                    "customer_name": order_details[1],
                    "date_for_transport": order_details[7],
                    "letter_name": order_details[3],
                    "order_date": order_details[4],
                    "order_id": order_details[0],
                    "order_price": order_details[2],
                    "phone_number": order_details[5],
                    "track_id": track_id
                }
        except mysql.connector.Error as err:
            db_connection.rollback()
            raise err

class AddOrder(Resource):
    def post(self):
        content_type = request.headers.get('Content-Type')
        
        if content_type == 'application/json':
            data = request.json
        else:
            return "Content type is not supported."

        try:
            db_cursor = db_connection.cursor()

            # Prepare order data
            order_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            phone_number = get_phone_number(data.get('phoneNumber', ''))
            customer_name = data.get('customerName', '')
            order_price = data.get('orderPrice', '')
            letter_name = data.get('letterName', 'Cezaevine Mektup')
            email = data.get('email', '')
            isWhatsApp = data.get('isWhatsApp', True)

            # Calculate new order_id
            if isWhatsApp:
                # Fetch last order_id from the database
                last_order_id_query = "SELECT MAX(CAST(SUBSTRING(order_id, 4) AS UNSIGNED)) FROM whatsapp_orders WHERE order_id LIKE 'WP_%'"
                db_cursor.execute(last_order_id_query)
                last_order_id = db_cursor.fetchone()[0]

                if last_order_id:
                    new_order_id = f"WP_{last_order_id + 1}"
                else:
                    new_order_id = "WP_1"
            else:
                last_order_id_query = "SELECT MAX(order_id) FROM website_orders"
                db_cursor.execute(last_order_id_query)
                last_order_id = db_cursor.fetchone()[0]

                if last_order_id:
                    new_order_id = last_order_id + 1
                else:
                    new_order_id = 1

            # Insert order data into the database
            if (isWhatsApp):
                insert_query = "INSERT INTO whatsapp_orders (order_id, customer_name, phone_number, email, letter_name, order_price, order_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                db_cursor.execute(insert_query, (new_order_id, customer_name, phone_number, email, letter_name, order_price, order_date))
            else:
                date_for_transport = ""
                customer_id = get_customer_id(customer_name)
                if customer_id is None:
                    return Response(json.dumps({"error": "Customer not found"}, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')
                insert_query = "INSERT INTO website_orders (order_id, customer_name, order_price, letter_name, order_date, phone_number, customer_id, date_for_transport) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                db_cursor.execute(insert_query, (new_order_id, customer_name, order_price, letter_name, order_date, phone_number, customer_id, date_for_transport))

            db_connection.commit()

            # Construct response data
            response_data = {
                'order_id': new_order_id,
                'customer_name': customer_name,
                'phone_number': phone_number,
                'email': email,
                'letter_name': letter_name,
                'order_price': order_price,
                'order_date': order_date
            }

            return Response(json.dumps(response_data, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')

        except mysql.connector.Error as err:
            return Response(json.dumps({"error": str(err)}, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')

class AddCustomer(Resource):
    def post(self):
        content_type = request.headers.get('Content-Type')
        
        if content_type == 'application/json':
            data = request.json
        else:
            return "Content type is not supported."

        try:
            db_cursor = db_connection.cursor()

            # Fetch last order_id from the database
            last_customer_id_query = "SELECT MAX(customer_id) FROM customer_list"
            db_cursor.execute(last_customer_id_query)
            last_customer_id_query = db_cursor.fetchone()[0]

            # Calculate new order_id
            if last_customer_id_query:
                new_customer_id = int(last_customer_id_query) + 1
            else:
                new_customer_id = 1

            # Prepare order data
            customer_id = int(new_customer_id)
            customer_name = data.get('customerName', '')
            email = data.get('email', '')
            status = data.get('status', '')
            privilage = data.get('privilage', '')
            signup_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert order data into the database
            insert_query = "INSERT INTO customer_list (customer_id, customer_name, email, status, privilage, signup_date) VALUES (%s, %s, %s, %s, %s, %s)"
            db_cursor.execute(insert_query, (customer_id, customer_name, email, status, privilage, signup_date))
            db_connection.commit()

            # Construct response data
            response_data = {
                'customer_id': customer_id,
                'customer_name': customer_name,
                'email': email,
                'status': status,
                'privilage': privilage,
                'signup_date': signup_date
            }

            return Response(json.dumps(response_data, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')

        except mysql.connector.Error as err:
            return Response(json.dumps({"error": str(err)}, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')
            
class GetJail(Resource):
    def get(self, jail_name):
        db_cursor = db_connection.cursor()

        if (str(jail_name[0]).islower):
            jail_name = str(jail_name[0]).upper() + jail_name[1:]

        if jail_name in city_ids.sehirler:
            jail_id = city_ids.sehirler[jail_name]
        else:
            return Response(json.dumps({"error": "Invalid jail name."}, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')

        select_query = "SELECT * FROM cezaevi_list WHERE CityID = %s"
        db_cursor.execute(select_query, (jail_id,))
        jail_data = db_cursor.fetchall()

        if jail_data:
            jails = []
            for data in jail_data:
                jail = {
                    "id": data[0],
                    "CityID": data[1],
                    "name": data[2],
                    "adres": data[3],
                    "tipi": data[4]
                }
                jails.append(jail)
            return jsonify(jails)
        else:
            return Response(json.dumps({"error": "Jail data not found."}, ensure_ascii=False).encode('utf8'), content_type='application/json; charset=utf-8')

api.add_resource(OrderData, '/orders/<customer_name>')
api.add_resource(CustomerData, '/customers/<customer_name>')
api.add_resource(ImportTrackID, '/import_track/<order_id>/<track_id>')
api.add_resource(AddOrder, '/add_order')
api.add_resource(AddCustomer, '/add_customer')
api.add_resource(GetJail, '/jails/<jail_name>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
