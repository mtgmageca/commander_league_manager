import sys
import os
import json
from datetime import datetime
import urllib.parse
import streamlit as st


def get_points(pa_league_data, pc_player, pc_session_id="", pc_round_id=""):
    ln_points = 0
    if pc_session_id:
        if pc_round_id:
            if pc_session_id in pa_league_data["PLAYERS"][pc_player]["SESSIONS"].keys() and pc_round_id in pa_league_data["PLAYERS"][pc_player]["SESSIONS"][pc_session_id]["ROUNDS"].keys():
                ln_points = pa_league_data["PLAYERS"][pc_player]["SESSIONS"][pc_session_id]["ROUNDS"][pc_round_id]

        else:
            if pc_session_id in pa_league_data["PLAYERS"][pc_player]["SESSIONS"].keys():
                if "ROUNDS" in pa_league_data["PLAYERS"][pc_player]["SESSIONS"][pc_session_id].keys():
                    for lc_round_id in pa_league_data["PLAYERS"][pc_player]["SESSIONS"][pc_session_id]["ROUNDS"].keys():
                        ln_points += pa_league_data["PLAYERS"][pc_player]["SESSIONS"][pc_session_id]["ROUNDS"][lc_round_id]

    else:
        for lc_session_id in pa_league_data["PLAYERS"][pc_player]["SESSIONS"].keys():
            if "ROUNDS" in pa_league_data["PLAYERS"][pc_player]["SESSIONS"][lc_session_id].keys():
                for lc_round_id in pa_league_data["PLAYERS"][pc_player]["SESSIONS"][lc_session_id]["ROUNDS"].keys():
                    ln_points += pa_league_data["PLAYERS"][pc_player]["SESSIONS"][lc_session_id]["ROUNDS"][lc_round_id]

    return ln_points


def main(pc_data_file):
    ll_cont = True
    if os.path.isfile(pc_data_file):
        try:
            lo_json_data=open(pc_data_file).read()
            la_league_data = json.loads(lo_json_data)
        except Exception as e:
            print("Error reading league data file: " + str(e))
            ll_cont = False

    else:
        print("Unable to find league data file: " + pc_data_file)
        ll_cont = False

    if ll_cont:
        st.session_state["data_file"] = pc_data_file
        #la_query_params = st.query_params

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

        lc_session_id = ""
        #if "session_id" in la_query_params:
        #    lc_session_id = la_query_params["session_id"]

        if "session_id" in st.session_state:
            lc_session_id = st.session_state["session_id"]

        lc_league_name = os.path.basename(pc_data_file).upper()
        lc_league_name = lc_league_name[0:lc_league_name.find("_")]
        st.write("")
        st.write("")
        st.write("")
        st.markdown("<center><h2>" + lc_league_name + " Commander League</h2></center>", unsafe_allow_html=True)
        if lc_session_id:
            st.markdown('<center><a href="/?session_id=" target="_self">(Home)</a></center>', unsafe_allow_html=True)

        lo_hc1, lo_hc2, lo_hc3, lo_hc4 = st.columns([2, 5, 2, 2])

        #-- Default View
        with lo_hc2:
            st.write("")
            lo_ic1, lo_ic2 = st.columns([1, 5])
            lo_ic1.write("##### Player List:")

            with lo_ic2:
                if st.button("Add Player"):
                    st.switch_page("pages/add_player.py")

            if len(la_league_data["PLAYERS"].keys()) > 0:
                lc_html_table = "<table><tr><th>Player</th><th>Commander</th><th>Points</th><th>Total Rares</th></tr>"
                la_sorted_list = {}
                for lc_player in la_league_data["PLAYERS"].keys():
                    ln_points = get_points(la_league_data, lc_player)

                    lc_commander = la_league_data["PLAYERS"][lc_player]["COMMANDER"]
                    if la_league_data["PLAYERS"][lc_player]["SECONDARY_COMMANDER"]:
                        lc_commander += " / " + la_league_data["PLAYERS"][lc_player]["SECONDARY_COMMANDER"]

                    la_sorted_list[lc_player] = {"POINTS": ln_points, "COMMANDER": lc_commander}

                la_sorted_list = dict(sorted(la_sorted_list.items(), key=lambda item: (-item[1]["POINTS"], item[0])))

                for lc_player in la_sorted_list.keys():
                    ln_total_rares = la_league_data["INITIAL_RARES"]
                    for lc_session_id in la_league_data["PLAYERS"][lc_player]["SESSIONS"].keys():
                        if "RARES" in la_league_data["PLAYERS"][lc_player]["SESSIONS"][lc_session_id]:
                            ln_total_rares += la_league_data["PLAYERS"][lc_player]["SESSIONS"][lc_session_id]["RARES"]

                    lc_html_table += "<tr><td>" + lc_player + "</td><td>" + la_sorted_list[lc_player]["COMMANDER"] + "</td><td>" + str(la_sorted_list[lc_player]["POINTS"]) + "</td><td>" + str(ln_total_rares) + "</td></tr>"
                    #lo_ic1, lo_ic2 = st.columns([1, 3])
                    #lo_ic1.write(lc_player + " (" + str(la_sorted_list[lc_player]["POINTS"]) + ")")
                    #lo_ic2.write(la_sorted_list[lc_player]["COMMANDER"])

                lc_html_table += "</table>"
                st.markdown(lc_html_table, unsafe_allow_html=True)

            else:
                st.write("No players found.")

            st.write("")
            st.write("")

        with lo_hc3:
            st.write("")
            lo_ic1, lo_ic2 = st.columns([1, 6])
            with lo_ic2:
                st.write("##### Session List:")
                if len(la_league_data["SESSIONS"]) > 0:
                    for lc_session_id in la_league_data["SESSIONS"].keys():
                        #lc_session_link = '<a href="./?session_id=' + lc_session_id + '" target="_self">' + lc_session_id[4:6] + '/' + lc_session_id[6:8] + '/' + lc_session_id[0:4] + '</a>'
                        #st.markdown(lc_session_link, unsafe_allow_html=True)
                        lc_display_session = lc_session_id[4:6] + '/' + lc_session_id[6:8] + '/' + lc_session_id[0:4]
                        if st.button(lc_display_session):
                            st.session_state["session_id"] = lc_session_id
                            st.session_state["default_checkboxes"] = True
                            st.switch_page("pages/session.py")

                else:
                    st.write("No sessions found.")

                if st.button("Add Session"):
                    lc_current_date = datetime.now().strftime("%Y%m%d")
                    if lc_current_date in la_league_data["SESSIONS"].keys():
                        st.warning("Session for the current date already exists.")
                    else:
                        la_league_data["SESSIONS"][lc_current_date] = {}
                        st.session_state["session_id"] = lc_current_date

                        try:
                            with open(pc_data_file, "w") as f:
                                json.dump(la_league_data, f, indent=4)

                        except Exception as e:
                            st.error("Error saving league data file: " + str(e))

                        st.rerun()

    if ll_cont:
        ln_return_code = 0
    else:
        ln_return_code = 1

    return ln_return_code


#-- Call Main program
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("%s:  Error: %s\n" % (sys.argv[0], "Not enough command options given"))
        print("Argument 1 (required): League data file (e.g. C:\\temp\\MSH_data.json)")
        print(" ")
        sys.exit(3)
    else:
        pc_data_file = sys.argv[1]
        ln_exit_code = main(pc_data_file)

        sys.exit(ln_exit_code)
