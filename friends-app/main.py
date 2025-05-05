import streamlit as st

st.set_page_config(
    page_title='Our Awsome App',
    page_icon='👋',
)

st.write("# Welcome to Our Awsome App! 👋")

st.sidebar.success("Select your usage above.")

st.markdown(
    """
    Our awsome app is an app that allows you to predict whether you will fit in with 
    a certain group based on social media post.
    **👈 Select a demo from the sidebar** to see some use cases
    of our app!
    ### Dataset
    - [Students' Social Network Profile 
    Clustering](https://www.kaggle.com/datasets/zabihullah18/students-social-network-profile-clustering)
    
"""
)

GROUP_TEXT = {
    0: '17 year old, have few friends, rarely post about dance, music, god',
    1: '17 year old or younger, have a lot of friends (50-80), post about music, god',
    2: '17-18 year old, super popular (150+ friends), post about music, god the most, most likely female',
    3: '17 year old, have a bit of friends (20-30), post about music more than everyone',
    4: 'Funny, trolling group',
    5: '17-18 year old, very popular (80-150), post about dance, music, most likely female',
    6: '17 year old, have big group of friends (30-50), post about music, god',
}

SERVER_URL = "http://127.0.0.1"
SERVER_PORT = "8000"
BASE_URL = SERVER_URL + ":" + SERVER_PORT

if 'group_meaning' not in st.session_state:
    st.session_state['group_meaning'] = GROUP_TEXT
if 'base_url' not in st.session_state:
    st.session_state['base_url'] = BASE_URL
