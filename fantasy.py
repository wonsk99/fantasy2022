import requests
from bs4 import BeautifulSoup as bs

import pandas as pd

# Function: getSoup
# Just shorthand to soupify
#
#
def getSoup(link):
	page = requests.get(link, headers={"User-agent": "Hi"})
	soup = bs(page.content, "html.parser")
	return soup

# Function: changeLink
# Just shorthand to jump between pages
#
#
def changeLink(link, text):
	li = link.split("/")
	li[-2] = text
	clink = "/".join(li)
	return clink

# Function: testLinks
# Test links... for testing purposes lol
#
#
def testLinks():
	LECmatchlist = "https://gol.gg/tournament/tournament-matchlist/LEC%20Spring%202022/"
	links = []

	soup = getSoup(LECmatchlist)
	matches = soup.find_all("tr")

	for match in matches:
		row = match.find_all("td")
		if not row:
			continue
		if row[4].text == "WEEK2":
			baselink = 'https://gol.gg/'
			a = row[0].find_all("a", href=True)
			matchlink = a[0]['href']
			baselink += "/".join(matchlink.split("/")[1:])
			links.append(baselink)

	print(links)
	return links

# Function: getLinks
# Get links to both regions' games
#
#
def getLinks():
	LCSmatchlist = "https://gol.gg/tournament/tournament-matchlist/LCS%20Spring%202022/"
	LECmatchlist = "https://gol.gg/tournament/tournament-matchlist/LEC%20Spring%202022/"

	eweek = input("Which week?\n")
	cweek = int(eweek) - 3
	lcsweek = "WEEK" + str(cweek)
	lecweek = "WEEK" + str(eweek)

	links = []

	for matchlist in [LCSmatchlist, LECmatchlist]:
		print("Parsing {}".format(matchlist))
		if matchlist == LCSmatchlist:
			lweek = lcsweek
		else:
			lweek = lecweek
		soup = getSoup(matchlist)
		matches = soup.find_all("tr")

		for match in matches:
			row = match.find_all("td")
			if not row:
				continue
			if row[4].text == lweek:
				baselink = 'https://gol.gg/'
				a = row[0].find_all("a", href=True)
				matchlink = a[0]['href']
				baselink += "/".join(matchlink.split("/")[1:])
				baselink = changeLink(baselink, "page-game")
				links.append(baselink)

	print("There were {} total matches in both regions".format(len(links)))
	print(links)
	return links

# Function: teamData
# Get the team data for each game
#
#
def teamData(ttdata, f3):
	tt = ttdata[0]
	ttc = ttdata[1]
	teamInfo = tt.find_all("div", class_="row")[1]	
	tTurr = int(teamInfo.find_all("span", class_="score-box " + ttc + "_line")[1].text.strip())
	at = tt.find_all("div", class_="col-2")[1].find_all("img")
	firstTurret = 0
	if len(at) == 2:
		firstTurret = 1
	
	# Dragons
	tDrag = int(teamInfo.find_all("span", class_="score-box " + ttc + "_line")[2].text.strip())

	# Elder Dragon
	dt = tt.find_all("div", class_="col-2")[2].find_all("img")

	tElders = 0
	
	for drag in dt:
		if drag['src'] == "../_img/elder-dragon.png":
			tElders += 1

	# Barons
	tBaron = int(teamInfo.find_all("span", class_="score-box " + ttc + "_line")[3].text.strip())

	# Win
	tWinfo = tt.find_all("div", class_="row")[0]

	t1 = tWinfo.find("div", class_="col-12 " + ttc + "-line-header").text.split(" - ")[0].strip()
	
	tWin = 1 if (tWinfo.find("div", class_="col-12 " + ttc + "-line-header").text.split(" - ")[1].strip() == "WIN") else 0

	# Win in < 30 min
	timeInfo = soup.find_all("div", class_="col-6 text-center")[0]
	gametime = int(timeInfo.find("h1").text.split(":")[0])
	
	tThirty = 0
	
	if gametime < 30:
		tThirty = tWin

	if t1 not in f3:
		f3[t1] = {"Turrets": 0, "Dragons": 0, "Elder Dragons": 0, "Barons": 0, "Win": 0, "Win in 30": 0, "First Turret": 0, "Games Played": 0}

	f3[t1]["Turrets"] += tTurr
	f3[t1]["Dragons"] += tDrag
	f3[t1]["Elder Dragons"] += tElders
	f3[t1]["Barons"] += tBaron
	f3[t1]["Win"] += tWin
	f3[t1]["Win in 30"] += tThirty
	f3[t1]["First Turret"] += int(firstTurret)
	f3[t1]["Games Played"] += 1

	return f3

# Function: allPlayers
# Get data for all the players
#
#
def allPlayers(soup, f2):
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

	return f2

# Function: firstBlood
# First blood info is dumb on gol.gg
#
#
def firstBlood(f2, soup):
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

	return f2

# MAIN FUNCTION
#
#
if __name__ == "__main__":
	# Player and Team Data
	fPLAYER = {}
	fTEAM = {}

	links = getLinks()
	#links = testLinks()

	for link in links:
		print("Parsing {}".format(link))
		# Team Stuff LINK
		soup = getSoup(link)
		teams = soup.find_all("div", class_="col-12 col-sm-6")
		bt = teams[0]
		rt = teams[1]

		for teamBR in [(bt,"blue"), (rt, "red")]:
			fTEAM = teamData(teamBR, fTEAM)

		# Basic INFO LINK
		tlink = changeLink(link,"page-fullstats")
		soup = getSoup(tlink)
		fPLAYER = allPlayers(soup, fPLAYER)
	
	
		# First Blood LINK
		flink = changeLink(link,"page-timeline")
		soup = getSoup(flink)
		fPLAYER = firstBlood(fPLAYER, soup)	
		

# Convert data dictionaries to CSV
df = pd.DataFrame(fPLAYER)
df.to_csv('player.csv')

tf = pd.DataFrame(fTEAM)
tf.to_csv('team.csv')
