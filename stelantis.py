from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import os



Name = os.environ.get("RACF_USERNAME")
Passwort = os.environ.get("RACF_PASSWORD")
System = os.environ.get("SYSTEM", "Integration")

if not Name or not Passwort:
    raise RuntimeError("RACF_USERNAME und RACF_PASSWORD müssen als Environment Variables gesetzt sein.")


#setup
def setup_driver():
    service = Service(executable_path="chromedriver.exe")
    return webdriver.Chrome(service=service)

#anmeldung
def login(driver):
    #website
    if System == "Produktion":
        driver.get("https://stellantis.customer-intelligence-services.de/apex/f?p=110:3030:735940432336::NO:3030:AI_ACTIVE_NAVIGATION_NODE,TAB_AKTIV:764,%253A:NO&cs=3TCez-ugXz8cAi4xrF685VS9Elw7AAerEMaVsC9eaEgDKvHU6hrECOI1AbrSowjr4mQDefMnfS0hqm3b1imcIUQ")
    else:
        driver.get("http://gtunxlvd01642:7777/apex/f?p=110:3030:9769295304625::NO:3030:AI_ACTIVE_NAVIGATION_NODE,TAB_AKTIV:764,%253A:NO&cs=3a_iYlJt645oN3b_jPiigYEsZ_FIVm_-R8rPrh2Goo9iORxWzVYiiaRhZv97IjS2duZ1YZL-z-TStbFHMpJiIKg")
    # Element finden und darauf klicken
    link_element = driver.find_element(By.XPATH, "//a[contains(text(), 'here')]")
    link_element.click()
    #warten auf anmeldung
    WebDriverWait(driver, 5).until (EC.presence_of_all_elements_located((By.ID, "P101_USERNAME")))
    input_element = driver.find_element(By.ID, "P101_USERNAME")
    input_element.send_keys(Name)
    input_element = driver.find_element(By.ID, "P101_PASSWORD")
    input_element.send_keys(Passwort + Keys.ENTER)

#Kampagnen Codes suchen
def search_campaign(driver, campaign_code_value, nsc_value):
    #Kampagnen Code
    input_element = driver.find_element(By.ID, "P3030_CAMPAIGN_ERECA_CODE")
    input_element.send_keys(campaign_code_value + Keys.ENTER)
    #Land auswählen
    input_element = driver.find_element(By.ID, "P3030_BUSINESS_UNIT")
    input_element.send_keys(nsc_value + Keys.ENTER)
    #suchen
    input_element = driver.find_element(By.ID, "P3030_SEARCH")
    input_element.click()
    # todo:
    # Sicherstellen, dass Der richtige Kampagnencode ist und nicht ihrgend eine genommen und kopiert wird.
    #


#Die Richtige Kampagne mit richtiger Version finden:
def select_highest_version(driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "t15standardalternatingrowcolors")))
        # HTML-code der Tabelle
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 't15standardalternatingrowcolors'})
        #variablen für höchste Versionen
        highest_version = ""
        highest_wave = ""
        campaign_with_highest_version = ""
        
        #durch Zeilen der Tabelle gehen, die spalten heißen in html tr und td
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 0:

                campaign_name = columns[3].text.strip()
                if campaign_name.strip() and not campaign_name.strip().replace(" ", "").isdigit() and 'drv' not in campaign_name.lower(): # Überprüfen, ob drv nicht drin ist und die Zeichenfolge nicht leer ist
                    match = re.search(r'V\d+', campaign_name)
                    if match:
                        version = match.group()
                    else:
                        version = "V1"
                    match = re.search(r'W\d+', campaign_name)
                    if match:
                        wave = match.group()
                    else:
                        wave = "W1"

                    print(f"Campaign Name: {campaign_name}, Version: {version}, Wave: {wave}")

                    if len(version) > 0 and len(wave) > 0:
                        print(" ")                

                        if version > highest_version:
                            highest_version = version
                            highest_wave = wave
                            campaign_with_highest_version = campaign_name
                        elif version == highest_version and wave > highest_wave:
                            highest_wave = wave
                            campaign_with_highest_version = campaign_name  
        print(f"Campaign with highest version: {campaign_with_highest_version}, Version: {highest_version}, Wave: {highest_wave}")
        return campaign_with_highest_version if campaign_with_highest_version else ""
    except Exception as e:
        print("Nix da Kampagnen", e)
        return ""
        #todo:
        #   Kampagne dann erstellen, Hier nicht Chatgpt!
        #

def Kopieren(driver, campaign_with_highest_version):

    #Bearbeiten
    if campaign_with_highest_version:
        # HTML-Code der Tabelle
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 't15standardalternatingrowcolors'})

        # Den Link zur Kampagne mit der höchsten Version finden
        link = None
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 0:
                campaign_name = columns[3].text.strip()
                if campaign_name == campaign_with_highest_version:
                    link = row.find('a', href=True)
                    break

        # Wenn der Link gefunden wurde, darauf klicken
        if link:
            link_url = link['href']
            if(System == "Produktion"):
                driver.get("https://stellantis.customer-intelligence-services.de/apex/" + link_url)
            else:
                driver.get("http://gtunxlvd01642:7777/apex/" + link_url)

    #Das eigentliche Kopieren:
    input_element = driver.find_element(By.ID, "P3040_COPY_CAMPAIGN")
    input_element.click()

    # driver.switch_to.window(popup_window_handle)
    # input_element = driver.find_element(By.NAME, "P3100_NEW_CAMPAIGN_NAME")
    
    # input_element.click()
    # # todo
    #  # Bedingungen für den Namen der Kopie festlegen
    
    # campaign_name_parts = campaign_with_highest_version.split()
    # new_campaign_name = campaign_name_parts[0] + " " + campaign_name_parts[1] + " "
    # version_match = re.search(r'V(\d+)', campaign_with_highest_version)
    
    # if version_match:
    #     version = version_match.group(1)
    # else:
    #     version = "INI"
    # new_campaign_name += version + " 2nd "
    # wave_match = re.search(r'W(\d+)', campaign_with_highest_version)
    
    # if wave_match:
    #     wave = int(wave_match.group(1)) + 1
    # else:
    #     wave = 1
    
    # new_campaign_name += "W" + str(wave)
    # # Textfeld ausfüllen
    # input_element.clear()
    # input_element.send_keys(new_campaign_name)
    # # Entfernen von " (COPY)"
    # if " (COPY)" in new_campaign_name:
    #     new_campaign_name = new_campaign_name.replace(" (COPY)", "")
    #     input_element.clear()
    #     input_element.send_keys(new_campaign_name)
    # input("Drücke Enter für weiter")
        
#Main Methode, wo die eigentlich sauce abgeht
def main():
    driver = setup_driver()
    login(driver)
    excel_file = '2nd_Notification_Q1_2024.xlsx'
    df = pd.read_excel(excel_file)
    for index, row in df.iterrows():
        search_campaign(driver, row['Campaign-Code '], row['NSC '])
        HighestVersion = select_highest_version(driver)
        Kopieren(driver, HighestVersion)
        time.sleep(300)
    #schließen
    input("drücke Enter zum schließen")
    driver.quit()

if __name__ == "__main__":
    main()    