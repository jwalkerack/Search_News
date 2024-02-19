


def drop_database(database_name: str, config):
    import mysql.connector
    from mysql.connector.errors import ProgrammingError, DataError, OperationalError, InterfaceError, Error
    from Code.Zz_functions import handle_all_exceptions, ErrorLogFile

    # Adjust config to not specify the database, or connect to the default/system database
    config_without_db = config.copy()
    config_without_db.pop('database', None)  # Remove the 'database' key if it exists
    try:
        cnx = mysql.connector.connect(**config_without_db)
        cursor = cnx.cursor()

        # Query to check if the database exists
        check_db_query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{database_name}'"
        cursor.execute(check_db_query)
        if cursor.fetchone():
            # Database exists, proceed to drop
            drop_db_query = f"DROP DATABASE {database_name}"
            cursor.execute(drop_db_query)
            cnx.commit()
            print(f"Database {database_name} dropped")
        else:
            # Database does not exist, raise an exception
            raise Exception(f"Database {database_name} does not exist")
    except Exception as e:
        print(e)
        handle_all_exceptions(e, ErrorLogFile)  # Make sure this function is defined to handle exceptions appropriately.
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()



if __name__ == "__main__":
    from Configuration import config_complete , config_pass
    drop_database("TopicNewsStory_DEV", config_complete)

