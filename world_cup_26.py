# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 19:11:43 2026

@author: matta
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def send_to_google(pred_df, player):
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
    sh = client.open("World_Cup_26_Predictor")
    try:
        worksheet = sh.add_worksheet(title=player, rows=100, cols=20)
    except gspread.exceptions.APIError:
        # If sheet already exists, open it instead
        worksheet = sh.worksheet(player)

    # Write the DataFrame to the sheet
    worksheet.update("A1", [["Tournament Winner"]])
    worksheet.update("B1", [[winner]])


    worksheet.update("A2", [["Golden Boot"]])
    worksheet.update("B2", [[golden]])

    #worksheet.update([pred_df.columns.values.tolist()] + pred_df.values.tolist())
    worksheet.update("A4", [pred_df.columns.tolist()])
    worksheet.update("A5", pred_df.values.tolist())


st.title("World Cup Prediction App")

player = st.text_input("PLAYER NAME:", placeholder="Type your name here")
winner = st.text_input("My World Cup Winner:", placeholder="Type Team here")
golden = st.text_input("Golden Boot Winner:", placeholder="Type your Player here")

st.write("Once Predictions are complete, hit the below button")

TOTAL_MATCHES = 72

pred_count = st.session_state.get("pred_count", 0)
all_groups_complete = pred_count == TOTAL_MATCHES

disabled = (
    not all_groups_complete or
    "pred_df" not in st.session_state
)

if st.button("Submit Predictions", disabled=disabled):
    send_to_google(st.session_state["pred_df"], player)
    st.success("Submitted! Good luck!")

st.write("Enter your predictions below")
    
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

