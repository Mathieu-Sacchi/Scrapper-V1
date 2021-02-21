# pip install beautifulsoup4
# pip install lxml
# pip install requests
# pip install selenium

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from seleniumrequests import Chrome
import time
import csv

# Path to the chrome driver
PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

driver.get("https://ultimatevclist.com/")

# Click login button
login_button = driver.find_element_by_link_text("Log in")
login_button.click()

# Fill in username and password
username_field = driver.find_element_by_id("login-email")
username_field.send_keys("benoit.sui@gmail.com")
password_field = driver.find_element_by_id("Password-2")
password_field.send_keys("tqqSLbnYy3p9Qs!")
password_field.send_keys(Keys.RETURN)

# Remove filters
time.sleep(3)
unicorn_checkbox = driver.find_element_by_css_selector("div.w-dyn-item")
unicorn_checkbox.click()
stage_dropdown = driver.find_element_by_id("w-dropdown-toggle-0")
stage_dropdown.click()
seed_checkbox = driver.find_element_by_id("checkbox-3")
seed_checkbox.click()
type_dropdown = driver.find_element_by_id("w-dropdown-toggle-1")
type_dropdown.click()
type_checkbox_list = driver.find_elements_by_id("Checkbox")
vanilla_checkbox = type_checkbox_list[0]
vanilla_checkbox.click()
european_checkbox = type_checkbox_list[1]
european_checkbox.click()

# Getting html from selenium
time.sleep(1)
html_text = driver.page_source

# List of fund cards
soup = BeautifulSoup(html_text, 'lxml')
funds = soup.find_all('div', class_="fund-card")

# Collecting data for each fund
funds_data_list = []

for fund in funds:

    fund_data_dict = {}

    name = fund.find('a', class_="text-link text name").text
    fund_data_dict['Investor\'s Name'] = name

    try:
        ticket = fund.find('div', class_="type left ticket").find('div', class_="text hidden").text
    except:
        ticket = "N/A"
    # print("Ticket : " + ticket)
    if ticket != "N/A":
        fund_data_dict['Ticket Size'] = ticket

    try:
        specifics = fund.find('div', class_="type left specifics").find('div', class_="text hidden").text
    except:
        specifics = "N/A"
    if specifics != "N/A":
        fund_data_dict['Description'] = specifics

    try:
        stages = fund.find('div', class_="stages static").find_all('div', class_="tags")
    except:
        stages = "N/A"
    stage_list=[]
    for stage in stages:
        if 'w-condition-invisible' not in stage['class']:
            stage_list.append(stage.text)
    fund_data_dict['Target Stages'] = stage_list


    notable_investments = []
    investments = fund.find_all('div', class_="collection-item w-dyn-item")
    for investment in investments:
        notable_investments.append(investment.text)
    fund_data_dict['Star Investments'] = notable_investments

    funds_data_list.append(fund_data_dict)

print(funds_data_list)

time.sleep(5)
driver.quit()

keys = funds_data_list[0].keys()
with open('Investor Data.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(funds_data_list)

# expand_button_list = driver.find_elements_by_xpath("//img[@class='lottie-animation cross']")


# driver.post('https://api.memberstack.io/member/login', data = payload)


# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
