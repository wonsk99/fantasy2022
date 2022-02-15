import requests
from bs4 import BeautifulSoup as bs

import pandas as pd

# Get link
def getLinks():
	LCSmatchlist = "https://gol.gg/tournament/tournament-matchlist/LCS%20Spring%202022/"
	LECmatchlist = "https://gol.gg/tournament/tournament-matchlist/LEC%20Spring%202022/"

	week = input("Which week?\n")
	cweek = int(week) - 3
	lcsweek = "WEEK" + str(cweek)
	lecweek = "WEEK" + str(week)

	print(lcsweek, lecweek)

	matchlist = LECmatchlist

	weeks = []
	weeks.append(lcsweek)
	weeks.append(lecweek)

print(weeks)

matchpage = requests.get(matchlist, headers={"User-agent": "Hi"})
soup = bs(matchpage.content, "html.parser")

matches = soup.find_all("tr")

links = []

for match in matches:
	row = match.find_all("td")
	if not row:
		continue
	for week in weeks:
		if row[4].text == week:
			baselink = 'https://gol.gg/'
			a = row[0].find_all("a", href=True)
			matchlink = a[0]['href']
			baselink += "/".join(matchlink.split("/")[1:])
			links.append(baselink)

print(links)

# Get Player Names and Stats
#
#

f2 = {}
f3 = {}

