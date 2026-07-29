from .helpers import populate_database_with_borrows, populate_database_with_items

"""
Tests for the Borrow endpoints.
"""

def test_create_borrow(client):
    populate_database_with_items(client)
    itemId = 1
    email = "user@test.com"
    borrowDate = "2026-03-10T11:53:50.151000"
    expectedReturnDate = "2026-03-20"
    isReturned = False
    response = client.post(
            "/borrows/",
            json={"itemId": itemId,
              "email": email,
              "borrowDate": borrowDate,
              "expectedReturnDate": expectedReturnDate,
              "isReturned": isReturned
             }
        )
    assert response.status_code == 201
    assert response.json() == {
        "borrowId": 1,
        "itemId": itemId,
        "email": email,
        "borrowDate": borrowDate,
        "expectedReturnDate": expectedReturnDate,
        "isReturned": isReturned
    }

def test_create_borrow_for_nonexistent_item(client):
    response = client.post("/borrows/",
                json={"itemId": 1,
                    "email": "user1@test.com",
                    "borrowDate": "2026-03-11T11:53:50.151000",
                    "expectedReturnDate": "2026-03-12",
                    "isReturned": False
                    }
                )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Item with ID 1 does not exist.'}

def test_create_borrow_for_individual_item_with_active_borrow(client):
    populate_database_with_items(client)
    response = client.get("/items/4e7bdd31-6cfe-4528-a769-42fcfb01748d")
    assert response.status_code == 200
    assert response.json()['isCollection'] == False
    itemId = response.json()['itemId']
    response = client.post("/borrows/",
                json={"itemId": itemId,
                    "email": "user1@test.com",
                    "borrowDate": "2026-03-11T11:53:50.151000",
                    "expectedReturnDate": "2026-03-12",
                    "isReturned": False
                    }
                )
    assert response.status_code == 201 # Create first active borrow
    response = client.post("/borrows/",
                json={"itemId": itemId,
                    "email": "user2@test.com",
                    "borrowDate": "2026-03-11T11:53:50.151000",
                    "expectedReturnDate": "2026-03-12",
                    "isReturned": False
                    }
                )
    assert response.status_code == 400
    assert response.json() == {'detail': 'Item is already borrowed and not yet returned.'}

def test_create_borrow_for_collection_item_with_active_borrow(client):
    populate_database_with_items(client)
    response = client.get("/items/cfcc62ec-d003-447f-936e-c2816cfa3291")
    assert response.status_code == 200
    assert response.json()['isCollection'] == True
    itemId = response.json()['itemId']
    response = client.post("/borrows/",
                json={"itemId": itemId,
                    "email": "user1@test.com",
                    "borrowDate": "2026-03-11T11:53:50.151000",
                    "expectedReturnDate": "2026-03-12",
                    "isReturned": False
                    }
                )
    assert response.status_code == 201 # Create first active borrow
    response = client.post("/borrows/",
                json={"itemId": itemId,
                    "email": "user2@test.com",
                    "borrowDate": "2026-03-11T11:53:50.151000",
                    "expectedReturnDate": "2026-03-12",
                    "isReturned": False
                    }
                )
    assert response.status_code == 201 # Create second active borrow

def test_create_borrow_with_invalid_fields(client):
    populate_database_with_items(client)
    itemId = "abc"
    email = False
    borrowDate = True
    expectedReturnDate = 1
    isReturned = "abc"
    response = client.post(
            "/borrows/",
            json={"itemId": itemId,
              "email": email,
              "borrowDate": borrowDate,
              "expectedReturnDate": expectedReturnDate,
              "isReturned": isReturned
             }
        )
    assert response.status_code == 422
    errors = response.json()['detail']
    
    # Check that we have 5 validation errors
    assert len(errors) == 5
    
    # Check error types and locations, independent of order
    error_locs = {tuple(err['loc']): err['type'] for err in errors}
    assert error_locs[('body', 'itemId')] == 'int_parsing'
    assert error_locs[('body', 'email')] == 'string_type'
    assert error_locs[('body', 'borrowDate')] == 'datetime_type'
    assert error_locs[('body', 'expectedReturnDate')] == 'date_from_datetime_inexact'
    assert error_locs[('body', 'isReturned')] == 'bool_parsing'

