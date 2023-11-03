"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
# This is a demo Unicorn Reservation System front-end web application.
# To run:
#   1. Install the dependencies: pip3 install -r requirements.txt
#   2. Run the command:  streamlit run urs-ui.py --server.port 8080
#   3. The UI will be available in the browser
"""
import json
import os
import uuid
import requests
import streamlit as st


# Initialize Contexts
if 'api_endpoint_url' not in st.session_state:
    if os.path.isfile("config.json"):
        with open("config.json","r",encoding="utf-8") as f:
            app_config = json.load(f)
        st.session_state['api_endpoint_url'] = app_config["api_endpoint"].strip()
    else:
        st.session_state['api_endpoint_url'] = "https://{APIGATEWAYID}.execute-api.{REGION}.amazonaws.com/Prod/"

if 'unicorn_art' not in st.session_state:
    with open("_img/unicorn_art.md","r",encoding="utf-8") as f:
        st.session_state['unicorn_art'] = f.read()

def update_api_endpoint():
    """
    Endpoint has changes, save it for next run
    """
    endpoint_json = {"api_endpoint": st.session_state['api_endpoint_url'].strip()}
    with open("config.json","w",encoding="utf-8") as out_file:
        json.dump(endpoint_json, out_file)
        st.write("API Endpoint saved, refresh browser to take effect.")


# Retrieve Application Endpoint

def upload_file_to_s3(api_endpoint_url: str, file_to_upload: str) -> str:
    """
    Upload a data file to S3
    :param: api_endpoint_url - the endpoint of the API Gateway
    :param: file_to_upload - Path to the file to upload to S3
    :return: Status of the write
    """
    get_presigned_url = f"{api_endpoint_url}/geturl"
    response = requests.get(get_presigned_url,timeout=120)
    with open(file_to_upload, 'rb') as upload_file_ptr:
        files = {'file': (file_to_upload, upload_file_ptr)}
        http_response = requests.post(response.json()['url'],
                                      data=response.json()['fields'],
                                      files=files)
    if http_response.ok:
        return "Data file written to S3.  Wait 20 seconds and refresh browser."
    else:
        return "ERROR: Data file not written to S3."

def get_inventory(api_endpoint_url: str, fetch_loc: str, available_only = False) -> list:
    """
    Get Unicorn Inventory
    :param: api_endpoint_url - the endpoint of the API Gateway
    :param: fetch_loc - Filtering location
    :param: available_only - boolean, if true, returns only available unicorns
    :return: List of unicorn (dictionaries)
    """
    try:
        inventory_url = f"{api_endpoint_url}/list/{fetch_loc}"
        if available_only:
            inventory_url = inventory_url + "?available=True"

        # TODO: Pagination
        response = requests.get(inventory_url, timeout=120)
        return response.json()["unicorn_list"]
    except Exception as err:
        print(err)
        st.write("No Unicorns Found.")
        return []

def reserve_unicorn(api_endpoint_url: str, unicorn_name: str, unicorn_reserve_for : str) -> bool:
    """
    Reserve a Unicorn
    :param: api_endpoint_url - the endpoint of the API Gateway
    :param: unicorn_name - Unicorn to reserve
    :param: unicorn_reserve_for - Name of the person to reserve the unicorn for
    :return: True on success 
    """
    post_payload = {"unicorn": unicorn_name, "reserved_for": unicorn_reserve_for }
    inventory_url = f"{api_endpoint_url}/checkout"
    response = requests.post(inventory_url, timeout=120, data=post_payload)
    return response.ok

def get_locations(api_endpoint_url: str) -> list:
    """
    Get the list of unicorn locations
    :param: api_endpoint_url - the endpoint of the API Gateway
    :return: Array of locations
    """
    try:    
        location_list_url = f"{api_endpoint_url}/locations"
        response = requests.get(location_list_url, timeout=120)
        return response.json()["locations"]
    except Exception as err:
        print(err)
        return []
    

location_list = get_locations(st.session_state['api_endpoint_url'])

# Generate the Application Title
col1, col2 = st.columns([1, 4])
col1.markdown(st.session_state['unicorn_art'])
col2.header('Unicorn Reservation System (URS)', divider='rainbow')
col2.write("""*Reserving Happy Unicorns Around the World!*""")

# The rest of the Application is on 3 tabs
listing_tab, reserve_tab, admin_tab = st.tabs(["Listing", "Reserve", "Administration"])

# Listing Tab
with listing_tab:
    location_listing = st.radio("Pick a location for the Unicorn listing:", location_list)
    u_inv = get_inventory(st.session_state['api_endpoint_url'], location_listing)
    st.table(u_inv)

# Reserve Tab
with reserve_tab:
    location_res = st.radio("Pick a location for Unicorn reservations:", location_list)
    u_list = [ u["Name"] for u in get_inventory(st.session_state['api_endpoint_url'], location_res, True ) ]
    if len(u_list) > 0:
        unicorn_to_reserve = st.selectbox('Which Unicorn would you like to reserve?', u_list)
        reserve_for = st.text_input("Reserve Unicorn for:")
        if st.button(f"Reserve {unicorn_to_reserve}"):
            if reserve_unicorn(st.session_state['api_endpoint_url'], unicorn_to_reserve, reserve_for):
                st.write(f"Unicorn Reserved: {unicorn_to_reserve}")
            else:
                st.write(f"Error reserving Unicorn {unicorn_to_reserve}!")
    else:
        st.write("No unicorns available at this location.")

# Administration Tab
with admin_tab:
    # Api Gateway Setup
    new_api_endpoint = st.text_input("API Endpoint (Hit Return to Apply):", 
                  max_chars=2048,
                  key="api_endpoint_url",
                  on_change=update_api_endpoint
    )
    
    # File picker for uploading to the unicorn inventory
    uploaded_file = st.file_uploader("Choose a CSV file for the Unicorn Inventory.", type=["csv"])
    if uploaded_file is not None:
        TEMP_FILE_NAME = str(uuid.uuid4()) + ".csv"
        string_data = uploaded_file.getvalue().decode("utf-8")
        with open(TEMP_FILE_NAME,"w",encoding="utf-8") as out_file:
            out_file.write(string_data)
        st.write(upload_file_to_s3(st.session_state['api_endpoint_url'], TEMP_FILE_NAME))
        os.remove(TEMP_FILE_NAME)
