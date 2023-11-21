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
import time
import requests
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

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
    if len(st.session_state['api_endpoint_url']) > 10:
        with st.spinner("Saving New API Endpoint..."):
            endpoint_json = {"api_endpoint": st.session_state['api_endpoint_url'].strip()}
            with open("config.json","w",encoding="utf-8") as out_file:
                json.dump(endpoint_json, out_file)
        st.write("API Endpoint saved, refreshing browser to take effect.")
        time.sleep(1)
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
            

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
        return "Data file written to S3.  Waiting 20 seconds for processing and will then refresh browser."
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
    

# Initialize Inventory Tab Pick Lists and Displays   
if 'inventory_locations' not in st.session_state:
    st.session_state['inventory_locations'] = get_locations(st.session_state['api_endpoint_url'])
    if len(st.session_state['inventory_locations']) > 0:
        location_inv = st.session_state['inventory_locations'][0]
        st.session_state['inventory_picked_location'] = location_inv
        st.session_state['inventory_unicorns'] = get_inventory(st.session_state['api_endpoint_url'], location_inv )
    else:
        st.session_state['inventory_picked_location'] = ""
        st.session_state['inventory_unicorns'] = []

# Initialize Reservation Tab Pick Lists and Displays  
if 'reservation_locations' not in st.session_state:
    st.session_state['reservation_locations'] = get_locations(st.session_state['api_endpoint_url'])
    if len(st.session_state['reservation_locations']) > 0:
        location_res = st.session_state['reservation_locations'][0]
        st.session_state['reservation_picked_location'] = location_res
        u_list = [ u["Name"] for u in get_inventory(st.session_state['api_endpoint_url'], location_res, True ) ]
        st.session_state['reservation_unicorns'] = u_list
    else:
        st.session_state['reservation_picked_location'] = ""
        st.session_state['reservation_unicorns'] = []

def update_unicorn_inventory_list():
    """
    Update the sessions state for the list of unicorns for the current inventory location
    """
    location_inv = st.session_state['inventory_picked_location']
    if location_inv != "":
        u_list = get_inventory(st.session_state['api_endpoint_url'], location_inv )
    else:
        u_list = []
    st.session_state['inventory_unicorns'] = u_list

def update_unicorn_reserve_list():
    """
    Update the sessions state for the reservable unicorns for the current reserve location
    """
    location_res = st.session_state['reservation_picked_location']
    if location_res != "":
        u_list = [ u["Name"] for u in get_inventory(st.session_state['api_endpoint_url'], location_res, True ) ]
    else:
        u_list = []
    st.session_state['reservation_unicorns'] = u_list


# Generate the Application Title
col1, col2 = st.columns([1, 4])
col1.markdown(st.session_state['unicorn_art'])
col2.header('Unicorn Reservation System (URS)', divider='rainbow')
col2.write("""*Reserving Happy Unicorns Around the World!*""")

# The rest of the Application is on 3 tabs
listing_tab, reserve_tab, admin_tab = st.tabs(["Listing", "Reserve", "Administration"])

# Listing Tab
with listing_tab:
    st.radio("Pick a location for the Unicorn listing:", 
             options=st.session_state['inventory_locations'],
             key="inventory_picked_location",
             on_change=update_unicorn_inventory_list)
    st.table(st.session_state['inventory_unicorns'])

# Reserve Tab
with reserve_tab:
    st.radio("Pick a location for Unicorn reservations:",
                            options = st.session_state['reservation_locations'],
                            key="reservation_picked_location",
                            on_change=update_unicorn_reserve_list)
    
    if len(st.session_state['reservation_unicorns']) > 0:

        redraw_handle = st.empty()
        redraw_handle.selectbox(label='Which Unicorn would you like to reserve?',
                                         options=st.session_state['reservation_unicorns'],
                                         key="reservation_unicorn_name")
        reserve_for = st.text_input("Reserve Unicorn for:")
        if st.button(f"Reserve Unicorn"):
            unicorn_to_reserve = st.session_state['reservation_unicorn_name']
            with st.spinner("Reserving Unicorn..."):
                reserve_status = reserve_unicorn(st.session_state['api_endpoint_url'], 
                                                 st.session_state['reservation_unicorn_name'], 
                                                 reserve_for)
            if reserve_status:
                st.write(f"Unicorn Reserved: {unicorn_to_reserve}")
                time.sleep(1)
                streamlit_js_eval(js_expressions="parent.window.location.reload()")
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
        with st.spinner("Uploading file to S3..."):
            TEMP_FILE_NAME = str(uuid.uuid4()) + ".csv"
            string_data = uploaded_file.getvalue().decode("utf-8")
            with open(TEMP_FILE_NAME,"w",encoding="utf-8") as out_file:
                out_file.write(string_data)
            out_message = upload_file_to_s3(st.session_state['api_endpoint_url'], TEMP_FILE_NAME)
            os.remove(TEMP_FILE_NAME)
        with st.spinner(out_message):
            time.sleep(20)
            streamlit_js_eval(js_expressions="parent.window.location.reload()")

