from Code.Zz_functions import handle_all_exceptions , ErrorLogFile
from mysql.connector import connect, Error

unprocessedTopicUrls = ["https://www.bbc.co.uk/news/topics/c207p54md43t","https://www.bbc.co.uk/news/topics/crr7mlg0dg1t"]

# smallTopis = [ "https://www.bbc.co.uk/news/topics/cj1g47k231yt"]
#unprocessedTopicUrls = [3]

config = {
    'user': 'root',
    'password': 'example',  # Use your root password here
    'host': 'localhost',
    'port': 3308,
    'database': 'TopicNewsStory_DEV'
}



def get_database_connection(config):
    try:
        cnx = connect(**config)
        return cnx
    except Error as e:
        handle_all_exceptions(e, ErrorLogFile)
        return None

def count_of_TopicUrl(TopicUrl):
    search_for_topic = "SELECT COUNT(id) FROM topic WHERE url = %s"
    cnx = get_database_connection(config)
    if cnx is None:
        return 0  # or handle this scenario as needed
    cursor = cnx.cursor()
    try:
        cursor.execute(search_for_topic, (TopicUrl,))
        result = cursor.fetchall()
        count = result[0][0]
        return count
    except Exception as e:
        handle_all_exceptions(e, ErrorLogFile)
    finally:
        cnx.close()

def insert_Topic(url):
    topicOccurance = count_of_TopicUrl(url)
    if topicOccurance == 0:
        insert_story = "INSERT INTO topic (url) VALUES (%s)"
        cnx = get_database_connection(config)
        if cnx is None:
            return  # or handle this scenario as needed
        cursor = cnx.cursor()
        try:
            cursor.execute(insert_story, (url,))
            cnx.commit()
        except Exception as e:
            handle_all_exceptions(e, ErrorLogFile)
        finally:
            cnx.close()
    else:
        print("The Topic Already exists")

for tp in unprocessedTopicUrls:
    print (tp)
    try:
        if type(tp) != str:
            raise Exception(f"Url  {tp} is not a string")
        insert_Topic(tp)
    except Exception as e:
            handle_all_exceptions(e, ErrorLogFile)