def load_fixtures():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = st.secrets["google"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

    client = gspread.authorize(creds)
    sh = client.open("World_Cup_26_Predictor")

    worksheet = sh.worksheet("Fixtures")  # name of the tab
    data = worksheet.get_all_records()

    df = pd.DataFrame(data)
    return df

fixtures = load_fixtures()
#fixtures = pd.read_excel(r"C:\Users\matta\OneDrive\Documents\Matt's Stuff\Footy\World Cup 2026\FIFA_WC_26_Fixtures.xlsx")

groups = sorted(fixtures["Group"].unique())
teams = sorted(set(fixtures["Team A"]).union(fixtures["Team B"]))

def compute_group_table(matches):
    """
    matches: list of dicts with keys:
        'Team A', 'Team B', 'Result', 'Margin'
    """

    teams = sorted(set([m["Team A"] for m in matches] + 
                       [m["Team B"] for m in matches]))

    table = pd.DataFrame({
        "Team": teams,
        "P": 0, "W": 0, "D": 0, "L": 0,"GD": 0, "Pts": 0
    }).set_index("Team")

    for m in matches:
        A = m["Team A"]
        B = m["Team B"]
        result = m["Result"]
        margin = m["Margin"]

        if result == A:
            gd_A, gd_B = margin, -margin
            table.loc[A, "W"] += 1
            table.loc[B, "L"] += 1
            table.loc[A, "Pts"] += 3

        elif result == B:
            gd_A, gd_B = -margin, margin
            table.loc[B, "W"] += 1
            table.loc[A, "L"] += 1
            table.loc[B, "Pts"] += 3

        else:  # Draw
            gd_A = gd_B = 0
            table.loc[A, "D"] += 1
            table.loc[B, "D"] += 1
            table.loc[A, "Pts"] += 1
            table.loc[B, "Pts"] += 1

        # Update goals
        table.loc[A, "GD"] += gd_A
        table.loc[B, "GD"] += gd_B

        table.loc[A, "P"] += 1
        table.loc[B, "P"] += 1


    # Sort by points, GD, GF
    table = table.sort_values(
        by=["Pts", "GD"],
        ascending=[False, False]
    )

    return table.reset_index()

predictions = []

tabs = st.tabs([f"Group {g}" for g in groups])
group_tables = {}

for tab, group in zip(tabs, groups):
    with tab:
        st.subheader(f"Matches in Group {group}")
        group_df = fixtures[fixtures["Group"] == group]
        group_predictions = []
        match_status = []
        
        for i, row in group_df.iterrows():
        
            match_num = row['Match']
            st.markdown(
                f"### {team_label(row['Team A'])} vs {team_label(row['Team B'])}",
                unsafe_allow_html=True
                )

            # Result buttons
            result = st.segmented_control(
               label="Select result",
               options=[row["Team A"], "Draw", row["Team B"]],
               key=f"result_{group}_{i}"
               )

            if result == "Draw":
                margin = 0
                st.text('Margin - 0')
                margin_selected = True   # Draw requires no margin
            else:
                margin = st.segmented_control(
                    label="Margin of Victory",
                    options=[1, 2, 3, 4, 5, 6, 7],
                    key=f"margin_{group}_{i}"
                    )
                # Margin is only valid if user actually clicked something
                margin_selected = margin in [1,2,3,4,5,6,7]

            # --- ONLY ADD MATCH IF COMPLETE ---
            prediction_complete = (result is not None) and margin_selected
            match_status.append(prediction_complete)
            
            # --- BONUS CHECK ---
            bonus_key = f"bonus_{match_num}"

            # Only allow checking if fewer than 3 are selected OR this one is already selected
            current_selected = sum(
                1 for k, v in st.session_state.items() if k.startswith("bonus_") and v
                )

            disabled = current_selected >= 3 and not st.session_state.get(bonus_key, False)

            bonus = st.checkbox("Bonus Game", key=bonus_key, disabled=disabled)

            if prediction_complete:
                group_predictions.append({
                    "Team A": row["Team A"],
                    "Team B": row["Team B"],
                    "Result": result,
                    "Margin": margin
                })
                predictions.append({
                    "Match": match_num,
                    "Team A": row["Team A"],
                    "Team B": row["Team B"],
                    "Result": result,
                    "Margin": margin,
                    "Bonus": st.session_state.get(f"bonus_{match_num}",False)
                })
        
        # -------------------------
        # PROGRESS BAR
        # -------------------------
        total_matches = len(group_df)
        completed = sum(match_status)
            
        st.progress(completed / total_matches)
        st.caption(f"{completed} of {total_matches} matches predicted")
        
        # ---- LIVE GROUP TABLE ----
        st.markdown("## Group Table")
        table = compute_group_table(group_predictions)
        table.insert(0, "Pos", range(1, len(table) + 1))
        
        # Apply flags to the Team column
        table["Team"] = table["Team"].apply(team_label)
        table = table.reset_index(drop=True)
        # Display with HTML so flags render
        st.markdown(table.to_html(escape=False, index=False), unsafe_allow_html=True)
        group_tables[group] = table.copy()
    
pred_df = pd.DataFrame(predictions).sort_values("Match").reset_index(drop=True)
st.session_state["pred_df"] = pred_df

# Store how many predictions are complete
st.session_state["pred_count"] = len(predictions)


st.markdown("## Best 3rd‑Place Teams")


third_place_rows = []

for group, table in group_tables.items():
    if len(table) >= 3:
        third = table.iloc[2]  # 3rd place
        third_place_rows.append({
            "Group": group,
            "Team": third["Team"],
            "Pts": third["Pts"],
            "GD": third["GD"]
        })

third_df = pd.DataFrame(third_place_rows)

# Sort by tournament rules
third_df = third_df.sort_values(
    by=["Pts", "GD"],
    ascending=[False, False]
).reset_index(drop=True)

# Apply flags
third_df["Team"] = third_df["Team"].apply(team_label)
third_df.insert(0, "Pos", range(1, len(third_df) + 1))

html = third_df.to_html(escape=False, index=False)
rows = html.split("</tr>")
# Insert a separator row after row 7 (i.e., after 8th row)
separator = """
<tr style='background-color:#000; height:3px;'>
    <td colspan='100%'></td>
</tr>
"""
rows.insert(9, separator)  # index 8 = after row 7

html_with_line = "</tr>".join(rows)

# Display
st.markdown(html_with_line, unsafe_allow_html=True)


KNOCKOUT_MAP = [
    ("2A", "2B"),
    ("1E", "1Ev"),
    ("1F", "2C"),
    ("1C", "2F"),
    ("1I", "1Iv"),
    ("2E", "2I"),
    ("1A", "1Av"),
    ("1L", "1Lv"),
    ("1D", "1Dv"),
    ("1G", "1Gv"),
    ("2K", "2L"),
    ("1H", "2J"),
    ("1B", "1Bv"),
    ("1J", "2H"),
    ("1K", "1Kv"),
    ("2D", "2G")
]

st.write("Your predictions:")
st.dataframe(pred_df)

    
