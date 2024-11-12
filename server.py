from flask import Flask, jsonify, request
from dotenv import load_dotenv
import mysql.connector
import random
import os
import datetime
import asyncio

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
    update crop types --Done
    create task types --Done
    dlete task --Done
    list task types --Done
    update task types --Done
    delete task types --Done
    create mediums --Done
    list mediums --Done
    update mediums --Done
    delete mediums --Done
    create locations --Done
    update locations --Done
    delete locations --Done
    list locations --Done
    delete crops --Done
    create farmer --Done
    update farmer --Done
    list farmers --Done
    delete farmer --Done
    create farm  --Done
    list farm --Done
    update farm --Done
    delete farm  --Done
    create journal entry --Done
    read journal entry  --Done
    delete journal entry --Done
    modify journal entry --Done
    Crop Search query
'''
rand = random.SystemRandom()

# Load environment variables
load_dotenv()

app = Flask(__name__)

async def getID():
    return random.randint(0,4000000000)

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
        cur.execute("SELECT * FROM tbl_crops WHERE fld_s_SubscriberID_pk = %s", (subID,))
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

@app.route('/getCropsVerbose/<string:subID>', methods=['GET'])
def getCropsverbose(subID):
    try:
        cur = conn.cursor()
        query = """SELECT DISTINCT c.*, m.fld_m_MediumType, l.fld_l_LocatonName, f.fld_f_FarmName, ct.fld_ct_CropTypeName FROM tbl_crops AS c 
        JOIN tbl_media AS m ON c.fld_m_MediumID_fk = m.fld_m_MediumID_pk AND c.fld_s_SubscriberID_pk = m.fld_s_SubscriberID_pk
        JOIN tbl_locations AS l ON  c.fld_l_LocationID_fk = l.fld_l_LocationID_pk AND c.fld_s_SubscriberID_pk = l.fld_s_SubscriberID_pk
        JOIN tbl_farms AS f ON   c.fld_f_FarmID_fk = f.fld_f_FarmID_pk AND c.fld_s_SubscriberID_pk = f.fld_s_SubscriberID_pk
        JOIN tbl_croptypes as ct ON c.fld_ct_CropTypeID_fk = ct.fld_ct_CropTypeID_pk AND c.fld_s_SubscriberID_pk = ct.fld_s_SubscriberID_pk
         WHERE c.fld_s_SubscriberID_pk = %s; 
                """
        cur.execute(query,(subID,))
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
async def add_crop():
    data = request.get_json()
    subID = data.get('subID')
    cropData = data.get('cropData')
    newCropID = await getID()
    try:
        cur = conn.cursor()
        queryData = (
            newCropID, subID, cropData['fld_c_ZipCode'], cropData['fld_c_State'],
            cropData['fld_f_FarmID_fk'], cropData['fld_c_HRFNumber'], cropData['fld_m_MediumID_fk'],
            cropData['fld_l_LocationID_fk'], cropData['fld_ct_CropTypeID_fk'], cropData['fld_c_CropName'],
            cropData['fld_c_Variety'], cropData['fld_c_Source'], cropData['fld_c_DatePlanted'],
            cropData['fld_c_Comments'], cropData['fld_c_Yield'], cropData['fld_c_WasStartedIndoors'],
            cropData['fld_c_isActive']
        )
        print(f"Query Data: {queryData}")
        query = """
        INSERT INTO tbl_crops (
            fld_c_CropID_pk, fld_s_SubscriberID_pk, fld_c_ZipCode, fld_c_State, fld_f_FarmID_fk,
            fld_c_HRFNumber, fld_m_MediumID_fk, fld_l_LocationID_fk, fld_ct_CropTypeID_fk,
            fld_c_CropName, fld_c_Variety, fld_c_Source, fld_c_DatePlanted, fld_c_Comments,
            fld_c_Yield, fld_c_WasStartedIndoors, fld_c_isActive
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, queryData)
        conn.commit()
        return "Crop added successfully", 200
    except Exception as e:
        print(f"Error: {e}, CropData: {cropData}")
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
        UPDATE tbl_crops
        SET fld_m_MediumID_fk = %s, fld_f_FarmID_fk = %s, fld_ct_CropTypeID_fk = %s, fld_CropImg = %s, 
            fld_c_CropName = %s, fld_c_Variety = %s, fld_c_Source = %s, fld_c_DatePlanted = %s, 
            fld_c_Comments = %s, fld_c_Yield = %s, fld_c_IsActive = %s, fld_c_WasStartedIndoors = %s
        WHERE fld_s_SubscriberID_pk = %s
        """
        cur.execute(query, ( cropUpdate['fld_m_MediumID_fk'], cropUpdate['fld_f_FarmID_fk'], cropUpdate['fld_ct_CropTypeID_fk'], cropUpdate['fld_CropImg'],
                    cropUpdate['fld_c_CropName'], cropUpdate['fld_c_Variety'], cropUpdate['fld_c_Source'], cropUpdate['fld_c_DatePlanted'], cropUpdate['fld_c_Comments'],
                    cropUpdate['fld_c_Yield'], cropUpdate['fld_c_IsActive'], cropUpdate['fld_sc_WasStartedIndoors'], subID))
        conn.commit()
        return "Updated Subscriber Info Successfully"
    except Exception as e:
        print(f"Error: {e}")
        return "Error updating database", 500
    finally:
        cur.close()

@app.route('/deleteCrop',methods=['POST'])
def deleteCrop():
    params = request.get_json()
    subID = request.get('subID')
    cropID = request.get('cropID')
    try:
        cur = conn.cursor()
        query = """
        DELETE FROM tbl_crops WHERE fld_s_SubscriberID_pk = %s AND fld_c_CropID_pk = %s;
        """
        cur.execute(query, (subID, cropID))
        conn.commit()
        return "Crop Deleted successfully", 200
    except Exception as e:
        print(f"Error:{e}")
        return "Error Deleting Crop"
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
@app.route('/listTasks/<string:subID>', methods=['GET'])
def listTasks(subID):
    try:
        cur = conn.cursor()
        query = """SELECT t.*,  tt.fld_tt_TaskTypeName FROM tbl_tasks AS t
        JOIN tbl_taskTypes AS tt ON t.fld_s_SubscriberID_pk = tt.fld_s_SubscriberID_pk AND t.fld_tt_TaskTypeID_fk = tt.fld_tt_TaskTypeID_pk
        WHERE t.fld_s_SubscriberID_pk = %s;"""
        cur.execute(query, (subID,))
        results = cur.fetchall()
        return jsonify(results), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error connecting to database", 500
    finally:
        cur.close()

@app.route('/deleteTask', methods=['POST'])
def deleteTask():
    params = request.get_json()
    subID = params.get('subID')
    taskID = params.get('taskID')
    try:
        cur = conn.cursor()
        query = """
        DELETE FROM tbl_tasks WHERE fld_s_SusbscriberID_pk = %s AND %s fld_t_TaskID_pk = %s
        """
        cur.execute(query, (subID, taskID))
        conn.commit()
        return "Successfully deleted task", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error deleting task"
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
              fld_t_TaskIconPath = %s WHERE fld_s_SubscriberID_pk = %s AND fld_t_TaskID_pk = %s
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
async def addTask():
    params = request.get_json()
    newTask = params.get('newTask')
    subID = params.get('subID')
    taskTypeID = params.get('taskTypeID')
    farmerID = params.get('farmerID')
    locationID = params.get('locationID')
    taskID = await getID()
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
            return addTask()
    except Exception as e:
        print(f"Error: {e}")
        return "Error Connecting to Database", 500

@app.route('/addFarmer', methods=['POST'])
async def addFarmer():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    farmerName = params.get('farmerName')
    farmerID = await getID()
    try:
        cur = conn.cursor()
        query = """
        INSERT INTO tbl_farmers (fld_fs_FarmerID_pk, fld_f_FarmID_fk, fld_s_SubscriberID_pk, fld_fs_FarmerFullName) VALUES (%s, %s, %s, %s);
        """
        cur.execute(query, (farmerID, farmID, subID, farmerName))
        conn.commit()
        return "Farmer Added Successfully", 200 
    except mysql.Error.IntegrityError as err:
        if "Duplicate entry" in str(err):
            print(f"Primary Key conflict ... Attempting with new key")
            return ()
    except Exception as e:
        print(f"Error: {e}")
        return "Error Executing Endpoint", 500
    finally:
        cur.close()

@app.route('/updateFarmer', methods=['POST'])
def updateFarmer():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    farmerName = params.get('farmerName')
    farmerID = params.get('farmerID')   
    try:
        cur = conn.cursor()
        query = """
        UPDATE tbl_farmers SET fld_fs_FarmerFullName = %s, fld_f_FarmID_fk = %s WHERE fld_s_SubscriberID_pk = %s AND fld_fs_FarmerID_pk = %s;
        """
        cur.execute(query, (farmerName, farmID, subID, farmerID))
        conn.commit()
        return "Successfully Updated Farmer", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error Updating Farmer", 500
    finally:
        cur.close()

@app.route('/deleteFarmer', methods=['POST'])
def deleteFarmer():
    params = request.get_json()
    subID = params.get('subID')
    farmerID = params.get('farmerID')
    try:
        cur = conn.cursor()
        query = """
        DELETE FROM tbl_farmers WHERE fld_s_SubscriberID_pk = %s AND  fld_fs_FarmerID_pk= %s;
        """
        cur.execute(query, (subID, farmerID))
        conn.commit()
        return "Successfully Updated Farmers"
    except Exception as e:
        print(f"Error: {e}")
        return "Error Deleting Farmer"
    
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


@app.route('/updateCropType', methods=['POST'])
def updateCropType():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID') 
    cropTypeID = params.get('cropsTypeID')
    cropData = params.get('cropData')
    try:
        cur = conn.cursor()
        query = """
         UPDATE tbl_cropTypes SET fld_f_FarmID_fk = %s, fld_ct_CropTypeName = %s WHERE fld_s_SubscriberID_pk = %s AND fld_ct_CropTypeID_pk = %s;
        """
        cur.execute(query, (farmID, cropData, subID, cropTypeID))
        conn.commit()
        return "Crop Type updated successfully", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error executing endpoint", 500
    finally:
        cur.close()



#add a new crop type
@app.route('/addCropType', methods=['POST'])
async def addCropType():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    cropTypeID = await getID()
    cropData = params.get('cropData')
    try:
        cur = conn.cursor()
        query = """
            INSERT INTO tbl_cropTypes(fld_ct_CropTypeID_pk, fld_f_FarmID_fk, fld_ct_CropTypeName, fld_s_SubscriberID_pk)
            VALUES(%s,%s,%s,%s);
        """
        cur.execute(query, (cropTypeID, farmID, cropData, subID))
        conn.commit()
        return "Successfully added Crop Type", 200
    except mysql.Error.IntegrityError as err:
        if "Duplicate entry" in str(err):
            print(f"Primary Key conflict ... Attempting with new key")
            return addCropType()
    except Exception as e:
        print(f"Error connecting to database: {e}") 
        return "Error connecting to database", 500
    finally:
        cur.close()

@app.route('/listTaskTypes/<string:subID>')
def listTaskTypes(subID):
    try:
        cur = conn.cursor()
        query = """
        SELECT * FROM tbl_taskTypes WHERE fld_s_SubscriberID_pk = %s;
        """
        cur.execute(query,(subID,))
        results = cur.fetchall()
        return jsonify(results), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error executing query", 500
    finally:
        cur.close()
    


@app.route('/updateTaskType', methods=['POST'])
def updateTaskType():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    taskTypeID = params.get('taskTypeID')
    taskType = params.get('taskType')
    try:
        cur = conn.cursor()
        query = """
        UPDATE tbl_taskTypes SET fld_f_FarmID_fk=%s, fld_tt_TaskTypeName=%s WHERE fld_s_SubscriberID_pk = %s AND fld_tt_TaskTypeID_pk = %s

        """
        cur.execute(query, (farmID, taskType, subID, taskTypeID))
        conn.commit()
        return "Successfully Updated TaksType", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Errpr executing endpoint", 500
    finally:
        cur.close()

@app.route('/deleteTaskType', methods=['POST'])
def deleteTaskType():
    params = request.get_json()
    subID = params.get('subID')
    taskTypeID = params.get('taskTypeID')
    try:
        cur = conn.cursor()
        query = """
        DELETE FROM tbl_taskTypes WHERE fld_s_SubscriberID_pk = %s AND fld_tt_TaskTypeID_pk = %s;
        """
        cur.execute(query, (subID, taskTypeID))
        conn.commit()
        return "Successfully deleted task Type"
    except Exception as e:
        print(f"Error: {e}")
        return "Error Deleting Task Type", 500
    
    finally:
        cur.close()

@app.route('/addTaskType', methods=['POST'])
async def addTaskType():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    taskTypeID = await getID()
    print(f"Task ID to be insterted:{taskTypeID}")
    taskType = params.get('taskType')
    try:
        cur = conn.cursor()
        query= """
            INSERT INTO tbl_taskTypes (fld_tt_TaskTypeID_pk, fld_f_FarmID_fk, fld_s_SubscriberID_pk, fld_tt_TaskTypeName) VALUES (%s,%s,%s,%s);
        """
        cur.execute(query, (taskTypeID, farmID, subID, taskType))
        conn.commit()
        return "Successfully added task type", 200
    except mysql.Error.IntegrityError as err:
        if "Duplicate entry" in str(err):
            print(f"Primary Key conflict ... Attempting with new key")
            return addTaskType()
    except Exception as e:
        print(f"Error: {e}")
        return "Error executing endpoint", 500
    finally:
        cur.close()


@app.route('/getMediums/<string:subID>', methods=['GET'])
def getMediums(subID):
    try:
        cur = conn.cursor()
        query = """
        SELECT * FROM tbl_mediums WHERE fld_s_SubscriberID_pk = %s;
        """
        cur.exeute(query, (subID,))
        results = cur.fetchall()
        return jsonify(results), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error executing Endpoint", 500
    finally:
        cur.close()


@app.route('/updateMedium', methods=['POST'])
def updateMedium():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    mediumID = rand.randint()
    mediumType = request.get('mediumType')
    try:
        cur = conn.cursor()
        query = """
        UPDATE tbl_media SET fld_m_MediumType=%s, fld_f_FarmID_fk=%s WHERE fld_s_SubscriberID_pk =%s AND fld_m_MediumID_pk;
        """
        cur.execute(query,(mediumType, farmID, subID, mediumID))
        conn.commit()
        return "updated Medium successfully", 200
    except Exception as e:
        return "Error executing query", 500
    finally:
        cur.close()


@app.route('/getCropLocation/<string:subID>/<int:cropID>', methods =['GET'])
def getCropLocation(subID, cropID):
    try:
        cur = conn.cursor()
        query = """
        SELECT l.* FROM tbl_locations AS l INNER JOIN tbl_crops AS C ON l.fld_s_SubscriberID_pk = c.fld_s_SubscriberID_pk AND  l.fld_l_LocationID_pk = c.fld_l_LocationID_fk WHERE c.fld_s_SubscriberID_pk = %s AND c.fld_c_CropID_pk = %s;
        """
        cur.execute(query, (subID, cropID))
        results = cur.fetchone()
        return jsonify(results), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error executing endpoint", 500
    finally:
        cur.close()


@app.route('/getCropMedium/<string:subID>/<int:cropID>', methods =['GET'])
def getCropMedium(subID, cropID):
    try:
        cur = conn.cursor()
        query = """
        SELECT m.* FROM tbl_media AS m INNER JOIN tbl_crops AS C ON m.fld_s_SubscriberID_pk = c.fld_s_SubscriberID_pk AND  m.fld_m_MediumID_pk = c.fld_m_MediumID_fk WHERE c.fld_s_SubscriberID_pk = %s AND c.fld_c_CropID_pk = %s;
        """
        cur.execute(query, (subID, cropID))
        results = cur.fetchone()
        return jsonify(results), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error executing endpoint", 500
    finally:
        cur.close()

@app.route('/deleteMedium', methods=['POST'])
def deleteMedium():
    params = request.get_json()
    subID = params.get('subID')
    mediumID = params.get('mediumID')
    try:
        cur = conn.cursor()
        query = """
        DELETE FROM tbl_media WHERE fld_s_SusbscriberID_pk = %s AND fld_m_MediumID_pk = %s;
        """
        cur.execute(query,(subID, mediumID))
        conn.commit()
        return "Medium deletd successfully", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error Deleting Medium", 500
    finally: 
        cur.close()


@app.route('/addMedium', methods=['POST'])
async def addMedium():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    mediumID = await getID()
    mediumType = request.get('mediumType')
    try:
        cur = conn.cursor()
        query = """
        INSERT INTO tbl_media (tbl_m_MediumID_pk, fld_m_MediumType, fld_s_SubscriberID_pk, fld_f_FarmID_fk);
        VALUES(%s,%s,%s,%s)
        """
        cur.execute(query,(mediumID, mediumType, subID, farmID))
        conn.commit()
        return "New Medium added successfully", 200
    except mysql.Error.IntegrityError as err:
        if "Duplicate entry" in str(err):
            print(f"Primary Key conflict ... Attempting with new key")
            return addMedium()
    except Exception as e:
        return "Error executing query", 500
    finally:
        cur.close()
    
@app.route('/deleteLocation', methods=['POST'])
def deleteLocation():
    params = request.get_json()
    subID = params.get('subID')
    locationID = params.get('locationID')
    try:
        cur = conn.cursor()
        query = """
        DELETE FROM tbl_locations WHERE fld_s_SubscriberID_pk = %s AND fld_l_LocationID_pk = %s;     
        """
        cur.execute(query, (subID, locationID))
        conn.commit()
        return "Deleted location successfully", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error Deleting Location", 500
    finally:
        cur.close()

@app.route('/updateLocation', methods=['POST'])
def updateLocation():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    locationID = params.get('locationID')
    locationName = params.get('locationName')
    try:
        cur =conn.cursor()
        query = """
        UPDATE tbl_locations SET fld_f_FarmID_fk = %s, fld_l_LocationName = %s WHERE fld_s_SubscriberID_pk = %s AND fld_l_LocationID_pk = %s; 
        """
        cur.execute(query, (farmID, locationName, subID, locationID))
        conn.commit()
        return "Successfully Updated Location", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error Updating Location"
    finally:
        cur.close()

@app.route('/addLocation', methods=['POST'])
async def addLocation():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    locationID = await getID()
    locationName = params.get('locationName')
    try:
        cur = conn.cursor()
        query = """
        INSERT INTO tbl_locations (fld_l_LocationID_pk, fld_f_FarmID_fk, fld_s_SubscriberID_pk, fld_l_LocationName) VALUES(%s,%s,%s,%s)
        """
        cur.execute(query,(locationID, farmID, subID, locationName))
        conn.commit()
        return "New Locarion Added Successfully", 500
    except mysql.Error.IntegrityError as err:
        if "Duplicate entry" in str(err):
            print(f"Primary Key conflict ... Attempting with new key")
            return addLocation()       
    except Exception as e:
        print(f"Error: {e}")
        return "Error Executing endpoint", 500
    finally:
        cur.close()

@app.route('/listLocation/<string:subID>', methods=['GET'])
def listLocations(subID):
    try:
        cur = conn.cursor()
        query = """
        SELECT * FROM tbl_locations WHERE fld_s_SubscriberID_pk = %s;
        """
        cur.execute(query, (subID,))
        results = cur.fetchall()
        return jsonify(results), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error Getting Locations"
    finally:
        cur.close()

@app.route('/listFarms/<string:subID>', methods=['GET'])
def listFarms(subID):
    try:
        cur = conn.cursor()
        query = """
        SELECT * FROM tbl_farms WHERE fld_s_SubscriberID_pk = %s;
        """
        cur.execute(query, (subID,))
        results = cur.fetchall()
        return jsonify(results), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error getting Farms"
    finally: cur.close()

@app.route('/updateFarm', methods=['POST'])
def updateFarm():
    params = request.get_json()
    subID = params.get('subID')
    farmName = params.get('farmName')
    farmID = rand.randint()
    try:
        cur = conn.cursor()
        query = """
        UPDATE tbl_farms SET fld_f_FarmName = %s WHERE fld_s_SubscriberID_pk = %s AND fld_f_FarmName = %s;
        """
        cur.execute(query, (farmName, subID, farmID))
        conn.commit()
        return "Successfully updated farm", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error Updating Farm", 500
    finally: 
        cur.close()


@app.route('/deleteFarm', methods=['POST'])
def deleteFarm():
    params = request.get_json()
    subID = params.get('subID')
    farmID = params.get('farmID')
    try:
        cur = conn.cursor()
        query = """
        DELETE FROM tbl_farms WHERE fld_s_SubscriberID_pk = %s AND fld_f_FarmID_pk = %s;
        """
        cur.execute()
        conn.commit()
        return "Successfully Deleted Farm", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error Deleting Farm", 500
    finally:
        cur.close()



@app.route('/addFarm', methods=['POST'])
async def addFarm():
    params = request.get_json()
    subID = params.get('subID')
    farmName = params.get('farmName')
    farmID = await getID()
    try:
        cur = conn.cursor()
        query = """
        INSERT INTO tbl_farms (fld_f_FarmID_pk, fld_s_SubscriberID_pk, fld_f_FarmName) VALUES(%s, %s, %s);
        """
        cur.execute(query, (farmID, subID, farmName))
        conn.commit()
        return "Farm added succesfully", 200
    except mysql.Error.IntegrityError as err:
        if "Duplicate entry" in str(err):
            print(f"Primary Key conflict ... Attempting with new key")
            return addFarm()
    except Exception as err:
        print(f"Error: {err}")
        return "Error Executing Endpoint", 500
    finally:
        cur.close()

@app.route('/listJournalEntries/<string:subID>', methods=['GET'])
def listJournalEntries(subID):
    try:
        cur = conn.cursor()
        query = """
        SELECT * FROM tbl_journalentries WHERE fld_s_SubscriberID_pk = %s;
        """
        cur.execute(query, (subID,))
        results = cur.fetchall()
        return jsonify(results), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error Getting journal entries", 500
    finally:
        cur.close()

@app.route('/deleteJournalEntry', methods=['POST'])
def deleteJournalEntry():
    params = request.get_json()
    subID = params.get('subID')
    entryID = params.get('entryID')
    try:
        cur = conn.cursor()
        query = """
        DELETE FROM tbl_journalentries WHER fld_s_SubscriberID_pk = %s AND fld_j_EntryID_pk = %s;
        """
        cur.execute(query, (subID, entryID))
        conn.commit()
        return "Successfully Deleted Journal Entry", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error deleting entry", 500
    finally:
        cur.close()

@app.route('/updateJournalEntry', methods=['POST'])
def updateJournalEntry():
    params = request.get_json()
    subID = params.get('subID')
    entryID = params.get('entryID')
    contents = params.get('entry')
    try:
        cur = conn.cursor()
        query = """
        UPDATE tbl_journalentries SET fld_j_Contents = %s WHERE fld_s_SubscriberID_pk = %s AND fld_j_EntryID_pk = %s;
        """
        cur.execute(query,(contents, subID, entryID))
        conn.commit()
        return "Successfully Updated Journal", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error updating Journal", 400
    finally: 
        cur.close()


@app.route('/addJournalEntry', methods=['POST'])
async def addJournalEntry():
    params = request.get_json()
    subID = params.get('subID')
    date = datetime.now()
    entryID = await getID()
    contents = params.get('entry')
    try:
        cur = conn.cursor()
        query = """
        INSERT INTO tbl_journalentries (fld_j_EntryID_pk, fld_j_Date, fld_s_SubscriberID_pk, fld_j_Contents) VALUES (%s, %s, %s, %s);
        """
        cur.execute(query, (entryID, date, subID, contents))
        conn.commit()
        return "New Journal entered successfully", 200
    except mysql.Error.IntegrityError as err:
        if "Duplicate entry" in str(err):
            print(f"Primary Key conflict ... Attempting with new key")
            return addJournalEntry()
    except Exception as e:
        print(f"Error: {e}")
        return "Error Executing Endpoint", 500


@app.route('/')
def index():
    return "This thing on?", 200

# Error handling for 404
@app.errorhandler(404)
def not_found(e):
    return "Sorry, can't find that!", 404

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT')), debug=True)