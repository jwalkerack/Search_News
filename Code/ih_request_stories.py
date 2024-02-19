from Code.Zz_functions import handle_all_exceptions , ErrorLogFile
# Generate Stories which need to be processed
# Loop through these stories
# Make a request ?
## If the request is vali
##  {'StoryId' : Soup }

config = {
    'user': 'root',
    'password': 'example',  # Use youra root password here
    'host': 'localhost',
    'port': 3308,
    'database': 'TopicNewsStory_DEV'
}

def extract_author_names_from_pulled(author_text):
    import re
    # Remove the 'By ' prefix if it exists
    author_text = author_text.replace('By ', '')

    # Define a regular expression pattern to split the string
    # This pattern looks for commas, 'and', or '&' as delimiters.
    pattern = r',|\band\b|\&'

    # Split the author_text using the defined pattern
    authors = re.split(pattern, author_text)

    # Strip whitespace from each author name and filter out any empty strings
    author_names = [author.strip() for author in authors if author.strip()]

    return author_names



def extract_time_elements(soup):
    from datetime import datetime
    try:
        time_element = soup.find('time', {'data-testid': 'timestamp'})
        if time_element is not None:
            datetimex = time_element.get('datetime')
            NewTime = datetime.fromisoformat(datetimex.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            text = time_element.get_text().strip()
        else:
            print("Time element not found")
            NewTime = ""
            text = ""
        return [NewTime, text]
    except Exception as e:
        print ("Your In the Except ... by why")
        print(f'Error: {e}')
        return ["", ""]

def extract_contributor_name(soup):
    import re
    # Using a regular expression to match the class
    contributor_div = soup.find('div', class_=re.compile(".*TextContributorName.*"))
    if contributor_div:
        return contributor_div.get_text(strip=True)
    else:
        return ""

def extract_Topics(soup):
    links_with_text = []
    topic_list_div = soup.find('div', {'data-component': 'topic-list'})

    if topic_list_div:
        for link in topic_list_div.find_all('a', href=True):
            if "/topics/" in link['href']:
                links_with_text.append(link.get_text(strip=True))

    return links_with_text


def get_main_content(soup):
    try:
        maincontent = soup.find(id='main-content')
        all_text = maincontent.get_text(separator=' ', strip=True)
    except:
        all_text = soup.find('div').get_text(separator=' ', strip=True)
    return all_text


def run_data_extraction(soup):
    rawAuthor = extract_contributor_name(soup)
    authors = extract_author_names_from_pulled(rawAuthor)
    topics = extract_Topics(soup)
    ExtractDateTime = extract_time_elements(soup)
    storyCreatedOn = ExtractDateTime[0]
    plainText = get_main_content(soup)
    Data = {"storyText": plainText , "Authors" : authors ,"topics" :topics , "storyCreatedOn" :storyCreatedOn}
    return Data




def fetch_and_store_html(URL,storyId):
    import requests
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(URL, headers=headers)
        if response.status_code == 200:
            html_content = response.text
            from bs4 import BeautifulSoup as bs
            soup = bs(html_content, "html.parser")
            rawAuthor = extract_contributor_name(soup)
            authors = extract_author_names_from_pulled(rawAuthor)
            topics = extract_Topics(soup)
            ExtractDateTime = extract_time_elements(soup)
            storyCreatedOn = ExtractDateTime[0]
            plainText = get_main_content(soup)
            # Assuming the status is True for successful fetch
            data_to_store = {'url': URL, 'plain_text': plainText, 'status': True, 'storyId' : storyId, 'Authors':authors,
                             'topics': topics , 'storyCreatedOn':storyCreatedOn }
        else:
            # Assuming you want to note the status code if not 200
            data_to_store = {'url': URL, 'status': response.status_code}
    except requests.exceptions.RequestException as e:
        handle_all_exceptions(e,ErrorLogFile)
        # In case of request exceptions, store the error
        data_to_store = {'url': URL, 'error': str(e), 'status': False, 'storyId' : storyId}

    return data_to_store


def add_data_to_mongo_db(Data,Collection):
    from pymongo import MongoClient, errors
    # Connect to MongoDB
    # Replace 'localhost' with the Docker host IP if necessary, or use 'mongo' if using Docker's default network
    client = MongoClient('mongodb://admin:password@localhost:27017/')
    db = client['news_database']
    collectionY = db[Collection]
    try:
        result = collectionY.insert_one(Data)
        # Check if the insert was successful by looking for the inserted_id
        if result.inserted_id:
            print(f"Data inserted successfully with _id: {result.inserted_id}")
            return True
        else:
            print("Insert failed.")
            return False
    except errors.PyMongoError as e:
        handle_all_exceptions(e, ErrorLogFile)
        # Handle any errors that occur during the insert
        print(f"An error occurred: {e}")
        return False

def select_stories_to_requested():
    select_query = """SELECT * FROM story WHERE processsedCount = 0 LIMIT 10000 ;"""
    import mysql.connector
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    try:
        cursor.execute(select_query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        handle_all_exceptions(e, ErrorLogFile)
        print(e)
    finally:
        cnx.close()


def check_story_id_exists(story_id):
    from pymongo import MongoClient
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://admin:password@localhost:27017/')
        db = client['news_database']
        collection = db['story_struc']

        # Query the collection for the storyId
        query_result = collection.find_one({'storyId': story_id})

        # Check if a document was found
        if query_result:
            print(f"Story ID {story_id} exists in the collection.")
            return True
        else:
            print(f"Story ID {story_id} does not exist in the collection.")
            return False
    except Exception as e:
        handle_all_exceptions(e, ErrorLogFile)


def update_Story(storyId):
    ## Updates the story table by incrementing the processsedCount by 1 for the given storyId.
    import mysql.connector
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    update_query = """UPDATE story SET processsedCount = processsedCount + 1 WHERE id = %s"""
    try:
        cursor.execute(update_query, (storyId,))
        cnx.commit()
    except Exception as e:
        handle_all_exceptions(e, ErrorLogFile)
    finally:
        cnx.close()

stories = select_stories_to_requested()

for s in stories:
    storyID =  s[0]
    storyURL = "https://www.bbc.co.uk/" + s[1]
    get_html = fetch_and_store_html(storyURL,storyID)
    if get_html['status'] == True:
        add_data_to_mongo_db(get_html, 'story_struc')
    if check_story_id_exists(storyID) == True:
        update_Story(storyID)
        ##### Need to set StoryTable to processed

    #
    #print (get_html)