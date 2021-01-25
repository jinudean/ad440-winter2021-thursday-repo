import json
import pyodbc
import logging
import os
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger for /users function is processing a request.')

    # Check request method
    method = req.method
    if not method:
        logging.critical('No method available')
        raise Exception('No method passed')

    # Create a new connection
    logging.debug("Attempting DB connection!")
    try:
        conn = get_db_connection()
    except pyodbc.DatabaseError as e:
        logging.error("Failed to connect to DB: " + e.args[0])
        logging.debug("Error: " + e.args[1])
        if e.args[0] == '28000':
            return func.HttpResponse(
                "Internal Server Error",
                status_code=500
            )
    logging.debug("Connection to DB successful!")

    try:
        # Return results according to the method
        if method == "GET":
            logging.debug("Attempting to retrieve users...")
            all_users_http_response = get_users(conn)
            logging.debug("Users retrieved successfully!")
            return all_users_http_response

        elif method == "POST":
            logging.debug("Attempting to add user...")
            user_req_body = req.get_json()
            new_user_id_http_response = add_user(conn, user_req_body)
            logging.debug("User added successfully!")
            return new_user_id_http_response

        else:
            logging.warn(f"Request with method {method} has been recieved, but that is not allowed for this endpoint")
            return func.HttpResponse(status_code=405)

    #displays erros encountered when API methods were called
    except Exception as e:
        return func.HttpResponse("Error: %s" % str(e), status_code=500)
    finally: 
        conn.close()
        logging.debug('Connection to DB closed')


def get_db_connection():
    # Database credentials.
    server = os.environ["ENV_DATABASE_SERVER"]
    database = os.environ["ENV_DATABASE_NAME"]
    username = os.environ["ENV_DATABASE_USERNAME"]
    password = os.environ["ENV_DATABASE_PASSWORD"]

    # Define driver
    driver = '{SQL Server}'

    # Define the connection string
    connection_string = "Driver={};Server={};Database={};Uid={};Pwd={};Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;".format(
        driver, server, database, username, password)

    return pyodbc.connect(connection_string)

def get_users(conn):
    with conn.cursor() as cursor:
        logging.debug(
            "Using connection cursor to execute query (select all from users)")
        cursor.execute("SELECT * FROM users")

        # Get users
        logging.debug("Fetching all queried information")
        users_table = list(cursor.fetchall())

        # Clean up to put them in JSON.
        users_data = [tuple(user) for user in users_table]

        # Empty data list
        users = []

        users_columns = [column[0] for column in cursor.description]
        for user in users_data:
            users.append(dict(zip(users_columns, user)))

        # users = dict(zip(columns, rows))
        logging.debug(
            "User data retrieved and processed, returning information from get_users function")
        return func.HttpResponse(json.dumps(users), status_code=200, mimetype="application/json")

def add_user(conn, user_req_body):
    with conn.cursor() as cursor:
        # Unpack user data
        firstName = user_req_body["firstName"]
        lastName = user_req_body["lastName"]
        email = user_req_body["email"]

        # Create the query
        add_user_query = """
                         SET NOCOUNT ON;
                         DECLARE @NEWID TABLE(ID INT);

                         INSERT INTO dbo.users (firstName, lastName, email)
                         OUTPUT inserted.userId INTO @NEWID(ID)
                         VALUES('{}', '{}', '{}');

                         SELECT ID FROM @NEWID
                         """.format(firstName, lastName, email)


        logging.debug(
            "Using connection cursor to execute query (add a new user and get id)")
        count = cursor.execute(add_user_query)

        # Get the user id from cursor
        user_id = cursor.fetchval()
        
        logging.debug(
            "User added and new user id retrieved, returning information from add_user function")
        return func.HttpResponse(json.dumps({"userId": user_id}), status_code=200, mimetype="application/json")
