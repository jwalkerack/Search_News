# BBC News Data Pipeline Application

## Description

This application automates the sourcing of news data from BBC News by targeting specific topic pages to access URLs for individual stories. It then makes requests to each story, processes the data, and extracts key information, which is subsequently saved into a MongoDB database. This database powers a Streamlit app, enabling users to perform queries and retrieve stories related to their interests.

The project was developed to practice building a data pipeline and to explore data storage in both SQL and MongoDB databases, with a focus on learning how to containerize applications using Docker for easier deployment and scalability.

## Installation and Setup

This project is containerized with Docker, streamlining the setup and execution process. Ensure you have Docker and Docker Compose installed on your system before proceeding.

## Features

Automated data extraction from BBC News topic pages.
Data processing and MongoDB storage.
Streamlit application for user queries and story display.
Dockerized environment for easy setup and deployment.

## Technologies Used

Python for backend and data processing.
MongoDB for data storage.
Streamlit for the user interface.
Docker for containerization and deployment.
