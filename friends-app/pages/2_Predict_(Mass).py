import streamlit as st
import pandas as pd

st.set_page_config(page_title="Predict (Mass)", page_icon="📝")
# TODO: Read and parse file
uploaded_file = st.file_uploader("Choose an excel file", type="xlsx")
if uploaded_file:
    df1 = pd.read_excel(uploaded_file)
    st.write(df1)
# TODO: Feed to API
# TODO: Display Prediction


# its going, not done yet