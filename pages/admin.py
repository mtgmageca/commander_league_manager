import sys
import os
import time
import json
import streamlit as st
from main import get_points


def generate_draft_order(pa_league_data):
    la_sorted_players = {}
    for lc_player, la_player_data in pa_league_data["PLAYERS"].items():
        ln_session_count = 0
        for lc_session in la_player_data["SESSIONS"].keys():
            if len(la_player_data["SESSIONS"][lc_session]["ROUNDS"]) > 0:
                ln_session_count += 1

        ln_rating = ln_session_count * 1000
        ln_rating += get_points(pa_league_data, lc_player)
        la_sorted_players[lc_player] = ln_rating

    #-- Sort players by rating
    la_sorted_players = sorted(la_sorted_players.items(), key=lambda x: x[1], reverse=True)

    lc_draft_order = "<center><h4>Draft Order</h4></center>"
    lc_draft_order += "<table style='margin-left:auto;margin-right:auto;'>"
    lc_draft_order += "<tr><th>Player</th><th>Rating</th></tr>"
    for la_player in la_sorted_players:
        lc_draft_order += "<tr><td>" + la_player[0] + "</td><td>" + str(la_player[1]) + "</td></tr>"
    lc_draft_order += "</table>"
    return lc_draft_order

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

    lc_draft_order = ""
    with lo_hc2:
        lo_ic1, lo_ic2, lo_ic3 = st.columns([1, 3, 2])
        st.write("")
        with lo_ic2:
            if st.button("Generate Draft Order"):
                lc_draft_order = generate_draft_order(la_league_data)

        with lo_ic3:
            if st.button("Home"):
                st.switch_page("main.py")

        st.markdown(lc_draft_order, unsafe_allow_html=True)

else:
    st.write("Error loading league data.")
    time.sleep(3)
    st.switch_page("main.py")
