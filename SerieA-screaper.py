import requests
from bs4 import BeautifulSoup
import pandas as pd


standings_url = "https://fbref.com/en/comps/11/2021-2022/2021-2022-Serie-A-Stats"

data = requests.get(standings_url)
data.text
# print(data.text)

soup = BeautifulSoup(data.text, features="html.parser")
standings_table = soup.select('table.stats_table')[0]
links = standings_table.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if "/squads" in l]
# print(links)

team_urls = [f'https://fbref.com{l}' for l in links]

#print(team_urls)

"""Extract match stats using pandas and requests"""
team_url = team_urls[0]
data = requests.get(team_url)

matches = pd.read_html(data.text, match="Scores & Fixtures")
print(matches[0])

"""find all links"""

soup = BeautifulSoup(data.text, features="html.parser")
links = soup.find_all("a")
links = [l.get("href") for l in links]
links = [l for l in links if l and "all_comps/shooting/" in l]

"""Extract shooting stats"""
data = requests.get(f"https://fbref.com{links[0]}")
data.text

shooting = pd.read_html(data.text, match="Shooting")[0]
print(shooting.head())

"""drop columns"""
shooting.columns = shooting.columns.droplevel()

"""pandas merge data"""
team_data = matches[0].merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")

# print(shooting.shape)

"""Scraping data for multiple season and teams with a loop"""