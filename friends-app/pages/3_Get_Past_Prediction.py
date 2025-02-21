import streamlit as st
import pandas as pd
import requests

SERVER_URL = "http://127.0.0.1"
SERVER_PORT = "8000"
END_POINT = "predict"
st.set_page_config(page_title="Past Predictions", page_icon="📒")

# TODO: get data from API and display
url = SERVER_URL + ":" + SERVER_PORT + "/" + END_POINT
try:
    response = requests.get(url)
    result_code = response.status_code
    result_data = response.json()
    if result_code // 100 < 4:
        st.success("Request successful")
        st.write(response.json())
    else:
        st.error("Request failed")
except Exception as e:
    st.warning("Server side error. Please contact admin.")
    st.error(e)
