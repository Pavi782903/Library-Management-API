# Library Management API

A REST API built using:

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

The application manages books, library members, borrowing and returning books.

---

# Features

## Book CRUD

- Create book
- Get all books
- Get book by ID
- Update book
- Delete book

## Member CRUD

- Create member
- Get all members
- Get member by ID
- Update member
- Delete member

## Search

Search books by:

- Category
- Author

Examples:

GET /books?category=Programming

GET /books?author=Robert

## Borrowing

POST /members/{member_id}/books/{book_id}/borrow

## Returning

POST /members/{member_id}/books/{book_id}/return

---

# Database

SQLite is used as the database.

The file:

library.db

is automatically created when the FastAPI application starts.

Tables:

- books
- members
- borrow_records

---

# Installation

## 1. Create virtual environment

Windows:

python -m venv venv

## 2. Activate virtual environment

CMD:

venv\Scripts\activate

PowerShell:

venv\Scripts\Activate.ps1

## 3. Install packages

pip install -r requirements.txt

---

# Run Application

Run:

uvicorn app.main:app --reload

Or:

python -m uvicorn app.main:app --reload

The API will run at:

http://127.0.0.1:8000

---

# Swagger UI

Open:

http://127.0.0.1:8000/docs

Swagger UI can be used to test every endpoint.

---

# ReDoc

Open:

http://127.0.0.1:8000/redoc

---

# API Endpoints

## Books

### Create Book

POST /books

Example:

{
    "name": "Python Programming",
    "author": "Robert Martin",
    "category": "Programming",
    "isbn": "978-1234567890",
    "price": 599.99,
    "available_quantity": 5
}

Expected status:

201 Created

---

### Get All Books

GET /books

Expected status:

200 OK

---

### Search By Category

GET /books?category=Programming

Expected status:

200 OK

---

### Search By Author

GET /books?author=Robert

Expected status:

200 OK

---

### Get Book By ID

GET /books/1

Expected status:

200 OK

If book does not exist:

404 Not Found

---

### Update Book

PUT /books/1

Example:

{
    "price": 699.99,
    "available_quantity": 10
}

Expected status:

200 OK

---

### Delete Book

DELETE /books/1

Expected status:

204 No Content

---

# Members

## Create Member

POST /members

Example:

{
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "9876543210",
    "membership_type": "Premium"
}

Expected status:

201 Created

---

## Get All Members

GET /members

Expected status:

200 OK

---

## Get Member By ID

GET /members/1

Expected status:

200 OK

If member does not exist:

404 Not Found

---

## Update Member

PUT /members/1

Example:

{
    "phone": "9999999999",
    "membership_type": "Premium"
}

Expected status:

200 OK

---

## Delete Member

DELETE /members/1

Expected status:

204 No Content

---

# Borrow Book

POST /members/1/books/1/borrow

A successful borrow decreases:

available_quantity

by 1.

Example response:

{
    "message": "Book borrowed successfully",
    "member_id": 1,
    "book_id": 1,
    "book_name": "Python Programming",
    "available_quantity": 4,
    "borrowed_at": "2026-09-30T10:30:00"
}

---

# Return Book

POST /members/1/books/1/return

A successful return increases:

available_quantity

by 1.

Example response:

{
    "message": "Book returned successfully",
    "member_id": 1,
    "book_id": 1,
    "book_name": "Python Programming",
    "available_quantity": 5,
    "returned_at": "2026-09-30T10:40:00"
}

---

# Validation Rules

## Book

name:
Required.

author:
Required.

category:
Required.

isbn:
Required and unique.

price:
Must be greater than 0.

available_quantity:
Must be greater than or equal to 0.

---

## Member

name:
Required.

email:
Required, valid email format and unique.

phone:
Optional.

membership_type:
Optional. Defaults to Standard.

---

# HTTP Status Codes

201 Created
Used when creating a book or member.

200 OK
Used for successful GET, PUT, borrow and return operations.

204 No Content
Used when deleting a book or member.

404 Not Found
Used when book/member does not exist.

409 Conflict
Used for duplicate ISBN, duplicate member email,
book unavailable, duplicate active borrowing,
or returning a book that was not borrowed.

422 Unprocessable Entity
Used for invalid request data.

500 Internal Server Error
Used for unexpected server/database errors.

---

# Testing Scenarios

## Valid Tests

1. Create a book
2. Create a member
3. Get all books
4. Get book by ID
5. Update book
6. Delete book
7. Search books by category
8. Search books by author
9. Borrow a book
10. Return a book

## Invalid Tests

1. Borrow non-existing book
2. Borrow non-existing member
3. Borrow book when quantity is 0
4. Return book that was not borrowed
5. Duplicate ISBN
6. Duplicate member email
7. Invalid price
8. Invalid quantity
9. Get non-existing book
10. Get non-existing member

---

# Example Invalid Book

POST /books

{
    "name": "Invalid Book",
    "author": "Author",
    "category": "Programming",
    "isbn": "ISBN-INVALID",
    "price": -100,
    "available_quantity": 5
}

Expected:

422 Unprocessable Entity

---

# Example Invalid Quantity

POST /books

{
    "name": "Invalid Quantity Book",
    "author": "Author",
    "category": "Programming",
    "isbn": "ISBN-12345",
    "price": 500,
    "available_quantity": -1
}

Expected:

422 Unprocessable Entity

---

# Duplicate ISBN

Create a book with an ISBN that already exists.

Expected:

409 Conflict

Example:

{
    "detail": "Book with ISBN '978-1234567890' already exists"
}

---

# Duplicate Member Email

Create a member using an email that already exists.

Expected:

409 Conflict

Example:

{
    "detail": "Member with email 'john@example.com' already exists"
}

---

# Borrow When Quantity Is Zero

If:

available_quantity = 0

then borrowing returns:

409 Conflict

Example:

{
    "detail": "Book 'Python Programming' is currently unavailable. Available quantity is 0."
}

---

# Return Without Borrowing

If a member tries to return a book that they have not borrowed:

409 Conflict

Example:

{
    "detail": "Member 1 has not borrowed book 1"
}

---

# Postman Testing

Start the API:

uvicorn app.main:app --reload

Create a Postman collection called:

Library Management API

Use base URL:

http://127.0.0.1:8000

Examples:

POST http://127.0.0.1:8000/books

GET http://127.0.0.1:8000/books

GET http://127.0.0.1:8000/books/1

PUT http://127.0.0.1:8000/books/1

DELETE http://127.0.0.1:8000/books/1

POST http://127.0.0.1:8000/members

GET http://127.0.0.1:8000/members

GET http://127.0.0.1:8000/members/1

PUT http://127.0.0.1:8000/members/1

DELETE http://127.0.0.1:8000/members/1

GET http://127.0.0.1:8000/books?category=Programming

GET http://127.0.0.1:8000/books?author=Robert

POST http://127.0.0.1:8000/members/1/books/1/borrow

POST http://127.0.0.1:8000/members/1/books/1/return

For POST and PUT requests use:

Body
-> raw
-> JSON

---

# Project Structure

LIBRARY_MANAGEMENT_API/

    app/
        __init__.py
        main.py
        database.py
        models.py
        schemas.py

        routers/
            __init__.py
            books.py
            members.py
            borrowing.py

    requirements.txt
    .gitignore
    README.md
    library.db

---

# Application URLs

Root:

http://127.0.0.1:8000/

Swagger:

http://127.0.0.1:8000/docs

ReDoc:

http://127.0.0.1:8000/redoc

Health:

http://127.0.0.1:8000/health