"""
Created on 1 nov 2022

@author: jcescribano
@author: jjcorrales
"""
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# url inicial de la navegación
url = "https://contrataciondelestado.es/wps/portal/licitaciones"
# nombre del fichero de salida generado
nombre_fichero = 'contratacionTodo.csv'
# localización del driver de selenium
path_gecko = "/usr/bin/geckodriver"
# localización del ejecutable del navegador que vamos usar: firefox
path_firefox = "/usr/bin/firefox"

def abrir_firefox():
    #Configura, genera y devuelve el driver de selenium para firefox
    ops = webdriver.FirefoxOptions()
    ops.binary_location = path_firefox
    # Con el siguiente parametro hacemos que Firefox se ejecute en segundo plano
    # con esto se consigue que la ejecución sea más rápida
    ops.headless = True
    # Cambiar el user agent no es realmente necesario cuando se esta utilizando selenium ya que se esta
    # realizando la navegación utilizando el firefox instalado en la máquina donde se ejecuta este script
    ops.set_preference("general.useragent.override","Mozilla/5.0 (X11; Linux i686; rv:107.0) Gecko/20100101 Firefox/107.0")
    serv = Service(path_gecko)
    return webdriver.Firefox(service=serv, options=ops)

def anadir_datos(nombre_fichero_anadir, fila_para_guardar):
    #Añado una fila de datos al fichero de salida
    with open(nombre_fichero_anadir, 'a', encoding='UTF8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fila_para_guardar)


def guardar_datos(tbody):
    # Extraigo los datos que necesito del cuerpo de la página e invoco a la función de guardar a fichero
    # En cada fila guardo la información de un expediente
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
    # La información que necesitamos se encuentra en tablas paginadas.
    # Esta función se encarga de realizar la navegación por las tablas paginadas y recuperar la información
    # que necesitamos de la tabla que se encuentra en cada una de las paginas
    navegador = abrir_firefox()
    navegador.get(url)
    navegador.find_element(By.CLASS_NAME, 'divLogo').click()
    navegador.find_element(By.ID, 'viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:button1').click()
    finalizado=False
    contador=1
    while not finalizado:
        #La carga de resultados despues de pinchar en el enlace es muy lenta. El siguiente comando se
        #encarga de esperar hasta que un elemento de la tabla se ha cargado
        WebDriverWait(navegador, 1000).until(ec.text_to_be_present_in_element
                                             ((By.CSS_SELECTOR, "[id$=textfooterInfoNumPagMAQ]"), str(contador)))
        #recupero el número de página en la que se encuentra la navegación
        pagina_actual = int(navegador.find_element(By.CSS_SELECTOR, "[id$=textfooterInfoNumPagMAQ]").text)
        #recupero el número de páginas total
        pagina_final = int(navegador.find_element(By.CSS_SELECTOR, "[id$=textfooterInfoTotalPaginaMAQ]").text)
        #pagina_final = 10
        #convierto la página a un objeto BeatifulSoup para facilitar el procesado de los elementos
        #que necesitamos
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
