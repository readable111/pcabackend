import unittest
import json
import requests  # Use requests to make real HTTP requests to the deployed Flask app

BASE_URL = "https://cabackend-a9hseve4h2audzdm.canadacentral-01.azurewebsites.net"  # Replace this with the actual URL of your deployed app

class TestApp(unittest.TestCase):

    # Setup and teardown methods
    @classmethod
    def setUpClass(cls):
        cls.client = requests.Session()  # Use requests session to maintain cookies and headers
        cls.client.headers.update({'Content-Type': 'application/json'})  # Set default headers

    def test_get_current_date(self):
        response = self.client.get(f"{BASE_URL}/currentDate")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('date', data)

    def test_subscriber_info_success(self):
        response = self.client.get(f"{BASE_URL}/subscriberInfo/sub123")  # Replace with a valid subID
        self.assertEqual(response.status_code, 200)  # Expect success or not found
  # Expect a dictionary

    #def test_update_subscriber_info(self):
#        payload = {
#            "subID": "sub12345",
#            "subData": {
#                "fld_s_FirstName": "Test",
#                "fld_s_LastName": "User",
#                "fld_s_EmailAddr": "test@example.com",
#                "fld_s_StreetAddr": "123 Test St",
#                "fld_s_City": "TestCity",
#                "fld_s_PostalCode": "12345",
#                "fld_s_PhoneNum": "1234567890",
#                "fld_s_HasAmbientWeather": 1,
#                "fld_s_AmbientWeatherKey": ""
#            }
#        }
#        response = self.client.post(f"{BASE_URL}/updateSubscriberInfo", json=payload)
#        self.assertEqual(response.status_code, 200)
#        self.assertEqual(response.text, "Updated Subscriber Info Successfully")
#    
#        response = self.client.get(f"{BASE_URL}/getCrops/testSubID")  # Replace with a valid subID
#        self.assertIn(response.status_code, [200, 404, 500])  # Expect success or not found
#        if response.status_code == 200:
#            data = response.json()
#            self.assertIsInstance(data, list)  # Expect a list

    def test_listTasks(self):
        response = self.client.get(f"{BASE_URL}/listTasks/test_subID/1")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_deleteTask(self):
        response = self.client.post(f"{BASE_URL}/deleteTask", json={"subID": "sub12345", "taskID": 123})
        self.assertEqual(response.status_code, 200)

    def test_editTask(self):
        taskUpdate = {
            "fld_t_IsCompleted": 1,
            "fld_t_DateDue": "2024-01-01",
            "fld_t_DateCompleted": "2024-01-02",
            "fld_t_Comments": "Updated",
            "fld_t_TaskIconPath": "/path/to/icon"
        }
        response = self.client.post(f"{BASE_URL}/editTask", json={
            "subID": "sub123",
            "taskID": 1,
            "taskUpdate": taskUpdate
        })
        self.assertIn(response.status_code, [200, 500])

    def test_addTask(self):
        newTask = {
            "fld_t_DateDue": "2024-01-01",
            "fld_t_Comments": "New task",
            "fld_t_TaskIconPath": "/path/to/icon"
        }
        response = self.client.post(f"{BASE_URL}/addTask", json={
            "subID": "sub123",
            "taskTypeID": 1,
            "farmerID": 1,
            "locationID": 1,
            "newTask": newTask
        })
        self.assertEqual(response.status_code, 200)

    def test_listFarmers(self):
        response = self.client.get(f"{BASE_URL}/listFarmers/test_subID")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_updateCropType(self):
        response = self.client.post(f"{BASE_URL}/updateCropType", json={
            "subID": "sub12345",
            "farmID": 1,
            "cropTypeID": 1,
            "cropData": "New Crop Type"
        })
        self.assertIn(response.status_code, [200, 500])

    def test_addCropType(self):
        response = self.client.post(f"{BASE_URL}/addCropType", json={
            "subID": "sub12345",
            "farmID": 1,
            "cropData": "Sample Crop Data"

        })
        self.assertEqual(response.status_code, 200)

    def test_listTaskTypes(self):
        response = self.client.get(f"{BASE_URL}/listTaskTypes/sub123")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_updateTaskType(self):
        response = self.client.post(f"{BASE_URL}/updateTaskType", json={
            "subID": "sub123",
            "farmID": 1,
            "taskTypeID": 1,
            "taskType": "Updated Task Type"
        })
        self.assertEqual(response.status_code, 200)

    def test_deleteTaskType(self):
        response = self.client.post(f"{BASE_URL}/deleteTaskType", json={
            "subID": "sub123",
            "taskTypeID": 2
        })
        self.assertEqual(response.status_code, 200)

    def test_addTaskType(self):
        response = self.client.post(f"{BASE_URL}/addTaskType", json={
            "subID": "sub123",
            "farmID": 1,
            "taskType": "Sample Task Type"
        })
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
