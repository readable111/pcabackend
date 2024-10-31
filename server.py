from flask import Flask, jsonify, request
from dotenv import load_dotenv
import mysql.connector
import random
import os
import datetime

'''TO DO LIST:
    endpoints:
    display profile information --Done  --works
    edit profile information --Done
    edit crop information  --Done
    list tasks  --Done
        list all tasks --Done
        list tasks by farmer --Done
    edit tasks --Done
    add tasks --Done
    create crop types --Done
    create task types --Done
    delete task types
    create mediums --Done
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
except mysql.connector.Error as err:
    print(f"Error: {err}")

# Routes

#current Date
@app.route('/currentDate', methods=['GET'])
def get_current_date():
    date = datetime.datetime.now()
    return jsonify(date=date.isoformat()), 200

#Get a subscribers information
@app.route('/subscriberInfo/<string:subID>', methods=['GET'])
def subscriberInfo(subID):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_subscribers WHERE fld_s_SubscriberID_pk = %s", (subID,))
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
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_crops WHERE fld_s_SubscriberID_pk = %s", (subID))
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
        cur = conn.cursor()
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
def updateCropInfo():
    params = request.get_json()
    subID =params.get('subID')
    cropUpdate = params.get('cropData')
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
    
    
@app.route('/searchCrops/<string:subID>/<string:userInput>', methods=['GET'])
def searchCrops():
    params = request.get_json()

#test database connection
@app.route('/connect', methods=['GET'])
def connect():
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
def listTasks(subID, farmerID):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_tasks WHERE fld_s_SubscriberID_pk = %s AND fld_fs_FarmerID_fk = %s", (subID, farmerID))
        results = cur.fetchall()
        return jsonify(results), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error connecting to database"
    finally:
        cur.close()
    
#Edit a certain task
@app.route('/editTask', methods=['POST'])
def editTask():
    params = request.get_json()
    subID = params.get('subID')
    taskID = params.get('taskID')
    taskUpdate = params.get('taskUpdate')
    try:
        cur = conn.cursor()
        query = """
            UPDATE tbl_tasks SET fld_t_IsCompleted = %s, fld_t_DateDue = %s, fld_t_DateCompleted = %s, fld_t_Comments = %s, fld_t_DateCompleted = %s,
              fld_t_TasksIconPath = %s WHERE fld_s_SubscriberID_pk = %s AND fld_t_TaskID_pk = %s
        """
        cur.execute(query, (taskUpdate['fld_t_IsCompleted'], taskUpdate['fld_t_DateDue'], taskUpdate['fld_t_DateCompleted'],
                            taskUpdate['fld_t_Comments'], taskUpdate['fld_t_DateCompleted'], taskUpdate['fld_t_TaskIconPath'], subID, taskID))
        conn.commit()
        return "Task edited succesfully", 200 
    except Exception as e:
        print(f"Error:{e}")
        return "Error: error connecting to database"
    finally:
        cur.close()


#add a new task
@app.route('/addTask', methods =['POST'])
def addtask():
    params = request.get_json()
    newTask = params.get('newTask')
    subID = params.get('subID')
    taskTypeID = params.get('taskTypeID')
    farmerID = params.get('farmerID')
    locationID = params.get('locationID')
    taskID = rand.randint()
    try:
        cur = conn.cursor()
        query = """
            INSERT INTO  tbl_tasks (fld_s_SubscriberID_pk , fld_t_TaskID_pk, fld_fs_FarmerID_fk, fld_tt_TaskTypeID_fk, fld_l_LocationID_fk,
            fld_t_IsCompleted, fld_t_DateDue, fld_t_Comments, fld_t_TaskIconPath) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cur.execute(query,(subID, taskID, farmerID, taskTypeID, locationID, 0, newTask['fld_t_DateDue'],newTask['fld_t_Comments'], newTask['fld_t_TaskIconPath'], ))
        conn.commit()
        return "New Task Created", 200
    except mysql.Error.IntegrityError as err:
        if "Duplicate entry" in str(err):
            print(f"Primary Key conflict ... Attempting with new key")
            return add_crop()
    except Exception as e:
        print(f"Error: {e}")
        return "Error Connecting to Database"

    
#List Farmers
@app.route('/listFarmers/<string:subID>', methods =['GET'])
def listFarmers(subID):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_farmers WHERE  fld_s_SubscriberID_pk = %s", (subID,))
        results = cur.fetchall()
        return jsonify(results)
    except Exception as e:
        print(f"Error: {e}")
        return "Error connecting to database"
    finally:
        cur.close()


#add a new crop type
@app.route('/addCropType', methods=['POST'])
def addCropType():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    cropTypeID = rand.randint()
    cropData = params.get('cropData')
    try:
        cur = conn.cursor()
        query = """
            INSERT INTO tbl_cropTypes(fld_ct_CropTypeID_pk, fld_f_FarmID_fk, fld_ct_CropTypeName, fld_s_SubscriberID_pk)
            VALUES(%s,%s,%s,%s);
        """
        cur.execute(query, (cropTypeID, farmID, cropData, subID))
        conn.commit()
    except mysql.Error.IntegrityError as err:
        if "Duplicate entry" in str(err):
            print(f"Primary Key conflict ... Attempting with new key")
            return addCropType()
    except Exception as e:
        print(f"Error connecting to database: {e}") 
        return "Error connecting to database", 500
    finally:
        cur.close()

@app.route('/addTaskType', methods=['POST'])
def addTaskType():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    taskTypeID = rand.randint()
    taskType = params.get('taskType')
    try:
        cur = conn.cursor()
        query= """
            INSERT INTO tbl_taskTypes (fld_tt_TaskTypeID_pk, fld_f_FarmID_fk, fld_s_SubscriberID_pk, fld_tt_TaskTypeName) VALUES (%s,%s,%s,%s);
        """
        cur.execute(query, (taskTypeID, farmID, subID, taskType))
        conn.commit()
    except mysql.Error.IntegrityError as err:
        print(f"Duplicate key Detected, retrying")
        addTaskType()
    except Exception as e:
        print(f"Error: {e}")
        return "Error executing endpoint"
    finally:
        cur.close()


@app.route('/addMedium', methods=['POST'])
def addMedium():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    mediumID = rand.randint()
    mediumType = request.get('mediumType')
    try:
        cur = conn.cursor()
        query = """
        INSERT INTO tbl_media (tbl_m_MediumID_pk, fld_m_MediumType, fld_s_SubscriberID_pk, fld_f_FarmID_fk)
        VALUES(%s,%s,%s,%s)
        """
        cur.execute(query,(mediumID, mediumType, subID, farmID))
        conn.commit()
        return "New Medium added successfully", 200
    except mysql.Error.IntegrityError as err:
        print(f"Duplicate key Detected, retrying")
        addMedium()
    except Exception as e:
        return "Error executing query", 500

@app.route('/')
def index():
    return "This thing on?", 200

# Error handling for 404
@app.errorhandler(404)
def not_found(e):
    return "Sorry, can't find that!", 404

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT')), debug=True)