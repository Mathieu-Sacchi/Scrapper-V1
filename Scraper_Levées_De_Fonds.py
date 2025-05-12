from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv


def ListOfLinksFromPage (Page_link):
    # Path to the chrome driver
    PATH = "C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    # link = "https://www.usine-digitale.fr/les-levees-de-fonds-de-la-semaine/"
    driver.get(Page_link)

    # Getting html from selenium
    time.sleep(1)
    html_text = driver.page_source

    # Deal with notification authorisations
    time.sleep(7)
    notif1 = driver.find_element_by_class_name("pushcrew-btn-close")
    notif1.click()
    notif2 = driver.find_element_by_id("didomi-notice-agree-button")
    notif2.click()

    # List of article links
    list_of_links = []

    # List of fund cards
    soup = BeautifulSoup(html_text, 'lxml')



    #Nbr of articles
    nbr_articles = len(soup.find_all('span', class_="dateEtiquette2"))

    # Collection of links for the first page
    for i in range(nbr_articles):
        link = soup.find_all('a', class_="contenu")[i]
        date = soup.find_all('span', class_="dateEtiquette2")[i]
        list_of_links.append({
            "Date": date.text[:10],
            "URL" : link.get('href')})

    time.sleep(2)
    driver.quit()

    return list_of_links


def ListOfPageLinks(base_link):
    # Path to the chrome driver
    PATH = "C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    # link = "https://www.usine-digitale.fr/les-levees-de-fonds-de-la-semaine/"
    driver.get(base_link)

    # Getting html from selenium
    time.sleep(1)
    html_text = driver.page_source

    # Deal with notification authorisations
    time.sleep(7)
    notif1 = driver.find_element_by_class_name("pushcrew-btn-close")
    notif1.click()
    notif2 = driver.find_element_by_id("didomi-notice-agree-button")
    notif2.click()

    # List of page links
    list_of_page_links = [base_link]

    soup = BeautifulSoup(html_text, 'lxml')

    # Nbr of pages
    last_page_nbr = len(soup.find_all('li', class_="isNoMobile"))

    # Collection of links for subsequent pages
    for page_number in range(2, last_page_nbr + 1):
        page_link = str(base_link) + str(page_number) + "/"
        list_of_page_links.append(page_link)

    time.sleep(2)
    driver.quit()

    return (list_of_page_links)


def ScrapePage (page_link):
    PATH = "C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    driver.get(page_link)
    html_text = driver.page_source

    # DataList
    list_of_data_dicts_for_page = []
    list_of_levee_texts = []
    list_of_levee_names = []
    list_of_levee_amounts = []
    list_of_levee_currencies = []
    list_of_levee_descriptions = []
    list_of_lists_of_sectors = []
    list_of_lists_of_investors = []

    # List of fund cards
    soup = BeautifulSoup(html_text, 'lxml')

    for levee in soup.find_all('span', class_="interTitre"):
        list_of_levee_texts.append(levee.text)


    # print(list_of_levee_texts)

    for levee_text in list_of_levee_texts:

        levee_text_split_list = levee_text.split(' ')
        nbr_words = len(levee_text_split_list)

        levee_name = levee_text.partition("a levé")[0]
        # print(f'Name is {levee_name}')
        list_of_levee_names.append(levee_name)

        levee_amount = levee_text_split_list[nbr_words-2]
        # print("Levee amount :")
        # print(levee_amount)
        list_of_levee_amounts.append(levee_amount)

        levee_currency = levee_text_split_list[nbr_words - 1]
        # print("Levee Currency :")
        # print(levee_currency)
        list_of_levee_currencies.append(levee_currency)

    for levee in soup.find_all('p'):

        if levee.text[:1] == "\n":
            levee_description_clean = levee.text.split("\n\t")[-1].replace('\n', '')
            # Dirty fix
            if "a levé" in levee_description_clean or 'Assurer et maintenir la conformité au RGPD' in levee_description_clean or 'Se mettre concrètement en conformité' in levee_description_clean or 'Classe virtuelle' in levee_description_clean or '\xa0' in levee_description_clean:
                continue
            list_of_levee_descriptions.append(levee_description_clean)

    for levee in soup.find_all('ul'):
        test_sector = False
        test_investor = False
        for levee_line in soup.select('ul li'):
            if "Secteur" in levee_line.text:
                # print(levee.text[13:])
                #lists_of_sectors = levee_line.text[13:].split(', ')
                lists_of_sectors = levee_line.text[levee_line.text.find(":")+2:].split(', ')
                # print(levee_line.text)
                # print(lists_of_sectors)
                list_of_lists_of_sectors.append(lists_of_sectors)
                test_sector = True

            if "Investisseur" in levee_line.text:
                # print(levee.text[19:])
                lists_of_investors = levee_line.text[levee_line.text.find(":")+2:].split(', ')
                # print(lists_of_investors)
                list_of_lists_of_investors.append(lists_of_investors)
                test_investor = True

        if test_sector is False:
            list_of_lists_of_sectors.append("N/A")
        if test_investor is False:
            list_of_lists_of_investors.append("N/A")


    levee_date_text = soup.find('time', class_="dateEtiquette3").text
    levee_date = levee_date_text[10:-7]

    # Move data from lists into a list of dictionaries

    for i in range(len(list_of_levee_names)):
        # print(f'Investors in {list_of_levee_names[i]} are {list_of_lists_of_investors[i]}, see link : {page_link}')

        # Data cleaning
        if "communiqu" not in str(list_of_levee_amounts[i] + list_of_levee_currencies[i]):
            montant_levee = str(list_of_levee_amounts[i] + list_of_levee_currencies[i])
        else:
            montant_levee = "N/A"


        levee_data_dict = {
            "Date": levee_date,
            "Nom Startup": list_of_levee_names[i],
            "Montant de la Levée": montant_levee,
            # "Description": list_of_levee_descriptions[i],
            "Secteurs": list_of_lists_of_sectors[i],
            "Investisseurs": list_of_lists_of_investors[i],
            "Lien Article" : page_link,
        }
        print(levee_data_dict)
        list_of_data_dicts_for_page.append(levee_data_dict)

    # time.sleep(2)
    driver.quit()

    return list_of_data_dicts_for_page

# print(ScrapePage('https://www.usine-digitale.fr/article/campings-com-spendesk-murfy-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1017254'))


