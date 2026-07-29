from .helpers import populate_database_with_items, populate_database_with_borrows

"""
Tests for the Item endpoints.
"""

def test_create_item(client):
    qrCode = "cfcc62ec-d003-447f-936e-c2816cfa3291"
    name = "Test item"
    description = "This is a test item."
    isCollection = False
    response = client.post(
        "/items/",
        json={"qrCode": qrCode, 
              "name": name, 
              "description": description,
              "isCollection": isCollection
              }
    )
    assert response.status_code == 201
    assert response.json() == {
        "itemId": 1,
        "qrCode": qrCode,
        "name": name,
        "description": description,
        "isCollection": isCollection,
        "borrows": []
    }

def test_create_item_with_duplicate_qr_code(client):
    populate_database_with_items(client)
    response = client.get("/items/")
    assert response.status_code == 200
    dataBefore = response.json()
    assert len(dataBefore) == 3 # 3 items in database
    response = client.post(
        "/items/",
        json={"qrCode": "cfcc62ec-d003-447f-936e-c2816cfa3291", 
              "name": "Test item", 
              "description": "Test description",
              "isCollection": False
              }
    )
    assert response.status_code == 400
    assert response.json() == {'detail': "Item with QR code 'cfcc62ec-d003-447f-936e-c2816cfa3291' already exists."}
    response = client.get("/items/")
    assert response.status_code == 200
    dataAfter = response.json()
    assert dataBefore == dataAfter # Invalid item creation = no change to database


def test_create_item_with_invalid_fields(client):
    qrCode = 123
    name = True
    description = False
    isCollection = "abc"
    response = client.post(
        "/items/",
        json={"qrCode": qrCode, 
              "name": name, 
              "description": description,
              "isCollection": isCollection
              }
    )
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
        {
            'input': qrCode,
            'loc': ['body', 'qrCode'],
            'msg': 'Input should be a valid string',
            "type": 'string_type',
        },
        {
            'input': name,
            'loc': ['body', 'name'],
            'msg': 'Input should be a valid string',
            'type': 'string_type',
        },
        {
            'input': description,
            'loc': ['body', 'description'],
            'msg': 'Input should be a valid string',
            'type': 'string_type',
        },
        {
            'input': isCollection,
            'loc': ['body','isCollection'],
            'msg': 'Input should be a valid boolean, unable to interpret input',
            'type': 'bool_parsing',
        },
        ]
    }

def test_get_items(client):
    populate_database_with_items(client)
    response = client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 items in database
    assert data[0] == {'name': 'Test item 1',
                        'isCollection': True, 
                        'itemId': 1, 
                        'qrCode': 'cfcc62ec-d003-447f-936e-c2816cfa3291', 
                        'description': 'This is test item 1.',
                        'borrows': []}
    assert data[1] == {'name': 'Test item 2',
                        'isCollection': True, 
                        'itemId': 2, 
                        'qrCode': '31f5d2f7-9a28-4121-9fa6-9f1190de274d', 
                        'description': 'This is test item 2.',
                        'borrows': []}
    assert data[2] == {'name': 'Test item 3',
                        'isCollection': False, 
                        'itemId': 3, 
                        'qrCode': '4e7bdd31-6cfe-4528-a769-42fcfb01748d', 
                        'description': 'This is test item 3.',
                        'borrows': []}
    
def test_get_items_gets_associated_borrows(client):
    populate_database_with_items(client)
    populate_database_with_borrows(client)
    response = client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 items in database
    assert data[0] == {'name': 'Test item 1',
                        'isCollection': True, 
                        'itemId': 1, 
                        'qrCode': 'cfcc62ec-d003-447f-936e-c2816cfa3291', 
                        'description': 'This is test item 1.',
                        'borrows': [
                                        {
                                            'borrowDate': '2026-03-11T11:53:50.151000',
                                            'borrowId': 1,
                                            'email': 'user1@test.com',
                                            'expectedReturnDate': '2026-03-12',
                                            'isReturned': False,
                                            'itemId': 1,
                                        },
                                        {
                                            'borrowDate': '2026-03-01T10:50:50.151000',
                                            'borrowId': 2,
                                            'email': 'user2@test.com',
                                            'expectedReturnDate': '2026-03-05',
                                            'isReturned': True,
                                            'itemId': 1,
                                        }
                        ]}
    assert data[1] == {'name': 'Test item 2',
                        'isCollection': True, 
                        'itemId': 2, 
                        'qrCode': '31f5d2f7-9a28-4121-9fa6-9f1190de274d', 
                        'description': 'This is test item 2.',
                        'borrows': [
                                        {
                                            'borrowDate': '2026-03-03T10:50:50.151000',
                                            'borrowId': 3,
                                            'email': 'user3@test.com',
                                            'expectedReturnDate': '2026-03-08',
                                            'isReturned': False,
                                            'itemId': 2,
                                        },
                        ]}
    assert data[2] == {'name': 'Test item 3',
                        'isCollection': False, 
                        'itemId': 3, 
                        'qrCode': '4e7bdd31-6cfe-4528-a769-42fcfb01748d', 
                        'description': 'This is test item 3.',
                        'borrows': []}
    
