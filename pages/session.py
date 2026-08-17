import sys
import os
import time
import json
import random
import streamlit as st
from main import get_points
from main import save


def generate_pods(pc_session_id, pa_league_data, pa_selected_players):
    ln_round_number = 0
    for lc_check_round in pa_league_data["SESSIONS"][pc_session_id].keys():
        if int(lc_check_round.replace("Round ", "")) > ln_round_number:
            ln_round_number = int(lc_check_round.replace("Round ", ""))

    lc_round_id = "Round " + str(ln_round_number + 1)
    pa_league_data["SESSIONS"][pc_session_id][lc_round_id] = {}

    la_pods = {}
    ln_total_players = len(pa_selected_players)
    if ln_total_players <= 5:
        la_pods["Pod 1"] = pa_selected_players

    else:
        la_sorted_players = sort_players(pa_league_data, pa_selected_players, pc_session_id, lc_round_id)
        la_pod_sizes = get_pod_sizes(ln_total_players)
        for lc_pod in la_pod_sizes.keys():
            la_pods[lc_pod] = []
            for _ in range(la_pod_sizes[lc_pod]):
                lc_player = next(iter(la_sorted_players))
                la_pods[lc_pod].append(lc_player)
                del la_sorted_players[lc_player]

    for lc_pod_id in la_pods.keys():
        pa_league_data["SESSIONS"][pc_session_id][lc_round_id][lc_pod_id] = la_pods[lc_pod_id]

        for lc_player in la_pods[lc_pod_id]:
            if pc_session_id in pa_league_data["PLAYERS"][lc_player]["SESSIONS"].keys():
                if "ROUNDS" not in pa_league_data["PLAYERS"][lc_player]["SESSIONS"][pc_session_id]:
                    pa_league_data["PLAYERS"][lc_player]["SESSIONS"][pc_session_id]["ROUNDS"] = {}

                pa_league_data["PLAYERS"][lc_player]["SESSIONS"][pc_session_id]["ROUNDS"][lc_round_id] = 0
            else:
                pa_league_data["PLAYERS"][lc_player]["SESSIONS"][pc_session_id] = {"ROUNDS": {lc_round_id: 0}}

    return pa_league_data

def get_pod_sizes(pn_total_players):
    ln_pod_number = 1
    ln_remaining_players = pn_total_players
    la_pod_sizes = {}
    while ln_remaining_players > 9:
        la_pod_sizes["Pod " + str(ln_pod_number)] = 4
        ln_remaining_players -= 4
        ln_pod_number += 1

    if ln_remaining_players % 4 == 0:
        while ln_remaining_players > 0:
            la_pod_sizes["Pod " + str(ln_pod_number)] = 4
            ln_remaining_players -= 4
            ln_pod_number += 1

    elif ln_remaining_players % 3 == 0:
        while ln_remaining_players > 0:
            la_pod_sizes["Pod " + str(ln_pod_number)] = 3
            ln_remaining_players -= 3
            ln_pod_number += 1

    else:
        while ln_remaining_players > 0:
            la_pod_sizes["Pod " + str(ln_pod_number)] = min(4, ln_remaining_players)
            ln_remaining_players -= min(4, ln_remaining_players)
            ln_pod_number += 1

    return la_pod_sizes

