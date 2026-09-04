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
        ll_edit = False
        if "edit" in st.session_state and st.session_state["edit"]:
            ll_edit = True

        lc_username = ""
        lc_original_username = ""
        lc_commander = ""
        lc_secondary_commander = ""
        if ll_edit:
            st.write("##### Edit Player Page")
            la_player_list = sorted(list(la_league_data["PLAYERS"].keys()))
            ln_index = 0
            if "selected_player" in st.session_state and st.session_state["selected_player"]:
                ln_index = la_player_list.index(st.session_state["selected_player"])

            lc_username = st.selectbox("Select Player to Edit:", options=la_player_list, index=ln_index)
            lc_original_username = lc_username
            lc_commander = la_league_data["PLAYERS"][lc_username]["COMMANDER"]
            lc_secondary_commander = la_league_data["PLAYERS"][lc_username]["SECONDARY_COMMANDER"]

        else:
            st.write("##### Add Player Page")

        with st.container(border=True):
            lc_username = st.text_input("Player Name:", value=lc_username)
            lc_commander = st.text_input("Commander:", value=lc_commander)
            lc_secondary_commander = st.text_input("Secondary Commander (if applicable):", value=lc_secondary_commander)

            lo_ic1, lo_ic2, lo_ic3 = st.columns([1, 2, 2])
            with lo_ic2:
                if st.button("Save"):
                    lc_username = lc_username.strip()
                    lc_commander = lc_commander.strip()
                    lc_secondary_commander = lc_secondary_commander.strip()
                    ll_cont = False

                    if not lc_username:
                        st.warning("Player name cannot be empty.")

                    elif not lc_commander:
                        st.warning("Commander name cannot be empty.")

                    elif lc_username in la_league_data["PLAYERS"] and lc_username != lc_original_username:
                        st.warning("Player already exists.")

                    else:
                        if lc_username != lc_original_username and lc_original_username in la_league_data["PLAYERS"]:
                            del la_league_data["PLAYERS"][lc_original_username]

                        la_league_data["PLAYERS"][lc_username] = {
                            "COMMANDER": lc_commander,
                            "SECONDARY_COMMANDER": lc_secondary_commander,
                            "SESSIONS": {}
                        }

                        ll_cont = save(lc_data_file, la_league_data)

                    if ll_cont:
                        st.session_state["selected_player"] = lc_username
                        time.sleep(1)
                        st.rerun()

            with lo_ic3:
                if st.button("Home"):
                    st.session_state["selected_player"] = ""
                    st.switch_page("main.py")

else:
    st.write("Error loading league data.")
    time.sleep(3)
    st.switch_page("main.py")