def test_get_items_with_collection_query_false(client):
    populate_database_with_items(client)
    response = client.get("/items?collection=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1 # 1 individual item in database
    assert data[0] == {'name': 'Test item 3',
                        'isCollection': False, 
                        'itemId': 3, 
                        'qrCode': '4e7bdd31-6cfe-4528-a769-42fcfb01748d', 
                        'description': 'This is test item 3.',
                        'borrows': []}
    
def test_get_items_with_collection_query_true(client):
    populate_database_with_items(client)
    response = client.get("/items?collection=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2 # 2 collection items in database
    assert data[0] == {'name': 'Test item 1',
                        'isCollection': True, 
                        'itemId': 1, 
                        'qrCode': 'cfcc62ec-d003-447f-936e-c2816cfa3291', 
                        'description': 'This is test item 1.',
                        'borrows': []}
    assert data[1] == {'name': 'Test item 2',
                        'isCollection': True, 
                        'itemId': 2, 
                        'qrCode': '31f5d2f7-9a28-4121-9fa6-9f1190de274d', 
                        'description': 'This is test item 2.',
                        'borrows': []}
    
def test_get_items_with_invalid_collection_query(client):
    populate_database_with_items(client)
    response = client.get("/items?collection=abc123")
    assert response.status_code == 422
    data = response.json()
    assert data['detail'][0] == {'type': 'bool_parsing', 
                                 'loc': ['query', 'collection'], 
                                 'msg': 'Input should be a valid boolean, unable to interpret input', 
                                 'input': 'abc123'
                                 }
    
def test_get_item_by_qr_code(client):
    populate_database_with_items(client)
    response = client.get("/items/cfcc62ec-d003-447f-936e-c2816cfa3291")
    assert response.status_code == 200
    assert response.json() == {"qrCode": "cfcc62ec-d003-447f-936e-c2816cfa3291", 
                               "name": "Test item 1", 
                               "itemId": 1,
                               "description": "This is test item 1.",
                               "isCollection": True,
                               "borrows": []
                               }
    
def test_get_item_by_qr_code_gets_associated_borrows(client):
    populate_database_with_items(client)
    populate_database_with_borrows(client)
    response = client.get("/items/cfcc62ec-d003-447f-936e-c2816cfa3291")
    assert response.status_code == 200
    assert response.json() == {"qrCode": "cfcc62ec-d003-447f-936e-c2816cfa3291", 
                               "name": "Test item 1", 
                               "itemId": 1,
                               "description": "This is test item 1.",
                               "isCollection": True,
                               'borrows': [
                                        {
                                            'borrowDate': '2026-03-11T11:53:50.151000',
                                            'borrowId': 1,
                                            'email': 'user1@test.com',
                                            'expectedReturnDate': '2026-03-12',
                                            'isReturned': False,
                                            'itemId': 1,
                                        },
                                        {
                                            'borrowDate': '2026-03-01T10:50:50.151000',
                                            'borrowId': 2,
                                            'email': 'user2@test.com',
                                            'expectedReturnDate': '2026-03-05',
                                            'isReturned': True,
                                            'itemId': 1,
                                        }
                                ]}
    
def test_get_item_by_nonexistent_qr_code(client):
    populate_database_with_items(client)
    response = client.get("/items/test")
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] ==  "Item with QR code 'test' does not exist."

def test_update_item(client):
    populate_database_with_items(client)
    response = client.get("/items/cfcc62ec-d003-447f-936e-c2816cfa3291")
    assert response.status_code == 200
    dataBefore = response.json()
    assert dataBefore == {"qrCode": "cfcc62ec-d003-447f-936e-c2816cfa3291", 
                               "name": "Test item 1", 
                               "itemId": 1,
                               "description": "This is test item 1.",
                               "isCollection": True,
                               "borrows": []
                               }
    response = client.patch("/items/cfcc62ec-d003-447f-936e-c2816cfa3291", 
                            json={"description": "Updated description"})
    assert response.status_code == 200
    dataAfter = response.json()
    assert dataAfter == {"qrCode": "cfcc62ec-d003-447f-936e-c2816cfa3291", 
                               "name": "Test item 1", 
                               "itemId": 1,
                               "description": "Updated description",
                               "isCollection": True,
                               "borrows": []
                               }
    assert dataBefore['qrCode'] == dataAfter['qrCode']
    assert dataBefore['name'] == dataAfter['name']
    assert dataBefore['itemId'] == dataAfter['itemId']
    assert dataBefore['description'] != dataAfter['description']
    assert dataBefore['isCollection'] == dataAfter['isCollection']
    assert dataBefore['borrows'] == dataAfter['borrows']

def test_update_item_with_no_fields(client):
    populate_database_with_items(client)
    response = client.patch("/items/cfcc62ec-d003-447f-936e-c2816cfa3291", json={})
    assert response.status_code == 400
    assert response.json() == {'detail': "No fields to update."}

def test_update_item_with_nonexistent_item(client):
    response = client.patch("/items/test", json={"description": "Updated description"})
    assert response.status_code == 404
    assert response.json() == {'detail': "Item with QR code 'test' does not exist."}

def test_delete_item(client):
    populate_database_with_items(client)
    response = client.get("/items/")
    data = response.json()
    assert len(data) == 3 # 3 items in database
    response = client.delete("/items/cfcc62ec-d003-447f-936e-c2816cfa3291")
    assert response.status_code == 204
    response = client.get("/items/")
    data = response.json()
    assert len(data) == 2 # 2 items in database after deletion

def test_delete_item_with_active_borrows(client):
    populate_database_with_items(client)
    populate_database_with_borrows(client)
    response = client.get("/items/")
    data = response.json()
    assert len(data) == 3 # 3 items in database
    response = client.delete("/items/cfcc62ec-d003-447f-936e-c2816cfa3291")
    assert response.status_code == 400
    data = response.json()
    assert data['detail'] == "Cannot delete item with active borrows."
    response = client.get("/items/")
    data = response.json()
    assert len(data) == 3 # No items deleted from database

def test_delete_nonexistent_item(client):
    populate_database_with_items(client)
    response = client.get("/items/")
    data = response.json()
    assert len(data) == 3 # 3 items in database
    response = client.delete("/items/test")
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == "Item with QR code 'test' does not exist."
    response = client.get("/items/")
    data = response.json()
    assert len(data) == 3 # No items deleted from database