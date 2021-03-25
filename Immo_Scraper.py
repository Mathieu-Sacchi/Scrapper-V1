from bs4 import BeautifulSoup
from selenium import webdriver
import re
import time
import unicodedata
import csv
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


def DonneesDepartement(link, departement):

    PATH = "C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    #link = "https://www.costes-viager.com/acheter/annonces/eyJsIjpudWxsLCJvIjpudWxsLCJ3YW50QVRlcm1lIjpudWxsLCJiaWVuVHlwZUlkIjotMSwiYm91cXVldCI6eyJtaW4iOm51bGwsIm1heCI6bnVsbH0sInJlbnRlIjp7Im1pbiI6bnVsbCwibWF4IjpudWxsfSwic3FsUXVlcnkiOnsiaWQiOm51bGwsImRvc3NpZXJJZHMiOm51bGwsIm1hbmRhdElkcyI6bnVsbCwib2Zmc2V0IjowLCJpZ25vcmVEb3NzaWVySWRzIjpudWxsLCJsaW1pdCI6MTAsIm9yZGVyQnkiOnt9fSwiT3B0aW9ucyI6e30sImlzRnVsbHlFeHRlbmRlZFNlYXJjaCI6ZmFsc2UsImlzRXh0ZW5kZWRTZWFyY2giOmZhbHNlLCJ3Ijp7IjMiOlt7ImlkIjo2MSwidHlwZSI6IjMiLCJsYWJlbCI6IlBBUy1ERS1DQUxBSVMtNjIgKGTDqXAuKSJ9XX19"
    driver.get(link)

    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(1)
        if new_height == last_height:
            break
        last_height = new_height

    # Once page is fully loaded

    time.sleep(1)
    html_text = driver.page_source

    soup = BeautifulSoup(html_text, 'lxml')

    list_annonces = soup.find_all('app-annonce', class_="flex-100 gap-bottom-20 ng-star-inserted")
    data_list = []


    for annonce in list_annonces:

        data_dict = {}

        for div in annonce.find_all('div'):
            if "m²" in div.text:
                description = div.text
        desc_list = description.split('-')

        data_dict["N° de département"] = departement

        type_logement = desc_list[0].strip()
        data_dict["Type de Logement"] = type_logement

        nbr_m2 = desc_list[1].split()[0]
        data_dict["Nombre de M²"] = int(nbr_m2)

        nbr_pieces = desc_list[2].split()[0]
        data_dict["Nombre de Pieces"] = int(nbr_pieces)


        commune = annonce.find('div', class_="commune").text
        if commune[-7:-5] != departement:                              # Selects for the department
            break
        data_dict["Commune"] = commune


        décote = annonce.find_all('span')[0].text[:3]+'%'
        data_dict["Décote"] = décote

        # Checks if sold
        if len(annonce.find_all('span', class_="label")) == 0:
            #link = "https://www.costes-viager.com" + annonce.find('a', class_="link")['href']
            #data_dict["Lien"] = link
            #data_dict["Vendu"] = "Oui"
            #data_list.append(data_dict)
            continue

        type_logement = annonce.find_all('span')[1].text
        data_dict["Type"] = type_logement
        if "valeur" in type_logement or "Vente" in type_logement:
            continue

        i=0
        data_dict["Age Femme"] = ""
        data_dict["Age Homme"] = ""
        data_dict["Valeur du Bien"] = ""
        data_dict["Prix d'Achat"] = ""
        data_dict["Bouquet"] = ""
        data_dict["Rente"] = ""
        for label in annonce.find_all('span', class_="label"):

            if label.text == "femme":
                age_femme = annonce.find_all('span', class_="value")[i].text
                data_dict["Age Femme"] = int(age_femme[:-3])

            if label.text == "homme":
                age_homme = annonce.find_all('span', class_="value")[i].text
                data_dict["Age Homme"] = int(age_homme[:-3])

            if label.text == "valeur du bien":
                valeur = unicodedata.normalize("NFKD", annonce.find_all('span', class_="value")[i].get_text())
                data_dict["Valeur du Bien"] = valeur

            if "prix d'achat" in label.text:
                prix = unicodedata.normalize("NFKD", annonce.find_all('span', class_="value")[i].get_text())
                data_dict["Prix d'Achat"] = prix

            if "bouquet" in label.text:
                bouquet = unicodedata.normalize("NFKD", annonce.find_all('span', class_="value")[i].get_text())
                data_dict["Bouquet"] = bouquet

            if "rente" in label.text:
                rente = unicodedata.normalize("NFKD", annonce.find_all('span', class_="value")[i].get_text())
                data_dict["Rente"] = rente

            i += 1

        link = "https://www.costes-viager.com" + annonce.find('a', class_="link")['href']
        data_dict["Lien"] = link

        # data_dict["Vendu"] = "Non"

        data_list.append(data_dict)

    return data_list

    driver.quit()

def ListDepartementData():

    list_of_departement_data = []
    departement_data_dict = {}

    for i in range(1, 96):
        if i < 10:
            departement = "0" + str(i)
        else:
            departement = str(i)

        lien = LinkDepartement(departement)

        departement_data_dict = DonneesDepartement(lien, departement)

        list_of_departement_data.extend(departement_data_dict)

    return list_of_departement_data



def LinkDepartement(departement):

    PATH = "C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    link = "https://www.costes-viager.com/"
    driver.get(link)

    time.sleep(1)

    departement_input = driver.find_element_by_id("mat-input-1")
    departement_input.send_keys(departement)

    time.sleep(1)

    ActionChains(driver).send_keys_to_element(departement_input, Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

    time.sleep(1)

    submit = driver.find_element_by_class_name("btn-validate")
    submit.send_keys(Keys.ENTER)

    time.sleep(1)

    link = driver.current_url
    driver.quit()
    print(departement)
    return link


if __name__ == '__main__':
    #print(DonneesDepartement("https://www.costes-viager.com/acheter/annonces/eyJsIjpudWxsLCJvIjpudWxsLCJ3YW50QVRlcm1lIjpudWxsLCJiaWVuVHlwZUlkIjotMSwiYm91cXVldCI6eyJtaW4iOm51bGwsIm1heCI6bnVsbH0sInJlbnRlIjp7Im1pbiI6bnVsbCwibWF4IjpudWxsfSwic3FsUXVlcnkiOnsiaWQiOm51bGwsImRvc3NpZXJJZHMiOm51bGwsIm1hbmRhdElkcyI6bnVsbCwib2Zmc2V0IjowLCJpZ25vcmVEb3NzaWVySWRzIjpudWxsLCJsaW1pdCI6MTAsIm9yZGVyQnkiOnt9fSwiT3B0aW9ucyI6e30sImlzRnVsbHlFeHRlbmRlZFNlYXJjaCI6ZmFsc2UsImlzRXh0ZW5kZWRTZWFyY2giOmZhbHNlLCJ3Ijp7IjMiOlt7ImlkIjo2MSwidHlwZSI6IjMiLCJsYWJlbCI6IlBBUy1ERS1DQUxBSVMtNjIgKGTDqXAuKSJ9XX19", '62'))
    data_list = ListDepartementData()
    print(data_list)
    print(len(data_list))

    keys = data_list[0].keys()
    with open('Viager.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_list)

