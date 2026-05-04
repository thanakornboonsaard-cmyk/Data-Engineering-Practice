import json
import os
import psycopg2
from psycopg2.extras import execute_values

# 1. ข้อมูลการเชื่อมต่อและพาธไฟล์ที่ระบุ
DATA_PATH = r"C:\Users\ASUS\Downloads\aCommerce_-_Data_Engineer_-_Quiz_(4) (2)\aCommerce_-_Data_Engineer_-_Quiz\quiz_data_engineer\2_sql\sample_data"
DB_CONFIG = {
    "host": "localhost",
    "dbname": "de_exam",
    "user": "de_user",
    "password": "password",
    "port": 5432
}

def load_json(file_name):
    """ฟังก์ชันสำหรับอ่านไฟล์ JSON จากพาธที่กำหนด"""
    file_full_path = os.path.join(DATA_PATH, file_name)
    if not os.path.exists(file_full_path):
        print(f"Warning: File {file_name} not found at {file_full_path}")
        return None
    with open(file_full_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_etl():
    conn = None
    try:
        # เชื่อมต่อฐานข้อมูล
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print(f"Connected to database '{DB_CONFIG['dbname']}' successfully.")

        # --- ส่วนที่ 1: Master Data ---
        
        # Shop
        shop_data = load_json('shop.json')
        if shop_data:
            if isinstance(shop_data, dict): shop_data = [shop_data]
            execute_values(cur, """
                INSERT INTO shop (shop_id, shop_name, country, created_time) 
                VALUES %s ON CONFLICT (shop_id) DO NOTHING
            """, [(s['shopId'], s['shopName'], s['country'], s['createdTime']) for s in shop_data])

        # Item
        item_data = load_json('item.json')
        if item_data:
            execute_values(cur, """
                INSERT INTO item (item_id, item_type, item_name, created_time) 
                VALUES %s ON CONFLICT (item_id) DO NOTHING
            """, [(i['itemId'], i['itemType'], i['itemName'], i['createdTime']) for i in item_data])

        # Promotion & Promotion Product
        promo_data = load_json('promotion.json')
        if promo_data:
            for p in promo_data:
                cur.execute("""
                    INSERT INTO promotion (promotion_id, promotion_name, start_time, end_time) 
                    VALUES (%s, %s, %s, %s) ON CONFLICT (promotion_id) DO NOTHING
                """, (p['promotionId'], p['promotionName'], p['startTime'], p['endTime']))
                
                promo_products = [(p['promotionId'], prod_id) for prod_id in p['products']]
                execute_values(cur, """
                    INSERT INTO promotion_product (promotion_id, product_id) 
                    VALUES %s ON CONFLICT DO NOTHING
                """, promo_products)

        # Exchange Rate
        rate_data = load_json('daily_usd_exchange_rate.json')
        if rate_data:
            rates_to_insert = []
            for r in rate_data:
                for curr, val in r['rates'].items():
                    rates_to_insert.append((r['date'], curr, val))
            execute_values(cur, """
                INSERT INTO daily_usd_exchange_rate (rate_date, currency_code, rate) 
                VALUES %s ON CONFLICT (rate_date, currency_code) DO NOTHING
            """, rates_to_insert)

        # --- ส่วนที่ 2: Transaction Data ---

        # Sales Order & Lines
        so_data = load_json('sales_order.json')
        if so_data:
            for so in so_data:
                cur.execute("""
                    INSERT INTO sales_order (sales_order_id, shop_id, created_time, currency_code) 
                    VALUES (%s, %s, %s, %s) ON CONFLICT (sales_order_id) DO NOTHING
                """, (so['salesOrderId'], so['shopId'], so['createdTime'], so['currencyCode']))
                
                for line in so['products']:
                    cur.execute("""
                        INSERT INTO sales_order_line (sales_order_id, line_number, product_id, quantity, gross_amount, reference_line_number) 
                        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (sales_order_id, line_number) DO NOTHING
                    """, (so['salesOrderId'], line['lineNumber'], line['productId'], line['quantity'], line['grossAmount'], line.get('referenceLineNumber')))
                    
                    soli_data = [(so['salesOrderId'], line['lineNumber'], item['itemId'], item['type'], item['quantity']) for item in line['items']]
                    execute_values(cur, """
                        INSERT INTO sales_order_line_item (sales_order_id, line_number, item_id, item_type, quantity) 
                        VALUES %s ON CONFLICT DO NOTHING
                    """, soli_data)

        # Item Receipt
        receipt_data = load_json('item_receipt.json')
        if receipt_data:
            for r in receipt_data:
                cur.execute("""
                    INSERT INTO item_receipt (receipt_id, supplier_id, received_time, currency_code) 
                    VALUES (%s, %s, %s, %s) ON CONFLICT (receipt_id) DO NOTHING
                """, (r['receiptId'], r['supplierId'], r['receivedTime'], r['currencyCode']))
                
                receipt_lines = [(r['receiptId'], l['lineNumber'], l['itemId'], l.get('expiryDate'), l['quantity'], l['purchased_amount']) for l in r['receiptDetail']]
                execute_values(cur, """
                    INSERT INTO item_receipt_line (receipt_id, line_number, item_id, expiry_date, quantity, purchased_amount) 
                    VALUES %s ON CONFLICT (receipt_line_id) DO NOTHING
                """, receipt_lines)

        conn.commit()
        print("Data ingestion to 'de_exam' completed successfully.")

    except Exception as e:
        print(f"Error during ETL process: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    run_etl()