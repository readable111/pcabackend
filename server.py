from flask import Flask, jsonify, request
from dotenv import load_dotenv
import mysql.connector
import random
import os
import datetime

'''TO DO LIST:
    endpoints:
    display profile information --Done
    edit profile information --Done
    edit crop information  --Done
    list tasks 
        list all tasks
        list tasks by farmer --Done
    edit tasks --Done
    create crop types
    create task types
    delete task types
    create mediums
    delete mediums
    create locations
    delete locations
    delete crops
    create farmer
    delete farmer
    create farm
    delete farm
    create journal entry
    delete journal entry
    modify journal entry
    Crop Search query
'''
rand = random.SystemRandom()

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

#current Date:w
@app.route('/currentDate', methods=['GET'])
def get_current_date():
    date = datetime.datetime.now()
    return jsonify(date=date.isoformat()), 200

#Get a subscribers information
@app.route('/subscriberInfo/<string:subID>', methods=['GET'])
def edit_profile(subID):
    conn = get_db_connection()
    if conn is None:
        return "Database connection error"
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_subscribers WHERE fld_s_SubscriberID_pk = %s")
        result = cur.fetchone()
        if result:
            return jsonify(result), 200
        else:
            return "Entity not found", 404
    except Exception as e:
        print(f"Error: {e}")
        return "Error retrieving data", 500
    finally:
        cur.close()

#Update a subscribers information 
@app.route('/updateSubscriberInfo', methods=['POST'])
def updateSubscriberInfo():
    params = request.get_json()
    subID =params.get('subID')
    newSubInfo = params.get('subData')
    conn = get_db_connection()
    if conn is None:
        return "Database connection error"
    try:
        cur = conn.cursor()
        query = """
        UPDATE tbl_subscribers  SET fld_s_FirstName=%s, fld_s_LastName=%s, fld_s_ProfilePicture=%s, fld_s_EmailAddr=%s,
        fld_s_StreetAddr=%s, fld_s_City=%s, fld_s_PostalCode=%s, fld_s_PhoneNum=%s, fld_s_HasAmbientWeather=%s,
        fld_s_AmbientWeatherKey=%s WHERE fld_s_SubscriberID_pk = %s
        """ 
        cur.execute(query, (newSubInfo['fld_s_FirstName'], newSubInfo['fld_s_LastName'], newSubInfo['fld_s_ProfilePicture'],
                    newSubInfo['fld_s_EmailAddr'], newSubInfo['fld_s_StreetAddr'], newSubInfo['fld_s_City'], newSubInfo['fld_s_PostalCode'],
                    newSubInfo['fld_s_PhoneNum'], newSubInfo['fld_s_HasAmbientWeather'], newSubInfo['fld_s_AmbientWeatherKey'], subID))
        conn.commit()
        return "Updated Subscriber Info Successfully"
    except Exception as e:
        print(f"Error: {e}")
        return "Error updating database", 500
    finally:
        cur.close()

#Get all a subscribers crops
@app.route('/getCrops/<string:subID>', methods=['GET'])
def getCrops(subID):
    params = request.get_json()
    subID = params.get("subID")
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
    finally:
        cur.close()
    

#Get list of Subscriber crops
@app.route('/cropspage/<string:subID>/<int:cropID>', methods=['GET'])
def crops_page(subID, cropID):
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_crops WHERE fld_s_SubscriberID_pk = %s AND fld_c_CropID_pk = %s", (subID, cropID))
        results = cur.fetchall()
        if results:
            return jsonify(results), 200
        else:
            return "Entity not found", 404
    except Exception as e:
        print(f"Error: {e}")
        return "Error retrieving data", 500
    finally:
        cur.close()

