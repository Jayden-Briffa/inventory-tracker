"""
Helper methods for the inventory_management_system test suite.
"""

def populate_database_with_items(client):
    """Create 3 items in the database."""
    client.post(
        "/items/",
        json={"qrCode": "cfcc62ec-d003-447f-936e-c2816cfa3291", 
              "name": "Test item 1", 
              "description": "This is test item 1.",
              "isCollection": True
              }
    )
    client.post(
        "/items/",
        json={"qrCode": "31f5d2f7-9a28-4121-9fa6-9f1190de274d", 
              "name": "Test item 2", 
              "description": "This is test item 2.",
              "isCollection": True
              }
    )
    client.post(
        "/items/",
        json={"qrCode": "4e7bdd31-6cfe-4528-a769-42fcfb01748d", 
              "name": "Test item 3", 
              "description": "This is test item 3.",
              "isCollection": False
              }
    )

def populate_database_with_borrows(client):
    """Create items and 3 borrows in the database."""
    populate_database_with_items(client)
    
    """Create 3 borrows in the database."""
    client.post(
        "/borrows/",
        json={"itemId": 1,
              "email": "user1@test.com",
              "borrowDate": "2026-03-11T11:53:50.151000",
              "expectedReturnDate": "2026-03-12",
              "isReturned": False
             }
    )
    client.post(
        "/borrows/",
        json={"itemId": 1,
              "email": "user2@test.com",
              "borrowDate": "2026-03-01T10:50:50.151000",
              "expectedReturnDate": "2026-03-05",
              "isReturned": True
             }
    )
    client.post(
        "/borrows/",
        json={"itemId": 2,
              "email": "user3@test.com",
              "borrowDate": "2026-03-03T10:50:50.151000",
              "expectedReturnDate": "2026-03-08",
              "isReturned": False
             }
    )