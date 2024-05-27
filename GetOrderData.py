import pandas as pd
import userInfo
from sqlalchemy import create_engine

def getOrderData():
    # Creating SQLAlchemy engine
    engine = create_engine(f"mysql+mysqlconnector://{userInfo.db_username}:{userInfo.db_password}@{userInfo.db_host}/{userInfo.db_database}")

    # MySQL query to fetch website_orders data
    website_orders_query = "SELECT * FROM website_orders"
    website_orders_df = pd.read_sql(website_orders_query, con=engine)

    # MySQL query to fetch whatsapp_orders data
    whatsapp_orders_query = "SELECT order_id, customer_name, phone_number, email, letter_name, order_price, order_date, track_id FROM whatsapp_orders"
    whatsapp_orders_df = pd.read_sql(whatsapp_orders_query, con=engine)

    # Selecting necessary columns from website_orders table
    website_orders_columns = ['order_id', 'customer_name', 'order_price', 'letter_name', 'order_date', 'phone_number', 'customer_id', 'date_for_transport', 'track_id']
    website_orders_df = website_orders_df[website_orders_columns]

    # Selecting necessary columns from whatsapp_orders table
    whatsapp_orders_columns = ['order_id', 'customer_name', 'phone_number', 'email', 'letter_name', 'order_price', 'order_date', 'track_id']
    whatsapp_orders_df = whatsapp_orders_df[whatsapp_orders_columns]

    # Merging data from both tables
    combined_df = pd.concat([website_orders_df, whatsapp_orders_df], ignore_index=True, sort=False)

    # Converting order_date column to datetime type
    combined_df['order_date'] = pd.to_datetime(combined_df['order_date'], format="%d/%m/%Y %H:%M:%S")

    # Cleaning NaN and infinite values
    combined_df['customer_id'] = combined_df['customer_id'].fillna(0)
    combined_df['customer_id'] = combined_df['customer_id'].replace([float('inf'), float('-inf')], 0)
    combined_df['track_id'] = combined_df['track_id'].where(combined_df['track_id'].notnull(), None)
    combined_df['customer_id'] = combined_df['customer_id'].astype(int)

    # Sorting by order_date column
    combined_df = combined_df.sort_values(by='order_date', ascending=False)

    # Convert order_date back to original format
    combined_df['order_date'] = combined_df['order_date'].dt.strftime("%d/%m/%Y %H:%M:%S")

    # Replace NaN date_for_transport with a message
    combined_df['date_for_transport'] = combined_df['date_for_transport'].apply(lambda x: "Bu Bir WhatsApp Siparişidir." if pd.isna(x) else x)

    # Converting DataFrame to dictionary
    data_dict = combined_df.to_dict(orient='records')

    return data_dict