def test_get_borrows(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    assert data[0] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    assert data[1] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    assert data[2] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    
def test_get_borrows_retrieves_borrows_in_ascending_order_of_expected_return_date(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    firstBorrowDate = data[0]['expectedReturnDate']
    secondBorrowDate = data[1]['expectedReturnDate']
    thirdBorrowDate = data[2]['expectedReturnDate']
    assert firstBorrowDate <= secondBorrowDate
    assert secondBorrowDate <= thirdBorrowDate

def test_get_borrows_with_returned_query_false(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?returned=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2 # 2 active borrows in database
    assert data[0] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    assert data[1] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    
def test_get_borrows_with_email_query(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?email=user1@test.com")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1 # 1 borrow from user1@test.com
    assert data[0] == {"borrowId": 1,
                        "itemId": 1,
                        "email": "user1@test.com",
                        "borrowDate": "2026-03-11T11:53:50.151000",
                        "expectedReturnDate": "2026-03-12",
                        "isReturned": False
                        }
    
def test_get_borrows_with_item_id_query(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?item_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2 # 2 borrows associated with item 1
    assert data[0] == {"borrowId": 2,
                        "itemId": 1,
                        "email": "user2@test.com",
                        "borrowDate": "2026-03-01T10:50:50.151000",
                        "expectedReturnDate": "2026-03-05",
                        "isReturned": True
                        }
    assert data[1] == {"borrowId": 1,
                        "itemId": 1,
                        "email": "user1@test.com",
                        "borrowDate": "2026-03-11T11:53:50.151000",
                        "expectedReturnDate": "2026-03-12",
                        "isReturned": False
                        }
    
def test_get_borrows_with_returned_query_true(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?returned=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1 # 1 returned borrows in database
    assert data[0] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    
def test_get_borrows_with_invalid_returned_query(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?returned=abc123")
    assert response.status_code == 422
    data = response.json()
    assert data['detail'][0] == {'type': 'bool_parsing', 
                                 'loc': ['query', 'returned'], 
                                 'msg': 'Input should be a valid boolean, unable to interpret input', 
                                 'input': 'abc123'
                                 }
    
def test_get_borrows_in_ascending_order_of_expected_return_date(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?order=asc&sort_by=expectedReturnDate")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    assert data[0] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    assert data[1] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    assert data[2] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    firstBorrowDate = data[0]['expectedReturnDate']
    secondBorrowDate = data[1]['expectedReturnDate']
    thirdBorrowDate = data[2]['expectedReturnDate']
    assert firstBorrowDate <= secondBorrowDate
    assert secondBorrowDate <= thirdBorrowDate

def test_get_borrows_in_descending_order_of_expected_return_date(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?order=desc&sort_by=expectedReturnDate")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    assert data[0] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    assert data[1] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    assert data[2] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    firstBorrowDate = data[0]['expectedReturnDate']
    secondBorrowDate = data[1]['expectedReturnDate']
    thirdBorrowDate = data[2]['expectedReturnDate']
    assert firstBorrowDate >= secondBorrowDate
    assert secondBorrowDate >= thirdBorrowDate

def test_get_borrows_in_ascending_order_of_borrow_date(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?order=asc&sort_by=borrowDate")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    assert data[0] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    assert data[1] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    assert data[2] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    firstBorrowDate = data[0]['borrowDate']
    secondBorrowDate = data[1]['borrowDate']
    thirdBorrowDate = data[2]['borrowDate']
    assert firstBorrowDate <= secondBorrowDate
    assert secondBorrowDate <= thirdBorrowDate

def test_get_borrows_in_descending_order_of_borrow_date(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?order=desc&sort_by=borrowDate")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    assert data[0] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    assert data[1] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    assert data[2] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    firstBorrowDate = data[0]['borrowDate']
    secondBorrowDate = data[1]['borrowDate']
    thirdBorrowDate = data[2]['borrowDate']
    assert firstBorrowDate >= secondBorrowDate
    assert secondBorrowDate >= thirdBorrowDate

def test_get_borrows_in_ascending_order_of_email_address(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?order=asc&sort_by=email")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    assert data[0] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    assert data[1] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    assert data[2] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    firstEmail = data[0]['email']
    secondEmail = data[1]['email']
    thirdEmail = data[2]['email']
    assert firstEmail <= secondEmail
    assert secondEmail <= thirdEmail

def test_get_borrows_in_descending_order_of_email_address(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?order=desc&sort_by=email")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    assert data[0] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    assert data[1] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    assert data[2] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    firstEmail = data[0]['email']
    secondEmail = data[1]['email']
    thirdEmail = data[2]['email']
    assert firstEmail >= secondEmail
    assert secondEmail >= thirdEmail

def test_get_borrows_in_ascending_order_of_borrow_id(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?order=asc&sort_by=borrowId")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    assert data[0] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    assert data[1] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    assert data[2] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    firstBorrowId = data[0]['borrowId']
    secondBorrowId = data[1]['borrowId']
    thirdBorrowId = data[2]['borrowId']
    assert firstBorrowId <= secondBorrowId
    assert secondBorrowId <= thirdBorrowId

def test_get_borrows_in_descending_order_of_borrow_id(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?order=desc&sort_by=borrowId")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    assert data[0] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    assert data[1] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    assert data[2] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    firstBorrowId = data[0]['borrowId']
    secondBorrowId = data[1]['borrowId']
    thirdBorrowId = data[2]['borrowId']
    assert firstBorrowId >= secondBorrowId
    assert secondBorrowId >= thirdBorrowId

def test_get_borrows_in_ascending_order_of_is_returned(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?order=asc&sort_by=isReturned")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    assert data[0] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    assert data[1] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    assert data[2] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    firstIsReturned = data[0]['isReturned']
    secondIsReturned = data[1]['isReturned']
    thirdIsReturned = data[2]['isReturned']
    assert firstIsReturned <= secondIsReturned
    assert secondIsReturned <= thirdIsReturned

def test_get_borrows_in_descending_order_of_is_returned(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows?order=desc&sort_by=isReturned")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    assert data[0] == {'itemId': 1, 
                       'email': 'user2@test.com', 
                       'expectedReturnDate': '2026-03-05', 
                       'borrowDate': '2026-03-01T10:50:50.151000', 
                       'borrowId': 2, 
                       'isReturned': True}
    assert data[1] == {'itemId': 2, 
                       'email': 'user3@test.com', 
                       'expectedReturnDate': '2026-03-08', 
                       'borrowDate': '2026-03-03T10:50:50.151000', 
                       'borrowId': 3, 
                       'isReturned': False}
    assert data[2] == {'itemId': 1, 
                       'email': 'user1@test.com', 
                       'expectedReturnDate': '2026-03-12', 
                       'borrowDate': '2026-03-11T11:53:50.151000', 
                       'borrowId': 1, 
                       'isReturned': False}
    firstIsReturned = data[0]['isReturned']
    secondIsReturned = data[1]['isReturned']
    thirdIsReturned = data[2]['isReturned']
    assert firstIsReturned >= secondIsReturned
    assert secondIsReturned >= thirdIsReturned

def test_get_borrows_order_query_with_no_sort_by_query_has_no_effect(client):
    populate_database_with_borrows(client)
    queryResponse = client.get("/borrows?order=asc")
    assert queryResponse.status_code == 200
    queryData = queryResponse.json()
    nonQueryResponse = client.get("/borrows/")
    assert nonQueryResponse.status_code == 200
    nonQueryData = nonQueryResponse.json()
    assert queryData == nonQueryData
    
def test_get_borrows_sort_by_query_with_no_order_query_has_no_effect(client):
    populate_database_with_borrows(client)
    queryResponse = client.get("/borrows?sort_by=borrowDate")
    assert queryResponse.status_code == 200
    queryData = queryResponse.json()
    nonQueryResponse = client.get("/borrows/")
    assert nonQueryResponse.status_code == 200
    nonQueryData = nonQueryResponse.json()
    assert queryData == nonQueryData
    
def test_get_borrows_order_query_must_be_asc_or_desc_or_else_error(client):
    populate_database_with_borrows(client)
    queryResponse = client.get("/borrows?order=abc&sort_by=borrowDate")
    assert queryResponse.status_code == 400
    data = queryResponse.json()
    assert data['detail'] == "Invalid order. Must be 'asc' or 'desc'"

def test_get_borrows_sort_by_invalid_query(client):
    populate_database_with_borrows(client)
    queryResponse = client.get("/borrows?order=asc&sort_by=abc")
    assert queryResponse.status_code == 400
    data = queryResponse.json()
    assert data['detail'] == "Invalid sort_by field. Must be one of: borrowDate, expectedReturnDate, borrowId, email, isReturned"


def test_get_borrow_by_id(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows/1")
    assert response.status_code == 200
    assert response.json() == {'itemId': 1, 
                              'email': 'user1@test.com', 
                              'expectedReturnDate': '2026-03-12', 
                              'borrowDate': '2026-03-11T11:53:50.151000', 
                              'borrowId': 1, 
                              'isReturned': False}
    
def test_get_borrow_by_nonexistent_qr_code(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows/9")
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] ==  "Borrow with ID '9' does not exist."

def test_get_borrow_by_invalid_qr_code(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows/test")
    assert response.status_code == 422
    
def test_update_borrow(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows/1")
    assert response.status_code == 200
    dataBefore = response.json()
    assert dataBefore == {"borrowId": 1,
                        "itemId": 1,
                        "email": "user1@test.com",
                        "borrowDate": "2026-03-11T11:53:50.151000",
                        "expectedReturnDate": "2026-03-12",
                        "isReturned": False
                        }
    response = client.patch("/borrows/1", 
                            json={"isReturned": True})
    assert response.status_code == 200
    dataAfter = response.json()
    assert dataAfter == {"borrowId": 1,
                        "itemId": 1,
                        "email": "user1@test.com",
                        "borrowDate": "2026-03-11T11:53:50.151000",
                        "expectedReturnDate": "2026-03-12",
                        "isReturned": True
                        }
    assert dataBefore['itemId'] == dataAfter['itemId']
    assert dataBefore['email'] == dataAfter['email']
    assert dataBefore['borrowDate'] == dataAfter['borrowDate']
    assert dataBefore['expectedReturnDate'] == dataAfter['expectedReturnDate']
    assert dataBefore['isReturned'] != dataAfter['isReturned']

def test_update_borrow_with_already_returned_borrow(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows/2")
    assert response.status_code == 200
    dataBefore = response.json()
    assert dataBefore == {"borrowId": 2,
                        "itemId": 1,
                        "email": "user2@test.com",
                        "borrowDate": "2026-03-01T10:50:50.151000",
                        "expectedReturnDate": "2026-03-05",
                        "isReturned": True
                        }
    response = client.patch("/borrows/2", 
                            json={"isReturned": True})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Item has already been returned.'}

def test_update_borrow_with_no_fields(client):
    populate_database_with_borrows(client)
    response = client.patch("/borrows/1", json={})
    assert response.status_code == 400
    assert response.json() == {'detail': "No fields to update."}

def test_update_borrow_with_nonexistent_borrow(client):
    response = client.patch("/borrows/500", json={})
    assert response.status_code == 404
    assert response.json() == {'detail': "Borrow with ID '500' does not exist."}

def test_delete_borrow(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows/")
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    response = client.delete("/borrows/1")
    assert response.status_code == 204
    response = client.get("/borrows/")
    data = response.json()
    assert len(data) == 2 # 2 borrows in database after deletion

def test_delete_nonexistent_borrow(client):
    populate_database_with_borrows(client)
    response = client.get("/borrows/")
    data = response.json()
    assert len(data) == 3 # 3 borrows in database
    response = client.delete("/borrows/123")
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == "Borrow with ID '123' does not exist."
    response = client.get("/borrows/")
    data = response.json()
    assert len(data) == 3 # No borrows deleted from database