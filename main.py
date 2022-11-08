"""
Created on 1 nov 2022

@author: jcescribano
"""
import csv
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from requests import get
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://contrataciondelestado.es/wps/portal/licitaciones"
nombre_fichero = 'contratacionTodo.csv'
path_gecko = "/usr/bin/geckodriver"
path_firefox = "/usr/bin/firefox"


def abrir_firefox():
    return webdriver.Firefox(executable_path=path_gecko, firefox_binary=path_firefox)


def anadir_datos(nombre_fichero_anadir, fila_para_guardar):
    with open(nombre_fichero_anadir, 'a', encoding='UTF8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fila_para_guardar)


def guardar_datos(tbody):
    for td in tbody.find_all('tr'):
        if td.find(class_="tdExpediente"):
            expediente = td.find(class_="tdExpediente").find_all('div')[0].text
            descripcion_expediente = td.find(class_="tdExpediente").find_all('div')[1].text
            lista_tipo_contrato = td.find(class_='tdTipoContrato').find_all('div')
            tipo_contrato = ""
            for tc in lista_tipo_contrato:
                tipo_contrato = tc.text + ";" + tipo_contrato
            estado = td.find(class_='tdEstado').text
            importe = td.find(class_='tdImporte').text
            fecha_limite = td.find(class_='tdFechaLimite').text
            organo_contratacion = td.find(class_='tdOrganoContratacion').text
            fila = [expediente, descripcion_expediente, tipo_contrato, estado, importe, fecha_limite, organo_contratacion]
            anadir_datos(nombre_fichero, fila)


def recuperar_informacion():
    navegador = abrir_firefox()
    navegador.get(url)
    navegador.find_element(By.CLASS_NAME, 'divLogo').click()
    navegador.find_element(By.ID, 'viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:button1').click()
    finalizado=False
    contador=1
    while not finalizado:
        WebDriverWait(navegador, 1000).until(EC.text_to_be_present_in_element
                                             ((By.CSS_SELECTOR, "[id$=textfooterInfoNumPagMAQ]"), str(contador)))
        pagina_actual = int(navegador.find_element(By.CSS_SELECTOR, "[id$=textfooterInfoNumPagMAQ]").text)
        pagina_final = int(navegador.find_element(By.CSS_SELECTOR, "[id$=textfooterInfoTotalPaginaMAQ]").text)
        #pagina_final = 10
        soup = BeautifulSoup(navegador.page_source, 'html.parser')
        cuerpo_pagina = soup.find('tbody')
        guardar_datos(cuerpo_pagina)
        if pagina_actual != (pagina_final + 1):
            navegador.find_element(By.CSS_SELECTOR, "[id$=footerSiguiente]").click()
            contador = contador + 1
            print("Se han descargado" + str(contador) + "páginas")
        else:
            finalizado = True
    navegador.close()


recuperar_informacion()
