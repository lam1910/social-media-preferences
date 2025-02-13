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