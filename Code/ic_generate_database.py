story = """    
CREATE TABLE IF NOT EXISTS story (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(255),
        processsedCount INT DEFAULT 0
    );"""

topic = """    
CREATE TABLE IF NOT EXISTS topic (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(255),
        processsedCount INT DEFAULT 0
    );"""


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


if __name__ == "__main__":
    from Configuration import config_complete, config_partial
    from Code.Zz_functions import handle_all_exceptions , ErrorLogFile
    create_database("TopicNewsStory_DEV", config_partial, ErrorLogFile)
    create_tables("TopicNewsStory_DEV", [story, topic], config_complete, ErrorLogFile)





