import sys
import os
import time
import json
import streamlit as st


ll_cont = True
lc_data_file = st.session_state["data_file"]

if not lc_data_file:
    print("Data file parameter missing.")
    ll_cont = False

if ll_cont and os.path.isfile(lc_data_file):
    try:
        lo_json_data=open(lc_data_file).read()
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
 
    if ll_cont:
        st.write("##### Add Player Page")
        lc_username = st.text_input("Player Name:")
        lc_commander = st.text_input("Commander:")
        lc_secondary_commander = st.text_input("Secondary Commander (if applicable):")

        lo_ic1, lo_ic2 = st.columns([1, 4])
        with lo_ic1:
            if st.button("Save"):
                ll_cont = False
                if not lc_username:
                    st.warning("Player name cannot be empty.")
                elif not lc_commander:
                    st.warning("Commander name cannot be empty.")
                elif lc_username in la_league_data["PLAYERS"]:
                    st.warning("Player already exists.")
                else:
                    lc_username = lc_username.strip()
                    lc_commander = lc_commander.strip()
                    lc_secondary_commander = lc_secondary_commander.strip()
                    la_league_data["PLAYERS"][lc_username] = {
                        "COMMANDER": lc_commander,
                        "SECONDARY_COMMANDER": lc_secondary_commander,
                        "SESSIONS": {}
                    }

                    try:
                        with open(lc_data_file, "w") as f:
                            json.dump(la_league_data, f, indent=4)

                        ll_cont = True

                    except Exception as e:
                        st.error("Error saving league data file: " + str(e))

                if ll_cont:
                    st.switch_page("main.py")

        with lo_ic2:
            if st.button("Cancel"):
                st.switch_page("main.py")

    else:
        st.write("Error loading league data.")
        time.sleep(3)
        st.switch_page("main.py")
