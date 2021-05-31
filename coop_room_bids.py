import numpy as np
import pandas as pd
import datetime as dt

now = dt.datetime.now()

# read the CSV files in
roombids_df = pd.read_csv("roombids.csv")
openrooms_df = pd.read_csv("open_rooms.csv")
preferences_df = pd.read_csv("preferences.csv")
points_df = pd.read_csv("points.csv")

# if gender is listed as NaN, replace it with "F"
# need to ask management on what to do for those who don't identify as male or female
roombids_df = roombids_df.drop(labels=["KEY"], axis=1)
roombids_df.loc[roombids_df["M"].isnull(), "M"] = roombids_df["F"]
roombids_df = roombids_df.drop(labels=["F"], axis=1)
#print(roombids_df)

# fill in NaN values
roombids_df[["POINTS"]] = roombids_df[["POINTS"]].fillna(value=0, axis=1)
roombids_df[["NAME"]] = roombids_df[["NAME"]].fillna(value="ZZZZZ", axis=1)
roombids_df = roombids_df.fillna(value="", axis=1)
#print(roombids_df)

# rename the "M" column as "GENDER" and use regex to clean the "NAME" column
roombids_df = roombids_df.rename(index=str, columns={"M" : "GENDER"})
roombids_df["NAME"].replace(regex=True, inplace=True, to_replace=r"\(.\)", value=r"")

# occupancy of each room changes depending on if its summer or not
if now.month in np.arange(5, 8):
    roombids_df["OCCUPANCY"].replace(regex=True, inplace=True, to_replace=r".*\(", value=r"")
    roombids_df["OCCUPANCY"].replace(regex=True, inplace=True, to_replace=r" .*\)", value=r"")
else:
    roombids_df["OCCUPANCY"].replace(regex=True, inplace=True, to_replace=r" \(.*\)", value=r"")

roombids_df["OCCUPANCY"] = roombids_df["OCCUPANCY"].str.upper()
roombids_df["GENDER"] = roombids_df["GENDER"].str.upper()

roombids_df["NAME"] = roombids_df["NAME"].str.split(", ").str[::-1].str.join("")
#print(roombids_df)

preferences_df["APP #"] = preferences_df["APP #"].str.replace(" ", "")
preferences_df["PREFERENCES"] = preferences_df["PREFERENCES"].str.replace(" ", "")
#print(preferences_df)

nosquat_df = roombids_df.loc[(roombids_df["SQUAT/NOT"] == "NO") | (roombids_df["SQUAT/NOT"] == "") | (roombids_df["ROOM"] == "")]
roombids_df = roombids_df.sort_values(["POINTS", "APP #"], ascending=[False, True])
nosquat_df = nosquat_df.sort_values(["POINTS", "APP #"], ascending=[False, True])
nosquat_df = nosquat_df.reset_index().drop(labels=["index"], axis=1)
#print(nosquat_df)

singles_pref = preferences_df.loc[preferences_df["TYPE"] == "S"]
doubles_pref = preferences_df.loc[preferences_df["TYPE"] == "D"]
triples_pref = preferences_df.loc[preferences_df["TYPE"] == "T"]

nosquat_df = nosquat_df.set_index("APP #")

# look through preferences for singles
singles_points_list = []
for _, row in singles_pref.iterrows():
    for val in row["APP #"].split(","):
        singles_points_list.append(nosquat_df.loc[int(val), "POINTS"])

singles_pref = pd.DataFrame(singles_pref)
singles_pref["TOTAL POINTS"] = singles_points_list

# sort on total points and subsort on application ID
singles_pref["MIN APP #"] = singles_pref["APP #"]
singles_pref = singles_pref.sort_values(["TOTAL POINTS", "MIN APP #"], ascending=[False, True])
singles_pref = singles_pref.set_index("MIN APP #")
singles_pref[["PREFERENCES"]] = singles_pref[["PREFERENCES"]].fillna(value="", axis=1)
#print(singles_pref)

# look through preferences for doubles and sum the roommates' points
doubles_points_list = []
for _, row in doubles_pref.iterrows():
    doubles_group_points = 0
    for val in row["APP #"].split(","):
        doubles_group_points += nosquat_df.loc[int(val), "POINTS"]
    doubles_points_list.append(doubles_group_points)

