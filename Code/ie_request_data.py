from Configuration import config_complete
from Code.Zz_functions import handle_all_exceptions , ErrorLogFile
from pymongo import MongoClient

def get_stories_under_topics1(topicId, topicUrl, payload):
    def Generate_Soup(URL):
        import requests
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
        from bs4 import BeautifulSoup as bs
        try:
            make_request = requests.get(URL, headers=headers)
            if make_request.status_code == 200:
                make_soup = [bs(make_request.text, "html.parser"), True]
            else:
                make_soup = [bs(make_request.text, "html.parser"), make_request.status_code]
            return make_soup
        except requests.exceptions.RequestException as e:
            handle_all_exceptions(e, ErrorLogFile)
            make_soup = [0, False]
            return make_soup

            print(f'Error: {e}')

    def Get_Pagination_Pages(soup):
        import re
        pagination_container = soup.find('div', class_=re.compile(".*NumberedPagesButtonsContainer*."))
        try:
            page_items = pagination_container.find_all('li')
            pages = []
            isMultiPage = True
            for item in page_items:
                a_tag = item.find('a')
                if a_tag:
                    url = a_tag['href']
                    page_number = item.find('div', class_=re.compile(".*StyledButtonContent.*")).get_text()
                    try:
                        page_number = int(page_number)
                        pages.append(page_number)
                    except:
                        pass
        except:
            pages = None
            isMultiPage = False

        return [isMultiPage, pages]

    def pagesRange(MaxPage):
        pages_list = list(range(2, MaxPage + 1))
        stringNum = ["?page=" + str(i) for i in pages_list]
        return stringNum

    def extract_simple_grid(soup,payload,topicId):
        import re
        articles_data = []
        try:
            container = soup.find('div', class_=re.compile(".*SimpleGridContainer*."))
            if container:
                articles = container.find_all('div', attrs={'type': 'article'})
                for article in articles:
                    # Find the story link
                    link_tag = article.find('a', class_=re.compile(".*PromoLink*."))
                    link = link_tag.get('href') if link_tag else None
                    payload["data"].append({"url": link,"topicId": topicId})
                return payload
        except:
            print("FLAKY CAN YOU DO BETTER")
            return [False, articles_data]

    def extract_stack_story(soup , payload,topicId):
        import re
        articles_data = []
        try:
            container = soup.find('div', class_=re.compile(".*StackWrapper*."))
            if container:
                articles = container.find_all('div', attrs={'type': 'article'})
                for article in articles:
                    # Find the story link
                    link_tag = article.find('a', class_=re.compile(".*LinkPostLink*."))
                    link = link_tag.get('href') if link_tag else None
                    payload["data"].append({"url": link,"topicId": topicId})
            return payload
        except:
            print("FLAKY CAN YOU DO BETTER")
            return [False, articles_data]

    def determine_storage_structure(soup):
        import re
        data_structure = {}

        container = soup.find('div', class_=re.compile(".*SimpleGridContainer*."))
        stackWrapper = soup.find('div', class_=re.compile(".*StackWrapper*."))
        if not container:
            data_structure["hasSimpleGridContainer"] = False
        else:
            data_structure["hasSimpleGridContainer"] = True
        if not stackWrapper:
            data_structure["hasStackWrapper"] = False
        else:
            data_structure["hasStackWrapper"] = True
        return data_structure
        ###  Run Processes

    make_request = Generate_Soup(topicUrl)
    if make_request[1] == True:
        containedPages = Get_Pagination_Pages(make_request[0])
        page_key_counter = 0
        if containedPages[0] != False:
            paginationPages = max(containedPages[1])
            pagesToProcess = pagesRange(paginationPages)
            YourPage = make_request[0]
            data_storage = determine_storage_structure(YourPage)
            if data_storage["hasSimpleGridContainer"] == True:
                extract_simple_grid(YourPage,payload,topicId )
            if data_storage["hasStackWrapper"] == True:
                extract_stack_story(YourPage,payload,topicId )
            page_key_counter += 1
            for pageNumber in pagesToProcess:
                topic_page_url = topicUrl + pageNumber
                make_topic_page_call = Generate_Soup(topic_page_url)
                if make_topic_page_call[1] == True:
                    YourPage = make_topic_page_call[0]
                    data_storage = determine_storage_structure(YourPage)
                    if data_storage["hasSimpleGridContainer"] == True:
                        extract_simple_grid(YourPage,payload,topicId)
                    if data_storage["hasStackWrapper"] == True:
                        extract_stack_story(YourPage,payload,topicId)
                    page_key_counter += 1
        else:
            pass

    return payload
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
        handle_all_exceptions(e,ErrorLogFile)
    finally:
        cnx.close()

def select_topics_to_requested(config):
    select_query = """SELECT * FROM topic WHERE processsedCount = 0 LIMIT 2 ;"""
    import mysql.connector
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    try:
        cursor.execute(select_query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        handle_all_exceptions(e, ErrorLogFile)
    finally:
        cnx.close()

payload_source = {"data" : []}

topicsForRequest = select_topics_to_requested(config_complete)
for t in topicsForRequest:
    topicId = str(t[0])
    topicUrl = t[1]
    try:
        if type(topicUrl) != str:
            raise Exception(f"Url  {tp} is not a string")
        get_stories_under_topics1(topicId, topicUrl, payload_source)
    except Exception as e:
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

def convert_keys_to_string(data):
    if isinstance(data, dict):
        return {str(key): convert_keys_to_string(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_keys_to_string(item) for item in data]
    else:
        return data




#AdjDataStorage = convert_keys_to_string(DataStorage)



Add_To_DB = add_topic_json_to_db(payload_source,"topics_json")

for item in payload_source["data"]:
    print (item)