def sort_players(pa_league_data, pa_selected_players, pc_session_id, pc_round_id):
    #-- Start with sorting by previous round points
    ln_round_number = int(pc_round_id.replace("Round ", ""))
    lc_round_id = "Round " + str(ln_round_number - 1)
    la_sorted_players = {}
    for lc_player in pa_selected_players:
        ln_rank = 0
        if pc_session_id in pa_league_data["PLAYERS"][lc_player]["SESSIONS"].keys() and lc_round_id in pa_league_data["PLAYERS"][lc_player]["SESSIONS"][pc_session_id]["ROUNDS"]:
            ln_rank = get_points(pa_league_data, lc_player, pc_session_id, lc_round_id) * 1000

        la_sorted_players[lc_player] = ln_rank

    la_sorted_players = dict(sorted(la_sorted_players.items(), key=lambda item: item[1], reverse=True))

    #-- Now apply adjustment to avoid players being in the same pod as last round
    la_adjustment_list = []
    la_adjustment_control_list = list(la_sorted_players.keys())
    for ln_loop in range(0, len(la_adjustment_control_list)):
        if ln_loop + 1 < len(la_adjustment_control_list):
            lc_player = la_adjustment_control_list[ln_loop]
            lc_check_player = la_adjustment_control_list[ln_loop + 1]

            if lc_round_id in pa_league_data["SESSIONS"][pc_session_id].keys():
                for lc_pod in pa_league_data["SESSIONS"][pc_session_id][lc_round_id].keys():
                    if lc_player in pa_league_data["SESSIONS"][pc_session_id][lc_round_id][lc_pod] and lc_check_player in pa_league_data["SESSIONS"][pc_session_id][lc_round_id][lc_pod]:
                        if lc_player not in la_adjustment_list:
                            la_sorted_players[lc_player] += 100
                            la_adjustment_list.append(lc_player)
                            la_adjustment_list.append(lc_check_player)

    la_sorted_players = dict(sorted(la_sorted_players.items(), key=lambda item: item[1], reverse=True))

    #-- Finally sort by total points
    #ln_player_count = 0
    for lc_player in la_sorted_players.keys():
        #ln_rank = la_sorted_players[lc_player]
        #ln_player_count += 1
        #if lc_round_id == "Round 0" or ln_player_count > 4:
        #    ln_rank += get_points(pa_league_data, lc_player)
        #    la_sorted_players[lc_player] = ln_rank
        la_sorted_players[lc_player] += get_points(pa_league_data, lc_player) + random.randint(1, 4)

    la_sorted_players = dict(sorted(la_sorted_players.items(), key=lambda item: item[1], reverse=True))

    return la_sorted_players

def apply_rares(pa_league_data, pc_session_id, pc_data_file):
    ll_cont = True
    la_sorted_players = {}
    for lc_round in pa_league_data["SESSIONS"][pc_session_id].keys():
        for lc_pod in pa_league_data["SESSIONS"][pc_session_id][lc_round].keys():
            for lc_player in pa_league_data["SESSIONS"][pc_session_id][lc_round][lc_pod]:
                if lc_player not in la_sorted_players:
                    la_sorted_players[lc_player] = get_points(pa_league_data, lc_player, pc_session_id)

    la_sorted_players = dict(sorted(la_sorted_players.items(), key=lambda item: item[1], reverse=True))
    ln_bucket_size = int(len(la_sorted_players)/3)

    ln_player_count = 0
    ln_point_cutoff1 = 0
    ln_point_cutoff2 = 0
    for lc_player in la_sorted_players.keys():
        ln_player_count += 1
        if ln_player_count == ln_bucket_size:
            ln_point_cutoff1 = la_sorted_players[lc_player]
        elif ln_player_count == ln_bucket_size * 2:
            ln_point_cutoff2 = la_sorted_players[lc_player]

    for lc_player in la_sorted_players.keys():
        if la_sorted_players[lc_player] > ln_point_cutoff1:
            pa_league_data["PLAYERS"][lc_player]["SESSIONS"][pc_session_id]["RARES"] = pa_league_data["MIN_RARES"]
        elif la_sorted_players[lc_player] > ln_point_cutoff2:
            pa_league_data["PLAYERS"][lc_player]["SESSIONS"][pc_session_id]["RARES"] = pa_league_data["MID_RARES"]
        else:
            pa_league_data["PLAYERS"][lc_player]["SESSIONS"][pc_session_id]["RARES"] = pa_league_data["MAX_RARES"]

    for lc_player in pa_league_data["PLAYERS"].keys():
        if lc_player not in la_sorted_players.keys():
            if pc_session_id not in pa_league_data["PLAYERS"][lc_player]["SESSIONS"]:
                pa_league_data["PLAYERS"][lc_player]["SESSIONS"][pc_session_id] = {}

            pa_league_data["PLAYERS"][lc_player]["SESSIONS"][pc_session_id]["RARES"] = pa_league_data["MIN_RARES"]

    ll_cont = save(pc_data_file, pa_league_data)

    return ll_cont


