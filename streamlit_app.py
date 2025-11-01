import streamlit as st
import requests
import pandas as pd
import re

# --- Page Configuration ---
st.set_page_config(page_title="Project Samarth", page_icon="🌾")
st.title("Project Samarth 🌾")
st.caption("Intelligent Q&A on India's Agricultural Economy & Climate")

# --- NEW: Add example questions and keywords ---
with st.info("Welcome! This prototype can answer questions combining one crop and one region."):
    st.write("**Available Crops:** `rice`, `wheat`, `maize`")
    st.write("**Available Regions:** `Punjab`, `Uttar Pradesh`, `Haryana`, `Kerala`, `Assam`")
    st.write("**Example queries:**")
    st.code("- Compare rice production and rainfall in Punjab\n- show me data on wheat in uttar pradesh\n- what is the maize production and rainfall in assam?")

# --- Configuration ---
# We now read the API key from Streamlit's secret management
try:
    API_KEY = st.secrets["API_KEY"]
except FileNotFoundError:
    st.error("API_KEY not found. Please add it to your Streamlit Secrets.")
    st.stop()
except KeyError:
    st.error("API_KEY not found. Please add it to your Streamlit Secrets.")
    st.stop()


# --- FIXED URLS ---
AGRICULTURE_API_URL = "https://api.data.gov.in/resource/2cd35c5a-e278-4a7c-8d1f-63316dbef7a6"
RAINFALL_API_URL = "https://api.data.gov.in/resource/8e0bd482-4aba-4d99-9cb9-ff124f6f1c2f"
# ------------------

# Define our keyword lists (moved from backend)
SUPPORTED_CROPS = {
    "rice": "Rice Production (000 Tonnes)",
    "wheat": "Wheat Production (000 Tonnes)",
    "maize": "Maize Production (000 Tonnes)"
}
SUPPORTED_REGIONS = ["PUNJAB", "UTTAR PRADESH", "HARYANA", "KERALA", "ASSAM"]

# --- Data Fetching Functions (from backend) ---

@st.cache_data(ttl=3600) # Cache data for 1 hour
def fetch_agriculture_data():
    """Fetches the All-India crop production data."""
    print("Fetching agriculture data...")
    url = f"{AGRICULTURE_API_URL}?api-key={API_KEY}&format=json&limit=1000"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data['records'])
        
        # Define columns to convert
        cols_to_convert = {
            'food_grains_cereals___rice_000_tonnes_': 'Rice Production (000 Tonnes)',
            'food_grains_cereals___wheat_000_tonnes_': 'Wheat Production (000 Tonnes)',
            'food_grains_cereals___maize_000_tonnes_': 'Maize Production (000 Tonnes)'
        }
        
        for api_col, friendly_name in cols_to_convert.items():
             if api_col in df.columns:
                df[friendly_name] = pd.to_numeric(df[api_col], errors='coerce')
        
        df = df.rename(columns={'_year': 'Year'})
        df['Year'] = df['Year'].str.split('-').str[0].astype(int)
        
        required_cols = ['Year'] + list(cols_to_convert.values())
        return df[required_cols]
        
    except Exception as e:
        print(f"Error in fetch_agriculture_data: {e}")
        st.error(f"Error fetching agriculture data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600) # Cache data for 1 hour
def fetch_rainfall_data():
    """Fetches the Sub-division wise rainfall data."""
    print("Fetching rainfall data...")
    url = f"{RAINFALL_API_URL}?api-key={API_KEY}&format=json&limit=5000"
    try:
        response = requests.get(url, timeout=20) 
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data['records'])
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df = df[df['subdivision'].str.contains('ANNUAL') == False]
        df['Annual Rainfall (mm)'] = pd.to_numeric(df['annual'], errors='coerce')
        df = df.rename(columns={'year': 'Year', 'subdivision': 'Sub-Division'})
        
        # Standardize region names to UPPERCASE for merging
        df['Sub-Division'] = df['Sub-Division'].str.upper()
        
        return df[['Year', 'Sub-Division', 'Annual Rainfall (mm)']]
    except Exception as e:
        print(f"Error in fetch_rainfall_data: {e}")
        st.error(f"Error fetching rainfall data: {e}")
        return pd.DataFrame()

# --- Q&A Logic Functions (from backend) ---

def parse_query(query):
    """Finds the first supported crop and region in a query."""
    query_lower = query.lower()
    crop_name = None
    region_name = None

    for crop_key in SUPPORTED_CROPS:
        if crop_key in query_lower:
            crop_name = SUPPORTED_CROPS[crop_key]
            break
            
    for region_key in SUPPORTED_REGIONS:
        if region_key.lower() in query_lower:
            region_name = region_key
            break
            
    return crop_name, region_name

def answer_question(crop_name, region_name):
    """ Fetches, merges, and analyzes data to answer the question."""
    
    agri_data = fetch_agriculture_data()
    rain_data = fetch_rainfall_data()
    
    if agri_data.empty or rain_data.empty:
        return "Error: Could not fetch data from one or more sources.", []
        
    region_rain_data = rain_data[rain_data['Sub-Division'] == region_name].copy()
    
    if region_rain_data.empty:
        return f"Error: Could not find rainfall data for region '{region_name}'.", []
    
    # Merge All-India agriculture with regional rainfall
    merged_data = pd.merge(agri_data, region_rain_data, on='Year', how='inner')
    
    if merged_data.empty:
        return "Error: Data fetched, but no overlapping years found.", []

    # Select only the columns we care about for the final answer
    final_cols = ['Year', crop_name, 'Annual Rainfall (mm)']
    merged_data = merged_data[final_cols]
    
    # Format the answer
    merged_data = merged_data.sort_values(by='Year', ascending=False).head(10)
    
    answer_string = f"Here is the comparison for {crop_name} (All-India) vs. rainfall in {region_name} (last 10 available years):\n\n"
    answer_string += merged_data.to_string(index=False)
    
    citations = [
        {"source": "All India Production of Principal Crops", "url": "https://api.data.gov.in/resource/2cd35c5a-e278-4a7c-8d1f-63316dbef7a6"},
        {"source": "Sub Divisional Monthly Rainfall (1901-2017)", "url": "https://api.data.gov.in/resource/8e0bd482-4aba-4d99-9cb9-ff124f6f1c2f"}
    ]
    
    return answer_string, citations

# --- Chat Interface (from frontend) ---

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("Show Data Sources"):
                for source in message["sources"]:
                    st.write(f"**{source['source']}**")
                    st.caption(f"API Endpoint: {source['url']}")

if prompt := st.chat_input("Ask a question about crops and climate..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- This is the NEW logic ---
    # We call the functions directly instead of using an API
    with st.chat_message("assistant"):
        with st.spinner("Thinking... (Fetching and analyzing live data)"):
            
            # 1. Parse the query
            crop, region = parse_query(prompt)
            
            if not crop or not region:
                answer = f"Sorry, I can only answer questions about crops ({', '.join(SUPPORTED_CROPS.keys())}) and regions ({', '.join(SUPPORTED_REGIONS)}). Please rephrase your query."
                sources = []
            else:
                # 2. Get the answer
                answer, sources = answer_question(crop, region)
            
            # 3. Display the answer
            st.markdown(answer)
            bot_message = {"role": "assistant", "content": answer}
            
            if sources:
                bot_message["sources"] = sources
                with st.expander("Show Data Sources"):
                    for source in sources:
                        st.write(f"**{source['source']}**")
                        st.caption(f"API Endpoint: {source['url']}")
            
            st.session_state.messages.append(bot_message)

