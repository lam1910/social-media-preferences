import traceback

import streamlit as st
import pandas as pd
import requests
import json

PERSONAL_ATTRIBUTES = [
    'grad_year', 'gender', 'age', 'number_of_friends'
]
SPORTS_ATTRIBUTES = [
    'basketball', 'football', 'soccer', 'softball', 'volleyball', 'swimming', 'cheerleading', 'baseball',
    'tennis', 'sports'
]
LIFESTYLE_ATTRIBUTES = [
    'cute', 'sex', 'sexy', 'hot', 'kissed', 'dance', 'band', 'marching', 'music', 'rock', 'god', 'church',
    'jesus', 'bible', 'hair', 'dress', 'blonde', 'mall', 'shopping', 'clothes', 'hollister', 'abercrombie',
    'die', 'death', 'drunk', 'drugs'
]
ALL_ATTRIBUTES = PERSONAL_ATTRIBUTES + SPORTS_ATTRIBUTES + LIFESTYLE_ATTRIBUTES
ALL_ATTRIBUTES_TYPE = {
    'grad_year': int, 'gender': str, 'age': float, 'number_of_friends': int, 'basketball': int, 'football': int,
    'soccer': int, 'softball': int, 'volleyball': int, 'swimming': int, 'cheerleading': int, 'baseball': int,
    'tennis': int, 'sports': int, 'cute': int, 'sex': int, 'sexy': int, 'hot': int, 'kissed': int, 'dance': int,
    'band': int, 'marching': int, 'music': int, 'rock': int, 'god': int, 'church': int, 'jesus': int, 'bible': int,
    'hair': int, 'dress': int, 'blonde': int, 'mall': int, 'shopping': int, 'clothes': int, 'hollister': int,
    'abercrombie': int, 'die': int, 'death': int, 'drunk': int, 'drugs': int
}

END_POINT = "predict"

st.set_page_config(page_title="Predict (Mass)", page_icon="📝")
# TODO: Read and parse file
try:
    base_url = st.session_state['base_url']
    group_text = st.session_state['group_meaning']
    url = base_url + "/" + END_POINT
except KeyError as err:
    st.warning('It seems like you are bypassing the main page. Please return to the main page first')
    url = 'http://localhost:8000' + "/" + END_POINT
    st.error(traceback.format_exc())

uploaded_file = st.file_uploader("Choose an csv file", type="csv")
has_index = st.checkbox('Is your file has index?', value=False)
has_header = st.checkbox('Is your file has header?', value=True)
if uploaded_file:
    if has_index:
        try:
            if not has_header:
                df1 = pd.read_csv(uploaded_file, names=ALL_ATTRIBUTES, index_col=0, dtype=ALL_ATTRIBUTES_TYPE,
                                  na_filter=False)
            else:
                df1 = pd.read_csv(uploaded_file, header=0, index_col=0, dtype=ALL_ATTRIBUTES_TYPE, na_filter=False)
            people = df1.to_dict(orient='records')
        except Exception as e:
            st.warning("File is not valid")
            st.error(e)
    else:
        try:
            if not has_header:
                df1 = pd.read_csv(uploaded_file, names=ALL_ATTRIBUTES, dtype=ALL_ATTRIBUTES_TYPE, na_filter=False)
            else:
                df1 = pd.read_csv(uploaded_file, header=0, dtype=ALL_ATTRIBUTES_TYPE, na_filter=False)
            people = df1.to_dict(orient='records')
        except Exception as e:
            st.warning("File is not valid")
            st.error(e)

# TODO: Feed to API
if uploaded_file:
    response = requests.post(url, data=json.dumps({'features': people}))

# TODO: Display Prediction
if uploaded_file and response:
    result_code = response.status_code
    result_data = response.json()
    if result_code // 100 < 4:
        st.success("Prediction successful")
        response_result = response.json()
        group_list = [group_text[respond['prediction']] for respond in response_result]
        df1['GroupResult'] = group_list
        st.write(df1)
    else:
        st.error("Prediction failed")
