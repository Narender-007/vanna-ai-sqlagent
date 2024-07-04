from io import StringIO
import pandas as pd
import psycopg2
import json
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore


class VannaAgent(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = VannaAgent(config={'api_key': 'sk-proj-AuVX1nOyM0Kqj8mSsYw3T3BlbkFJL1IWkuawfUW4qEB3u2YP', 'model': 'gpt-3.5-turbo-16k'})
conn_details = {'dbname':"odoo_db_16", 
        'user':"odoo_user", 
        "password":"1234", 
        "host":"localhost", 
        "port":5432 ,
       
        }  # fill this with your connection details
conn_redshift = psycopg2.connect(**conn_details)

# running
def run_sql_redshift(sql: str) -> pd.DataFrame:
    df = pd.read_sql_query(sql, conn_redshift)
    return df

vn.run_sql = run_sql_redshift
vn.run_sql_is_set = True
vn.allow_llm_to_see_data=True

# sql queries and questions traning vanna - ai
def trained_queries():
    try:
        training_data = [
        {
            "question": "What is the total tax in the month of January 2024?",
            "sql": "SELECT SUM(amount_tax) as total_tax FROM account_move WHERE invoice_date >= '2024-01-01' AND invoice_date <= '2024-01-31'"
        },
        {
            "question": "What is the total sales revenue in the month of january 2024?",
            "sql": "SELECT SUM(amount_total) as total_sales_revenue FROM sale_order WHERE date_order >= '2024-01-01 00:00:00' AND date_order <= '2024-01-31 23:59:59'"
        },
        {
            "question": "What is the average tax revenue generated from orders?",
            "sql": "SELECT AVG(tax_base_amount) AS average_tax_revenue FROM account_move_line WHERE tax_line_id IS NOT None;"
        },
        {
            "question": "What is the total tax generated",
            "sql": "SELECT SUM(tax_base_amount) as total_tax FROM account_move_line"
        },
        {
            "question": "what is today total products revenue generated?",
            "sql": "SELECT SUM(price_total) as total_revenue FROM sale_order_line WHERE create_date >= '2024-07-04 00:00:00' AND create_date <= '2024-07-31 23:59:59'"
        },
        {
            "question" : "what are the top 10 highest sales orders for the last week?",
            "sql" : "SELECT name, amount_total FROM sale_order WHERE state = 'sale' AND date_order >= '2024-06-24 00:00:00' AND date_order <= '2024-06-30 23:59:59' ORDER BY amount_total DESC LIMIT 10;"
        },
        {
            "question" : "What are the most frequently purchased products?",
            "sql" : "SELECT p.name, SUM(li.quantity) as total_quantity FROM line_items li JOIN products p ON li.product_id = p.product_id GROUP BY p.name ORDER BY total_quantity DESC LIMIT 10",
        },
        {
            "question" : "What is the recent order total price?",
            "sql" : "SELECT amount_total FROM sale_order ORDER BY date_order DESC LIMIT 1;"
        },
        {
            'question' : 'Find the total sales dicounts of today?',
            'sql' : "SELECT SUM(amount_total - amount_untaxed - amount_tax) AS total_discount FROM sale_order WHERE date_order >= '2024-07-03 00:00:00' AND date_order <= '2024-07-03 23:59:59'"
        },
        {
            'question' : 'What is the count of total customers in the month of january 2024? ',
            'sql' : "SELECT COUNT(id) FROM res_partner WHERE create_date >= '2024-01-01 00:00:00' AND create_date <= '2024-01-31 23:59:59'" 
        },
        {
            'question' : 'What is the total avarage unit per transaction?' ,
            'sql' : "SELECT AVG(qty) as average_units_per_transaction FROM pos_order_line;"
        },
        {
            'question' : 'what is the total product revenue for today?' ,
            'sql' : "SELECT SUM(amount_total) FROM sale_order WHERE date_order >= '2024-07-03 00:00:00' AND date_order <= '2024-07-03 23:59:59'"
        },
        {
            'question' : 'what is the total units ordered for today?' ,
            'sql' : "SELECT SUM(product_uom_qty) FROM sale_order_line WHERE create_date >= '2024-07-03 00:00:00' AND create_date <= '2024-07-03 23:59:59'"
        },
        {
            "question":"what is the amount of today all invoices",
            "sql":"SELECT SUM(amount_total) FROM account_move WHERE create_date >= '2024-07-03 00:00:00' AND create_date <= '2024-07-03 23:59:59' AND move_type = 'out_invoice'"
        },
        {
            "question": "what is my total average sales",
            "sql":"SELECT AVG(amount_total) as total_average_sales FROM sale_order;"
        },
        {
            "question": "what is sales yesterday",
            "sql": "SELECT * FROM sale_order WHERE DATE_TRUNC('day', date_order) = CURRENT_DATE - INTERVAL '1 day';"
        },
        {
            "question": "give me the today total sold products amount?",
            "sql": "SELECT SUM(amount_total) as today_total_products_revenue FROM sale_order WHERE DATE_TRUNC('day', date_order) = CURRENT_DATE;"
        },
        {
            "question": "What is the total expenditure on purchases for the current year?\n",
            "sql": "SELECT SUM(amount_total) as total_expenditure FROM purchase_order WHERE EXTRACT(YEAR FROM date_order) = EXTRACT(YEAR FROM CURRENT_DATE)"
        },
        {
            "question": "Que me digas el porcentaje de facturación a nivel de factura sobre mi total de 2024",
            "sql":"SELECT SUM(amount_total) as total_invoiced, SUM(amount_total_signed) as total_signed FROM account_move WHERE move_type = 'out_invoice' AND date >= '2024-01-01' AND date <= '2024-12-31'"
        },
        {
            "question":"cual es el ultimo precio de compra del Acoustic Bloc Screens",
            "sql":"SELECT price_unit FROM purchase_order_line WHERE product_id = (SELECT id FROM product_product WHERE default_code = 'FURN_6666') ORDER BY create_date DESC LIMIT 1;"
        },
        {
            "question":"Could you share a list of 5 sales products",
            "sql":"SELECT pt.name, pt.list_price FROM product_template pt LIMIT 5;"
        },
        {
            "question":'what is my sales last month by each day',
            "sql":"SELECT DATE(date_order) as order_date, SUM(amount_total) as total_sales FROM sale_order WHERE date_order >= '2024-06-01 00:00:00' AND date_order <= '2024-06-30 23:59:59' GROUP BY DATE(date_order) ORDER BY DATE(date_order)"
        },
        {
            "question":"What are the most frequently purchased products?",
            "sql":"SELECT pt.name, SUM(pol.product_qty) as total_quantity FROM purchase_order_line pol JOIN product_product pp ON pol.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id GROUP BY pt.name ORDER BY total_quantity DESC LIMIT 5;"
        },
        {
            "question":"how many purchase orders are about to receive in inventory and from which vendor?",
            "sql":"SELECT po.name AS purchase_order, rp.name AS vendor, sp.state AS picking_state FROM purchase_order po JOIN res_partner rp ON po.partner_id = rp.id JOIN stock_picking sp ON po.group_id = sp.group_id WHERE sp.state = 'assigned'"
        },
        {
            "question":"How many products have been added to inventory in the last month?",
            "sql":"SELECT COUNT(id) FROM stock_quant WHERE create_date >= '2024-06-04 00:00:00' AND create_date <= '2024-07-04 23:59:59'"
        },
        {
            "question": "How many products have been added to inventory in the last month?",
            "sql": "SELECT COUNT(*) FROM stock_move WHERE create_date >= CURRENT_DATE - INTERVAL '1 month' AND create_date < CURRENT_DATE;"
        },
        {
            "question": "How many products have been added to inventory in the this week?",
            "sql": "SELECT COUNT(id) FROM stock_quant WHERE create_date >= CURRENT_DATE - INTERVAL '6 days' AND create_date <= CURRENT_DATE + INTERVAL '1 day'"
        },
        {
            "question":"what is my sales last 7 days",
            "sql":"SELECT SUM(amount_total) as total_sales FROM sale_order WHERE date_order >= CURRENT_DATE - INTERVAL '7 days';"
        },
        {
            "question":"what is my sales this week",
            "sql":"SELECT SUM(amount_total) as total_sales FROM sale_order WHERE date_order >= CURRENT_DATE - INTERVAL '6 days' AND date_order <= CURRENT_DATE + INTERVAL '1 day'"
        },
        {
            "question":"what are my quotations",
            "sql":"SELECT name FROM sale_order WHERE state = 'draft'"
        },
        {
            "question":"what is my sales last month by each day",
            "sql":"SELECT DATE(date_order) AS order_date, SUM(amount_total) AS total_sales FROM sale_order WHERE date_order >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month' AND date_order < DATE_TRUNC('month', CURRENT_DATE) GROUP BY DATE(date_order) ORDER BY DATE(date_order)"
        },
        {
            "question":"give me list of details what is my sales last month by each day",
            "sql":"SELECT DATE(date_order) AS order_date, SUM(amount_total) AS total_sales FROM sale_order WHERE date_order >= CURRENT_DATE - INTERVAL '1 month' AND date_order < CURRENT_DATE GROUP BY DATE(date_order) ORDER BY DATE(date_order);"
        },
        {
            "question":"what is my sales last month by each day",
            "sql":""
        }

        ]

        # # Loop through the training data to train the model
        for data in training_data:
            vn.train(question=data["question"], sql=data["sql"])
        response = {"message":"training scuccessfully completed"}
    except Exception as e:
        response = {"message":str(e)}
    return response