#Add a crop to tbl_crops
@app.route('/addcrop', methods=['POST'])
def add_crop():
    data = request.get_json()
    subID = data.get('subID')
    cropData = data.get('cropData') 
    newCropID = rand.randint()
    conn = get_db_connection()
    if conn is None:
        return "Database connection error"

    try:
        cur = conn.cursor()
        # Assuming cropData includes all necessary fields
        query = """
        INSERT INTO tbl_crops (fld_c_CropID_pk, fld_s_SubscriberID_pk, fld_c_ZipCode, fld_c_State, fld_f_FarmID_fk, fld_c_HRFNumber
                               fld_m_MediumID_fk, fld_l_LocationID_fk, fld_ct_CropTypeID_fk, fld_CropImg, fld_c_HRFNumber,
                               fld_c_CropName, fld_c_Variety, fld_c_Source, fld_c_DatePlanted, fld_c_Comments,
                               fld_c_Yield, fld_c_WasStartedIndoors, fld_c_isActive)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (newCropID, subID, cropData["fld_c_ZipCode"], cropData["fld_c_State"],
                            cropData["fld_f_FarmID_fk"], cropData['fld_c_HRFNumber'], cropData["fld_m_MediumID_fk"], cropData["fld_l_LocationID_fk"],
                            cropData["fld_ct_CropTypeID_fk"], cropData["fld_CropImg"], cropData["fld_c_HRFNumber"],
                            cropData["fld_c_CropName"], cropData["fld_c_Variety"], cropData["fld_c_Source"],
                            cropData["fld_c_DatePlanted"], cropData["fld_c_Comments"], cropData["fld_c_Yield"],
                            cropData["fld_c_WasStartedIndoors"], cropData["fld_c_isActive"]))
        conn.commit()
        return "Crop added successfully", 200
    except mysql.connector.IntegrityError as err: #Handling duplicate keys, this method only called if the key generated is in conflict witht the records in the table
        if "Duplicate entry" in str(err):
            print(f"Primary Key conflict ... Attempting with new key")
            return add_crop()
    except Exception as e:
        print(f"Error: {e}")
        return "Error adding crop", 500
    finally:
        cur.close()

#Update a subscribers information 
@app.route('/updateCropInfo', methods=['POST'])
def updateSubscriberInfo(subID):
    params = request.get_json()
    subID =params.get('subID')
    cropUpdate = params.get('cropData')
    conn = get_db_connection()
    if conn is None:
        return "Database connection error"
    try:
        cur = conn.cursor()
        query = """
        UPDATE tbl_crops SET  fld_m_MediumID_fk, fld_f_FarmID_fk =%s, fld_ct_CropTypeID_fk=%s, fld_CropImg=%s, fld_c_CropName=%s, fld_c_Variety=%s,
        fld_c_Source=%s, fld_c_DatePlanted=%s, fld_c_Comments=%s,
        fld_c_Yield=%s, fld_c_IsActive=%s, fld_c_WasStartedIndoors=%s WHERE fld_s_SubscriberID_pk = %s
        """ 
        cur.execute(query, ( cropUpdate['fld_m_MediumId_fk'], cropUpdate['fld_f_FarmID_fk'], cropUpdate['fld_ct_CropTypeID_fk'], cropUpdate['fld_CropImg'],
                    cropUpdate['fld_c_CropName'], cropUpdate['fld_c_Variety'], cropUpdate['fld_c_Source'], cropUpdate['fld_c_DatePlanted'], cropUpdate['fld_c_Comments'],
                    cropUpdate['fld_c_Yield'], cropUpdate['fld_c_IsActive'], cropUpdate['fld_sc_WasStartedIndoors'], subID))
        conn.commit()
        return "Updated Subscriber Info Successfully"
    except Exception as e:
        print(f"Error: {e}")
        return "Error updating database", 500
    finally:
        cur.close()
    
    
@app.route('/searchCrops/<string:subID>/<string:userInput', methods=['GET'])
def searchCrops():
    params = request.get_json()

    conn=get_db_connection()
    if conn is None:
        return "Database Connection Error"
    
    

#test database connection
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
    finally: cur.close()


#Route for listing tasks by farmer    
@app.route('/listTasks/<string:subID>/<int:farmerID>', methods=['GET'])
def listTasks():
    conn = get_db_connection()
    if conn is None:
        return "Database connection error"
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_tasks WHERE fld_s_SubscriberID_pk = %s AND fld_f_FarmerID_fk = %s", subID, farmerID)
        results = cur.fetchall()
        return jsonify(results), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error connecting to database"
    finally:
        cur.close()
    
#Edit a certain task
@app.route('/editTask/<string:subID>/<int:taskID>', methods=['POST'])
def editTask():
    params = request.get_json()
    subID = params.get('subID')
    taskID = params.get('taskID')
    taskUpdate = params.get('taskUpdate')
    conn = get_db_connection()
    if conn is None:
        return "Database Connection Error"
    try:
        cur = conn.cursor()
        query = """
            UPDATE tbl_tasks SET fld_t_IsCompleted = %s, fld_t_DateDue = %s, fld_t_DateCompleted = %s, fld_t_Comments = %s, fld_t_DateCompleted = %s,
              fld_t_TasksIconPath = %s WHERE fld_s_SubscriberID_pk = %s AND fld_t_TaskID_pk = %s
        """
        cur.execute(query, (taskUpdate['fld_t_IsCompleted'], taskUpdate['fld_t_DateDue'], taskUpdate['fld_t_DateCompleted'],
                            taskUpdate['fld_t_Comments'], taskUpdate['fld_t_DateCompleted'], taskUpdate['fld_t_TaskIconPath'], subID, taskID))
        conn.commit()
        return "Task edited succesfully"   
    except Exception as e:
        print(f"Error:{e}")
        return "Error: error connecting to database"
    finally:
        cur.close()
    
#List Farmers
@app.route('/listFarmers/<string: subID>', methods =['GET'])
def listFarmers(subID):
    conn = get_db_connection()
    if conn is None:
        return "Database Connection Error"
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_farmers WHERE  fld_s_SubscriberID_pk = %s", (subID))
        results = cur.fetchall()
        return jsonify(results)
    except Exception as e:
        print(f"Error: {e}")
        return "Error connecting to database"
    finally:
        cur.close()


@app.route('/')
def index():
    return "This thing on?", 200

# Error handling for 404
@app.errorhandler(404)
def not_found(e):
    return "Sorry, can't find that!", 404

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT')), debug=True)