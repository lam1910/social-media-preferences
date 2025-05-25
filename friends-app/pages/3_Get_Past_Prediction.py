import traceback
from datetime import datetime, timedelta
from io import StringIO

import streamlit as st
import pandas as pd
import requests

END_POINT = "past-predictions"

st.set_page_config(page_title="Past Predictions", page_icon="📒")
# Date input widgets
st.sidebar.markdown('### Select date range for returning predictions:')
tomorrow = datetime.now() + timedelta(days=1)
start_date = st.sidebar.date_input('From', '2025-03-01', min_value='2010-01-01', max_value='2030-01-01')
end_date = st.sidebar.date_input('To', tomorrow, min_value='2010-01-01', max_value='2030-01-01')

# TODO: get data from API and display
try:
    base_url = st.session_state['base_url']
    group_text = st.session_state['group_meaning']
    url = base_url + "/" + END_POINT
except KeyError as err:
    st.warning('It seems like you are bypassing the main page. Please return to the main page first')
    url = 'http://localhost:8000' + "/" + END_POINT
    st.error(traceback.format_exc())

try:
    response = requests.get(url)
    result_code = response.status_code
    result_data = response.json()
    if result_code // 100 < 4:
        st.success("Request successful")
        response_result = response.text
        # Wrap the string in a StringIO object
        response_result = StringIO(response_result)
        df_out = pd.read_json(response_result, orient='records')
        list_pred = df_out.loc[:, 'prediction'].to_list()
        list_group = [group_text[pred] for pred in list_pred]
        df_out['group'] = list_group
        # Convert 'insertion_timestamp' to datetime
        df_out['insertion_timestamp'] = pd.to_datetime(df_out['insertion_timestamp'])
        filtered_df = df_out.copy(deep=True)
        # Filter data based on date input
        try:
            filtered_df = filtered_df[(filtered_df['insertion_timestamp'] >= pd.to_datetime(start_date)) & (
                    filtered_df['insertion_timestamp'] <= pd.to_datetime(end_date))]
            filtered_df = filtered_df.reset_index(drop=True)
        except KeyError as k_err:
            st.warning('Something wrong with the output table. Please contact support.')
            st.warning(traceback.format_exc())
        except Exception as err:
            st.warning('Something wrong with the date range. Please check your range or contact support.')
            st.warning(traceback.format_exc())
        st.write(filtered_df)
    else:
        st.error("Request failed")
except Exception as e:
    st.warning("Server side error. Please contact admin.")
    st.error(e)
