from Code.Zz_functions import handle_all_exceptions , ErrorLogFile
from Configuration import config_complete

def doesStoryUrlExist(storyUrl,config):
    ## Used to determine of a story URL exist in the story table
    select_count_url = "SELECT COUNT(id) FROM story WHERE url = %s"
    import mysql.connector
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    try:
        cursor.execute(select_count_url, (storyUrl,))
        result = cursor.fetchall()
        count = result[0][0]
        if count == 0:
            idExist = False
        else:
            idExist = True
        print (count)
        return idExist
    except Exception as e:
        handle_all_exceptions(e,ErrorLogFile)
    finally:
        cnx.close()

def insert_story(storyUrl,config):
    insert_story = "INSERT INTO story (url) VALUES (%s)"
    import mysql.connector
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    try:
        cursor.execute(insert_story, (storyUrl,))
        cnx.commit()
        cnx.close()
    except Exception as e:
        handle_all_exceptions(e, ErrorLogFile)
    finally:
        cnx.close()


def retrive_Mongo_Data(Collection):
    from pymongo import MongoClient
    # Connect to MongoDB
    # Replace 'localhost' with the Docker host IP if necessary, or use 'mongo' if using Docker's default network
    client = MongoClient('mongodb://admin:password@localhost:27017/')
    # Select the database
    db = client['news_database']
    # Select the collections
    collectionData = db[Collection]
    documents = collectionData.find({})
    return documents


def wipe_mongo(Collection):
    from pymongo import MongoClient
    try:
        # Connect to MongoDB
        # Replace 'localhost' with the Docker host IP if necessary, or use 'mongo' if using Docker's default network
        client = MongoClient('mongodb://admin:password@localhost:27017/')
        # Select the database
        db = client['news_database']
        # Select the collections
        collectionData = db[Collection]
        collectionData.delete_many({})
    except errors.ConnectionFailure as e:
        handle_all_exceptions(e, ErrorLogFile)
    except errors.PyMongoError as e:
        handle_all_exceptions(e, ErrorLogFile)



def add_topic_json_to_db(Data, YourTopic):
    try:
        client = MongoClient('mongodb://admin:password@localhost:27017/')
        db = client['news_database']
        collection = db[YourTopic]
        result = collection.insert_one(Data)
        if result.inserted_id:
            print(f"Data inserted successfully with _id: {result.inserted_id}")
            return True
    except errors.ConnectionFailure as e:
        handle_all_exceptions(e, ErrorLogFile)
        return False
    except errors.PyMongoError as e:
        handle_all_exceptions(e, ErrorLogFile)
        return False


def Read_Collection(CollectionName):
    from pymongo import MongoClient
    try:
        client = MongoClient('mongodb://admin:password@localhost:27017/')
        # Select the database
        db = client['news_database']
        # Select the collections
        story_collection = db[CollectionName]
        Stories = story_collection.find({})
        return Stories
    except errors.ConnectionFailure as e:
        handle_all_exceptions(e, ErrorLogFile)
    except errors.PyMongoError as e:
        handle_all_exceptions(e, ErrorLogFile)


def update_Topic(topicId,config):
    ## Updates the Topic Process to show its had an interation of processing
    import mysql.connector
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    update_query = """UPDATE topic SET processsedCount = processsedCount + 1 WHERE id = %s"""
    try:
        cursor.execute(update_query, (topicId,))
        cnx.commit()
    except Exception as e:
        handle_all_exceptions(e, ErrorLogFile)
    finally:
        cnx.close()

topicsStories = retrive_Mongo_Data('topics_json')
retrive_data = topicsStories[0]['data']

processedTopics = []

for story in retrive_data:
    storyUrl = story['url']
    topicId = story['topicId']
    print (storyUrl)
    if topicId not in processedTopics:
        processedTopics.append(topicId)
    isActive = doesStoryUrlExist(storyUrl,config_complete)
    if isActive == False:
        insert_story(storyUrl,config_complete)

### Update the Topics
for t in processedTopics:
    update_Topic(t, config_complete)

wipe_mongo('topics_json')