doubles_pref = pd.DataFrame(doubles_pref)
doubles_pref["TOTAL POINTS"] = doubles_points_list

# subsort on application ID after sorting on points
min_app_ids_doubles = []
for _, row in doubles_pref.iterrows():
    min_app_ids_doubles.append(min(row["APP #"].split(",")))

doubles_pref["MIN APP #"] = min_app_ids_doubles
doubles_pref = doubles_pref.sort_values(["TOTAL POINTS", "MIN APP #"], ascending=[False, True])
doubles_pref = doubles_pref.set_index("MIN APP #")
doubles_pref[["PREFERENCES"]] = doubles_pref[["PREFERENCES"]].fillna(value="", axis=1)
#print(doubles_pref)

# look through preferences for triples and sum the roommates' points
triples_points_list = []
for _, row in triples_pref.iterrows():
    triples_group_points = 0
    for val in row["APP #"].split(","):
        if val != "":
            triples_group_points += nosquat_df.loc[int(val), "POINTS"]
    triples_points_list.append(triples_group_points)

triples_pref = pd.DataFrame(triples_pref)
triples_pref["TOTAL POINTS"] = triples_points_list

min_app_ids_triples = []
for _, row in triples_pref.iterrows():
    min_app_ids_triples.append(min(row["APP #"].split(",")))

triples_pref["MIN APP #"] = min_app_ids_triples
triples_pref = triples_pref.sort_values(["TOTAL POINTS", "MIN APP #"], ascending=[False, True])
triples_pref = triples_pref.set_index("MIN APP #")
triples_pref[["PREFERENCES"]] = triples_pref[["PREFERENCES"]].fillna(value="", axis=1)
#print(triples_pref)

# find open rooms for each occupancy
open_singles = openrooms_df.loc[openrooms_df["TYPE"] == "S"]
open_doubles = openrooms_df.loc[openrooms_df["TYPE"] == "D"]
open_triples = openrooms_df.loc[openrooms_df["TYPE"] == "T"]
open_singles = open_singles.set_index("ROOM")
open_doubles = open_doubles.set_index("ROOM")
open_triples = open_triples.set_index("ROOM")

assigned_triples = []

# assign triples first
for _, row in triples_pref.iterrows():
    last_elem_ind = len(row["PREFERENCES"].split(",")) - 1
    for val in row["PREFERENCES"].split(","):
        if val in open_triples.index.values:
            assigned_triples.append(val)
            open_triples = open_triples.drop([val])
            break
        if val == "" and len(row["PREFERENCES"].split(",")) == 1:
            assigned_triples.append(val)
            continue
        if val == "" and row["PREFERENCES"].split(",")[last_elem_ind] == val:
            assigned_triples.append("")
        if val != "" and val not in open_triples.index.values and len(row["PREFERENCES"].split(",")) == 1:
            assigned_triples.append("")

#if triples_pref.shape[0] > len(assigned_triples):
#    for i in range(triples_pref.shape[0] - len(assigned_triples) - 1):
#        assigned_triples.append("")

#print(assigned_triples)
triples_pref["ASSIGNED ROOM"] = assigned_triples

triples_pref = triples_pref.reset_index().set_index("APP #")
singles_pref = singles_pref.reset_index().set_index("APP #")
doubles_pref = doubles_pref.reset_index().set_index("APP #")
#print(triples_pref)

triples_pref = triples_pref[(triples_pref[["PREFERENCES"]] != "").all(axis=1)]
singles_pref = singles_pref[(singles_pref[["PREFERENCES"]] != "").all(axis=1)]
doubles_pref = doubles_pref[(doubles_pref[["PREFERENCES"]] != "").all(axis=1)]

app_id_double_split = [ids for segs in doubles_pref.index.values for ids in segs.split(",")]
app_id_triple_split = [ids for segs in triples_pref.index.values for ids in segs.split(",")]

for app_id in app_id_triple_split:
    if app_id in singles_pref.index.values:
        singles_pref = singles_pref.drop([app_id])

assigned_singles = []

singles_pref = singles_pref[(singles_pref[["PREFERENCES"]] != "").all(axis=1)]

