from flask import Flask, jsonify, request,render_template
import pandas as pd
import requests as req
from datetime import date,datetime,timedelta
import logging
import random
from flask_socketio import SocketIO
import urllib.parse
from flask_accept import accept
import json
from flask_sse import sse
from flask_cors import CORS
from redis.commands.core import ResponseT
from urllib.parse import parse_qs
import csv
import os

app = Flask(__name__)
CORS(app)
app.config["REDIS_URL"] = "redis://localhost:6379"
CORS(sse)
app.register_blueprint(sse, url_prefix='/sse')

today=datetime.now()

holiday=[]

df=pd.DataFrame()

logging.basicConfig(level=logging.DEBUG)
data = pd.read_csv('supply_chain_data.csv')

products_to_generate = 100
log_csv_file_path = 'discount_data.csv'

def read_csv_file(filepath):
    data=[]
    try:
        with open(filepath,mode='r',newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Error writing to file {e}")

    return data 
def clear_csv_file(filepath):
    with open(filepath,'w',newline='') as file:
        writer= csv.writer(file)
        writer.writerow(['Product ID','Discount'])

@app.route('/products', methods=['GET'])
def get_products():

    products = data.to_dict(orient='records')
    return jsonify({'products': products})

def calculate_stock_need(product_data):
    
    total_stock=product_data['Availability']+product_data['Number of products sold']
    availability_percentage= (product_data['Availability']/total_stock) * 100
    
    return availability_percentage #return true if the stock needed


@app.route('/analyze_discount', methods=['GET'])
def adjust_prices():

    #For recording Supply-Chain Data

    
    products= data.to_dict(orient='records')
    product_number=0
    if products:
        for product in products:
            product_number +=1
            availability_percentage = calculate_stock_need(product)
            discount = discount_calculation(availability_percentage)
        
        return jsonify(products)
    else:
        return jsonify({'error': 'No products found'})
            

def discount_calculation(availability_percentage):

    discount_percentage=0
    if availability_percentage >50:
        discount_percentage+=20
    elif availability_percentage>25:
        discount_percentage+=10

    return discount_percentage #to make sure there isn't too much discount added

@app.route('/generate_order',methods=['GET'])
def generate_order():
    
    #For generating new availability and prices for a new day simulation

    availability = [random.randint(1, 100) for _ in range(products_to_generate)]
    number_of_products_sold = [random.randint(8, 1000) for _ in range(products_to_generate)]
    stock_levels = [random.randint(1, 100) for _ in range(products_to_generate)]

    df = pd.DataFrame()
    df['SKU'] = data['SKU']
    df['Price'] = data['Price']
    df['Availability'] = availability
    df['Number of products sold'] = number_of_products_sold
    df['Stock levels'] = stock_levels

    products = df.to_dict(orient='records')

    if products:
        return jsonify(products)
    else:
        return jsonify({'message': 'product not found'}),404

@app.route('/products/all', methods=['GET'])
def get_products_all():

    #product = data[data['SKU'].str.upper().str.strip() == sku.upper()].to_dict(orient='records')
    product = data.to_dict(orient='records')

     
    if product:
        return jsonify({'product': product})

    else:
        return jsonify({'message': 'product not found'}),404



@app.route('/products/analyze', methods=['GET'])
def analyze_products():

    try:
        analyzed_products = []  # List to hold all processed products

        for index, row in data.iterrows():
            product_data = row.to_dict()  # Convert each row to a dictionary
        
            total_stock = product_data['Availability'] + product_data['Number of products sold']
            availability_percentage = calculate_stock_need(product_data)
            stock_threshold = 15 #as an example -->can be changed later
      
            stock_need = availability_percentage<stock_threshold
            product_data['Stock Need'] = stock_need


            analyzed_products.append(product_data)  # Add the processed product data to the line

        return jsonify({'analyzed_products': analyzed_products})
    
    except Exception as e:
        app.logger.error(f"Error fetching products : {e}")
        return jsonify({'message': 'Internal server error'}),500

@app.route('/calendar',)
def get_calendar():
    
    #For checking if there's a holiday exists in the next 7 days


    global today
    target_week = today + timedelta(days=7)
    base_url='https://date.nager.at/api/v3/publicholidays/2024/DE'
    response = req.get(base_url)
    holiday=[]
    for i in response.json():
        if datetime.strptime(i['date'],'%Y-%m-%d') < target_week and datetime.strptime(i['date'],'%Y-%m-%d') > today:
            holiday.append({'name':i['name'],'date':i['date'],'types':i['types']})
    return jsonify(holiday)

@app.route('/check_calendar',methods=['GET'])
def check_holiday():
    
    #Returns true if there's a holiday present in the next 7 days

    calendar_response = get_calendar().get_json()
    is_holiday= calendar_response !=[]

    return jsonify(is_holiday)

@app.route('/calendar_discount',methods=['GET'])
def calendar_discount():
    

    #Returns the holiday discount to the CPEE

    return jsonify(15)

@app.route('/receive_data',methods=['GET','POST'])
def receive_discount():


    #Creates/Writes the data coming from CPEE to the new csv


    #decoded_data = urllib.parse.unquote(request.get_data().decode("utf-8"))
   # data = json.loads(decoded_data.split('=')[1])
    data = request.get_data().decode('utf-8')
    parsed_data = parse_qs(data)
    # print(parsed_data)
    product_id = parsed_data.get('product_id',[''])[0]
    discount = parsed_data.get('discount',[''])[0]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_exists = False
    if os.path.exists(log_csv_file_path):
        file_exists = True

    try:
        with open(log_csv_file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["SKU", "Discount", "Timestamp"])

            writer.writerow([product_id, discount, timestamp])

    except Exception as e:
        print(f"Error writing to file {e}")

    return jsonify(), 200

#@app.before_request
#def before_request():
#     instance_header = request.headers.get('instance')

#     if instance_header != 'flaskardelen':

#          return jsonify({'message':'Access denied'}),403

@app.route('/',methods=['POST'])
def receive_discount2():
    
    #For filtering and getting the 'Data Probes' that is sent from CPEE and to send it with SSE 

    notification_str=request.form.get('notification',None)
    # print(request.form)
    # print('-----------------------------')
    if not notification_str: 
        return jsonify({'error':'Notification data not found'}),400

    notification = json.loads(notification_str)
    # print(notification_str)
    if notification.get('instance-name')=='flaskardelen' and notification.get('content', {}).get('activity') == 'a6':
        updated_values = notification.get('content', {}).get('values', {}).get('updated_values', [])
        # print(updated_values)
        if updated_values is None:
            updated_values = json.dumps([])
        # extracted_values= {}
        # for item in updated_values:
            # sku_discount_pair=item.get('null') #new
           # for key,value in item.items():
               # if key=="null":
                   # for pair in value:
            # if isinstance(sku_discount_pair,list) and len(sku_discount_pair) ==2: #pair became sku_discount_pair 
                             # sku,discount=sku_discount_pair
                             # extracted_values[sku]=discount
            # else:
                            # print("Invalid pair format:",sku_discount_pair)
        sse.publish(updated_values)
        print(datetime.now())
        print(updated_values)
        print('-----------------------------------------')
        # return jsonify({'message': 'Data processed successfully', 'data': extracted_values}), 200
    # else:
         # return jsonify({'message': 'Data not from our instance or activity not a6'}), 200
    return jsonify(), 200

@app.route('/dummy',methods=['GET','POST'])
def dummy():

    #This reads the csv file and compares its timestamp with the timestamp sent from CPEE to send the newest values

    last_read_timestamp = request.args.get('last_read_timestamp')
    # Define the format of the string
    #format_string = "%Y-%m-%d %H:%M:%S %z"
    format_string = "%Y-%m-%d %H:%M:%S"
    format_string_without ="%Y-%m-%d %H:%M:%S"
    if not last_read_timestamp:
        last_read_timestamp = datetime.now().strftime(format_string_without)
    # Parse the string into a datetime object
   # print(f'The length of the result: {len(result)}')
            
    datetime_object = datetime.strptime(last_read_timestamp, format_string).replace(tzinfo=None)
   # datetime_object = datetime.strptime(last_read_timestamp, format_string)
    if not os.path.exists(log_csv_file_path):
        return jsonify(), 200
    df = pd.read_csv(log_csv_file_path)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format=format_string_without)

    result = df[df["Timestamp"] >= datetime_object]
    result = result.sort_values(by=['SKU', 'Timestamp'], ascending=[True, False])
    result = result.drop_duplicates(subset=['SKU'], keep='first')

    result['SKU_Number'] = result['SKU'].str.replace('SKU', '').astype(int)
    result = result[(result['SKU_Number'] < 10)]
    result = result.drop(columns=['SKU_Number'])

    result_json = json.dumps(result.to_json(orient="records"))
    # print(last_read_timestamp)
    # print(result_json)

    return jsonify(result_json), 200
