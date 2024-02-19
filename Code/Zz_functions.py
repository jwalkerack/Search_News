import logging
from mysql.connector import Error, ProgrammingError, DataError, OperationalError, InterfaceError
def handle_all_exceptions(exception, logfile):
    import inspect
    import logging
    from pymongo.errors import PyMongoError, OperationFailure, ConnectionFailure, ConfigurationError
    from mysql.connector.errors import ProgrammingError, DataError, OperationalError, InterfaceError, Error
    # Set up logging on first exception handled
    if not logging.getLogger().hasHandlers():
        setup_logging(logfile)
    # Get the name of the current function
    current_function = inspect.currentframe().f_back.f_code.co_name

    # Handle MySQL errors
    if isinstance(exception, ProgrammingError):
        logging.error("%s - MySQL Programming Error: %s", current_function, exception)
    elif isinstance(exception, DataError):
        logging.error("%s - MySQL Data Error: %s", current_function, exception)
    elif isinstance(exception, OperationalError):
        logging.error("%s - MySQL Operational Error: %s", current_function, exception)
    elif isinstance(exception, InterfaceError):
        logging.error("%s - MySQL Connection Error: %s", current_function, exception)
    elif isinstance(exception, Error):
        logging.error("%s - MySQL General Database Error: %s", current_function, exception)

    # Handle MongoDB errors
    elif isinstance(exception, OperationFailure):
        logging.error("%s - MongoDB Operation Failure: %s", current_function, exception)
    elif isinstance(exception, ConnectionFailure):
        logging.error("%s - MongoDB Connection Failure: %s", current_function, exception)
    elif isinstance(exception, ConfigurationError):
        logging.error("%s - MongoDB Configuration Error: %s", current_function, exception)
    elif isinstance(exception, PyMongoError):
        logging.error("%s - MongoDB General Error: %s", current_function, exception)

    # Log general exceptions
    else:
        logging.error("%s - Unexpected Error: %s", current_function, exception)


def setup_logging(Location):
    """ Sets up the logging configuration. """
    logging.basicConfig(filename=Location,
                        filemode='a',  # Append to the log file
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.ERROR)



def create_database(databaseName, config, logfile):
    import mysql.connector
    try:
        cnx = mysql.connector.connect(**config)
        if cnx.is_connected():
            print("Connection is Open !!")
            cursor = cnx.cursor()
            dbQuery = f"CREATE DATABASE IF NOT EXISTS {databaseName};"
            cursor.execute(dbQuery)
            print(f"The {databaseName} has been created")
    except mysql.connector.Error as e:
        handle_all_exceptions(e, logfile)
        print(f"Failed to create {databaseName}: {e}")
    except Exception as e:
        handle_all_exceptions(e, logfile)
        print(f"An unexpected error occurred: {e}")
    else:
        cnx.close()

def create_tables(database,tables,config,logfile):
    ## This Function Takes a series of SQL table statements , which are defined above and creates these Tables
    import re
    import mysql.connector
    cnx = mysql.connector.connect(**config)
    if cnx.is_connected():
        print("Connection is Open !!")
        cursor = cnx.cursor()
        cursor.execute(f"USE {database};")
        for table in tables:
            try:
                cursor.execute(table)
                cnx.commit()
                pattern = r"CREATE TABLE IF NOT EXISTS\s+(\w+)\s*\("
                match = re.search(pattern, table)
                if match:
                    table_name = match.group(1)
                else:
                    table_name = "Table name not found"
                print (f"The {table_name} has been created")
            except Exception as e:
                handle_all_exceptions(e, logfile)
                print (f"The {table} creation contained errors - {e}")

        cursor.close()
        cnx.close()


ErrorLogFile = r"C:\Users\44756\PycharmProjects\Mongo_News\errorLog.csv"