# look through preferences for singles
for _, row in singles_pref.iterrows():
    last_elem_ind = len(row["PREFERENCES"].split(",")) - 1
    for val in row["PREFERENCES"].split(","):
        if val in open_singles.index.values:
            assigned_singles.append(val)
            open_singles = open_singles.drop([val])
            break
        if val == "" and len(row["PREFERENCES"].split(",")) == 1:
            assigned_singles.append(val)
            continue
        if val == "" and row["PREFERENCES"].split(",")[last_elem_ind] == val:
            assigned_singles.append("")
        if val != "" and val not in open_singles.index.values and len(row["PREFERENCES"].split(",")) == 1:
            assigned_singles.append("")

#if singles_pref.shape[0] > len(assigned_singles):
#    for i in range(singles_pref.shape[0] - len(assigned_singles) - 1):
#        assigned_singles.append("")

singles_pref["ASSIGNED ROOM"] = assigned_singles
#print(singles_pref)

# remove preferences for other occupancies of a person has just been assigned to a new room
for app_id in singles_pref.index.values:
    if app_id in app_id_double_split:
        sing_doub_contains_id = [s for s in doubles_pref.index.values if app_id in s]
        if sing_doub_contains_id == []:
            continue
        if sing_doub_contains_id[0] in doubles_pref.index.values:
            doubles_pref = doubles_pref.drop(sing_doub_contains_id)

for app_id in app_id_triple_split:
    if app_id in app_id_double_split:
        trip_doub_contains_id = [s for s in doubles_pref.index.values if app_id in s]
        if trip_doub_contains_id == []:
            continue
        if trip_doub_contains_id[0] in doubles_pref.index.values:
            doubles_pref = doubles_pref.drop(trip_doub_contains_id)

assigned_doubles = []

doubles_pref = doubles_pref[(doubles_pref[["PREFERENCES"]] != "").all(axis=1)]

# look through preferences for doubles
for _, row in doubles_pref.iterrows():
    last_elem_ind = len(row["PREFERENCES"].split(",")) - 1
    for val in row["PREFERENCES"].split(","):
        if val in open_doubles.index.values:
            assigned_doubles.append(val)
            open_doubles = open_doubles.drop([val])
            break
        if val == "" and len(row["PREFERENCES"].split(",")) == 1:
            assigned_doubles.append(val)
            continue
        if val == "" and row["PREFERENCES"].split(",")[last_elem_ind] == val:
            assigned_doubles.append("")
        if val != "" and val not in open_doubles.index.values and len(row["PREFERENCES"].split(",")) == 1:
            assigned_doubles.append("")

#if doubles_pref.shape[0] > len(assigned_doubles):
#    for i in range(doubles_pref.shape[0] - len(assigned_doubles) - 1):
#        assigned_doubles.append("")

doubles_pref["ASSIGNED ROOM"] = assigned_doubles
#print(doubles_pref)

tsd_assign = triples_pref.append(singles_pref)
tsd_assign = tsd_assign.append(doubles_pref)
tsd_assign = tsd_assign.dropna()

tsd_assign.index.name = "APP #"
tsd_assign = tsd_assign.reset_index()
tsd_assign = tsd_assign.sort_values(["TOTAL POINTS", "MIN APP #"], ascending=[False, True])
#print(tsd_assign)

names = []
for _, row in tsd_assign.iterrows():
    group_names = []
    for val in row["APP #"].split(","):
        group_names.append(nosquat_df.loc[int(val), "NAME"])
    names.append(group_names)

tsd_assign["NAMES"] = names
#tsd_assign["NAMES"] = tsd_assign["NAMES"].replace(regex=True, to_replace=r"/[\[\]']+", value=r"")

tsd_assign["TYPE"] = tsd_assign["TYPE"].replace(to_replace="T", value="TRIPLE")
tsd_assign["TYPE"] = tsd_assign["TYPE"].replace(to_replace="S", value="SINGLE")
tsd_assign["TYPE"] = tsd_assign["TYPE"].replace(to_replace="D", value="DOUBLE")
#print(tsd_assign)

# save the assignments to a CSV file
tsd_assign.to_csv(path_or_buf="assigned_rooms_output.csv")
