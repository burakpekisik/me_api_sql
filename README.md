# ME API SQL

This project implements a RESTful API for managing data using SQL. The project is built with **Flask**, a lightweight Python web framework, and interacts with a SQL database to perform CRUD (Create, Read, Update, Delete) operations. It features robust error handling and data validation to ensure data integrity.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)
- [Usage](#usage)
- [License](#license)

## Features

- **CRUD Operations**: Perform Create, Read, Update, and Delete operations on the SQL database.
- **SQL Database Integration**: Efficiently manages data using SQL databases.
- **Error Handling**: Provides detailed error responses for invalid operations.
- **Validation**: Ensures the validity and integrity of data input and output.
- **Scalability**: The API structure allows easy expansion with additional endpoints.

## Technologies Used

- **Python**: The core language for the project.
- **Flask**: Micro web framework used to build the API.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library for database operations.
- **SQLite**: The database management system used for local development (can be replaced with other SQL databases like PostgreSQL or MySQL).

## Installation

To run the project locally, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/burakpekisik/me_api_sql.git
    ```

2. **Navigate to the project directory:**
    ```bash
    cd me_api_sql
    ```

3. **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    ```

4. **Activate the virtual environment:**

    - On Windows:
      ```bash
      venv\Scripts\activate
      ```

    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

5. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

6. **Create a `.env` file:**
    In the root directory, create a `.env` file and configure your database and other necessary environment variables:
    ```env
    FLASK_APP=app.py
    FLASK_ENV=development
    DATABASE_URL=sqlite:///your_database.db
    ```

7. **Initialize the database:**
    Run the following command to set up the database:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

8. **Run the application:**
    ```bash
    flask run
    ```
    The server will start at `http://localhost:5000`.

## Configuration

All configuration options, such as the database URL and Flask settings, are managed via the `.env` file. For example:

```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=sqlite:///me_api_sql.db
```

## API Endpoints

### Base URL: `http://localhost:5000/api`

#### 1. Create Data

- **Endpoint**: `/create`
- **Method**: POST
- **Description**: Create a new entry in the database.
- **Request Body**:
    ```json
    {
        "field1": "value1",
        "field2": "value2"
    }
    ```
- **Response**:
    ```json
    {
        "message": "Data created successfully"
    }
    ```

#### 2. Read Data

- **Endpoint**: `/read/<id>`
- **Method**: GET
- **Description**: Retrieve data by ID.
- **Response**:
    ```json
    {
        "id": 1,
        "field1": "value1",
        "field2": "value2"
    }
    ```

#### 3. Update Data

- **Endpoint**: `/update/<id>`
- **Method**: PUT
- **Description**: Update data by ID.
- **Request Body**:
    ```json
    {
        "field1": "newValue1",
        "field2": "newValue2"
    }
    ```
- **Response**:
    ```json
    {
        "message": "Data updated successfully"
    }
    ```

#### 4. Delete Data

- **Endpoint**: `/delete/<id>`
- **Method**: DELETE
- **Description**: Delete data by ID.
- **Response**:
    ```json
    {
        "message": "Data deleted successfully"
    }
    ```

## Error Handling

This API provides standardized error messages and appropriate HTTP status codes for various failure scenarios, including:

- **400 Bad Request**: The request was malformed or contained invalid data.
- **404 Not Found**: The requested resource was not found in the database.
- **500 Internal Server Error**: The server encountered an unexpected condition.

## Usage

You can test the API using tools such as [Postman](https://www.postman.com/) or [cURL](https://curl.se/). Here is an example of how to make a request using cURL:

### Example Request

```bash
curl -X POST http://localhost:5000/api/create \
-H "Content-Type: application/json" \
-d '{
    "field1": "value1",
    "field2": "value2"
}'
```
## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.
