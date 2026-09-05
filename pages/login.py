import sys
import os
import time
import json
import base64
import streamlit as st
from main import push_dat_file
from main import save


lc_data_file = st.session_state["data_file"]
lc_admin_user = st.secrets["ADMIN_USER"]
lc_admin_password = st.secrets["ADMIN_PASSWORD"]


st.markdown("<center><h2>Admin Login</h2></center>", unsafe_allow_html=True)

lo_hc1, lo_hc2, lo_hc3 = st.columns([1, 1, 1])

with lo_hc2:
    st.write("")

    with st.form("login_form"):
        lc_username = st.text_input("Admin User:")
        #lc_password = st.text_input("Password:")
        lc_password = st.text_input("Password:", type="password", autocomplete="current-password")

        lo_ic1, lo_ic2 = st.columns([1, 4])
        with lo_ic1:
            if st.form_submit_button("Login"):
                ll_cont = False
                if not lc_username:
                    st.warning("User name cannot be empty.")

                elif not lc_password:
                    st.warning("Password cannot be empty.")

                else:
                    lc_username = lc_username.strip()
                    lc_password = lc_password.strip()

                    lc_admin_user = ""
                    if "ADMIN_USER" in st.secrets:
                        lc_admin_user = st.secrets["ADMIN_USER"]

                    lc_admin_password = ""
                    if "ADMIN_PASSWORD" in st.secrets:
                        lc_admin_password = st.secrets["ADMIN_PASSWORD"]

                    if lc_admin_user and lc_admin_password and lc_admin_user == lc_username and lc_admin_password == lc_password:
                        st.session_state["admin_login"] = True
                        lc_admin_login = lc_username + ":" + lc_password
                        lc_admin_login = base64.b64encode(lc_admin_login.encode("utf-8")).decode("utf-8")
                        st.query_params["admin_login"] = lc_admin_login
                        print(st.query_params)
                        st.switch_page("main.py", query_params=st.query_params)

                    else:
                        st.warning("Invalid user name or password.")

        with lo_ic2:
            if st.form_submit_button("Cancel"):
                st.switch_page("main.py")
