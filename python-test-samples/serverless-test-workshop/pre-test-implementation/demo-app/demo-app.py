# streamlit run demo-app.py

import json
import requests         # To install: pip install requests
import os
import boto3            # To install: pip install boto3
import logging
import uuid
import streamlit as st  # To install: pip install streamlit


def upload_file_to_s3(api_endpoint_url: str, file_to_upload: str) -> None:
    """
    Upload a data file to S3
    """
    get_presigned_url = f"{api_endpoint_url}/geturl"
    response = requests.get(get_presigned_url,timeout=120)
    with open(file_to_upload, 'rb') as f:
        files = {'file': (file_to_upload, f)}
        http_response = requests.post(response.json()['url'], data=response.json()['fields'], files=files)
    if http_response.ok:
        st.write("Data file written to S3.")
    else:
        st.write("Data file not written to S3.")

def get_inventory(api_endpoint_url: str, fetch_loc: str) -> list:
    """
    Get Unicorn Inventory
    """
    inventory_url = f"{api_endpoint_url}/list/{fetch_loc}"
    # TODO: Pagination
    response = requests.get(inventory_url, timeout=120)
    return response.json()["unicorn_list"]

def reserve_unicorn(api_endpoint_url: str, unicorn_name: str) -> bool:
    """
    Reserve a Unicorn
    """
    inventory_url = f"{api_endpoint_url}/checkout/{unicorn_name}"
    response = requests.get(inventory_url, timeout=120)
    return response.ok

# Application Settings
with open("demo-app-config.json","r",encoding="utf-8") as f:
    app_config = json.load(f)
api_endpoint = app_config["api_endpoint"]
location_list = app_config["location_list"]

# App Title
st.write("""
# Unicorn Reservation System (UCS)
*Reserving Happy Unicorns Around the World!*
""")
st.image("_img/unicorn.png", width=100)

tab1, tab2, tab3 = st.tabs(["Listing", "Reserve", "Administration"])

with tab1:
    location_listing = st.radio("Pick a location for the list", location_list)
    u_inv = get_inventory(api_endpoint, location_listing) 
    st.table(u_inv)

with tab2:
    location_res = st.radio("Pick a location for reservations", location_list)
    u_list = [ u["Name"] for u in get_inventory(api_endpoint, location_res) ]
    unicorn_to_reserve = st.selectbox('Which Unicorn would you like to reserve?', u_list)
    if st.button(f"Reserve {unicorn_to_reserve}"):
        if reserve_unicorn(api_endpoint, unicorn_to_reserve):
            st.write(f"Unicorn Reserved: {unicorn_to_reserve}")
        else:
            st.write(f"Error reserving Unicorn {unicorn_to_reserve}!")
        
with tab3:
    # File picker for uploading to the unicorn inventory
    uploaded_file = st.file_uploader("Choose a CSV file for the Unicorn Inventory.", type=["CSV","csv"])
    if uploaded_file is not None:
        TEMP_FILE_NAME = str(uuid.uuid4()) + ".csv"
        string_data = uploaded_file.getvalue().decode("utf-8")
        with open(TEMP_FILE_NAME,"w",encoding="utf-8") as out_file:
            out_file.write(string_data)
        upload_file_to_s3(api_endpoint, TEMP_FILE_NAME)
        os.remove(TEMP_FILE_NAME)



