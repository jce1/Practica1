'''
Created on 1 nov 2022

@author: anon
'''
import csv

from selenium import webdriver
from bs4 import BeautifulSoup
from requests import get
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url="https://contrataciondelestado.es/wps/portal/licitaciones"


def open_browser():

    try:
        driver = webdriver.Firefox(executable_path="/usr/bin/geckodriver", firefox_binary='/usr/bin/firefox')
        driver.get(url)
        driver.find_element(By.CLASS_NAME,'divLogo').click()
        driver.find_element(By.ID, 'viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:button1').click()
        element = WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.CLASS_NAME, "cabeceraTexto")))
        tablaResultados=driver.find_element(By.ID,'myTablaBusquedaCustom')
        print(tablaResultados)
        expedientes=driver.find_elements(By.ID,'tdExpediente')
        print(expedientes)
        tabla = driver.find_element(By.TAG_NAME, 'tbody')
       
        print(tabla.text)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tbody = soup.find('tbody')
        data = []
        with open('contratacion.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for td in tbody.find_all('tr'):
                row = [i.text for i in td.find_all('td')]
                spamwriter.writerow(row)
                data.append(row)


        print("fin")
    except TimeoutException:
        print("Timed out waiting for page to load")



open_browser()
