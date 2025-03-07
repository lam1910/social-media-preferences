import streamlit as st
import pandas as pd
import requests

SERVER_URL = "http://127.0.0.1"
SERVER_PORT = "8000"
END_POINT = "past-predictions"

GROUP_TEXT = {
    0: '17 year old, have few friends, rarely post about dance, music, god',
    1: '17 year old or younger, have a lot of friends (50-80), post about music, god',
    2: '17-18 year old, super popular (150+ friends), post about music, god the most, most likely female',
    3: '17 year old, have a bit of friends (20-30), post about music more than everyone',
    4: 'Funny, trolling group',
    5: '17-18 year old, very popular (80-150), post about dance, music, most likely female',
    6: '17 year old, have big group of friends (30-50), post about music, god',
}

st.set_page_config(page_title="Past Predictions", page_icon="📒")

# TODO: get data from API and display
url = SERVER_URL + ":" + SERVER_PORT + "/" + END_POINT
try:
    response = requests.get(url)
    result_code = response.status_code
    result_data = response.json()
    if result_code // 100 < 4:
        st.success("Request successful")
        response_result = response.json()
        for i in range(len(response_result)):
            st.write('Person {} group: {}'.format(i + 1, GROUP_TEXT[response_result[i]['prediction']]))
    else:
        st.error("Request failed")
except Exception as e:
    st.warning("Server side error. Please contact admin.")
    st.error(e)
