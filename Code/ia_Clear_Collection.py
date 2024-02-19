def flushCollection(CollectionName):
    from Code.Zz_functions import handle_all_exceptions , ErrorLogFile
    from pymongo import MongoClient
    try:
        client = MongoClient('mongodb://admin:password@localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['news_database']
        if CollectionName not in db.list_collection_names():
            raise Exception(f"Collection '{CollectionName}' does not exist.")
        collection = db[CollectionName]
        collection.delete_many({})
    except Exception as e:
        handle_all_exceptions(e, ErrorLogFile)

flushTopics = flushCollection("topics_json")
flushStories = flushCollection("story_struc")

###

flushNonDoesNotExist = flushCollection("Testing_error_writing")