for link in links:
	print(link)
	# Error checking
	if not link:
		print(":p")
		continue

	if "page-game" not in link:
		print("Error: Invalid site (make sure it is a 'page-game' page)")
		continue

	if "page-game/" not in link:
		link = link+"/"


	# Team Stuff link
	#
	#

	# SOUP
	page = requests.get(link, headers={"User-agent": "Hi"})
	
	soup = bs(page.content, "html.parser")

	teams = soup.find_all("div", class_="col-12 col-sm-6")
	bt = teams[0]
	rt = teams[1]

	bTeaminfo = bt.find_all("div", class_="row")[1]
	rTeaminfo = rt.find_all("div", class_="row")[1]

	# Turret
	bTurr = int(bTeaminfo.find_all("span", class_="score-box blue_line")[1].text.strip())
	rTurr = int(rTeaminfo.find_all("span", class_="score-box red_line")[1].text.strip())
	
	# First Turret
	ab = bt.find_all("div", class_="col-2")[1].find_all("img")
	ar = rt.find_all("div", class_="col-2")[1].find_all("img")

	firstTurret = -1

	if len(ab) == 2:
		firstTurret = 0
	if len(ar) == 2:
		firstTurret = 1

	# Dragons
	bDrag = int(bTeaminfo.find_all("span", class_="score-box blue_line")[2].text.strip())
	rDrag = int(rTeaminfo.find_all("span", class_="score-box red_line")[2].text.strip())

	# Elder Dragon
	db = bt.find_all("div", class_="col-2")[2].find_all("img")
	dr = rt.find_all("div", class_="col-2")[2].find_all("img")

	bElders = 0
	rElders = 0
	
	for drag in db:
		if drag['src'] == "../_img/elder-dragon.png":
			bElders += 1

	for drag in dr:
		if drag['src'] == "../_img/elder-dragon.png":
			rElders += 1

	# Barons
	bBaron = int(bTeaminfo.find_all("span", class_="score-box blue_line")[3].text.strip())
	rBaron = int(rTeaminfo.find_all("span", class_="score-box red_line")[3].text.strip())

	# Win
	bWinfo = bt.find_all("div", class_="row")[0]
	rWinfo = rt.find_all("div", class_="row")[0]

	bTeamName = bWinfo.find("div", class_="col-12 blue-line-header").text.split(" - ")[0].strip()
	rTeamName = rWinfo.find("div", class_="col-12 red-line-header").text.split(" - ")[0].strip()
	
	bWin = 1 if (bWinfo.find("div", class_="col-12 blue-line-header").text.split(" - ")[1].strip() == "WIN") else 0
	rWin = 1 if (rWinfo.find("div", class_="col-12 red-line-header").text.split(" - ")[1].strip() == "WIN") else 0

	# Win in < 30 min
	timeInfo = soup.find_all("div", class_="col-6 text-center")[0]
	gametime = int(timeInfo.find("h1").text.split(":")[0])
	
	bThirty = 0
	rThirty = 0
	
	if gametime < 30:
		bThirty = bWin
		rThirty = rWin

	
	t1 = bTeamName
	t2 = rTeamName

	if t1 not in f3:
		f3[t1] = {"Turrets": 0, "Dragons": 0, "Elder Dragons": 0, "Barons": 0, "Win": 0, "Win in 30": 0, "First Turret": 0, "Games Played": 0}
	if t2 not in f3:
		f3[t2] = {"Turrets": 0, "Dragons": 0, "Elder Dragons": 0, "Barons": 0, "Win": 0, "Win in 30": 0, "First Turret": 0, "Games Played": 0}

	f3[t1]["Turrets"] += bTurr
	f3[t1]["Dragons"] += bDrag
	f3[t1]["Elder Dragons"] += bElders
	f3[t1]["Barons"] += bBaron
	f3[t1]["Win"] += bWin
	f3[t1]["Win in 30"] += bThirty
	f3[t1]["First Turret"] += int(not firstTurret)
	f3[t1]["Games Played"] += 1

	f3[t2]["Turrets"] += rTurr
	f3[t2]["Dragons"] += rDrag
	f3[t2]["Elder Dragons"] += rElders
	f3[t2]["Barons"] += rBaron
	f3[t2]["Win"] += rWin
	f3[t2]["Win in 30"] += rThirty
	f3[t2]["First Turret"] += int(firstTurret)
	f3[t2]["Games Played"] += 1

	# Basic INFO LINK
	#
	#
	
	li = link.split("/")
	li[-2] = "page-fullstats"
	tlink = "/".join(li)
	print(tlink)
	
	# SOUP
	page = requests.get(tlink, headers={"User-agent": "Hi"})
	
	soup = bs(page.content, "html.parser")
	
	# Get the table
	allPlayers = soup.find_all("table", class_="completestats tablesaw")[0]

	# Cleaner csv
	as2 = allPlayers.find_all("tr")[1:]
	names = []
	for stat in as2:
		statName = stat.find_all("td")[0].text
		# We only care about these values
		onlyStats = ["Player", "Role", "Kills", "Deaths", "Assists", "CS", "Triple kills", "Quadra kills", "Penta kills", "Solo kills"]
		if statName not in onlyStats:
			continue
		for v in range(0,10):
			if statName == "Player":
				nm = stat.find_all("td")[v+1].text
				if nm not in f2:
					f2[nm] = {"First Blood": 0, "Kills": 0, "Deaths": 0, "Assists": 0, "CS": 0, "Triple kills": 0, "Quadra kills": 0, "Penta kills": 0, "Solo kills": 0, "Games Played": 0}
				f2[nm]["Games Played"] += 1
				names.append(nm)
				continue
			if statName == "Role":
				f2[names[v]][statName] = stat.find_all("td")[v+1].text
				continue
			valStat = stat.find_all("td")[v+1].text
			if not valStat:
				valStat = 0
			f2[names[v]][statName] += int(valStat)
		
	'''
	# Easier way to csv
	for i in range(0,10):
		f2.append({})
	as2 = allPlayers.find_all("tr")[1:]
	for stat in as2:	
		statName = stat.find_all("td")[0].text
		# We only care about these values
		onlyStats = ["Player", "Role", "Kills", "Deaths", "Assists", "CS", "Triple kills", "Quadra kills", "Penta kills", "Solo kills"]
		if statName not in onlyStats:
			continue
		for v in range(0,10):
			f2[v][statName] = stat.find_all("td")[v+1].text
	'''

	# First Blood link
	#
	#
	
	fb = link.split("/")
	fb[-2] = "page-timeline"
	flink = "/".join(fb)
	print(flink)

	# SOUP
	page = requests.get(flink, headers={"User-agent": "Hi"})
	
	soup = bs(page.content, "html.parser")
	
	# Get the table
	timeline = soup.find_all("table", class_="nostyle timeline trhover")[0]

	events = timeline.find_all("td")

	firstblood = ""

	for i in range(0,len(events)):
		event = events[i].find_all("img")
		if not event:
			continue
		if len(event):
			e = event[0]
			if e['src'] == "../_img/kill-icon.png":
				firstblood = events[i-2].text
				break

	if firstblood:
		f2[firstblood]["First Blood"] += 1
		'''
		for s2 in f2:
			if s2["Player"] == firstblood:
				s2["First Blood"] = True
				break
		'''

df = pd.DataFrame(f2)
df.to_csv('player.csv')

tf = pd.DataFrame(f3)
tf.to_csv('team.csv')
