import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

backend_url = "https://script.google.com/macros/s/AKfycbwf3KjeOf3Ryg886hkfmS8Sl9FujlnXvwa2ki0JI-5C4wAdOjsnaZ_1Mx5101EF56XO1w/exec"

def load_data():
    try:
        response = requests.get(backend_url)
        if response.status_code == 200:
            result = response.json()
            if "data" in result:
                df = pd.DataFrame(result["data"], columns=("phoneNumber", "discountCode", "issueDate", "expirationTime"))
                df = df.sort_values("expirationTime", ascending=False)
                df["active"] = pd.to_datetime(df["expirationTime"]) > pd.to_datetime("now", unit="ns", utc=True)
                st.session_state.data = df
            elif "error" in result:
                st.error(f"{result["error"]}")
        else:
            st.error(f"Error calling back-end with status code {response.status_code}")
    except requests.RequestException as e:
        st.error(f"Error calling back-end: {e}")

tab1, tab2 = st.tabs(["List of codes", "Get a new code"])

with tab1:

    st.title("List of generated discount codes")

    if st.button("Refresh data"):
    	load_data()

    load_data()

    st.dataframe(st.session_state.data, column_config = {
            "phoneNumber": "Phone number",
            "discountCode": "Discount code",
            "issueDate": st.column_config.DateColumn("Issue date"),
            "expirationTime": st.column_config.DatetimeColumn("Expiration time"),
            "active": st.column_config.CheckboxColumn("Active")
        })

with tab2:

    st.title("Get a discount code")

    phone_number = st.text_input("User's phone number")

    if st.button("Get discount code"):
        try:
            response = requests.post(backend_url, json={"phoneNumber": phone_number})
            if response.status_code == 200:
                result = response.json()
                if "code" in result:
                    st.success(f"Discount code: {result["code"]}")
                elif "error" in result:
                    st.error(f"{result["error"]}")
            else:
                st.error(f"Error calling back-end with status code {response.status_code}")
        except requests.RequestException as e:
            st.error(f"Error calling back-end: {e}")
