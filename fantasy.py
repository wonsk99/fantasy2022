import requests
from bs4 import BeautifulSoup as bs

import pandas as pd

'''
#link = input("Game link from gol.gg:\n")
link = "https://gol.gg/game/stats/30016/page-game/"
page = requests.get(link, headers={"User-agent": "Hi"})

soup = bs(page.content, "html.parser")

# Get Team Names
blue_team_h = soup.find_all("div", class_="col-12 blue-line-header")[0]
red_team_h = soup.find_all("div", class_="col-12 red-line-header")[0]

blue_team = blue_team_h.find("a").text
red_team = red_team_h.find("a").text

print(blue_team)
print(red_team)
'''

# Get Player Names and Stats
#
#
#link = input("Game link from gol.gg:\n")
link = "https://gol.gg/game/stats/30016/page-fullstats/"

# Error checking
if not link:
	print(":p")
	exit()

if "page-fullstats" not in link:
	print("Error: Invalid site (make sure it is a 'page-fullstats' page)")
	exit()

if "page-fullstats/" not in link:
	link = link+"/"

# SOUP
page = requests.get(link, headers={"User-agent": "Hi"})

soup = bs(page.content, "html.parser")

# Get the table
allPlayers = soup.find_all("table", class_="completestats tablesaw")[0]

'''
allStatsNames = allPlayers.find_all("tr")[1]
allStats = allPlayers.find_all("tr")[2:]

# Initialize dictionary
fantasy = {}

# Get all the names
names = allStatsNames.find_all("td")[1:]
liNames = []
for nm in names:
	fantasy[nm.text] = {}
	liNames.append(nm.text)

# Get all the stats
for stat in allStats:
	statName = stat.find_all("td")[0].text
	for v in range(1,11):
		fantasy[liNames[v-1]][statName] = stat.find_all("td")[v].text

for n in liNames:
	print(n, fantasy[n])
	break
'''


# Easier way to csv
f2 = []
for i in range(0,10):
	f2.append({})
as2 = allPlayers.find_all("tr")[1:]
for stat in as2:	
	statName = stat.find_all("td")[0].text
	for v in range(0,10):
		f2[v][statName] = stat.find_all("td")[v+1].text


# First Blood link
#
#
fb = link.split("/")
fb[-2] = "page-timeline"
flink = "/".join(fb)

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
	for s2 in f2:
		if s2["Player"] == firstblood:
			s2["First Blood"] = True
			break

# Team Stuff link
#
#
ts = link.split("/")
ts[-2] = "page-game"
tlink = "/".join(ts)

# SOUP
page = requests.get(tlink, headers={"User-agent": "Hi"})

soup = bs(page.content, "html.parser")

teams = soup.find_all("div", class_="col-12 col-sm-6")

print(len(teams))

exit()

df = pd.DataFrame(f2)
df.to_csv('file.csv')
