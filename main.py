"""
Created on 1 nov 2022

@author: jcescribano
"""
import csv
from selenium import webdriver
from bs4 import BeautifulSoup
from requests import get
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://contrataciondelestado.es/wps/portal/licitaciones"
nombreFichero = 'contratacion.csv'
pathGecko = "/usr/bin/geckodriver"
pathFirefox = "/usr/bin/firefox"


def abrir_firefox():
    return webdriver.Firefox(executable_path=pathGecko, firefox_binary=pathFirefox)


def anadir_datos(nombre_fichero, fila_para_guardar):
    with open(nombre_fichero, 'a', encoding='UTF8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fila_para_guardar)


def guardar_datos(tbody):
    for td in tbody.find_all('tr'):
        if td.find(class_="tdExpediente"):
            expediente = td.find(class_="tdExpediente").find_all('div')[0].text
            descripcionExpediente = td.find(class_="tdExpediente").find_all('div')[1].text
            listaTipoContrato = td.find(class_='tdTipoContrato').find_all('div')
            tipoContrato = ""
            for tc in listaTipoContrato:
                tipoContrato = tc.text + ";" + tipoContrato
            estado = td.find(class_='tdEstado').text
            importe = td.find(class_='tdImporte').text
            fechaLimite = td.find(class_='tdFechaLimite').text
            organoContratacion = td.find(class_='tdOrganoContratacion').text
            fila=[expediente, descripcionExpediente, tipoContrato, estado, importe, fechaLimite, organoContratacion]
            anadir_datos(nombreFichero, fila)

def recuperarInformacion():
    navegador = abrir_firefox()
    navegador.get(url)
    navegador.find_element(By.CLASS_NAME, 'divLogo').click()
    navegador.find_element(By.ID, 'viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:button1').click()
    WebDriverWait(navegador, 1000).until(EC.presence_of_element_located((By.CLASS_NAME, "cabeceraTexto")))
    soup = BeautifulSoup(navegador.page_source, 'html.parser')
    tbody = soup.find('tbody')
    guardar_datos(tbody)
    navegador.close()


recuperarInformacion()
