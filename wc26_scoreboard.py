# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 21:42:12 2026

@author: matta
"""
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime
from zoneinfo import ZoneInfo
from datetime import date,datetime,timedelta
#import gspread
#from google.oauth2.service_account import Credentials

st.title("World Cup Prediction Scoreboard")

st.markdown("""
## 🏆 Points System Reminder

- **3 points** for each correct Round of 32 winner
- **6 points** for each correct Round of 16 winner
- **8 points** for each Quarter Final winner
- **12 points** for each Semi Final winner 
- **10 points** for 3rd Place Playoff winner
- **18 points** for Final winner
- **Half points** for a correct inherited winner

- **20 points** for **Winner**
- **10 points** for **Golden Boot**

""")

@st.cache_data(ttl=120)  # cache for 5 minutes
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

    # Return both the data AND the timestamp
    last_updated = (datetime.utcnow() + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M:%S BST")

    return df, last_updated

results_df, results_updated = load_sheet_tab("World_Cup_2026_Scoreboard", "Results")
scoreboard_df, scoreboard_updated = load_sheet_tab("World_Cup_2026_Scoreboard", "Scoreboard")
player_df, player_updated = load_sheet_tab("World_Cup_2026_Scoreboard", "Copy of Player_Pred")
ko_df, ko_updated = load_sheet_tab("World_Cup_2026_Scoreboard", "Knockouts")
player_ko_df, player_ko_updated = load_sheet_tab("World_Cup_2026_Scoreboard", "Copy of KO_Pred")

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

def center_columns(df, cols):
    df = df.copy()
    for col in cols:
        df[col] = df[col].apply(
            lambda x: f"<div style='text-align:center;'>{x}</div>"
        )
    return df

def colour_leader(df, cols):
    df = df.copy()

    for col in cols:
        df[col] = df[col].apply(lambda x: (
            str(x).replace(
                "LEADER",
                "<span style='color:red; font-weight:bold;'>LEADER</span>"
            )
            if "LEADER" in str(x)
            else x
        ))

    return df

def highlight_column(df, col):
    df = df.copy()
    df[col] = df[col].apply(
        lambda x: (
                "<div style='background-color: orange; "
                "display: block; width: 100%; height: 100%; "
                "padding: 0px; text-align: center;'>"
                f"{x}</div>"
            )
    )
    return df

def prepare_results_table(df):
    df = df.copy()

    # --- 1. Add flags to Team A and Team B ---
    df["Team A"] = df["Team A"].apply(team_label)
    df["Team B"] = df["Team B"].apply(team_label)

    # Convert floats → nullable Int64
    #df["AS"] = df["AS"].astype("Int64")
    #df["BS"] = df["BS"].astype("Int64")

    # Convert to string so we can safely replace NaN with ""
    df["AS"] = df["AS"].astype("string")
    df["BS"] = df["BS"].astype("string")

    # Replace <NA> with blank
    df["AS"] = df["AS"].fillna("")
    df["BS"] = df["BS"].fillna("")

    # --- 3. Centre the score columns ---
    df["AS"] = df["AS"].apply(lambda x: f"<div style='text-align:center;'>{x}</div>")
    df["BS"] = df["BS"].apply(lambda x: f"<div style='text-align:center;'>{x}</div>")
    df["-"] = df["-"].apply(lambda x: f"<div style='text-align:center;'>{x}</div>")
    
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Date"] = df["Date"].dt.strftime("%d-%b")

    df["Time (BST)"] = df["Time (BST)"].astype(str).str.slice(0, 5)

    # --- 4. Centre the dash column if you have one ---

    return df

#results = pd.read_excel(r"C:\Users\matta\OneDrive\Documents\Matt's Stuff\Footy\World Cup 2026\wc26_app_leaderboard.xlsx",sheet_name="Results")
#leaderboard = pd.read_excel(r"C:\Users\matta\OneDrive\Documents\Matt's Stuff\Footy\World Cup 2026\wc26_app_leaderboard.xlsx",sheet_name="Leaderboard")


#fixtures = pd.read_excel(r"C:\Users\matta\OneDrive\Documents\Matt's Stuff\Footy\World Cup 2026\WC2026_Scoreboard.xlsx",sheet_name="Fixtures")
#leaderboard_2 = pd.read_excel(r"C:\Users\matta\OneDrive\Documents\Matt's Stuff\Footy\World Cup 2026\WC2026_Scoreboard.xlsx",sheet_name="Leaderboard")


md_dict = {'2026-06-11':1,'2026-06-12':2,'2026-06-13':3,'2026-06-14':4,
           '2026-06-15':5,'2026-06-16':6,'2026-06-17':7,'2026-06-18':8,
           '2026-06-19':9,'2026-06-20':10,'2026-06-21':11,'2026-06-22':12,
           '2026-06-23':13,'2026-06-24':14,'2026-06-25':15,'2026-06-26':16,
           '2026-06-27':17,'2026-06-28':18,'2026-06-29':19}

#scoreboard = load_scoreboard()
#leader_sort = leaderboard.sort_values(
#    by=["Pos","Group Stage"],
#    ascending=[True, False]
#).reset_index(drop=True)

#leader_sort_2 = leaderboard_2.sort_values(
#    by=["Pos","Group Stage"],
#    ascending=[True, False]
#).reset_index(drop=True)

#results["Date"] = pd.to_datetime(results["Date"]).dt.date
md_dict.get((date.today() + timedelta(days=2)).strftime("%Y-%m-%d"))
#new_results = results[results['MD']<md_dict.get((date.today() + timedelta(days=2)).strftime("%Y-%m-%d"))]
#new_results = new_results.drop(columns=['MD','Location'])

#fixtures["Date"] = pd.to_datetime(fixtures["Date"]).dt.date
#md_dict.get((date.today() + timedelta(days=2)).strftime("%Y-%m-%d"))
#new_fix = fixtures[fixtures['MD']<md_dict.get((date.today() + timedelta(days=2)).strftime("%Y-%m-%d"))]
#new_fix = new_fix.drop(columns=['MD'])

#leader_sort_2 = leader_sort_2.drop(columns=['Knockouts'])


results_df["Date"] = pd.to_datetime(results_df["Date"]).dt.date
results_df = results_df[results_df['MD']<md_dict.get((date.today() + timedelta(days=1)).strftime("%Y-%m-%d"))]
results_df = results_df.drop(columns=['MD'])

scoreboard_df = scoreboard_df.sort_values(
    by=["Points","Groups"],
    ascending=[False, False]
).reset_index(drop=True)
#scoreboard_df = scoreboard_df.drop(columns=['Knockouts'])

# Your key dates
date_A = pd.to_datetime("2026-07-03")
date_B = pd.to_datetime("2026-07-05")
date_C = pd.to_datetime("2026-07-07")
date_D = pd.to_datetime("2026-07-10")
date_E = pd.to_datetime("2026-07-12")
date_F = pd.to_datetime("2026-07-15")
date_G = pd.to_datetime("2026-07-16")

# Today or selected date
selected_date = date.today()
selected_date = pd.to_datetime(selected_date)

# Logic for which rounds to show
if selected_date < date_A:
    allowed_rounds = ["R32"]

elif date_A <= selected_date < date_B:
    allowed_rounds = ["R32", "R16"]

elif date_B <= selected_date < date_C:
    allowed_rounds = ["R16"]
    
elif date_C <= selected_date < date_D:
    allowed_rounds = ["R16","QF"]

elif date_D <= selected_date < date_E:
    allowed_rounds = ["QF"]

elif date_E <= selected_date < date_F:
    allowed_rounds = ["QF","SF"]

elif date_F <= selected_date < date_G:
    allowed_rounds = ["SF"]

else:
    allowed_rounds = ["SF","3F", "F"]  # optional future rounds

# Filter your dataframe
filtered_df = ko_df[ko_df["Round"].isin(allowed_rounds)]


player_columns = {
    "Player Stats": [
        "team_a",
        "draw",
        "team_b"
    ],
    "Matt Allen": [
        "Matt Allen-Pred",
        "Matt Allen-Mg",
        "Matt Allen-Bonus"
    ],
    "Steve Allen": [
        "Steve Allen-Pred",
        "Steve Allen-Mg",
        "Steve Allen-Bonus"
    ],
    "Cameron Russell": [
        "Cameron Russell-Pred",
        "Cameron Russell-Mg",
        "Cameron Russell-Bonus"
    ],
    "Hamish MacCaig": [
        "Hamish MacCaig-Pred",
        "Hamish MacCaig-Mg",
        "Hamish MacCaig-Bonus"
    ],
    "Mark Mooney": [
        "Mark Mooney-Pred",
        "Mark Mooney-Mg",
        "Mark Mooney-Bonus"
    ],
    "Samantha Allen": [
        "Samantha Allen-Pred",
        "Samantha Allen-Mg",
        "Samantha Allen-Bonus"
    ],
    "Molly Wedge": [
        "Molly Wedge-Pred",
        "Molly Wedge-Mg",
        "Molly Wedge-Bonus"
    ],
    "Chris Allen": [
        "Chris Allen-Pred",
        "Chris Allen-Mg",
        "Chris Allen-Bonus"
    ],
    "Matthew Drury": [
        "Matthew Drury-Pred",
        "Matthew Drury-Mg",
        "Matthew Drury-Bonus"
    ],
    "Hugh Cunningham": [
        "Hugh Cunningham-Pred",
        "Hugh Cunningham-Mg",
        "Hugh Cunningham-Bonus"
    ],
    "Greg Donaldson": [
        "Greg Donaldson-Pred",
        "Greg Donaldson-Mg",
        "Greg Donaldson-Bonus"
    ],
    "Matthew Bottrill": [
        "Matthew Bottrill-Pred",
        "Matthew Bottrill-Mg",
        "Matthew Bottrill-Bonus"
    ],
    "James Wilton": [
        "James Wilton-Pred",
        "James Wilton-Mg",
        "James Wilton-Bonus"
    ],
    "Rob Allen": [
        "Rob Allen-Pred",
        "Rob Allen-Mg",
        "Rob Allen-Bonus"
    ],
    "Duncan Bruce": [
        "Duncan Bruce-Pred",
        "Duncan Bruce-Mg",
        "Duncan Bruce-Bonus"
    ],
    "Aimee B": [
        "Aimee B-Pred",
        "Aimee B-Mg",
        "Aimee B-Bonus"
    ]
}


ko_player_columns = ["Matt Allen","Steve Allen","Cameron Russell",
                     "Hamish MacCaig","Mark Mooney","Samantha Allen",
                     "Molly Wedge","Chris Allen","Matthew Drury",
                     "Hugh Cunningham","Greg Donaldson","Matthew Bottrill",
                     "James Wilton","Rob Allen","Duncan Bruce","Aimee B"]

tab1, tab2, tab5 = st.tabs(["🏆 Leaderboard", "📊 Results", "🔮 Player Predictions"])

#tab4:,"🔮 Player Predictions"

with tab1:
    st.subheader("Leaderboard")
    st.markdown(f"**Scoreboard last updated:** {scoreboard_updated}")
    #new_leader = center_columns(leader_sort,['Pos','Points','Gap','Group Stage','Bonus Games'])
    #new_new_leader = highlight_column(new_leader, 'Points')
    #new_new_new_leader = colour_leader(new_new_leader, ["Gap"])
    #st.markdown(
    #new_new_new_leader.to_html(index=False, escape=False),
    #unsafe_allow_html=True)
    
    #new_leader_2 = center_columns(leader_sort_2,['Pos','Points','Gap','Group Stage','Bonus Points'])
    #new_new_leader_2 = highlight_column(new_leader_2, 'Points')
    #new_new_new_leader_2 = colour_leader(new_new_leader_2, ["Gap"])
    #st.markdown(
    #new_new_new_leader_2.to_html(index=False, escape=False),
    #unsafe_allow_html=True)
    
    scoreboard_df = center_columns(scoreboard_df,['Pos','Points','Gap','KOs','Groups','Winner',])
    scoreboard_df = highlight_column(scoreboard_df, 'Points')
    scoreboard_df = colour_leader(scoreboard_df, ["Gap"])
    st.markdown(
    scoreboard_df.to_html(index=False, escape=False),
    unsafe_allow_html=True)
    
with tab2:
    st.subheader("Results & Upcoming Fixtures")
    st.markdown(f"**Results last updated:** {results_updated}")
    #results_display = prepare_results_table(new_results)
    #st.markdown(
    #    results_display.to_html(index=False, escape=False),
    #    unsafe_allow_html=True
    #)
    #results_display = prepare_results_table(new_fix)
    #st.markdown(
    #    results_display.to_html(index=False, escape=False),
    #    unsafe_allow_html=True
    #)
    
    results_display = prepare_results_table(filtered_df)
    st.markdown(
        results_display.to_html(index=False, escape=False),
        unsafe_allow_html=True
    )

####RETIRING TAB3#######
#with tab3:
#    st.subheader("Predictions")
#    html = player_df.to_html(index=False, escape=False)

#    rows = html.split("</tr>")
#    new_rows = []
    
#    for row in rows:
#        if "<tr" not in row:
#            continue

        # Split into cells (both <td> and <th>)
#        cells = (
#            row.replace("</th>", "</td>")  # normalize headers to td for splitting
#            .split("</td>")
#            )

#        new_cells = []

#        for i, cell in enumerate(cells):
#            if "<td" in cell or "<th" in cell:
                # Restore correct closing tag
#                closing = "</th>" if "<th" in cell else "</td>"
#                new_cells.append(cell + closing)

#                col_num = i + 1

                # Insert separator AFTER col 6, then 9, 12, 15...
#                if col_num > 3 and (col_num - 3) % 3 == 0:
#                   new_cells.append(
#                        "<td style='border-right:3px solid #000; padding:0;'></td>"
#                        )

#        new_rows.append("".join(new_cells))

#    html_with_lines = "</tr>".join(new_rows)
#    st.markdown(html_with_lines, unsafe_allow_html=True)

#with tab4:
#    st.subheader("Player Predictions")
#    # Columns that should always appear
#    base_cols = ["Match", "Group", "Team A", "Team B", "AS", "BS"]

    # Pin "Player Stats" at the top
#    pinned = ["Player Stats"]

    # Sort all player names except the pinned one
#    others = sorted([p for p in player_columns.keys() if p not in pinned])

    # Build final dropdown list
#    player_options = pinned + ["All Players"] + others

    # Multiselect dropdown
#    players = st.multiselect(
#        "Choose players",
#        player_options
#        )

    # If "All Players" is selected, include everyone
#    if "All Players" in players:
#        players = list(player_columns.keys())

    # If "Player Stats" is selected, handle it separately if needed
    # (Right now it will just be ignored unless you define what it means)
#    players = [p for p in players if p in player_columns]

    # Collect all selected player columns
#    selected_player_cols = []
#    for p in players:
#        selected_player_cols.extend(player_columns[p])

    # Final columns to show
#    cols_to_show = base_cols + selected_player_cols

    # Display
#    st.dataframe(player_df[cols_to_show])

def colour_winner(val):
    return f"<div style='background-color:#d4edda; text-align:center;'>{val}</div>"

with tab5:
    st.subheader("Player Predictions")
    # Columns that should always appear
    base_cols = ["M", "Rd", "Team A", "Team B", "Winner"]

    # Pin "Player Stats" at the top
    #pinned = ["Player Stats"]

    # Sort all player names except the pinned one
    others = sorted(ko_player_columns)

    # Build final dropdown list
    player_options = ["All Players"] + others

    # Multiselect dropdown
    players = st.multiselect(
        "Choose players",
        player_options
        )

    # If "All Players" is selected, include every KO column
    if "All Players" in players:
        selected_player_cols = ko_player_columns
    else:
        # Otherwise use only the selected columns
        selected_player_cols = [p for p in players if p in ko_player_columns]

    # Final columns to show
    cols_to_show = base_cols + selected_player_cols
    
    selected_date = date.today()
    selected_date = pd.to_datetime(selected_date)
    date_a = pd.to_datetime("2026-07-03")
    date_b = pd.to_datetime("2026-07-07")
    date_c = pd.to_datetime("2026-07-11")
    date_d = pd.to_datetime("2026-07-15")
    
    if selected_date <= date_a:
        allowed_rounds = ["R32"]

    elif selected_date <= date_b:
        allowed_rounds = ["R32", "R16"]

    elif selected_date <= date_c:
        allowed_rounds = ["R32", "R16","QF"]
        
    elif selected_date <= date_d:
        allowed_rounds = ["R32", "R16","QF","SF"]
    
    else:
        allowed_rounds = ["R32", "R16","QF","SF","3F","F"]
    
    t2_df = player_ko_df[player_ko_df['Rd'].isin(allowed_rounds)]
    final_df = t2_df[cols_to_show]
    final_df["Winner"] = final_df["Winner"].apply(colour_winner)
    
    # Display
    #st.dataframe(final_df)
    st.markdown(final_df.to_html(escape=False), unsafe_allow_html=True)

#st.dataframe(leader_sort,hide_index=True)