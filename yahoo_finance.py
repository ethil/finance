import requests
from bs4 import BeautifulSoup

# last price
def last(ticker):

	page = requests.get("https://finance.yahoo.com/quote/"+ticker)
	content = page.text
	soup = BeautifulSoup(content, 'html.parser')
	price = float( soup.find("span", attrs={"class": "Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)", "data-reactid": "14"}).decode_contents(formatter="html") )
	print("Last price: ", price)
	
	return price

# dividend yield
def div_yield(ticker):

	dividend = 0
	page = requests.get("https://finance.yahoo.com/quote/"+ticker)
	content = page.text
	soup = BeautifulSoup(content, 'html.parser')
	#print(soup)
	try: # most stocks
		div = soup.find("td", attrs={"class": "Ta(end) Fw(600) Lh(14px)", "data-test":"DIVIDEND_AND_YIELD-value"}).decode_contents(formatter="html")
		if div != 'N/A (N/A)': # no dividend
			dividend = float(div.split(" ",1)[1][1:-2])
	except:
		try: # most ETF
			div = soup.find("span", attrs={"class":"Trsdu(0.3s)", "data-reactid":"74"}).decode_contents(formatter="html")
			dividend = float(div[:-1])
		except:
			pass

	print("Dividend yield: ", dividend)
	
	return dividend / 100
