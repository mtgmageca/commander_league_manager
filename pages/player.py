import sys
import os
import time
import json
import streamlit as st
from main import push_dat_file
from main import save


ll_cont = True
lc_data_file = st.session_state["data_file"]

if not lc_data_file:
    print("Data file parameter missing.")
    ll_cont = False

if ll_cont and os.path.isfile(lc_data_file):
    try:
        lo_json_data = open(lc_data_file).read()
        la_league_data = json.loads(lo_json_data)

    except Exception as e:
        print("Error reading league data file: " + str(e))
        ll_cont = False

else:
    print("Unable to find league data file: " + lc_data_file)
    ll_cont = False

if ll_cont:
    lc_league_name = os.path.basename(lc_data_file).upper()
    lc_league_name = lc_league_name[0:lc_league_name.find("_")]
    st.markdown("<center><h2>" + lc_league_name + " Commander League</h2></center>", unsafe_allow_html=True)

    lo_hc1, lo_hc2, lo_hc3 = st.columns([1, 1, 1])

    with lo_hc2:
        st.write("")
        lc_username = ""
        if "username" in st.session_state and st.session_state["username"]:
            lc_username = st.session_state["username"]

        lc_commander = ""
        if "commander" in st.session_state and st.session_state["commander"]:
            lc_commander = st.session_state["commander"]

        lc_secondary_commander = ""
        if "secondary_commander" in st.session_state and st.session_state["secondary_commander"]:
            lc_secondary_commander = st.session_state["secondary_commander"]

        if lc_username:
            st.write("##### Edit Player Page")
        else:
            st.write("##### Add Player Page")

        lc_username = st.text_input("Player Name:", value=lc_username)
        lc_commander = st.text_input("Commander:", value=lc_commander)
        lc_secondary_commander = st.text_input("Secondary Commander (if applicable):", value=lc_secondary_commander)

        lo_ic1, lo_ic2 = st.columns([1, 4])
        with lo_ic1:
            if st.button("Save"):
                lc_username = lc_username.strip()
                lc_commander = lc_commander.strip()
                lc_secondary_commander = lc_secondary_commander.strip()
                ll_cont = False

                if not lc_username:
                    st.warning("Player name cannot be empty.")

                elif not lc_commander:
                    st.warning("Commander name cannot be empty.")

                elif lc_username in la_league_data["PLAYERS"] and lc_username != st.session_state["username"]:
                    st.warning("Player already exists.")

                else:
                    if lc_username != st.session_state["username"] and st.session_state["username"] in la_league_data["PLAYERS"]:
                        del la_league_data["PLAYERS"][st.session_state["username"]]

                    la_league_data["PLAYERS"][lc_username] = {
                        "COMMANDER": lc_commander,
                        "SECONDARY_COMMANDER": lc_secondary_commander,
                        "SESSIONS": {}
                    }

                    ll_cont = save(lc_data_file, la_league_data)

                if ll_cont:
                    st.session_state["username"] = ""
                    st.session_state["commander"] = ""
                    st.session_state["secondary_commander"] = ""
                    st.switch_page("main.py")

        with lo_ic2:
            if st.button("Cancel"):
                st.session_state["username"] = ""
                st.session_state["commander"] = ""
                st.session_state["secondary_commander"] = ""
                st.switch_page("main.py")

else:
    st.write("Error loading league data.")
    time.sleep(3)
    st.switch_page("main.py")
