import sys
import os
import time
import json
import streamlit as st
from main import get_points
from main import save


ll_cont = True
lc_data_file = st.session_state["data_file"]
lc_session_id = st.session_state["session_id"]
lc_round_id = st.session_state["round_id"]

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

lc_league_name = os.path.basename(lc_data_file).upper()
lc_league_name = lc_league_name[0:lc_league_name.find("_")]
st.markdown("<center><h2>" + lc_league_name + " Commander League</h2></center>", unsafe_allow_html=True)

if ll_cont:
    lo_hc1, lo_hc2, lo_hc3 = st.columns([1, 1, 1])

    with lo_hc2:
        st.write("")
        st.write("##### Points Page")
        st.write(lc_round_id)
        la_points = {}
        for lc_pod_id in la_league_data["SESSIONS"][lc_session_id][lc_round_id].keys():
            with st.container(border=True):
                st.write(lc_pod_id)
                for lc_player in la_league_data["SESSIONS"][lc_session_id][lc_round_id][lc_pod_id]:
                    ln_current_points = get_points(la_league_data, lc_player, lc_session_id, lc_round_id)

                    lo_ic1, lo_ic2, lo_ic3 = st.columns([2, 2, 1])
                    lo_ic1.write("- " + lc_player)
                    la_points[lc_player] = lo_ic2.number_input(lc_player, min_value=0, max_value=5, value=ln_current_points, label_visibility="collapsed")

        lo_ic1, lo_ic2 = st.columns([1, 4])
        with lo_ic1:
            if st.button("Save"):
                for lc_player in la_points.keys():
                    if lc_session_id not in la_league_data["PLAYERS"][lc_player]["SESSIONS"]:
                        la_league_data["PLAYERS"][lc_player]["SESSIONS"][lc_session_id] = {}

                    if "ROUNDS" not in la_league_data["PLAYERS"][lc_player]["SESSIONS"][lc_session_id]:
                        la_league_data["PLAYERS"][lc_player]["SESSIONS"][lc_session_id]["ROUNDS"] = {}

                    la_league_data["PLAYERS"][lc_player]["SESSIONS"][lc_session_id]["ROUNDS"][lc_round_id] = la_points[lc_player]

                ll_cont = save(lc_data_file, la_league_data)

                if ll_cont:
                    st.session_state["data_file"] = lc_data_file
                    st.session_state["session_id"] = lc_session_id
                    st.session_state["default_checkboxes"] = True
                    st.switch_page("pages/session.py")

        with lo_ic2:
            if st.button("Cancel"):
                st.session_state["data_file"] = lc_data_file
                st.session_state["session_id"] = lc_session_id
                st.session_state["default_checkboxes"] = True
                st.switch_page("pages/session.py")

else:
    st.write("Error loading league data.")
    time.sleep(3)
    st.switch_page("main.py")
