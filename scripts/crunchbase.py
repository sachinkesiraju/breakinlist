from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from collections import defaultdict
from random import randint
from bs4 import BeautifulSoup
import time
import json
import urllib
import csv
import pdb

driver = webdriver.Safari()

with open('jquery-3.2.1.js', 'r') as jquery_js: 
	jquery = jquery_js.read() 
	#driver.execute_script(jquery) #inject jquery into selenium driver

def scrape_funding_details(company_url):
	if not company_url:
		return None

	investors_url = company_url + "/investors/investors_list"
	try:
		driver.get(investors_url)
	except TimeoutException as ex:
		writeToFile()
		print("Exception has been thrown. " + str(ex))
		driver.close()
	time.sleep(6 + randint(0, 3))

	#WebDriverWait(driver, 15).until(jquery_complete,  "Timeout waiting for page to load")
	driver.execute_script("var jq = document.createElement('script'); jq.src = 'https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js'; document.getElementsByTagName('head')[0].appendChild(jq);")
	time.sleep(3)

	#pdb.set_trace()

	# Scrape funding history
	#funding_table = driver.execute_script("return $('.grid-body').find('.grid-cell.flex.layout-row.layout-align-start-center')")
	funding_data = driver.execute_script("var vals = []; $('.grid-body').find('.grid-cell.flex.layout-row.layout-align-start-center').each(function(index, val) { vals.push($.trim($(val).text())); }); return vals;")
	investors = []
	for i in range(0, len(funding_data), 4):
		investor_name = funding_data[i]
		is_lead_investor = funding_data[i + 1]
		if is_lead_investor.strip() == "-": is_lead_investor = "No"
		funding_round = funding_data[i + 2]
		funding_round = funding_round.split('-')[0]
		funding_partners = funding_data[i + 3]
		funding_partners = funding_partners.replace('\n', '')
		funding_partners = [partner.strip() for partner in funding_partners.split(',') if funding_partners.strip() != "-"]
		print(investor_name + " " + is_lead_investor + " " + funding_round + " " + ','.join(funding_partners))
		investor = {"investor_name": investor_name, "is_lead_investor": is_lead_investor, "funding_round": funding_round, "partners": funding_partners}
		investors.append(investor)
	return investors

def writeToFile():
	with open('funding_data.json', 'a') as funding_data:
		json.dump(crunchbase_data, funding_data)

crunchbase_data = {}

try:
	# Import company list from csv
	companies = defaultdict(list) 
	with open('new_top_companies.csv') as companies_file:
		reader = csv.DictReader(companies_file)
		for row in reader: 
			for (k, v) in row.items():
				companies[k].append(v)
		companies = companies['Company Name URL']
		for company_url in companies[1920:]:
			print('\nReading company url: '+company_url)
			funding_data = scrape_funding_details(company_url)
			if not funding_data:
				continue
			crunchbase_data[company_url] = funding_data
			time.sleep(3)
except KeyboardInterrupt:
	writeToFile()
