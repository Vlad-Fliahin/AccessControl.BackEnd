import requests

from bs4 import BeautifulSoup


URL = "https://bank.gov.ua/ua/markets/exchangerates"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
table = soup.find("table", id="exchangeRates")
rows = table.findAll("tr")

html_codes = table.findAll(attrs={"data-label": "Код літерний"})
codes = []
for code in html_codes:
    local_soup = BeautifulSoup(str(code), 'html.parser')
    codes.append(local_soup.text)

html_prices = table.findAll(attrs={"data-label": "Офіційний курс"})
prices = []
for code in html_prices:
    local_soup = BeautifulSoup(str(code), 'html.parser')
    prices.append(local_soup.text)
print(prices)

usd_id = codes.index('USD')
print(prices[usd_id])
print(usd_id)

