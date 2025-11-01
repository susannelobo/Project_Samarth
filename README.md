# Project Samarth: Intelligent Q&A System

This project is a functional prototype of an intelligent Q&A system designed to answer complex, natural language questions about India's agricultural economy and its relationship with climate patterns.

It sources its information live from the data.gov.in portal, demonstrating the ability to reason across multiple, inconsistent data sources in real-time.

Features

Intelligent Chatbot: A simple, user-friendly chat interface (built with Streamlit) to ask natural language questions.

Dynamic Data Fetching: A Python backend (built with Flask) that programmatically fetches data from live government APIs.

Real-Time Data Cleaning: On-the-fly data cleaning and standardization using the pandas library to handle inconsistent column names and data types.

Cross-Domain Analysis: The system's "brain" merges data from the Ministry of Agriculture and the India Meteorological Department (IMD) on a shared 'Year' column.

Full Traceability: Every answer is returned with citations for the specific data.gov.in API endpoints used, fulfilling the core value of accuracy and traceability.

System Architecture (Local Development)

The prototype runs as two separate services:

app.py (The Backend/Brain):

A Flask web server that listens for requests at the /chat endpoint.

Parses the user's query for keywords (e.g., rice, punjab).

Calls the fetch_agriculture_data() and fetch_rainfall_data() functions.

Merges the two resulting dataframes.

Returns a JSON response containing the formatted answer and data sources.

frontend.py (The Frontend/UI):

A Streamlit web application that provides the chat interface.

When a user sends a message, it makes a POST request to the backend's /chat endpoint.

It then displays the bot's answer, including the expandable "Data Sources" section.

How to Run the Project (Locally)

You must run both services simultaneously in two separate terminals.

Prerequisites

Make sure you have all the required Python libraries:

pip install flask pandas requests streamlit


Step 1: Get Your API Key

Create a free account on https://data.gov.in/.

Navigate to "My Account" and generate an API key.

Copy this key.

Step 2: Run the Backend

Open your app.py file.

Paste your API key into the API_KEY = "..." variable at the top.

Open Terminal 1 and run:

python app.py


This will start the backend server at http://127.0.0.1:5000. Leave this terminal running.

Step 3: Run the Frontend

Open Terminal 2 (a new terminal).

Navigate to your project folder and run:

streamlit run frontend.py


Streamlit will automatically open your default browser to the chat application.

You can now ask questions based on the available keywords listed in the app!

How to Deploy to Streamlit Community Cloud

Streamlit Community Cloud runs a single file. Therefore, we must use the combined streamlit_app.py file, which contains both the backend logic and the frontend UI.

Step 1: Create Your Deployment Files

Ensure you have these two files in your project folder:

streamlit_app.py: The combined application code (provided in the Canvas).

requirements.txt: A file listing the project's dependencies (provided in the Canvas).

Step 2: Push to GitHub

Create a new public repository on GitHub.

Upload your streamlit_app.py and requirements.txt files to this repository.

Step 3: Deploy on Streamlit

Go to Streamlit Community Cloud and sign in (you can use your GitHub account).

Click the "New app" button.

Repository: Select the GitHub repository you just created.

Branch: Select your main branch (e.g., main or master).

Main file path: Type streamlit_app.py.

Click the "Advanced settings..." link.

Go to the "Secrets" section. This is where you will safely store your API key.

Paste the following into the Secrets text box, replacing the placeholder with your actual key:

API_KEY = "PASTE_YOUR_DATA_GOV_API_KEY_HERE"


Click "Save".

Click the "Deploy!" button.

Streamlit will now build your application and host it on a public URL. This may take a few minutes.
