import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from collections import Counter
# MongoDB connection setup
client = MongoClient('mongodb://admin:password@localhost:27017/')  # Update with your MongoDB URI
db = client['news_database']  # Update with your database name
collection = db['story_struc']  # Update with your collection name

# Streamlit UI
st.title('MongoDB Query App')


def display_results(query):
    results = collection.find(query)

    # Prepare data with URL and first 50 characters of plain_text
    data = [{'URL': result['url'], 'Text Snippet': result['plain_text'][:50]} for result in results]

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)  # Display the URLs and text snippets as a table
        st.write(f"Total records found: {len(data)}")  # Display the count of records

        # Count topics occurrences if needed, as shown in the previous example
        # Reset the cursor if you need to iterate again for topics count
        results.rewind()
        topics = []
        for result in results:
            if 'topics' in result:  # Ensure there is a topics field
                topics.extend(result['topics'])

        topic_counts = Counter(topics)
        if topics:
            topics_df = pd.DataFrame(topic_counts.items(), columns=['Topic', 'Count']).sort_values(by='Count',
                                                                                                   ascending=False)
            st.subheader('Topics Count')
            st.table(topics_df)  # Using st.table for a static table display
    else:
        st.write("No records found.")

# Date range query
st.subheader('Query by Date Range')
start_date, end_date = st.date_input('Start date'), st.date_input('End date')
if st.button('Query Date Range'):
    start_datetime, end_datetime = datetime.combine(start_date, datetime.min.time()), datetime.combine(end_date, datetime.max.time())
    display_results({'storyCreatedOn': {'$gte': start_datetime, '$lte': end_datetime}})

# Query before a specific date
st.subheader('Query Before Date')
before_date = st.date_input('Before date', key='before_date')
if st.button('Query Before Date'):
    before_datetime = datetime.combine(before_date, datetime.max.time())
    display_results({'storyCreatedOn': {'$lt': before_datetime}})

# Authors query
st.subheader('Query by Authors')
author_input = st.text_input('Author Name')
if st.button('Query Author'):
    display_results({'Authors': author_input})

# Topics query
st.subheader('Query by Topics')
topic_input = st.text_input('Topic')
if st.button('Query Topic'):
    display_results({'topics': topic_input})

# Text search
st.subheader('Text Search in plain_text')
text_search = st.text_input('Search Text')
if st.button('Query Text'):
    display_results({'plain_text': {'$regex': text_search, '$options': 'i'}})