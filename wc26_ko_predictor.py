# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 22:53:22 2026

@author: matta
"""
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def send_to_google(pred_df, player,penalty_match_ids):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    #creds = Credentials.from_service_account_file(
    #    "divine-builder-498621-p4-c83fc60642e8.json",
    #    scopes=scope
    #)
    creds_dict = st.secrets["google"]
    creds = Credentials.from_service_account_info(creds_dict,scopes=scope)
    
    client = gspread.authorize(creds)
    sh = client.open("World_Cup_26_KO_Predictor")
    try:
        worksheet = sh.add_worksheet(title=player, rows=100, cols=20)
    except gspread.exceptions.APIError:
        # If sheet already exists, open it instead
        worksheet = sh.worksheet(ko_player)
        
    # Write the DataFrame to the sheet
    worksheet.update("A1", [["Player"]])
    worksheet.update("B1", [[player]])
    # 3rd finalist
    worksheet.update("A2", [["3rd Finalist"]])
    worksheet.update("B2", [[third_final]])
    # Penalties
    worksheet.update("A3", [["Penalty Shootouts"]])
    worksheet.update("B3", [[", ".join(map(str, penalty_match_ids))]])

    #worksheet.update([pred_df.columns.values.tolist()] + pred_df.values.tolist())
    worksheet.update("A4", [pred_df.columns.tolist()])
    worksheet.update("A5", pred_df.values.tolist())

st.title("World Cup Knockouts Predictor App")

ko_player = st.text_input("PLAYER NAME:", placeholder="Type your name here")

st.markdown("""
#### 📝 Instructions

Pick your **Knockout Bracket** for the rest of the tournament. Go through each tab and pick your winners and your Penalty Shootout matches!
There are still lots of points up for grabs so plenty of time to catch the front runners!

#### 🏆 Points System

Points are awarded for every correct pick:
- **3 points** for each correct Round of 32 winner
- **4 points** for each correct Round of 16 winner
- **6 points** for each Quarter Final winner
- **8 points** for each Semi Final winner 
- **6 points** for 3rd Place Playoff winner
- **12 points** for Final winner (**can** be different from your pick during the Group Stage, these are separate from each other)

