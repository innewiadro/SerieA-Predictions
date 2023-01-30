import requests
from bs4 import BeautifulSoup


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

print(team_urls)