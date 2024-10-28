from flask import Flask, jsonify
from dotenv import load_dotenv
import mysql.connector
import os
import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database connection function with SSL
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('AZURE_MYSQL_HOST'),
            user=os.getenv('AZURE_MYSQL_USER'),
            password=os.getenv('AZURE_MYSQL_PASSWORD'),
            database=os.getenv('AZURE_MYSQL_DATABASE'),
            port=int(os.getenv('AZURE_MYSQL_PORT')),
            ssl_ca="./DigiCertGlobalRootCA.crt.pem",  # Path to the SSL certificate
            ssl_verify_cert=True,
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Routes
@app.route('/currentDate', methods=['GET'])
def get_current_date():
    date = datetime.datetime.now()
    return jsonify(date=date.isoformat()), 200

@app.route('/editprofile', methods=['GET'])
def edit_profile(subID):
    conn = get_db_connection()
    if conn is None:
        return "Database connection error"
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_subscribers")
        result = cur.fetchone()
        if result:
            return jsonify(result), 200
        else:
            return "Entity not found", 404
    except Exception as e:
        print(f"Error: {e}")
        return "Error retrieving data", 500

@app.route('/home/<int:id>', methods=['GET'])
def home(id):
    conn = get_db_connection()
    if conn is None:
        return "Database connection error"
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_crops WHERE fld_s_SubscriberID_pk = %s", (id,))
        results = cur.fetchall()
        if results:
            return jsonify(results), 200
        else:
            return "Entity not found", 404
    except Exception as e:
        print(f"Error: {e}")
        return "Error retrieving data", 500

@app.route('/cropspage/<int:id>', methods=['GET'])
def crops_page(id):
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_crops WHERE fld_s_SubscriberID_pk = %s", (id,))
        results = cur.fetchall()
        if results:
            return jsonify(results), 200
        else:
            return "Entity not found", 404
    except Exception as e:
        print(f"Error: {e}")
        return "Error retrieving data", 500

@app.route('/addcrop', methods=['POST'])
def add_crop():
    data = request.get_json()
    subID = data.get('subID')
    cropData = data.get('cropData') 
    conn = get_db_connection()
    if conn is None:
        return "Database connection error"

    try:
        cur = conn.cursor()
        # Assuming cropData includes all necessary fields
        query = """
        INSERT INTO tbl_crops (fld_c_CropID_pk, fld_s_SubscriberID_pk, fld_c_ZipCode, fld_c_State, fld_f_FarmID_fk,
                               fld_m_MediumID_fk, fld_l_LocationID_fk, fld_ct_CropTypeID_fk, fld_CropImg, fld_c_HRFNumber,
                               fld_c_CropName, fld_c_Variety, fld_c_Source, fld_c_DatePlanted, fld_c_Comments,
                               fld_c_Yield, fld_c_WasStartedIndoors, fld_c_isActive)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (cropData["fld_c_CropID_pk"], subID, cropData["fld_c_ZipCode"], cropData["fld_c_State"],
                            cropData["fld_f_FarmID_fk"], cropData["fld_m_MediumID_fk"], cropData["fld_l_LocationID_fk"],
                            cropData["fld_ct_CropTypeID_fk"], cropData["fld_CropImg"], cropData["fld_c_HRFNumber"],
                            cropData["fld_c_CropName"], cropData["fld_c_Variety"], cropData["fld_c_Source"],
                            cropData["fld_c_DatePlanted"], cropData["fld_c_Comments"], cropData["fld_c_Yield"],
                            cropData["fld_c_WasStartedIndoors"], cropData["fld_c_isActive"]))
        conn.commit()
        return "Crop added successfully", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error adding crop", 500

@app.route('/connect', methods=['GET'])
def connect():
    conn = get_db_connection()
    if conn is None:
        return "Database connection error"
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_subscribers;")
        results = cur.fetchall()
        return jsonify(results), 200
    except Exception as e:
        print(app.config)
        print(f"Error: {e}")
        return "Error connecting to database", 500

@app.route('/')
def index():
    return "This thing on?", 200

# Error handling for 404
@app.errorhandler(404)
def not_found(e):
    return "Sorry, can't find that!", 404

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT')), debug=True)
