import streamlit as st
import requests
import pandas as pd
from urllib.parse import urlencode, urlunparse
import json

SERVER_URL = "http://127.0.0.1"
SERVER_PORT = "8000"
END_POINT = "predict"

GROUP_TEXT = {
    0: '17 year old, have few friends, rarely post about dance, music, god',
    1: '17 year old or younger, have a lot of friends (50-80), post about music, god',
    2: '17-18 year old, super popular (150+ friends), post about music, god the most, most likely female',
    3: '17 year old, have a bit of friends (20-30), post about music more than everyone',
    4: 'Funny, trolling group',
    5: '17-18 year old, very popular (80-150), post about dance, music, most likely female',
    6: '17 year old, have big group of friends (30-50), post about music, god',
}

st.set_page_config(page_title="Predict (User Input)", page_icon="✍️")

# TODO: create a form input
# Create a form
with st.form("my_form"):
    st.write("Some info about yourself")
    grad_year = st.number_input('What is your year grad?', min_value=2000, max_value=2020, step=1)
    gender = st.selectbox('What is your gender?', ['M', 'F', 'NA'])
    age = st.number_input('How old are you?', min_value=13, max_value=20, step=1)
    no_friends = st.number_input('How many friends do you have?', min_value=0, max_value=610, step=10)
    basketball = st.number_input('How many time did you post #basketball?', min_value=0, max_value=400, step=5)
    football = st.number_input('How many time did you post #football?', min_value=0, max_value=400, step=5)
    soccer = st.number_input('How many time did you post #soccer?', min_value=0, max_value=400, step=5)
    softball = st.number_input('How many time did you post #softball?', min_value=0, max_value=400, step=5)
    volleyball = st.number_input('How many time did you post #volleyball?', min_value=0, max_value=400, step=5)
    swimming = st.number_input('How many time did you post #swimming?', min_value=0, max_value=400, step=5)
    cheerleading = st.number_input('How many time did you post #cheerleading?', min_value=0, max_value=400, step=5)
    baseball = st.number_input('How many time did you post #baseball?', min_value=0, max_value=400, step=5)
    tennis = st.number_input('How many time did you post #tennis?', min_value=0, max_value=400, step=5)
    sports = st.number_input('How many time did you post #sports?', min_value=0, max_value=400, step=5)
    cute = st.number_input('How many time did you post #cute?', min_value=0, max_value=400, step=5)
    sex = st.number_input('How many time did you post #sex?', min_value=0, max_value=400, step=5)
    sexy = st.number_input('How many time did you post #sexy?', min_value=0, max_value=400, step=5)
    hot = st.number_input('How many time did you post #hot?', min_value=0, max_value=400, step=5)
    kissed = st.number_input('How many time did you post #kissed?', min_value=0, max_value=400, step=5)
    dance = st.number_input('How many time did you post #dance?', min_value=0, max_value=400, step=5)
    band = st.number_input('How many time did you post #band?', min_value=0, max_value=400, step=5)
    marching = st.number_input('How many time did you post #marching?', min_value=0, max_value=400, step=5)
    music = st.number_input('How many time did you post #music?', min_value=0, max_value=400, step=5)
    rock = st.number_input('How many time did you post #rock?', min_value=0, max_value=400, step=5)
    god = st.number_input('How many time did you post #god?', min_value=0, max_value=400, step=5)
    church = st.number_input('How many time did you post #church?', min_value=0, max_value=400, step=5)
    jesus = st.number_input('How many time did you post #jesus?', min_value=0, max_value=400, step=5)
    bible = st.number_input('How many time did you post #bible?', min_value=0, max_value=400, step=5)
    hair = st.number_input('How many time did you post #hair?', min_value=0, max_value=400, step=5)
    dress = st.number_input('How many time did you post #dress?', min_value=0, max_value=400, step=5)
    blonde = st.number_input('How many time did you post #blonde?', min_value=0, max_value=400, step=5)
    mall = st.number_input('How many time did you post #mall?', min_value=0, max_value=400, step=5)
    shopping = st.number_input('How many time did you post #shopping?', min_value=0, max_value=400, step=5)
    clothes = st.number_input('How many time did you post #clothes?', min_value=0, max_value=400, step=5)
    hollister = st.number_input('How many time did you post #hollister?', min_value=0, max_value=400, step=5)
    abercrombie = st.number_input('How many time did you post #abercrombie?', min_value=0, max_value=400, step=5)
    die = st.number_input('How many time did you post #die?', min_value=0, max_value=400, step=5)
    death = st.number_input('How many time did you post #death?', min_value=0, max_value=400, step=5)
    drunk = st.number_input('How many time did you post #drunk?', min_value=0, max_value=400, step=5)
    drugs = st.number_input('How many time did you post #drugs?', min_value=0, max_value=400, step=5)

    # To list of value
    person = dict(gradyear=grad_year, gender=gender, age=age, NumberOffriends=no_friends, basketball=basketball,
                  football=football, soccer=soccer, softball=softball, volleyball=volleyball, swimming=swimming,
                  cheerleading=cheerleading, baseball=baseball, tennis=tennis, sports=sports, cute=cute, sex=sex,
                  sexy=sexy, hot=hot, kissed=kissed, dance=dance, band=band, marching=marching, music=music, rock=rock,
                  god=god, church=church, jesus=jesus, bible=bible, hair=hair, dress=dress, blonde=blonde, mall=mall,
                  shopping=shopping, clothes=clothes, hollister=hollister, abercrombie=abercrombie, die=die,
                  death=death, drunk=drunk, drugs=drugs)


    # Every form must have a submit button
    submitted = st.form_submit_button('Submit')

# TODO: Feed to API
if submitted:
    url = SERVER_URL + ":" + SERVER_PORT + "/" + END_POINT
    response = requests.post(url, data=json.dumps({'features': [person]}))

# TODO: Display Prediction
if submitted and response:
    result_code = response.status_code
    result_data = response.json()
    if result_code // 100 < 4:
        st.success("Prediction successful")
        response_result = response.json()
        st.write('Person group: {}'.format(GROUP_TEXT[int(response_result['prediction'])]))
    else:
        st.error("Prediction failed")