- Select 3 games you think will have a **Penalty Shootout** - **5 points** for each correct game
- **6 points** are available for a "3rd Finalist" - an extra team you think might make the final that you haven't picked to make it
""")


st.write("Enter your predictions below")
st.write("Once Predictions are complete, hit the below button")

@st.cache_data
def load_sheet_tab(sheet_name, tab_name):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = st.secrets["google"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    
    client = gspread.authorize(creds)
    
    # Open the Google Sheet
    sheet = client.open(sheet_name)

    # Select the tab (worksheet)
    worksheet = sheet.worksheet(tab_name)

    # Convert to DataFrame
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    return df

fixtures = load_sheet_tab("World_Cup_26_KO_Predictor", "KO_Fixtures")
ko_teams = load_sheet_tab("World_Cup_26_KO_Predictor", "KO_Dict")

#fixtures = pd.read_excel(r"C:\Users\matta\OneDrive\Documents\Matt's Stuff\Footy\World Cup 2026\WC2026_Scoreboard.xlsx",sheet_name="KO_Fixtures")
#ko_teams = pd.read_excel(r"C:\Users\matta\OneDrive\Documents\Matt's Stuff\Footy\World Cup 2026\WC2026_Scoreboard.xlsx",sheet_name="KO_Dict")

ko_dict = ko_teams.set_index(ko_teams.columns[0])[ko_teams.columns[1]].to_dict()

options = ["Select Team"] + sorted(ko_dict.values())
third_final = st.selectbox("Choose 3rd Finalist", options)
if third_final != "Select Team":
    st.session_state[f"{third_final}"] = third_final
    
EXPECTED = {
    "R32": [str(m) for m in range(73, 89)],   # 16 matches
    "R16": [str(m) for m in range(89, 97)],   # 8 matches
    "QF":  [f"QF{i}" for i in range(1, 5)],   # 4 matches
    "SF":  [f"SF{i}" for i in range(1, 3)],   # 2 matches
    "3RD": ["3RD"],                           # 1 match
    "FINAL": ["FINAL"],                          # 1 match
}

def missing_picks():
    missing = []

    for round_name, matches in EXPECTED.items():
        for match_id in matches:
            key = f"winner_{match_id}"
            if key not in st.session_state:
                missing.append(f"{round_name} – Match {match_id}")

    return missing

def handle_submit():
    # 0. Check player name
    if not ko_player or ko_player.strip() == "":
        st.error("Please enter your player name.")
        return
    missing = missing_picks()

    if missing:
        st.error("You still have matches to pick:")
        for m in missing:
            st.write(f"• {m}")
        return  # <-- NOT st.stop()

    if "penalty_picks" not in st.session_state or len(st.session_state["penalty_picks"]) != 3:
        st.error("Please select exactly 3 matches that will go to penalties.")
        return
    
    if third_final not in st.session_state:
        st.error("Please choose a 3rd Place Finalist.")
        return

    send_to_google(st.session_state["pred_df"], ko_player,st.session_state["penalty_picks"])
    st.success("Submitted! Good luck!")

if st.button("Submit Predictions"):
    handle_submit()
    
FLAG_URLS = {
    "Mexico": "https://flagcdn.com/w40/mx.png",
    "South Africa": "https://flagcdn.com/w40/za.png",
    "Czechia": "https://flagcdn.com/w40/cz.png",
    "Korea Republic": "https://flagcdn.com/w40/kr.png",
    "Canada": "https://flagcdn.com/w40/ca.png",
    "Bosnia and Herzegovina": "https://flagcdn.com/w40/ba.png",
    "Qatar": "https://flagcdn.com/w40/qa.png",
    "Switzerland": "https://flagcdn.com/w40/ch.png",
    "Haiti": "https://flagcdn.com/w40/ht.png",
    "Scotland": "https://flagcdn.com/w40/gb-sct.png",
    "Brazil": "https://flagcdn.com/w40/br.png",
    "Morocco": "https://flagcdn.com/w40/ma.png",
    "United States": "https://flagcdn.com/w40/us.png",
    "Paraguay": "https://flagcdn.com/w40/py.png",
    "Australia": "https://flagcdn.com/w40/au.png",
    "Türkiye": "https://flagcdn.com/w40/tr.png",
    "Ivory Coast": "https://flagcdn.com/w40/ci.png",
    "Ecuador": "https://flagcdn.com/w40/ec.png",
    "Germany": "https://flagcdn.com/w40/de.png",
    "Curaçao": "https://flagcdn.com/w40/cw.png",
    "Netherlands": "https://flagcdn.com/w40/nl.png",
    "Japan": "https://flagcdn.com/w40/jp.png",
    "Sweden": "https://flagcdn.com/w40/se.png",
    "Tunisia": "https://flagcdn.com/w40/tn.png",
    "Iran": "https://flagcdn.com/w40/ir.png",
    "New Zealand": "https://flagcdn.com/w40/nz.png",
    "Belgium": "https://flagcdn.com/w40/be.png",
    "Egypt": "https://flagcdn.com/w40/eg.png",
    "Saudi Arabia": "https://flagcdn.com/w40/sa.png",
    "Uruguay": "https://flagcdn.com/w40/uy.png",
    "Spain": "https://flagcdn.com/w40/es.png",
    "Cape Verde": "https://flagcdn.com/w40/cv.png",
    "France": "https://flagcdn.com/w40/fr.png",
    "Senegal": "https://flagcdn.com/w40/sn.png",
    "Iraq": "https://flagcdn.com/w40/iq.png",
    "Norway": "https://flagcdn.com/w40/no.png",
    "Argentina": "https://flagcdn.com/w40/ar.png",
    "Algeria": "https://flagcdn.com/w40/dz.png",
    "Austria": "https://flagcdn.com/w40/at.png",
    "Jordan": "https://flagcdn.com/w40/jo.png",
    "Portugal": "https://flagcdn.com/w40/pt.png",
    "DR Congo": "https://flagcdn.com/w40/cd.png",
    "Uzbekistan": "https://flagcdn.com/w40/uz.png",
    "Colombia": "https://flagcdn.com/w40/co.png",
    "Ghana": "https://flagcdn.com/w40/gh.png",
    "Panama": "https://flagcdn.com/w40/pa.png",
    "England": "https://flagcdn.com/w40/gb-eng.png",
    "Croatia": "https://flagcdn.com/w40/hr.png"
}


def team_label(team):
    url = FLAG_URLS.get(team, "")
    return f"<img src='{url}' width='25' style='vertical-align:middle;'> {team}"

def resolve_team(code, loser=False):
    # 1. Slot code (1A, 2B, 3F)
    if isinstance(code, str) and code in ko_dict:
        return ko_dict[code]

    # 2. Knockout match IDs like "QF1", "SF2", "F1"
    if isinstance(code, str) and (
        code.startswith("QF") or 
        code.startswith("SF") or 
        code == "F"
    ):
        key = f"loser_{code}" if loser else f"winner_{code}"
        team = st.session_state.get(key)
        return team if team else f"Winner M{code}"

    # 3. Real team name (USA, Germany, Brazil)
    if isinstance(code, str) and not code.isdigit():
        return code

    # 4. Numeric match ID (74, "74")
    try:
        match_id = int(code)
        key = f"loser_{match_id}" if loser else f"winner_{match_id}"
        team = st.session_state.get(key)
        return team if team else f"Winner M{match_id}"
    except:
        pass

    # 5. Fallback
    return f"Winner M{code}"


#("Pick a '3rd Finalist':", placeholder="Pick your Team")

rounds = {r: g for r, g in fixtures.groupby("Round")}
round_order = [
    "Round Of 32",
    "Round Of 16",
    "Quarter Finals",
    "Semi Finals",
    "3rd Place Final",
    "Final",
    "Penalty Shootout Picks"
]
tabs = st.tabs(round_order)
tab_r32, tab_r16, tab_qf, tab_sf, tab_third,tab_final,tab_pens = tabs
fixtures["Team A"] = fixtures["Team A"].replace(ko_dict)
fixtures["Team B"] = fixtures["Team B"].replace(ko_dict)

predictions = []

with tab_r32:
    st.subheader("Round of 32 – 3pts each")

    r32_df = fixtures[fixtures["Round"] == "R32"]

    for _, row in r32_df.iterrows():
        match_id = row["Match"]
        team_a = resolve_team(row["Team A"])
        team_b = resolve_team(row["Team B"])

        st.markdown(f"**Match {match_id}**")
        st.markdown(
            f"#### {team_label(team_a)} vs {team_label(team_b)}",
            unsafe_allow_html=True
            )

        result = st.segmented_control(
            label="Select winner",
            options=[team_a, team_b],
            key=f"r32_{match_id}"
        )

        if result is not None:
            st.session_state[f"winner_{match_id}"] = result
        prediction_complete = result is not None
        
        if prediction_complete:
            predictions.append({
                "Match":match_id,
                "Round":"R32",
                "Team A":team_a,
                "Team B":team_b,
                "Result":result,
                "Grp_Pos": ", ".join([key for key, val in ko_dict.items() if val == result]),
                "M_Pos":match_id
                })
        

with tab_r16:
    st.subheader("Round of 16 – 4pts each")

    r16_pairs = [
        (74, 77),
        (73, 75),
        (76, 78),
        (79, 80),
        (83, 84),
        (81, 82),
        (86, 88),
        (85, 87),
    ]

    r16_match_ids = list(fixtures[fixtures["Round"] == "R16"]["Match"])

    for (m1, m2), match_id in zip(r16_pairs, r16_match_ids):
        team_a = resolve_team(m1)
        team_b = resolve_team(m2)

        st.markdown(f"**Match {match_id}**")
        st.markdown(
            f"#### {team_label(team_a)} vs {team_label(team_b)}",
            unsafe_allow_html=True
            )

        result = st.segmented_control(
            label="Select winner",
            options=[team_a, team_b],
            key=f"r16_{match_id}"
        )

        if result is not None:
            st.session_state[f"winner_{match_id}"] = result
        prediction_complete = result is not None
        
        if prediction_complete:
            predictions.append({
                "Match":match_id,
                "Round":"R16",
                "Team A":team_a,
                "Team B":team_b,
                "Result":result,
                "Grp_Pos": ", ".join([key for key, val in ko_dict.items() if val == result]),
                "M_Pos":match_id
                })

with tab_qf:
    st.subheader("Quarter Finals – 6pts each")
    qf_pairs = [
        (89, 90),
        (93, 94),
        (91, 92),
        (95, 96),
    ]

    qf_match_ids = list(fixtures[fixtures["Round"] == "QF"]["Match"])

    for (m1, m2), match_id in zip(qf_pairs, qf_match_ids):
        team_a = resolve_team(m1)
        team_b = resolve_team(m2)

        st.markdown(f"**Match {match_id}**")
        st.markdown(
            f"#### {team_label(team_a)} vs {team_label(team_b)}",
            unsafe_allow_html=True
            )

        result = st.segmented_control(
            label="Select winner",
            options=[team_a, team_b],
            key=f"qf_{match_id}"
        )

        if result is not None:
            st.session_state[f"winner_{match_id}"] = result
        prediction_complete = result is not None
        
        if prediction_complete:
            predictions.append({
                "Match":match_id,
                "Round":"QF",
                "Team A":team_a,
                "Team B":team_b,
                "Result":result,
                "Grp_Pos": ", ".join([key for key, val in ko_dict.items() if val == result]),
                "M_Pos":match_id
                })

with tab_sf:
    st.subheader("Semi Finals – 8pts each")
    sf_pairs = [
        ("QF1", "QF2"),
        ("QF3", "QF4"),
    ]

    for i, (m1, m2) in enumerate(sf_pairs, start=1):
        match_id = f"SF{i}"   # <-- THIS IS THE FIX
        team_a = resolve_team(m1)
        team_b = resolve_team(m2)

        st.markdown(f"**Match {match_id}**")
        st.markdown(
            f"#### {team_label(team_a)} vs {team_label(team_b)}",
            unsafe_allow_html=True
            )

        result = st.segmented_control(
            label="Select winner",
            options=[team_a, team_b],
            key=f"sf_{match_id}"
        )

        if result is not None:
            st.session_state[f"winner_{match_id}"] = result
        
        if result == team_a:
            st.session_state[f"loser_{match_id}"] = team_b
        elif result == team_b:
            st.session_state[f"loser_{match_id}"] = team_a
        
        prediction_complete = result is not None
        
        if prediction_complete:
            predictions.append({
                "Match":match_id,
                "Round":"SF",
                "Team A":team_a,
                "Team B":team_b,
                "Result":result,
                "Grp_Pos": ", ".join([key for key, val in ko_dict.items() if val == result]),
                "M_Pos":match_id
                })

with tab_third:
    st.subheader("3rd Place Final – 6pts")
    third_pairs = [
        ("SF1", "SF2")
    ]

    third_match_ids = list(fixtures[fixtures["Round"] == "3F"]["Match"])

    for (m1, m2), match_id in zip(third_pairs, third_match_ids):
        team_a = resolve_team(m1,loser=True)
        team_b = resolve_team(m2,loser=True)

        st.markdown(f"**Match {match_id}**")
        st.markdown(
            f"#### {team_label(team_a)} vs {team_label(team_b)}",
            unsafe_allow_html=True
            )

        result = st.segmented_control(
            label="Select winner",
            options=[team_a, team_b],
            key=f"third_{match_id}"
        )

        if result is not None:
            st.session_state[f"winner_{match_id}"] = result
        prediction_complete = result is not None
        
        if prediction_complete:
            predictions.append({
                "Match":match_id,
                "Round":"3RD",
                "Team A":team_a,
                "Team B":team_b,
                "Result":result,
                "Grp_Pos": ", ".join([key for key, val in ko_dict.items() if val == result]),
                "M_Pos":match_id
                })

with tab_final:
    st.subheader("FINAL – 12pts")
    f_pairs = [
        ("SF1", "SF2")
    ]

    f_match_ids = list(fixtures[fixtures["Round"] == "F"]["Match"])

    for (m1, m2), match_id in zip(f_pairs, f_match_ids):
        team_a = resolve_team(m1)
        team_b = resolve_team(m2)

        st.markdown(f"**Match {match_id}**")
        st.markdown(
            f"#### {team_label(team_a)} vs {team_label(team_b)}",
            unsafe_allow_html=True
            )

        result = st.segmented_control(
            label="Select winner",
            options=[team_a, team_b],
            key=f"f_{match_id}"
        )

        if result is not None:
            st.session_state[f"winner_{match_id}"] = result
        prediction_complete = result is not None
        
        if prediction_complete:
            predictions.append({
                "Match":match_id,
                "Round":"FINAL",
                "Team A":team_a,
                "Team B":team_b,
                "Result":result,
                "Grp_Pos": ", ".join([key for key, val in ko_dict.items() if val == result]),
                "M_Pos":match_id
                })
        
import re

ORDER = {
    "NUM": 0,     # numeric matches 73–96
    "QF": 1,
    "SF": 2,
    "3RD": 3,
    "FINAL": 4,       # FINAL
    }

def match_sort_key(x):
    x = str(x)

    # Case 1: numeric match IDs (73–96)
    if x.isdigit():
        return (ORDER.get("NUM", 0), int(x))

    # Case 2: knockout match IDs (QF1, SF2, 3RD, F1, FINAL)
    m = re.match(r"([A-Za-z]+)(\d*)", x)
    if m:
        prefix, num = m.groups()
        num = int(num) if num.isdigit() else 0
        return (ORDER.get(prefix, 999), num)

    # Fallback
    return (999, 999)


pred_df = pd.DataFrame(predictions)
if pred_df.empty:
    pass
else:
    pred_df = pred_df.sort_values(
            by="Match",
            key=lambda col: col.map(match_sort_key)
            )

with tab_pens:
    st.subheader("Penalty Shootout Choices – 5pts")
    
    if pred_df.empty:
        pass
    else:
        pens = pred_df.copy()
        pens["label"] = pens.apply(
            lambda row: f"{row['Match']} – {row['Team A']} vs {row['Team B']}",
            axis=1
            )
        label_to_match = dict(zip(pens["label"], pens["Match"]))
        all_matches = pens["Match"].tolist()   # or fixtures["Match"]

        penalty_choices_labels = st.multiselect(
            "Select 3 matches you think will go to penalties",
            options=pens["label"].tolist(),
            max_selections=3
            )
        penalty_match_ids = [label_to_match[l] for l in penalty_choices_labels]
            
        st.session_state["penalty_picks"] = penalty_match_ids
        
        st.write(f"{penalty_match_ids}")


#sorted_list = sorted(my_list, key=custom_sort_key)


pred_df = pred_df.reset_index(drop=True)
st.session_state["pred_df"] = pred_df
if pred_df.empty:
    pass
else:
    st.write("Your predictions:")
    st.dataframe(pred_df)
