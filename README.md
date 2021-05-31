# Cooperative Room Bids

A room bidding system for the Berkeley Student Cooperative.

## Background

While living in the Berkeley Student Cooperative (BSC) during the fall semester of 2018, I was tasked with designing a room bidding system in a team of 3 people as my weekly workshift assignment. I was in charge of creating an algorithm to assign residents to rooms, depending on their seniority points and application ID, for 1,300 BSC residents. This code saves 4 hours each semester from the in-person process for each of the residents and the management teams.

The code for this project is available in `coop_room_bids.py`. The algorithm assigns residents to rooms in the order of triples, singles, and then doubles. Residents who plan to room together are assigned based on the sum of their seniority points and their minimum application ID which is used as a tie breaker for seniority points. Residents who are bidding on singles independently use their own seniority points and application ID. The resident or residents rooming together who bid on a room with the most seniority points and minimum application ID are selected to live in that room.

## Dataset

For the privacy of the residents, I am unable to share any data used in this project. However, I have described the CSV files and columns below.

### roombids.csv

Contains information for each resident.

`APP #` : Application ID of the resident \
`ROOM` : Room number that the resident lives in \
`OCCUPANCY` : Single, Double, or Triple room that the resident lives in \
`DISABILITY` : Briefly describes the resident's disability, otherwise NaN \
`NAME` : Resident's name \
`POINTS` : Number of points that the resident has \
`SQUAT/NOT` : Boolean value indicating if the resident is staying in the room or moving to a different room \
`M` : Resident's gender, later changed to "GENDER" in the code

### open_rooms.csv

Lists all of the open rooms.

`TYPE` : S, D, and T are used to denote a Single, Double, or Triple room \
`ROOM` : Room number

### preferences.csv

Preferences of each group of residents bidding together.

`TYPE` : S, D, and T are used to denote a Single, Double, or Triple room \
`APP #` : List of application IDs of the residents bidding on rooms together \
`PREFERENCES` : List of the residents' preferences

### points.csv

Mapping of application ID to the points that the resident has.

`ID` : Application ID \
`PT` : Number of points that the resident has

### assigned_rooms_output.csv
Output file containing the assignments for the resident(s) bidding together or by themselves.

`APP #` : Application IDs of all resident(s) \
`MIN APP #` : Minimum application ID of the resident(s) \
`TYPE` : Type of room that the resident(s) are assigned, e.g. SINGLE, DOUBLE, or TRIPLE \
`PREFERENCES` : Preferences of the resident(s) \
`TOTAL POINTS` : Sum of points of the resident(s) \
`ASSIGNED ROOM` : Room that the resident(s) are assigned to \
`NAMES` : List of names of the resident(s)