ll_cont = True
lc_error_message = ""
if "data_file" in st.session_state:
    lc_data_file = st.session_state["data_file"]

    if os.path.isfile(lc_data_file):
        try:
            lo_json_data=open(lc_data_file).read()
            la_league_data = json.loads(lo_json_data)
        except Exception as e:
            print("Error reading league data file: " + str(e))
            lc_error_message = "Error reading league data file!"
            ll_cont = False

    else:
        lc_error_message = "Unable to find league data file: " + lc_data_file
        ll_cont = False

else:
    lc_error_message = "Data file parameter missing!"
    ll_cont = False

if ll_cont:
    if "session_id" in st.session_state:
        lc_session_id = st.session_state["session_id"]
    else:
        lc_error_message = "Session ID parameter missing!"
        ll_cont = False

if ll_cont:
    if "default_checkboxes" in st.session_state:
        ll_default_checkboxes = st.session_state["default_checkboxes"]
    else:
        ll_default_checkboxes = False

    st.session_state["default_checkboxes"] = False
    ll_admin_login = False
    if "admin_login" in st.session_state:
        ll_admin_login = st.session_state["admin_login"]

    lc_league_name = os.path.basename(lc_data_file).upper()
    lc_league_name = lc_league_name[0:lc_league_name.find("_")]

    #-- Set layout and header columns
    st.set_page_config(layout="wide")
    st.markdown("""
        <style>
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)        

    lo_hc1, lo_hc2, lo_hc3, lo_hc4 = st.columns([2, 6, 1, 2])
    lo_hc2.write("")
    lo_hc2.markdown("<center><h2>" + lc_league_name + " Commander League</h2></center>", unsafe_allow_html=True)
    if lo_hc3.button("Home"):
        st.session_state["session_id"] = ""
        st.switch_page("main.py")

    lo_hc1, lo_hc2, lo_hc3, lo_hc4 = st.columns([2, 3, 3, 2])

    with lo_hc2:
        lc_display_session = lc_session_id[4:6] + "/" + lc_session_id[6:8] + "/" + lc_session_id[0:4]
        st.write("")
        lo_ic1, lo_ic2 = st.columns([3, 2])
        lo_ic1.write("##### Players for session " + lc_display_session + ":")

        with lo_ic2:
            if ll_admin_login:
                ll_apply_rares = True
                ln_total_points = 0
                for lc_player in la_league_data["PLAYERS"].keys():
                    ln_total_points += get_points(la_league_data, lc_player, lc_session_id)

                if ln_total_points == 0:
                    ll_apply_rares = False

                if ll_apply_rares:
                    if st.button("Apply Rares", key="rares_button"):
                        if apply_rares(la_league_data, lc_session_id, lc_data_file):
                            st.rerun()
                        else:
                            st.error("Failed to apply rares.")

        la_selected_players = []
        la_include = {}
        if len(la_league_data["SESSIONS"][lc_session_id].keys()) > 0:
            lc_latest_round = max(la_league_data["SESSIONS"][lc_session_id].keys())
        else:
            ll_default_checkboxes = False

        la_sorted_players_points = {}
        for lc_player in la_league_data["PLAYERS"].keys():
            la_sorted_players_points[lc_player] = get_points(la_league_data, lc_player, lc_session_id)

        la_sorted_players_points = dict(sorted(la_sorted_players_points.items(), key=lambda item: (-item[1], item[0])))

        lo_ic1, lo_ic2, lo_ic3, lo_ic4 = st.columns([2, 1, 1, 2])
        lo_ic1.write("Player")
        lo_ic2.write("Session Points")
        lo_ic3.write("Rares")

        for lc_player in la_sorted_players_points.keys():
            la_include[lc_player] = False
            if ll_default_checkboxes:
                for lc_pod in la_league_data["SESSIONS"][lc_session_id][lc_latest_round].keys():
                    if lc_player in la_league_data["SESSIONS"][lc_session_id][lc_latest_round][lc_pod]:
                        la_include[lc_player] = True
                        st.session_state[f"la_include['{lc_player}']"] = True
                        break

            lo_ic1, lo_ic2, lo_ic3, lo_ic4 = st.columns([2, 1, 1, 2])

            with lo_ic1:
                if ll_admin_login:
                    if st.checkbox(lc_player, key=f"la_include['{lc_player}']"):
                        if lc_player not in la_selected_players:
                            la_selected_players.append(lc_player)
                    else:
                        if lc_player in la_selected_players:
                            la_selected_players.remove(lc_player)

                else:
                    st.write(lc_player)

            lo_ic2.write(str(la_sorted_players_points[lc_player]))

            ln_rares = 0
            if lc_session_id in la_league_data["PLAYERS"][lc_player]["SESSIONS"] and "RARES" in la_league_data["PLAYERS"][lc_player]["SESSIONS"][lc_session_id]:
                ln_rares = la_league_data["PLAYERS"][lc_player]["SESSIONS"][lc_session_id]["RARES"]

            lo_ic3.write(str(ln_rares))

        st.write("")
        st.write("")

    with lo_hc3:
        st.write("")
        st.write("##### Pod List:")

        lc_max_round = 0
        if lc_session_id in la_league_data["SESSIONS"] and len(la_league_data["SESSIONS"][lc_session_id].keys()) > 0:
            lc_max_round = max(la_league_data["SESSIONS"][lc_session_id].keys())

        for lc_round_id in la_league_data["SESSIONS"][lc_session_id]:
            st.write("")
            with st.container(border=True):
                st.write(lc_round_id)
                for lc_pod_id in la_league_data["SESSIONS"][lc_session_id][lc_round_id].keys():
                    lc_players = ""
                    for lc_player in la_league_data["SESSIONS"][lc_session_id][lc_round_id][lc_pod_id]:
                        ln_points = get_points(la_league_data, lc_player, lc_session_id, lc_round_id)
                        lc_players += lc_player + " (" + str(ln_points) + "), "

                    lc_players = lc_players.rstrip(", ") + ""

                    st.write(lc_pod_id + ": " + lc_players)

                lo_ic1, lo_ic2 = st.columns([1, 4])
                if ll_admin_login:
                    if lo_ic1.button("Points", key=f"points_{lc_round_id}"):
                        #st.session_state["session_id"] = lc_session_id
                        st.session_state["round_id"] = lc_round_id
                        st.switch_page("pages/points.py")

                    if lc_round_id == lc_max_round:
                        if lo_ic2.button("Delete Round", key=f"delete_{lc_round_id}"):
                            for lc_player in la_league_data["PLAYERS"].keys():
                                if lc_session_id in la_league_data["PLAYERS"][lc_player]["SESSIONS"].keys() and "ROUNDS" in la_league_data["PLAYERS"][lc_player]["SESSIONS"][lc_session_id] and lc_round_id in la_league_data["PLAYERS"][lc_player]["SESSIONS"][lc_session_id]["ROUNDS"].keys():
                                    del la_league_data["PLAYERS"][lc_player]["SESSIONS"][lc_session_id]["ROUNDS"][lc_round_id]

                            if lc_round_id in la_league_data["SESSIONS"][lc_session_id]:
                                del la_league_data["SESSIONS"][lc_session_id][lc_round_id]

                            ll_cont = save(lc_data_file, la_league_data)

                            if ll_cont:
                                st.rerun()

        if len(la_selected_players) > 5:
            lc_pods = "Pods"
        else:
            lc_pods = "Pod"

        if ll_admin_login:
            ll_gen_pods_disabled = False
            if len(la_selected_players) < 1:
                ll_gen_pods_disabled = True

            if st.button("Generate " + lc_pods, disabled=ll_gen_pods_disabled):
                la_league_data = generate_pods(lc_session_id, la_league_data, la_selected_players)

                ll_cont = save(lc_data_file, la_league_data)

                if ll_cont:
                    st.rerun()

        st.write("")
        st.write("")

else:
    st.error(lc_error_message)
    time.sleep(3)
    st.switch_page("main.py")