def GetLeveeDataAllPages():

    # Fetches all the répertoire pages
    # base_url = "https://www.usine-digitale.fr/les-levees-de-fonds-de-la-semaine/"
    # list_of_page_links = ListOfPageLinks(base_url)

    # Fetches all the article links
    list_of_article_links = [{'Date': '19/02/2021',
                              'URL': 'https://www.usine-digitale.fr/article/smile-mentorshow-particeep-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1062714'},
                             {'Date': '12/02/2021',
                              'URL': 'https://www.usine-digitale.fr/article/bien-ici-libeo-homa-games-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1060234'},
                             {'Date': '05/02/2021',
                              'URL': 'https://www.usine-digitale.fr/article/not-so-dark-beam-cajoo-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1057509'},
                             {'Date': '29/01/2021',
                              'URL': 'https://www.usine-digitale.fr/article/dontnod-alma-chefclub-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1055024'},
                             {'Date': '15/01/2021',
                              'URL': 'https://www.usine-digitale.fr/article/iziwork-shippeo-getfluence-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1049254'},
                             {'Date': '08/01/2021',
                              'URL': 'https://www.usine-digitale.fr/article/too-good-to-go-tagpay-volta-medical-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1046839'},
                             {'Date': '21/12/2020',
                              'URL': 'https://www.usine-digitale.fr/article/lydia-follow-health-buybox-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1041739'},
                             {'Date': '11/12/2020',
                              'URL': 'https://www.usine-digitale.fr/article/luko-gorgias-mydatamodels-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1039099'},
                             {'Date': '04/12/2020',
                              'URL': 'https://www.usine-digitale.fr/article/ankorstore-ekimetrics-pigment-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1036374'},
                             {'Date': '27/11/2020',
                              'URL': 'https://www.usine-digitale.fr/article/medadom-grai-matter-labs-affluences-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1033449'},
                             {'Date': '20/11/2020',
                              'URL': 'https://www.usine-digitale.fr/article/innovafeed-yubo-preligens-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1030924'},
                             {'Date': '13/11/2020',
                              'URL': 'https://www.usine-digitale.fr/article/livestorm-tehtris-la-boite-concept-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1027604'},
                             {'Date': '06/11/2020',
                              'URL': 'https://www.usine-digitale.fr/article/deepreach-score-secure-payment-bulldozair-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1025174'},
                             {'Date': '30/10/2020',
                              'URL': 'https://www.usine-digitale.fr/article/odaseva-kshuttle-et-syslo-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1022339'},
                             {'Date': '23/10/2020',
                              'URL': 'https://www.usine-digitale.fr/article/dimpl-beam-luxurynsight-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1019774'},
                             {'Date': '16/10/2020',
                              'URL': 'https://www.usine-digitale.fr/article/campings-com-spendesk-murfy-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1017254'},
                             {'Date': '09/10/2020',
                              'URL': 'https://www.usine-digitale.fr/article/ynsect-simple-sekoia-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1014404'},
                             {'Date': '02/10/2020',
                              'URL': 'https://www.usine-digitale.fr/article/sendinblue-exotec-pandascore-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1011849'},
                             {'Date': '25/09/2020',
                              'URL': 'https://www.usine-digitale.fr/article/mirakl-comet-meetings-qobuz-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1008899'},
                             {'Date': '18/09/2020',
                              'URL': 'https://www.usine-digitale.fr/article/swan-supermood-per-angusta-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1006059'},
                             {'Date': '11/09/2020',
                              'URL': 'https://www.usine-digitale.fr/article/sarbacane-yomoni-spacefill-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1002849'},
                             {'Date': '04/09/2020',
                              'URL': 'https://www.usine-digitale.fr/article/medaviz-badakan-garantme-les-levees-de-fonds-de-la-french-tech-cette-semaine.N999929'},
                             {'Date': '28/08/2020',
                              'URL': 'https://www.usine-digitale.fr/article/betonyou-est-la-seule-levee-de-fonds-de-la-french-tech-cette-semaine.N997564'},
                             {'Date': '07/08/2020',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-clim8-a-leve-2-75-millions-d-euros-cette-semaine.N992739'},
                             {'Date': '31/07/2020',
                              'URL': 'https://www.usine-digitale.fr/editorial/withings-klassroom-les-levees-de-fonds-de-la-semaine.N990794'},
                             {'Date': '24/07/2020',
                              'URL': 'https://www.usine-digitale.fr/article/ab-tasty-voyageurs-du-monde-biloba-les-levees-de-fonds-de-la-semaine.N988484'},
                             {'Date': '16/07/2020',
                              'URL': 'https://www.usine-digitale.fr/article/exotrail-aryballe-technologies-sorare-les-levees-de-fonds-de-la-semaine.N986609'},
                             {'Date': '10/07/2020',
                              'URL': 'https://www.usine-digitale.fr/article/synapse-medicine-unlatch-darewise-les-levees-de-fonds-de-la-semaine.N984474'},
                             {'Date': '03/07/2020',
                              'URL': 'https://www.usine-digitale.fr/article/shipup-medireport-finfrog-les-levees-de-fonds-de-la-semaine.N982151'},
                             {'Date': '26/06/2020',
                              'URL': 'https://www.usine-digitale.fr/article/swile-memo-bank-ubble-les-levees-de-fonds-de-la-semaine.N979561'},
                             {'Date': '19/06/2020',
                              'URL': 'https://www.usine-digitale.fr/article/qwarkslab-elichens-bellman-les-levees-de-fonds-de-la-semaine.N977011'},
                             {'Date': '12/06/2020',
                              'URL': 'https://www.usine-digitale.fr/article/alkemics-mediarithmics-ambler-les-levees-de-fonds-de-la-semaine.N974671'},
                             {'Date': '05/06/2020',
                              'URL': 'https://www.usine-digitale.fr/article/saagie-h4d-castalie-les-levees-de-fonds-de-la-semaine.N972141'},
                             {'Date': '29/05/2020',
                              'URL': 'https://www.usine-digitale.fr/article/aircall-la-belle-vie-courbet-les-levees-de-fonds-de-la-semaine.N969741'},
                             {'Date': '22/05/2020',
                              'URL': 'https://www.usine-digitale.fr/article/contentsquare-angell-strapi-les-levees-de-fonds-de-la-semaine.N967141'},
                             {'Date': '15/05/2020',
                              'URL': 'https://www.usine-digitale.fr/article/playplay-neocase-e-novate-les-levees-de-fonds-de-la-semaine.N964701'},
                             {'Date': '08/05/2020',
                              'URL': 'https://www.usine-digitale.fr/article/back-market-owkin-zeway-les-levees-de-fonds-de-la-semaine.N962431'},
                             {'Date': '24/04/2020',
                              'URL': 'https://www.usine-digitale.fr/article/vestaire-collective-alan-andjaro-pres-de-150-millions-d-euros-leves-par-la-french-tech-cette-semaine.N957086'},
                             {'Date': '17/04/2020',
                              'URL': 'https://www.usine-digitale.fr/article/slite-d-aim-mylight-systems-les-levees-de-fonds-de-la-semaine.N954466'},
                             {'Date': '27/04/2020',
                              'URL': 'https://www.usine-digitale.fr/article/jus-mundi-adrenalead-cosmoz-les-levees-de-fonds-de-la-semaine.N952181'},
                             {'Date': '03/04/2020',
                              'URL': 'https://www.usine-digitale.fr/article/qarnot-computing-ekwateur-cureety-les-levees-de-fonds-de-la-semaine.N949696'},
                             {'Date': '27/03/2020',
                              'URL': 'https://www.usine-digitale.fr/article/closd-qualizy-lanslot-les-levees-de-fonds-de-la-semaine.N946566'},
                             {'Date': '20/03/2020',
                              'URL': 'https://www.usine-digitale.fr/article/pixpay-wellium-coverd-les-levees-de-fonds-de-la-semaine.N943271'},
                             {'Date': '13/03/2020',
                              'URL': 'https://www.usine-digitale.fr/article/alma-akur8-energiency-les-levees-de-fonds-de-la-semaine.N939761'},
                             {'Date': '06/03/2020',
                              'URL': 'https://www.usine-digitale.fr/article/mwm-colonies-in-sun-we-trust-les-levees-de-fonds-de-la-semaine.N937329'},
                             {'Date': '28/02/2020',
                              'URL': 'https://www.usine-digitale.fr/article/cityscoot-stonly-avoloi-les-levees-de-fonds-de-la-semaine.N935004'},
                             {'Date': '21/02/2020',
                              'URL': 'https://www.usine-digitale.fr/article/esmimoz-flexifleet-r-pur-les-levees-de-fonds-de-la-semaine.N932369'},
                             {'Date': '14/02/2020',
                              'URL': 'https://www.usine-digitale.fr/article/cybelangel-shippeo-tinubu-square-les-levees-de-fonds-de-la-semaine.N929879'},
                             {'Date': '07/02/2020',
                              'URL': 'https://www.usine-digitale.fr/article/kineis-inato-convelio-les-levees-de-fonds-de-la-semaine.N927264'},
                             {'Date': '31/01/2020',
                              'URL': 'https://www.usine-digitale.fr/article/manomano-powell-software-aviwest-les-levees-de-fonds-de-la-semaine.N924794'},
                             {'Date': '24/01/2020',
                              'URL': 'https://www.usine-digitale.fr/article/qonto-lumapps-hardloop-les-levees-de-fonds-de-la-semaine.N922579'},
                             {'Date': '17/01/2020',
                              'URL': 'https://www.usine-digitale.fr/article/lydia-matera-simplifield-les-levees-de-fonds-de-la-semaine.N920674'},
                             {'Date': '10/01/2020',
                              'URL': 'https://www.usine-digitale.fr/article/ecovadis-weblib-adux-les-levees-de-fonds-de-la-semaine.N918274'},
                             {'Date': '03/01/2020',
                              'URL': 'https://www.usine-digitale.fr/article/majelan-osmosis-click-care-les-levees-de-fonds-de-la-semaine.N916694'},
                             {'Date': '20/12/2019',
                              'URL': 'https://www.usine-digitale.fr/article/dreamquark-efficientip-picto-voici-les-levees-de-fonds-de-la-semaine.N915009'},
                             {'Date': '13/12/2019',
                              'URL': 'https://www.usine-digitale.fr/article/intercloud-outsight-qwil-les-levees-de-fonds-de-la-semaine.N912879'},
                             {'Date': '06/12/2019',
                              'URL': 'https://www.usine-digitale.fr/article/gitguardian-sancar-lota-cloud-les-levees-de-fonds-de-la-semaine.N910874'},
                             {'Date': '29/11/2019',
                              'URL': 'https://www.usine-digitale.fr/article/sewan-leavy-toucan-toco-les-levees-de-fonds-de-la-semaine.N908564'},
                             {'Date': '15/11/2019',
                              'URL': 'https://www.usine-digitale.fr/article/finfrog-net-reviews-wittyfit-les-levees-de-fonds-de-la-semaine.N903754'},
                             {'Date': '08/11/2019',
                              'URL': 'https://www.usine-digitale.fr/article/hoppen-libeo-neofarm-les-levees-de-fonds-de-la-semaine.N901929'},
                             {'Date': '01/11/2019',
                              'URL': 'https://www.usine-digitale.fr/article/vade-secure-brut-blade-les-levees-de-fonds-de-la-semaine.N899879'},
                             {'Date': '25/10/2019',
                              'URL': 'https://www.usine-digitale.fr/article/madbox-nicecactus-smaaart-les-levees-de-fonds-de-la-semaine.N897629'},
                             {'Date': '18/10/2019',
                              'URL': 'https://www.usine-digitale.fr/article/algolia-lemon-way-herow-les-levees-de-fonds-de-la-semaine.N895664'},
                             {'Date': '11/10/2019',
                              'URL': 'https://www.usine-digitale.fr/article/incepto-packetai-acinq-les-levees-de-fonds-de-la-semaine.N893304'},
                             {'Date': '27/09/2019',
                              'URL': 'https://www.usine-digitale.fr/article/meshroomvr-splio-lancey-les-levees-de-fonds-de-la-semaine.N888829'},
                             {'Date': '20/09/2019',
                              'URL': 'https://www.usine-digitale.fr/article/levee-de-fonds.N886094'},
                             {'Date': '13/09/2019',
                              'URL': 'https://www.usine-digitale.fr/article/akeneo-jobteaser-spendesk-les-start-up-de-la-french-tech-levent-plus-de-167-millions-d-euros.N883979'},
                             {'Date': '06/09/2019',
                              'URL': 'https://www.usine-digitale.fr/article/ubitransport-heuritech-ilek-les-levees-de-fonds-de-la-semaine.N881445'},
                             {'Date': '30/08/2019',
                              'URL': 'https://www.usine-digitale.fr/article/manager-one-lilm-les-levees-de-fonds-de-la-semaine.N878870'},
                             {'Date': '09/08/2019',
                              'URL': 'https://www.usine-digitale.fr/article/levees-de-fonds-de-la-semaine-nouga-obtient-850-000-euros.N873935'},
                             {'Date': '19/07/2019',
                              'URL': 'https://www.usine-digitale.fr/article/traxens-mailingblack-teaminside-les-levees-de-fonds-de-la-semaine.N868060'},
                             {'Date': '05/07/2019',
                              'URL': 'https://www.usine-digitale.fr/article/ornikar-dott-cubyn-les-levees-de-fonds-de-la-semaine.N862940'},
                             {'Date': '28/06/2019',
                              'URL': 'https://www.usine-digitale.fr/article/metron-bleckwen-taster-les-levees-de-fonds-de-la-semaine.N860515'},
                             {'Date': '21/06/2019',
                              'URL': 'https://www.usine-digitale.fr/article/meero-payfit-bioserenity-les-levees-de-fonds-de-la-semaine.N857815'},
                             {'Date': '14/06/2019',
                              'URL': 'https://www.usine-digitale.fr/article/vade-secure-lifen-ekwateur-voici-les-levees-de-fonds-de-la-semaine.N854635'},
                             {'Date': '31/05/2019',
                              'URL': 'https://www.usine-digitale.fr/article/visible-patient-atolia-mindsay-voici-les-levees-de-fonds-de-la-semaine.N849435'},
                             {'Date': '17/05/2019',
                              'URL': 'https://www.usine-digitale.fr/article/plus-de-30-m-leves-par-les-start-up-de-la-french-tech-cette-semaine.N844130'},
                             {'Date': '10/05/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/heetch-pixpay-brigad-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N841075'},
                             {'Date': '26/04/2019',
                              'URL': 'https://www.usine-digitale.fr/article/otonomy-wemaintain-swikly-voici-les-levees-de-fonds-de-la-french-tech-cette-semaine.N836275'},
                             {'Date': '19/04/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/360learning-lumapps-bankin-les-levees-de-fonds-de-la-semaine.N833515'},
                             {'Date': '12/04/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/qare-devialet-wilov-combien-les-start-up-ont-elles-leve-cette-semaine.N830430'},
                             {'Date': '05/04/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/ces-9-start-up-ont-leve-pres-de-257-m-cette-semaine.N827435'},
                             {'Date': '29/03/2019',
                              'URL': 'https://www.usine-digitale.fr/article/kyriba-cycloid-wgf-les-levees-de-fonds-de-la-semaine.N824260'},
                             {'Date': '22/03/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/doctolib-iteca-oslo-les-levees-de-fonds-de-la-semaine.N821315'},
                             {'Date': '15/03/2019',
                              'URL': 'https://www.usine-digitale.fr/article/plus-de-33-m-leves-par-les-start-up-de-la-french-tech-cette-semaine.N818660'},
                             {'Date': '08/03/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/ces-4-start-up-ont-leve-un-total-de-plus-de-58-m-cette-semaine.N815360'},
                             {'Date': '01/03/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/plus-de-112-millions-d-euros-levees-par-les-start-up-de-la-french-tech-cette-semaine.N812850'},
                             {'Date': '22/02/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/alan-sybel-thegreendata-le-recap-des-levees-de-fonds-de-la-semaine.N809770'},
                             {'Date': '15/02/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/malt-yes-we-hack-call-a-lawyer-les-levees-de-fonds-de-la-semaine.N806855'},
                             {'Date': '08/02/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/lunchr-pretto-testamento-combien-les-start-up-francaises-ont-elles-leve-cette-semaine.N804045'},
                             {'Date': '04/02/2019',
                              'URL': 'https://www.usine-digitale.fr/article/contentsquare-zenpark-diota-combien-les-start-up-de-la-french-tech-ont-elles-leve-la-semaine-derniere.N801710'},
                             {'Date': '25/01/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/wynd-schoolab-mooncard-combien-les-start-up-ont-elles-leve-cette-semaine.N797965'},
                             {'Date': '18/01/2019',
                              'URL': 'https://www.usine-digitale.fr/article/onepark-my-serious-game-singulart-combien-les-start-up-ont-elles-leve-cette-semaine.N794664'},
                             {'Date': '11/01/2019',
                              'URL': 'https://www.usine-digitale.fr/editorial/talentsoft-monbuilding-papyhappy-les-levees-de-fonds-de-la-semaine.N791114'},
                             {'Date': '14/12/2018',
                              'URL': 'https://www.usine-digitale.fr/article/finalcad-early-metrics-expensya-les-levees-de-fonds-de-la-semaine.N783539'},
                             {'Date': '07/12/2018',
                              'URL': 'https://www.usine-digitale.fr/article/agricool-sentryo-zelros-les-levees-de-fond-de-la-semaine.N780069'},
                             {'Date': '30/11/2018',
                              'URL': 'https://www.usine-digitale.fr/editorial/happytal-selency-air-affaires-les-levees-de-fonds-de-la-semaine.N777004'},
                             {'Date': '16/11/2018',
                              'URL': 'https://www.usine-digitale.fr/article/blablacar-melty-packitoo-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N770329'},
                             {'Date': '09/11/2018',
                              'URL': 'https://www.usine-digitale.fr/article/levee-de-fonds.N767199'},
                             {'Date': '26/10/2018',
                              'URL': 'https://www.usine-digitale.fr/article/padoa-syntony-crosscall-les-levees-de-fond-de-la-semaine.N760879'},
                             {'Date': '19/10/2018',
                              'URL': 'https://www.usine-digitale.fr/editorial/universign-foodvisor-carlili-combien-les-start-up-francaises-ont-elles-leve-cette-semaine.N757814'},
                             {'Date': '12/10/2018',
                              'URL': 'https://www.usine-digitale.fr/editorial/braincube-jow-shopopop-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N754479'},
                             {'Date': '28/09/2018',
                              'URL': 'https://www.usine-digitale.fr/editorial/qonto-iziwork-hydrao-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N747974'},
                             {'Date': '07/09/2018',
                              'URL': 'https://www.usine-digitale.fr/editorial/shine-velco-pricemoov-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N738419'},
                             {'Date': '24/08/2018',
                              'URL': 'https://www.usine-digitale.fr/editorial/emplio-moona-mainbot-combien-ont-leve-les-start-up-de-la-french-tech-cette-semaine.N732929'},
                             {'Date': '10/08/2018',
                              'URL': 'https://www.usine-digitale.fr/article/akewatu-welovedevs-kwit-immopop-finalgo-voici-les-levees-de-fonds-des-start-up-de-la-semaine.N729929'},
                             {'Date': '27/07/2018',
                              'URL': 'https://www.usine-digitale.fr/article/comwatt-wiidii-wimi-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N725404'},
                             {'Date': '20/07/2018',
                              'URL': 'https://www.usine-digitale.fr/article/lemon-way-tagpay-stimergy-les-levees-de-fonds-des-startups-de-la-semaine.N722399'},
                             {'Date': '13/07/2018',
                              'URL': 'https://www.usine-digitale.fr/editorial/meero-brut-captain-wallet-voici-les-levees-de-fonds-des-start-up-de-la-french-tech-cette-semaine.N719479'},
                             {'Date': '06/07/2018',
                              'URL': 'https://www.usine-digitale.fr/article/izicap-doctrine-influence4you-combien-les-startups-ont-elles-leve-cette-semaine.N716604'},
                             {'Date': '29/06/2018',
                              'URL': 'https://www.usine-digitale.fr/article/dreem-eyelights-fly4u-les-levees-de-fonds-des-startups-de-la-semaine.N713644'},
                             {'Date': '22/06/2018',
                              'URL': 'https://www.usine-digitale.fr/article/feed-paytweak-onoff-tiller-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N710624'},
                             {'Date': '15/06/2018',
                              'URL': 'https://www.usine-digitale.fr/editorial/plus-de-75-m-leves-par-les-start-up-de-la-french-tech-cette-semaine.N707474'},
                             {'Date': '09/06/2018',
                              'URL': 'https://www.usine-digitale.fr/article/lendix-perfectstay-swapcard-sezane-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N704134'},
                             {'Date': '01/06/2018',
                              'URL': 'https://www.usine-digitale.fr/article/les-levees-de-fonds-de-la-semaine.N701189'},
                             {'Date': '25/05/2018',
                              'URL': 'https://www.usine-digitale.fr/article/combien-ont-leve-les-start-up-de-la-french-tech-cette-semaine.N698279'},
                             {'Date': '11/05/2018',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-ultra-premium-direct-lita-co-orinox-les-levees-de-fonds-des-start-up-de-la-semaine.N692069'},
                             {'Date': '27/04/2018',
                              'URL': 'https://www.usine-digitale.fr/article/attestation-legale-slite-tilkee-hubrix-les-levees-de-fonds-de-la-semaine.N686634'},
                             {'Date': '20/04/2018',
                              'URL': 'https://www.usine-digitale.fr/article/les-levees-de-fonds-de-la-semaine.N683084'},
                             {'Date': '13/04/2018',
                              'URL': 'https://www.usine-digitale.fr/editorial/alan-singlespot-wesprint-les-levees-de-fonds-des-start-up-de-la-french-tech-cette-semaine.N679754'},
                             {'Date': '06/04/2018',
                              'URL': 'https://www.usine-digitale.fr/editorial/les-start-up-de-la-french-tech-ont-leve-6-2-m-cette-semaine.N676509'},
                             {'Date': '30/03/2018',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-comet-meetings-supervizor-ayomi-les-levees-de-fonds-de-la-semaine.N674089'},
                             {'Date': '23/03/2018',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-ornikar-antvoice-seald-les-start-up-ont-leve-plus-de-25-millions-d-euros-cette-semaine.N670629'},
                             {'Date': '16/03/2018',
                              'URL': 'https://www.usine-digitale.fr/article/les-levees-de-fonds-de-la-semaine.N667524'},
                             {'Date': '09/03/2018',
                              'URL': 'https://www.usine-digitale.fr/article/pres-de-41-m-leves-par-les-start-up-de-la-french-tech-cette-semaine.N664219'},
                             {'Date': '02/03/2018',
                              'URL': 'https://www.usine-digitale.fr/editorial/french-tech-habx-kalti-mirsense-hyperlex-les-levees-de-fonds-des-start-up-cette-semaine.N660924'},
                             {'Date': '23/02/2018',
                              'URL': 'https://www.usine-digitale.fr/article/les-levees-de-fonds-de-la-semaine.N657749'},
                             {'Date': '16/02/2018',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-xx-millions-d-euros-leves-par-xx-start-up-cette-semaine.N654649'},
                             {'Date': '09/02/2018',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-122-millions-d-euros-leves-par-15-start-up-cette-semaine.N651229'},
                             {'Date': '02/02/2018',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-145-millions-d-euros-leves-par-18-start-up-cette-semaine.N647373'},
                             {'Date': '26/01/2018',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-saagie-yousign-smile-pay-les-levees-de-fonds-de-la-semaine.N643848'},
                             {'Date': '19/01/2018',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-100-millions-d-euros-leves-par-13-start-up-cette-semaine.N640563'},
                             {'Date': '12/01/2018',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-simple-sellsy-lengow-les-levees-de-fonds-de-la-semaine.N636958'},
                             {'Date': '26/12/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-les-10-plus-grosses-levees-de-fonds-de-l-annee-2017.N631268'},
                             {'Date': '22/12/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-13-5-millions-d-euros-leves-par-11-start-up-cette-semaine.N631228'},
                             {'Date': '15/12/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-23-millions-d-euros-leves-par-10-start-up-cette-semaine.N628178'},
                             {'Date': '08/12/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-37-millions-d-euros-leves-par-13-start-up-cette-semaine.N624963'},
                             {'Date': '01/12/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-12-start-up-ont-leve-plus-de-63-millions-d-euros-cette-semaine.N621838'},
                             {'Date': '27/11/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-18-millions-d-euros-leves-par-13-start-up-cette-semaine.N618188'},
                             {'Date': '17/11/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-83-millions-d-euros-leves-par-15-start-up-cette-semaine.N615553'},
                             {'Date': '10/11/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-19-millions-d-euros-leves-par-12-start-up-cette-semaine.N612368'},
                             {'Date': '03/11/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-un-peu-plus-de-8-millions-d-euros-leves-par-5-start-up-cette-semaine.N609403'},
                             {'Date': '27/10/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-94-millions-d-euros-leves-par-14-start-up-cette-semaine.N606528'},
                             {'Date': '20/10/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-pres-de-34-millions-d-euros-leves-par-20-start-up-cette-semaine.N603363'},
                             {'Date': '24/10/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-11-start-up-ont-leve-plus-de-11-millions-d-euros-cette-semaine.N600038'},
                             {'Date': '06/10/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-95-millions-d-euros-leves-par-17-start-up-cette-semaine.N596788'},
                             {'Date': '29/09/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-78-millions-d-euros-leves-par-17-start-up-cette-semaine.N593888'},
                             {'Date': '22/09/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-87-millions-d-euros-leves-par-17-start-up-cette-semaine.N590653'},
                             {'Date': '15/09/2017',
                              'URL': 'https://www.usine-digitale.fr/article/semaine-fructueuse-pour-la-french-tech-avec-plus-de-126m-leves.N587623'},
                             {'Date': '08/09/2017',
                              'URL': 'https://www.usine-digitale.fr/article/belle-rentree-pour-la-french-tech-12-start-up-ont-leve-plus-de-83-millions-d-euros.N584603'},
                             {'Date': '01/09/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-4-start-up-ont-leve-plus-de-23-millions-d-euros-fin-aout.N581698'},
                             {'Date': '18/08/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-les-montants-leves-en-2017-devraient-doubler-par-rapport-a-2016.N577533'},
                             {'Date': '04/08/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-skillup-bowkr-les-levees-de-fonds-de-la-semaine.N573893'},
                             {'Date': '28/07/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-alltricks-o-gaming-lotprive-les-levees-de-fonds-de-la-semaine.N571558'},
                             {'Date': '14/07/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-22-4-millions-d-euros-leves-par-10-start-up-cette-semaine.N566059'},
                             {'Date': '07/07/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-66-millions-d-euros-leves-par-26-start-up-cette-semaine.N563042'},
                             {'Date': '30/06/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-22-millions-d-euros-leves-par-13-start-up-cette-semaine.N560188'},
                             {'Date': '16/06/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-15-start-up-ont-leve-83-millions-d-euros-cette-semaine.N553838'},
                             {'Date': '09/06/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-90-millions-d-euros-leves-par-15-start-up-cette-semaine.N550673'},
                             {'Date': '02/06/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-29-millions-d-euros-leves-par-15-start-up-cette-semaine.N547783'},
                             {'Date': '26/05/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-six-start-up-ont-leve-plus-de-65-millions-d-euros-cette-semaine.N545233'},
                             {'Date': '19/05/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-8-start-up-ont-leve-un-total-de-plus-de-52-millions-d-euros-cette-semaine.N542619'},
                             {'Date': '12/05/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-au-total-ces-14-start-up-ont-leve-plus-de-36-millions-d-euros-cette-semaine.N539489'},
                             {'Date': '05/05/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-pres-de-18-millions-d-euros-leves-par-7-start-up-cette-semaine.N536069'},
                             {'Date': '28/04/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-78-millions-d-euros-leves-par-6-start-up-cette-semaine.N533159'},
                             {'Date': '21/04/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-11-millions-d-euros-leves-par-9-start-up-cette-semaine.N529829'},
                             {'Date': '14/04/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-113-millions-d-euros-leves-par-9-start-up-cette-semaine.N527254'},
                             {'Date': '07/04/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-17-7-millions-d-euros-leves-par-7-start-up-cette-semaine.N524679'},
                             {'Date': '31/03/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-90-millions-d-euros-leves-par-13-start-up-cette-semaine.N521759'},
                             {'Date': '24/03/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-13-start-up-ont-leve-plus-de-37-millions-d-euros-cette-semaine.N518874'},
                             {'Date': '17/03/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-12-start-up-ont-leve-plus-de-18-millions-d-euros-cette-semaine.N515899'},
                             {'Date': '10/03/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-55-millions-d-euros-leves-par-11-start-up-cette-semaine.N512749'},
                             {'Date': '03/03/2017',
                              'URL': 'https://www.usine-digitale.fr/article/ces-six-start-up-de-la-french-tech-ont-leve-plus-de-11-millions-d-euros.N509699'},
                             {'Date': '24/02/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-41-millions-d-euros-leves-par-9-start-up-cette-semaine.N506439'},
                             {'Date': '17/02/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-6-5-millions-d-euros-leves-par-7-start-up-cette-semaine.N503484'},
                             {'Date': '10/02/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-7-start-up-ont-leve-plus-de-15-millions-d-euros-cette-semaine.N500154'},
                             {'Date': '06/02/2017',
                              'URL': 'https://www.usine-digitale.fr/article/qwant-resto-flash-yomoni-les-levees-de-fonds-de-la-semaine.N496709'},
                             {'Date': '20/01/2017',
                              'URL': 'https://www.usine-digitale.fr/editorial/ces-17-start-up-de-la-french-tech-ont-leve-plus-de-37m-d-euros-cette-semaine.N490549'},
                             {'Date': '13/01/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-23-millions-d-euros-leves-par-9-start-up-cette-semaine.N487329'},
                             {'Date': '06/01/2017',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-6-start-up-ont-leve-plus-de-5-millions-d-euros-cette-semaine.N484569'},
                             {'Date': '23/12/2016',
                              'URL': 'https://www.usine-digitale.fr/article/10-start-up-ont-leve-plus-de-6-5-m-cette-semaine.N480714'},
                             {'Date': '16/12/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-57-millions-d-euros-leves-par-12-start-up-cette-semaine.N478034'},
                             {'Date': '09/12/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-55-millions-d-euros-leves-par-8-start-up-cette-semaine.N474794'},
                             {'Date': '25/11/2016',
                              'URL': 'https://www.usine-digitale.fr/article/a-elles-7-ces-start-up-francaises-ont-leve-plus-de-190-millions-d-euros-cette-semaine.N468428'},
                             {'Date': '18/11/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-18-millions-d-euros-leves-par-9-start-up-cette-semaine.N465733'},
                             {'Date': '11/11/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-8-4-millions-d-euros-leves-par-8-start-up-cette-semaine.N462773'},
                             {'Date': '04/11/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-13-millions-d-euros-leves-par-8-start-up-cette-semaine.N459542'},
                             {'Date': '28/10/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-12-start-up-ont-leve-plus-de-65-millions-d-euros-cette-semaine.N456842'},
                             {'Date': '21/10/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-14-start-up-ont-leve-plus-de-44-millions-d-euros-cette-semaine.N453862'},
                             {'Date': '14/10/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-81-7-millions-d-euros-investis-dans-19-start-up.N451047'},
                             {'Date': '08/10/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-13-start-up-ont-leve-22-millions-d-euros-cette-semaine.N448357'},
                             {'Date': '30/09/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-92-millions-d-euros-leves-par-21-start-up-cette-semaine.N444407'},
                             {'Date': '23/09/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-37-millions-d-euros-leves-par-21-start-up-cette-semaine.N441097'},
                             {'Date': '09/09/2016',
                              'URL': 'https://www.usine-digitale.fr/article/rentree-en-fanfare-pour-la-french-tech-92-millions-d-euros-leves-par-15-start-up-cette-semaine.N435022'},
                             {'Date': '02/09/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-9-millions-d-euros-leves-par-7-startups-cette-semaine.N432107'},
                             {'Date': '05/08/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-7-millions-d-euros-leves-par-3-start-up-cette-semaine.N422222'},
                             {'Date': '22/07/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-6-4-millions-d-euros-leves-par-3-start-up-cette-semaine.N403462'},
                             {'Date': '15/07/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-30-millions-d-euros-leves-par-14-start-up-cette-semaine.N402797'},
                             {'Date': '08/07/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-22-millions-d-euros-leves-par-13-startups-cette-semaine.N401767'},
                             {'Date': '01/07/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-29-millions-d-euros-leves-par-16-start-up-cette-semaine.N400547'},
                             {'Date': '24/06/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-65-millions-d-euros-leves-par-19-start-up-cette-semaine.N399002'},
                             {'Date': '17/06/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-16-8-millions-d-euros-leves-par-16-startups-cette-semaine.N397702'},
                             {'Date': '10/06/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-32-millions-d-euros-leves-par-14-start-up-cette-semaine.N396382'},
                             {'Date': '03/06/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-15-millions-d-euros-leves-par-11-start-up-cette-semaine.N394912'},
                             {'Date': '27/05/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-20-millions-d-euros-leves-par-10-start-up-cette-semaine.N393607'},
                             {'Date': '20/05/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-11-start-up-ont-leve-15-millions-d-euros-cette-semaine.N392337'},
                             {'Date': '13/05/2016',
                              'URL': 'https://www.usine-digitale.fr/article/french-tech-9-start-up-ont-leve-36-millions-d-euros-cette-semaine.N391347'},
                             {'Date': '12/05/2016',
                              'URL': 'https://www.usine-digitale.fr/article/interaction-healthcare-la-pepite-qui-simule-les-cas-cliniques-leve-5-millions-d-euros.N391097'}]

    # list_of_article_links = []
    # for page_link in list_of_page_links:
        # list_of_article_links.extend(ListOfLinksFromPage(page_link))
    # print(list_of_article_links)

    # Fetches all the data from the pages
    # old_link_stop = False
    list_of_data_dicts=[]
    for article_link in list_of_article_links:
        if article_link["URL"] == "https://www.usine-digitale.fr/article/a-elles-7-ces-start-up-francaises-ont-leve-plus-de-190-millions-d-euros-cette-semaine.N468428":
            break
        # For some reason couldn't get it to work for these pages so i skipped 👉👈
        elif article_link["URL"] == "https://www.usine-digitale.fr/article/dontnod-alma-chefclub-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1055024":
            continue
        # elif article_link["URL"] == "https://www.usine-digitale.fr/article/exotrail-aryballe-technologies-sorare-les-levees-de-fonds-de-la-semaine.N986609":
            # continue
        elif article_link["URL"] == 'https://www.usine-digitale.fr/article/finalcad-early-metrics-expensya-les-levees-de-fonds-de-la-semaine.N783539':
            continue



        list_of_data_dicts_for_page = ScrapePage(article_link["URL"])
        list_of_data_dicts.extend(list_of_data_dicts_for_page)

    return (list_of_data_dicts)


data_list = GetLeveeDataAllPages()

keys = data_list[0].keys()
with open('Levée Data.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data_list)

list_of_article_links = [{'Date': '19/02/2021', 'URL': 'https://www.usine-digitale.fr/article/smile-mentorshow-particeep-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1062714'}, {'Date': '12/02/2021', 'URL': 'https://www.usine-digitale.fr/article/bien-ici-libeo-homa-games-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1060234'}, {'Date': '05/02/2021', 'URL': 'https://www.usine-digitale.fr/article/not-so-dark-beam-cajoo-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1057509'}, {'Date': '29/01/2021', 'URL': 'https://www.usine-digitale.fr/article/dontnod-alma-chefclub-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1055024'}, {'Date': '15/01/2021', 'URL': 'https://www.usine-digitale.fr/article/iziwork-shippeo-getfluence-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1049254'}, {'Date': '08/01/2021', 'URL': 'https://www.usine-digitale.fr/article/too-good-to-go-tagpay-volta-medical-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1046839'}, {'Date': '21/12/2020', 'URL': 'https://www.usine-digitale.fr/article/lydia-follow-health-buybox-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1041739'}, {'Date': '11/12/2020', 'URL': 'https://www.usine-digitale.fr/article/luko-gorgias-mydatamodels-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1039099'}, {'Date': '04/12/2020', 'URL': 'https://www.usine-digitale.fr/article/ankorstore-ekimetrics-pigment-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1036374'}, {'Date': '27/11/2020', 'URL': 'https://www.usine-digitale.fr/article/medadom-grai-matter-labs-affluences-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1033449'}, {'Date': '20/11/2020', 'URL': 'https://www.usine-digitale.fr/article/innovafeed-yubo-preligens-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1030924'}, {'Date': '13/11/2020', 'URL': 'https://www.usine-digitale.fr/article/livestorm-tehtris-la-boite-concept-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1027604'}, {'Date': '06/11/2020', 'URL': 'https://www.usine-digitale.fr/article/deepreach-score-secure-payment-bulldozair-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1025174'}, {'Date': '30/10/2020', 'URL': 'https://www.usine-digitale.fr/article/odaseva-kshuttle-et-syslo-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1022339'}, {'Date': '23/10/2020', 'URL': 'https://www.usine-digitale.fr/article/dimpl-beam-luxurynsight-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1019774'}, {'Date': '16/10/2020', 'URL': 'https://www.usine-digitale.fr/article/campings-com-spendesk-murfy-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1017254'}, {'Date': '09/10/2020', 'URL': 'https://www.usine-digitale.fr/article/ynsect-simple-sekoia-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1014404'}, {'Date': '02/10/2020', 'URL': 'https://www.usine-digitale.fr/article/sendinblue-exotec-pandascore-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1011849'}, {'Date': '25/09/2020', 'URL': 'https://www.usine-digitale.fr/article/mirakl-comet-meetings-qobuz-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1008899'}, {'Date': '18/09/2020', 'URL': 'https://www.usine-digitale.fr/article/swan-supermood-per-angusta-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1006059'}, {'Date': '11/09/2020', 'URL': 'https://www.usine-digitale.fr/article/sarbacane-yomoni-spacefill-les-levees-de-fonds-de-la-french-tech-cette-semaine.N1002849'}, {'Date': '04/09/2020', 'URL': 'https://www.usine-digitale.fr/article/medaviz-badakan-garantme-les-levees-de-fonds-de-la-french-tech-cette-semaine.N999929'}, {'Date': '28/08/2020', 'URL': 'https://www.usine-digitale.fr/article/betonyou-est-la-seule-levee-de-fonds-de-la-french-tech-cette-semaine.N997564'}, {'Date': '07/08/2020', 'URL': 'https://www.usine-digitale.fr/article/french-tech-clim8-a-leve-2-75-millions-d-euros-cette-semaine.N992739'}, {'Date': '31/07/2020', 'URL': 'https://www.usine-digitale.fr/editorial/withings-klassroom-les-levees-de-fonds-de-la-semaine.N990794'}, {'Date': '24/07/2020', 'URL': 'https://www.usine-digitale.fr/article/ab-tasty-voyageurs-du-monde-biloba-les-levees-de-fonds-de-la-semaine.N988484'}, {'Date': '16/07/2020', 'URL': 'https://www.usine-digitale.fr/article/exotrail-aryballe-technologies-sorare-les-levees-de-fonds-de-la-semaine.N986609'}, {'Date': '10/07/2020', 'URL': 'https://www.usine-digitale.fr/article/synapse-medicine-unlatch-darewise-les-levees-de-fonds-de-la-semaine.N984474'}, {'Date': '03/07/2020', 'URL': 'https://www.usine-digitale.fr/article/shipup-medireport-finfrog-les-levees-de-fonds-de-la-semaine.N982151'}, {'Date': '26/06/2020', 'URL': 'https://www.usine-digitale.fr/article/swile-memo-bank-ubble-les-levees-de-fonds-de-la-semaine.N979561'}, {'Date': '19/06/2020', 'URL': 'https://www.usine-digitale.fr/article/qwarkslab-elichens-bellman-les-levees-de-fonds-de-la-semaine.N977011'}, {'Date': '12/06/2020', 'URL': 'https://www.usine-digitale.fr/article/alkemics-mediarithmics-ambler-les-levees-de-fonds-de-la-semaine.N974671'}, {'Date': '05/06/2020', 'URL': 'https://www.usine-digitale.fr/article/saagie-h4d-castalie-les-levees-de-fonds-de-la-semaine.N972141'}, {'Date': '29/05/2020', 'URL': 'https://www.usine-digitale.fr/article/aircall-la-belle-vie-courbet-les-levees-de-fonds-de-la-semaine.N969741'}, {'Date': '22/05/2020', 'URL': 'https://www.usine-digitale.fr/article/contentsquare-angell-strapi-les-levees-de-fonds-de-la-semaine.N967141'}, {'Date': '15/05/2020', 'URL': 'https://www.usine-digitale.fr/article/playplay-neocase-e-novate-les-levees-de-fonds-de-la-semaine.N964701'}, {'Date': '08/05/2020', 'URL': 'https://www.usine-digitale.fr/article/back-market-owkin-zeway-les-levees-de-fonds-de-la-semaine.N962431'}, {'Date': '24/04/2020', 'URL': 'https://www.usine-digitale.fr/article/vestaire-collective-alan-andjaro-pres-de-150-millions-d-euros-leves-par-la-french-tech-cette-semaine.N957086'}, {'Date': '17/04/2020', 'URL': 'https://www.usine-digitale.fr/article/slite-d-aim-mylight-systems-les-levees-de-fonds-de-la-semaine.N954466'}, {'Date': '27/04/2020', 'URL': 'https://www.usine-digitale.fr/article/jus-mundi-adrenalead-cosmoz-les-levees-de-fonds-de-la-semaine.N952181'}, {'Date': '03/04/2020', 'URL': 'https://www.usine-digitale.fr/article/qarnot-computing-ekwateur-cureety-les-levees-de-fonds-de-la-semaine.N949696'}, {'Date': '27/03/2020', 'URL': 'https://www.usine-digitale.fr/article/closd-qualizy-lanslot-les-levees-de-fonds-de-la-semaine.N946566'}, {'Date': '20/03/2020', 'URL': 'https://www.usine-digitale.fr/article/pixpay-wellium-coverd-les-levees-de-fonds-de-la-semaine.N943271'}, {'Date': '13/03/2020', 'URL': 'https://www.usine-digitale.fr/article/alma-akur8-energiency-les-levees-de-fonds-de-la-semaine.N939761'}, {'Date': '06/03/2020', 'URL': 'https://www.usine-digitale.fr/article/mwm-colonies-in-sun-we-trust-les-levees-de-fonds-de-la-semaine.N937329'}, {'Date': '28/02/2020', 'URL': 'https://www.usine-digitale.fr/article/cityscoot-stonly-avoloi-les-levees-de-fonds-de-la-semaine.N935004'}, {'Date': '21/02/2020', 'URL': 'https://www.usine-digitale.fr/article/esmimoz-flexifleet-r-pur-les-levees-de-fonds-de-la-semaine.N932369'}, {'Date': '14/02/2020', 'URL': 'https://www.usine-digitale.fr/article/cybelangel-shippeo-tinubu-square-les-levees-de-fonds-de-la-semaine.N929879'}, {'Date': '07/02/2020', 'URL': 'https://www.usine-digitale.fr/article/kineis-inato-convelio-les-levees-de-fonds-de-la-semaine.N927264'}, {'Date': '31/01/2020', 'URL': 'https://www.usine-digitale.fr/article/manomano-powell-software-aviwest-les-levees-de-fonds-de-la-semaine.N924794'}, {'Date': '24/01/2020', 'URL': 'https://www.usine-digitale.fr/article/qonto-lumapps-hardloop-les-levees-de-fonds-de-la-semaine.N922579'}, {'Date': '17/01/2020', 'URL': 'https://www.usine-digitale.fr/article/lydia-matera-simplifield-les-levees-de-fonds-de-la-semaine.N920674'}, {'Date': '10/01/2020', 'URL': 'https://www.usine-digitale.fr/article/ecovadis-weblib-adux-les-levees-de-fonds-de-la-semaine.N918274'}, {'Date': '03/01/2020', 'URL': 'https://www.usine-digitale.fr/article/majelan-osmosis-click-care-les-levees-de-fonds-de-la-semaine.N916694'}, {'Date': '20/12/2019', 'URL': 'https://www.usine-digitale.fr/article/dreamquark-efficientip-picto-voici-les-levees-de-fonds-de-la-semaine.N915009'}, {'Date': '13/12/2019', 'URL': 'https://www.usine-digitale.fr/article/intercloud-outsight-qwil-les-levees-de-fonds-de-la-semaine.N912879'}, {'Date': '06/12/2019', 'URL': 'https://www.usine-digitale.fr/article/gitguardian-sancar-lota-cloud-les-levees-de-fonds-de-la-semaine.N910874'}, {'Date': '29/11/2019', 'URL': 'https://www.usine-digitale.fr/article/sewan-leavy-toucan-toco-les-levees-de-fonds-de-la-semaine.N908564'}, {'Date': '15/11/2019', 'URL': 'https://www.usine-digitale.fr/article/finfrog-net-reviews-wittyfit-les-levees-de-fonds-de-la-semaine.N903754'}, {'Date': '08/11/2019', 'URL': 'https://www.usine-digitale.fr/article/hoppen-libeo-neofarm-les-levees-de-fonds-de-la-semaine.N901929'}, {'Date': '01/11/2019', 'URL': 'https://www.usine-digitale.fr/article/vade-secure-brut-blade-les-levees-de-fonds-de-la-semaine.N899879'}, {'Date': '25/10/2019', 'URL': 'https://www.usine-digitale.fr/article/madbox-nicecactus-smaaart-les-levees-de-fonds-de-la-semaine.N897629'}, {'Date': '18/10/2019', 'URL': 'https://www.usine-digitale.fr/article/algolia-lemon-way-herow-les-levees-de-fonds-de-la-semaine.N895664'}, {'Date': '11/10/2019', 'URL': 'https://www.usine-digitale.fr/article/incepto-packetai-acinq-les-levees-de-fonds-de-la-semaine.N893304'}, {'Date': '27/09/2019', 'URL': 'https://www.usine-digitale.fr/article/meshroomvr-splio-lancey-les-levees-de-fonds-de-la-semaine.N888829'}, {'Date': '20/09/2019', 'URL': 'https://www.usine-digitale.fr/article/levee-de-fonds.N886094'}, {'Date': '13/09/2019', 'URL': 'https://www.usine-digitale.fr/article/akeneo-jobteaser-spendesk-les-start-up-de-la-french-tech-levent-plus-de-167-millions-d-euros.N883979'}, {'Date': '06/09/2019', 'URL': 'https://www.usine-digitale.fr/article/ubitransport-heuritech-ilek-les-levees-de-fonds-de-la-semaine.N881445'}, {'Date': '30/08/2019', 'URL': 'https://www.usine-digitale.fr/article/manager-one-lilm-les-levees-de-fonds-de-la-semaine.N878870'}, {'Date': '09/08/2019', 'URL': 'https://www.usine-digitale.fr/article/levees-de-fonds-de-la-semaine-nouga-obtient-850-000-euros.N873935'}, {'Date': '19/07/2019', 'URL': 'https://www.usine-digitale.fr/article/traxens-mailingblack-teaminside-les-levees-de-fonds-de-la-semaine.N868060'}, {'Date': '05/07/2019', 'URL': 'https://www.usine-digitale.fr/article/ornikar-dott-cubyn-les-levees-de-fonds-de-la-semaine.N862940'}, {'Date': '28/06/2019', 'URL': 'https://www.usine-digitale.fr/article/metron-bleckwen-taster-les-levees-de-fonds-de-la-semaine.N860515'}, {'Date': '21/06/2019', 'URL': 'https://www.usine-digitale.fr/article/meero-payfit-bioserenity-les-levees-de-fonds-de-la-semaine.N857815'}, {'Date': '14/06/2019', 'URL': 'https://www.usine-digitale.fr/article/vade-secure-lifen-ekwateur-voici-les-levees-de-fonds-de-la-semaine.N854635'}, {'Date': '31/05/2019', 'URL': 'https://www.usine-digitale.fr/article/visible-patient-atolia-mindsay-voici-les-levees-de-fonds-de-la-semaine.N849435'}, {'Date': '17/05/2019', 'URL': 'https://www.usine-digitale.fr/article/plus-de-30-m-leves-par-les-start-up-de-la-french-tech-cette-semaine.N844130'}, {'Date': '10/05/2019', 'URL': 'https://www.usine-digitale.fr/editorial/heetch-pixpay-brigad-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N841075'}, {'Date': '26/04/2019', 'URL': 'https://www.usine-digitale.fr/article/otonomy-wemaintain-swikly-voici-les-levees-de-fonds-de-la-french-tech-cette-semaine.N836275'}, {'Date': '19/04/2019', 'URL': 'https://www.usine-digitale.fr/editorial/360learning-lumapps-bankin-les-levees-de-fonds-de-la-semaine.N833515'}, {'Date': '12/04/2019', 'URL': 'https://www.usine-digitale.fr/editorial/qare-devialet-wilov-combien-les-start-up-ont-elles-leve-cette-semaine.N830430'}, {'Date': '05/04/2019', 'URL': 'https://www.usine-digitale.fr/editorial/ces-9-start-up-ont-leve-pres-de-257-m-cette-semaine.N827435'}, {'Date': '29/03/2019', 'URL': 'https://www.usine-digitale.fr/article/kyriba-cycloid-wgf-les-levees-de-fonds-de-la-semaine.N824260'}, {'Date': '22/03/2019', 'URL': 'https://www.usine-digitale.fr/editorial/doctolib-iteca-oslo-les-levees-de-fonds-de-la-semaine.N821315'}, {'Date': '15/03/2019', 'URL': 'https://www.usine-digitale.fr/article/plus-de-33-m-leves-par-les-start-up-de-la-french-tech-cette-semaine.N818660'}, {'Date': '08/03/2019', 'URL': 'https://www.usine-digitale.fr/editorial/ces-4-start-up-ont-leve-un-total-de-plus-de-58-m-cette-semaine.N815360'}, {'Date': '01/03/2019', 'URL': 'https://www.usine-digitale.fr/editorial/plus-de-112-millions-d-euros-levees-par-les-start-up-de-la-french-tech-cette-semaine.N812850'}, {'Date': '22/02/2019', 'URL': 'https://www.usine-digitale.fr/editorial/alan-sybel-thegreendata-le-recap-des-levees-de-fonds-de-la-semaine.N809770'}, {'Date': '15/02/2019', 'URL': 'https://www.usine-digitale.fr/editorial/malt-yes-we-hack-call-a-lawyer-les-levees-de-fonds-de-la-semaine.N806855'}, {'Date': '08/02/2019', 'URL': 'https://www.usine-digitale.fr/editorial/lunchr-pretto-testamento-combien-les-start-up-francaises-ont-elles-leve-cette-semaine.N804045'}, {'Date': '04/02/2019', 'URL': 'https://www.usine-digitale.fr/article/contentsquare-zenpark-diota-combien-les-start-up-de-la-french-tech-ont-elles-leve-la-semaine-derniere.N801710'}, {'Date': '25/01/2019', 'URL': 'https://www.usine-digitale.fr/editorial/wynd-schoolab-mooncard-combien-les-start-up-ont-elles-leve-cette-semaine.N797965'}, {'Date': '18/01/2019', 'URL': 'https://www.usine-digitale.fr/article/onepark-my-serious-game-singulart-combien-les-start-up-ont-elles-leve-cette-semaine.N794664'}, {'Date': '11/01/2019', 'URL': 'https://www.usine-digitale.fr/editorial/talentsoft-monbuilding-papyhappy-les-levees-de-fonds-de-la-semaine.N791114'}, {'Date': '14/12/2018', 'URL': 'https://www.usine-digitale.fr/article/finalcad-early-metrics-expensya-les-levees-de-fonds-de-la-semaine.N783539'}, {'Date': '07/12/2018', 'URL': 'https://www.usine-digitale.fr/article/agricool-sentryo-zelros-les-levees-de-fond-de-la-semaine.N780069'}, {'Date': '30/11/2018', 'URL': 'https://www.usine-digitale.fr/editorial/happytal-selency-air-affaires-les-levees-de-fonds-de-la-semaine.N777004'}, {'Date': '16/11/2018', 'URL': 'https://www.usine-digitale.fr/article/blablacar-melty-packitoo-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N770329'}, {'Date': '09/11/2018', 'URL': 'https://www.usine-digitale.fr/article/levee-de-fonds.N767199'}, {'Date': '26/10/2018', 'URL': 'https://www.usine-digitale.fr/article/padoa-syntony-crosscall-les-levees-de-fond-de-la-semaine.N760879'}, {'Date': '19/10/2018', 'URL': 'https://www.usine-digitale.fr/editorial/universign-foodvisor-carlili-combien-les-start-up-francaises-ont-elles-leve-cette-semaine.N757814'}, {'Date': '12/10/2018', 'URL': 'https://www.usine-digitale.fr/editorial/braincube-jow-shopopop-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N754479'}, {'Date': '28/09/2018', 'URL': 'https://www.usine-digitale.fr/editorial/qonto-iziwork-hydrao-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N747974'}, {'Date': '07/09/2018', 'URL': 'https://www.usine-digitale.fr/editorial/shine-velco-pricemoov-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N738419'}, {'Date': '24/08/2018', 'URL': 'https://www.usine-digitale.fr/editorial/emplio-moona-mainbot-combien-ont-leve-les-start-up-de-la-french-tech-cette-semaine.N732929'}, {'Date': '10/08/2018', 'URL': 'https://www.usine-digitale.fr/article/akewatu-welovedevs-kwit-immopop-finalgo-voici-les-levees-de-fonds-des-start-up-de-la-semaine.N729929'}, {'Date': '27/07/2018', 'URL': 'https://www.usine-digitale.fr/article/comwatt-wiidii-wimi-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N725404'}, {'Date': '20/07/2018', 'URL': 'https://www.usine-digitale.fr/article/lemon-way-tagpay-stimergy-les-levees-de-fonds-des-startups-de-la-semaine.N722399'}, {'Date': '13/07/2018', 'URL': 'https://www.usine-digitale.fr/editorial/meero-brut-captain-wallet-voici-les-levees-de-fonds-des-start-up-de-la-french-tech-cette-semaine.N719479'}, {'Date': '06/07/2018', 'URL': 'https://www.usine-digitale.fr/article/izicap-doctrine-influence4you-combien-les-startups-ont-elles-leve-cette-semaine.N716604'}, {'Date': '29/06/2018', 'URL': 'https://www.usine-digitale.fr/article/dreem-eyelights-fly4u-les-levees-de-fonds-des-startups-de-la-semaine.N713644'}, {'Date': '22/06/2018', 'URL': 'https://www.usine-digitale.fr/article/feed-paytweak-onoff-tiller-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N710624'}, {'Date': '15/06/2018', 'URL': 'https://www.usine-digitale.fr/editorial/plus-de-75-m-leves-par-les-start-up-de-la-french-tech-cette-semaine.N707474'}, {'Date': '09/06/2018', 'URL': 'https://www.usine-digitale.fr/article/lendix-perfectstay-swapcard-sezane-combien-les-start-up-de-la-french-tech-ont-elles-leve-cette-semaine.N704134'}, {'Date': '01/06/2018', 'URL': 'https://www.usine-digitale.fr/article/les-levees-de-fonds-de-la-semaine.N701189'}, {'Date': '25/05/2018', 'URL': 'https://www.usine-digitale.fr/article/combien-ont-leve-les-start-up-de-la-french-tech-cette-semaine.N698279'}, {'Date': '11/05/2018', 'URL': 'https://www.usine-digitale.fr/article/french-tech-ultra-premium-direct-lita-co-orinox-les-levees-de-fonds-des-start-up-de-la-semaine.N692069'}, {'Date': '27/04/2018', 'URL': 'https://www.usine-digitale.fr/article/attestation-legale-slite-tilkee-hubrix-les-levees-de-fonds-de-la-semaine.N686634'}, {'Date': '20/04/2018', 'URL': 'https://www.usine-digitale.fr/article/les-levees-de-fonds-de-la-semaine.N683084'}, {'Date': '13/04/2018', 'URL': 'https://www.usine-digitale.fr/editorial/alan-singlespot-wesprint-les-levees-de-fonds-des-start-up-de-la-french-tech-cette-semaine.N679754'}, {'Date': '06/04/2018', 'URL': 'https://www.usine-digitale.fr/editorial/les-start-up-de-la-french-tech-ont-leve-6-2-m-cette-semaine.N676509'}, {'Date': '30/03/2018', 'URL': 'https://www.usine-digitale.fr/article/french-tech-comet-meetings-supervizor-ayomi-les-levees-de-fonds-de-la-semaine.N674089'}, {'Date': '23/03/2018', 'URL': 'https://www.usine-digitale.fr/article/french-tech-ornikar-antvoice-seald-les-start-up-ont-leve-plus-de-25-millions-d-euros-cette-semaine.N670629'}, {'Date': '16/03/2018', 'URL': 'https://www.usine-digitale.fr/article/les-levees-de-fonds-de-la-semaine.N667524'}, {'Date': '09/03/2018', 'URL': 'https://www.usine-digitale.fr/article/pres-de-41-m-leves-par-les-start-up-de-la-french-tech-cette-semaine.N664219'}, {'Date': '02/03/2018', 'URL': 'https://www.usine-digitale.fr/editorial/french-tech-habx-kalti-mirsense-hyperlex-les-levees-de-fonds-des-start-up-cette-semaine.N660924'}, {'Date': '23/02/2018', 'URL': 'https://www.usine-digitale.fr/article/les-levees-de-fonds-de-la-semaine.N657749'}, {'Date': '16/02/2018', 'URL': 'https://www.usine-digitale.fr/article/french-tech-xx-millions-d-euros-leves-par-xx-start-up-cette-semaine.N654649'}, {'Date': '09/02/2018', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-122-millions-d-euros-leves-par-15-start-up-cette-semaine.N651229'}, {'Date': '02/02/2018', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-145-millions-d-euros-leves-par-18-start-up-cette-semaine.N647373'}, {'Date': '26/01/2018', 'URL': 'https://www.usine-digitale.fr/article/french-tech-saagie-yousign-smile-pay-les-levees-de-fonds-de-la-semaine.N643848'}, {'Date': '19/01/2018', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-100-millions-d-euros-leves-par-13-start-up-cette-semaine.N640563'}, {'Date': '12/01/2018', 'URL': 'https://www.usine-digitale.fr/article/french-tech-simple-sellsy-lengow-les-levees-de-fonds-de-la-semaine.N636958'}, {'Date': '26/12/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-les-10-plus-grosses-levees-de-fonds-de-l-annee-2017.N631268'}, {'Date': '22/12/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-13-5-millions-d-euros-leves-par-11-start-up-cette-semaine.N631228'}, {'Date': '15/12/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-23-millions-d-euros-leves-par-10-start-up-cette-semaine.N628178'}, {'Date': '08/12/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-37-millions-d-euros-leves-par-13-start-up-cette-semaine.N624963'}, {'Date': '01/12/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-12-start-up-ont-leve-plus-de-63-millions-d-euros-cette-semaine.N621838'}, {'Date': '27/11/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-18-millions-d-euros-leves-par-13-start-up-cette-semaine.N618188'}, {'Date': '17/11/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-83-millions-d-euros-leves-par-15-start-up-cette-semaine.N615553'}, {'Date': '10/11/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-19-millions-d-euros-leves-par-12-start-up-cette-semaine.N612368'}, {'Date': '03/11/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-un-peu-plus-de-8-millions-d-euros-leves-par-5-start-up-cette-semaine.N609403'}, {'Date': '27/10/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-94-millions-d-euros-leves-par-14-start-up-cette-semaine.N606528'}, {'Date': '20/10/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-pres-de-34-millions-d-euros-leves-par-20-start-up-cette-semaine.N603363'}, {'Date': '24/10/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-11-start-up-ont-leve-plus-de-11-millions-d-euros-cette-semaine.N600038'}, {'Date': '06/10/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-95-millions-d-euros-leves-par-17-start-up-cette-semaine.N596788'}, {'Date': '29/09/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-78-millions-d-euros-leves-par-17-start-up-cette-semaine.N593888'}, {'Date': '22/09/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-87-millions-d-euros-leves-par-17-start-up-cette-semaine.N590653'}, {'Date': '15/09/2017', 'URL': 'https://www.usine-digitale.fr/article/semaine-fructueuse-pour-la-french-tech-avec-plus-de-126m-leves.N587623'}, {'Date': '08/09/2017', 'URL': 'https://www.usine-digitale.fr/article/belle-rentree-pour-la-french-tech-12-start-up-ont-leve-plus-de-83-millions-d-euros.N584603'}, {'Date': '01/09/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-4-start-up-ont-leve-plus-de-23-millions-d-euros-fin-aout.N581698'}, {'Date': '18/08/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-les-montants-leves-en-2017-devraient-doubler-par-rapport-a-2016.N577533'}, {'Date': '04/08/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-skillup-bowkr-les-levees-de-fonds-de-la-semaine.N573893'}, {'Date': '28/07/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-alltricks-o-gaming-lotprive-les-levees-de-fonds-de-la-semaine.N571558'}, {'Date': '14/07/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-22-4-millions-d-euros-leves-par-10-start-up-cette-semaine.N566059'}, {'Date': '07/07/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-66-millions-d-euros-leves-par-26-start-up-cette-semaine.N563042'}, {'Date': '30/06/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-22-millions-d-euros-leves-par-13-start-up-cette-semaine.N560188'}, {'Date': '16/06/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-15-start-up-ont-leve-83-millions-d-euros-cette-semaine.N553838'}, {'Date': '09/06/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-90-millions-d-euros-leves-par-15-start-up-cette-semaine.N550673'}, {'Date': '02/06/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-29-millions-d-euros-leves-par-15-start-up-cette-semaine.N547783'}, {'Date': '26/05/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-six-start-up-ont-leve-plus-de-65-millions-d-euros-cette-semaine.N545233'}, {'Date': '19/05/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-8-start-up-ont-leve-un-total-de-plus-de-52-millions-d-euros-cette-semaine.N542619'}, {'Date': '12/05/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-au-total-ces-14-start-up-ont-leve-plus-de-36-millions-d-euros-cette-semaine.N539489'}, {'Date': '05/05/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-pres-de-18-millions-d-euros-leves-par-7-start-up-cette-semaine.N536069'}, {'Date': '28/04/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-78-millions-d-euros-leves-par-6-start-up-cette-semaine.N533159'}, {'Date': '21/04/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-11-millions-d-euros-leves-par-9-start-up-cette-semaine.N529829'}, {'Date': '14/04/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-113-millions-d-euros-leves-par-9-start-up-cette-semaine.N527254'}, {'Date': '07/04/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-17-7-millions-d-euros-leves-par-7-start-up-cette-semaine.N524679'}, {'Date': '31/03/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-90-millions-d-euros-leves-par-13-start-up-cette-semaine.N521759'}, {'Date': '24/03/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-13-start-up-ont-leve-plus-de-37-millions-d-euros-cette-semaine.N518874'}, {'Date': '17/03/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-12-start-up-ont-leve-plus-de-18-millions-d-euros-cette-semaine.N515899'}, {'Date': '10/03/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-55-millions-d-euros-leves-par-11-start-up-cette-semaine.N512749'}, {'Date': '03/03/2017', 'URL': 'https://www.usine-digitale.fr/article/ces-six-start-up-de-la-french-tech-ont-leve-plus-de-11-millions-d-euros.N509699'}, {'Date': '24/02/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-41-millions-d-euros-leves-par-9-start-up-cette-semaine.N506439'}, {'Date': '17/02/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-6-5-millions-d-euros-leves-par-7-start-up-cette-semaine.N503484'}, {'Date': '10/02/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-7-start-up-ont-leve-plus-de-15-millions-d-euros-cette-semaine.N500154'}, {'Date': '06/02/2017', 'URL': 'https://www.usine-digitale.fr/article/qwant-resto-flash-yomoni-les-levees-de-fonds-de-la-semaine.N496709'}, {'Date': '20/01/2017', 'URL': 'https://www.usine-digitale.fr/editorial/ces-17-start-up-de-la-french-tech-ont-leve-plus-de-37m-d-euros-cette-semaine.N490549'}, {'Date': '13/01/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-23-millions-d-euros-leves-par-9-start-up-cette-semaine.N487329'}, {'Date': '06/01/2017', 'URL': 'https://www.usine-digitale.fr/article/french-tech-6-start-up-ont-leve-plus-de-5-millions-d-euros-cette-semaine.N484569'}, {'Date': '23/12/2016', 'URL': 'https://www.usine-digitale.fr/article/10-start-up-ont-leve-plus-de-6-5-m-cette-semaine.N480714'}, {'Date': '16/12/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-57-millions-d-euros-leves-par-12-start-up-cette-semaine.N478034'}, {'Date': '09/12/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-55-millions-d-euros-leves-par-8-start-up-cette-semaine.N474794'}, {'Date': '25/11/2016', 'URL': 'https://www.usine-digitale.fr/article/a-elles-7-ces-start-up-francaises-ont-leve-plus-de-190-millions-d-euros-cette-semaine.N468428'}, {'Date': '18/11/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-18-millions-d-euros-leves-par-9-start-up-cette-semaine.N465733'}, {'Date': '11/11/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-8-4-millions-d-euros-leves-par-8-start-up-cette-semaine.N462773'}, {'Date': '04/11/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-13-millions-d-euros-leves-par-8-start-up-cette-semaine.N459542'}, {'Date': '28/10/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-12-start-up-ont-leve-plus-de-65-millions-d-euros-cette-semaine.N456842'}, {'Date': '21/10/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-14-start-up-ont-leve-plus-de-44-millions-d-euros-cette-semaine.N453862'}, {'Date': '14/10/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-plus-de-81-7-millions-d-euros-investis-dans-19-start-up.N451047'}, {'Date': '08/10/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-13-start-up-ont-leve-22-millions-d-euros-cette-semaine.N448357'}, {'Date': '30/09/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-92-millions-d-euros-leves-par-21-start-up-cette-semaine.N444407'}, {'Date': '23/09/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-37-millions-d-euros-leves-par-21-start-up-cette-semaine.N441097'}, {'Date': '09/09/2016', 'URL': 'https://www.usine-digitale.fr/article/rentree-en-fanfare-pour-la-french-tech-92-millions-d-euros-leves-par-15-start-up-cette-semaine.N435022'}, {'Date': '02/09/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-9-millions-d-euros-leves-par-7-startups-cette-semaine.N432107'}, {'Date': '05/08/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-7-millions-d-euros-leves-par-3-start-up-cette-semaine.N422222'}, {'Date': '22/07/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-6-4-millions-d-euros-leves-par-3-start-up-cette-semaine.N403462'}, {'Date': '15/07/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-30-millions-d-euros-leves-par-14-start-up-cette-semaine.N402797'}, {'Date': '08/07/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-22-millions-d-euros-leves-par-13-startups-cette-semaine.N401767'}, {'Date': '01/07/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-29-millions-d-euros-leves-par-16-start-up-cette-semaine.N400547'}, {'Date': '24/06/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-65-millions-d-euros-leves-par-19-start-up-cette-semaine.N399002'}, {'Date': '17/06/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-16-8-millions-d-euros-leves-par-16-startups-cette-semaine.N397702'}, {'Date': '10/06/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-32-millions-d-euros-leves-par-14-start-up-cette-semaine.N396382'}, {'Date': '03/06/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-15-millions-d-euros-leves-par-11-start-up-cette-semaine.N394912'}, {'Date': '27/05/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-20-millions-d-euros-leves-par-10-start-up-cette-semaine.N393607'}, {'Date': '20/05/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-11-start-up-ont-leve-15-millions-d-euros-cette-semaine.N392337'}, {'Date': '13/05/2016', 'URL': 'https://www.usine-digitale.fr/article/french-tech-9-start-up-ont-leve-36-millions-d-euros-cette-semaine.N391347'}, {'Date': '12/05/2016', 'URL': 'https://www.usine-digitale.fr/article/interaction-healthcare-la-pepite-qui-simule-les-cas-cliniques-leve-5-millions-d-euros.N391097'}]
