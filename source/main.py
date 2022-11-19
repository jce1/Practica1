"""
Created on 1 nov 2022

@author: jcescribano
@author: jjcorrales
"""
import csv
import multiprocessing
import time
import calendar
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# url inicial de la navegación
url = "https://contrataciondelestado.es/wps/portal/licitaciones"
# nombre del fichero de salida generado
nombre_fichero_base = 'contratacionTodo'
# localización del driver de selenium
path_gecko = "/usr/bin/geckodriver"
# localización del ejecutable del navegador que vamos usar: firefox
path_firefox = "/usr/bin/firefox"
# meses a descargar
meses = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# año a descargar
anio = 2022


# Configura, genera y devuelve el driver de selenium para firefox
def abrir_firefox():
    ops = webdriver.FirefoxOptions()
    ops.binary_location = path_firefox
    # Con el siguiente parametro hacemos que Firefox se ejecute en segundo plano
    # con esto se consigue que la ejecución sea más rápida y que el consumo de
    # recursos sea menor
    ops.headless = True
    # Cambiar el user agent no es realmente necesario cuando se esta utilizando selenium ya que se esta
    # realizando la navegación utilizando el firefox instalado en la máquina donde se ejecuta este script
    ops.set_preference("general.useragent.override",
                       "Mozilla/5.0 (X11; Linux i686; rv:107.0) Gecko/20100101 Firefox/107.0")
    serv = Service(path_gecko)
    return webdriver.Firefox(service=serv, options=ops)

# Esta función se encarga de crear y añadir filas al fichero de salida
def anadir_datos(nombre_fichero_anadir, fila_para_guardar):
    # Añado una fila de datos al fichero de salida
    with open(nombre_fichero_anadir, 'a', encoding='UTF8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fila_para_guardar)


# Extraigo los datos que necesito del cuerpo de la página e invoco a la función de guardar a fichero
# En cada fila guardo la información de un expediente
def guardar_datos(tbody, nombre_fichero):
    for td in tbody.find_all('tr'):
        if td.find(class_="tdExpediente"):
            expediente = td.find(class_="tdExpediente").find_all('div')[0].text
            descripcion_expediente = td.find(class_="tdExpediente").find_all('div')[1].text
            lista_tipo_contrato = td.find(class_='tdTipoContrato').find_all('div')
            tipo_contrato = ""
            if lista_tipo_contrato:
                for tc in lista_tipo_contrato:
                    tipo_contrato = tc.text + ";" + tipo_contrato
            estado = td.find(class_='tdEstado').text
            importe = td.find(class_='tdImporte').text
            fecha_limite = td.find(class_='tdFechaLimite').text
            organo_contratacion = td.find(class_='tdOrganoContratacion').text
            date_fecha_recuperacion = datetime.now()
            fecha_recuperacion = datetime.strftime(date_fecha_recuperacion, '%d-%m-%Y')
            fila = [expediente, descripcion_expediente, tipo_contrato, estado, importe, fecha_limite,
                    organo_contratacion, fecha_recuperacion]
            anadir_datos(nombre_fichero, fila)


# Esta función se encarga de realizar la navegación por las tablas paginadas y recuperar la información
# que necesitamos de la tabla que se encuentra en cada una de las paginas.
def recuperar_informacion_mes(mes, anio1):
    nombre_fichero_destino = nombre_fichero_base + "_" + str(mes) + "_" + str(anio1) + ".csv"
    ultimo_dia_mes = calendar.monthrange(anio1, mes)[1]
    navegador = abrir_firefox()
    navegador.get(url)
    # Cargo la página de busqueda de la información
    navegador.find_element(By.CLASS_NAME, 'divLogo').click()
    # Relleno las fechas
    inicio_mes = "01- " + str(mes) + "-" + str(anio1)
    fin_mes = str(ultimo_dia_mes) + "-" + str(mes) + "-" + str(anio1)
    navegador.find_element(By.CSS_SELECTOR, "[id$=textMinFecAnuncioMAQ2]").send_keys(inicio_mes)
    navegador.find_element(By.CSS_SELECTOR, "[id$=textMaxFecAnuncioMAQ]").send_keys(fin_mes)
    tiempo_inicio = time.time()
    # Pincho en buscar
    navegador.find_element(By.ID, 'viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:button1').click()
    finalizado = False
    contador = 1
    while not finalizado:
        # La carga de resultados despues de pinchar en el enlace es muy lenta. El siguiente comando se
        # encarga de esperar hasta que un elemento de la tabla se ha cargado
        WebDriverWait(navegador, 1000).until(ec.text_to_be_present_in_element
                                             ((By.CSS_SELECTOR, "[id$=textfooterInfoNumPagMAQ]"), str(contador)))
        # recupero el número de página en la que se encuentra la navegación
        pagina_actual = int(navegador.find_element(By.CSS_SELECTOR, "[id$=textfooterInfoNumPagMAQ]").text)
        # recupero el número de páginas total
        pagina_final = int(navegador.find_element(By.CSS_SELECTOR, "[id$=textfooterInfoTotalPaginaMAQ]").text)
        # convierto la página a un objeto BeatifulSoup para facilitar el procesado de los elementos
        # que necesitamos
        soup = BeautifulSoup(navegador.page_source, 'html.parser')
        cuerpo_pagina = soup.find('tbody')
        guardar_datos(cuerpo_pagina, nombre_fichero_destino)
        if pagina_actual != pagina_final:
            navegador.find_element(By.CSS_SELECTOR, "[id$=footerSiguiente]").click()
            contador = contador + 1
            tiempo_fin = time.time()
            print(str(mes) + str(anio1) + " La página ha tardado en procesarse " + str(tiempo_fin - tiempo_inicio))
            tiempo_inicio = tiempo_fin
            print(str(mes) + str(anio1) + "Se han descargado " + str(contador) + " páginas")
        else:
            finalizado = True
    navegador.close()
    print("Se ha finalizado la creación del fichero " + nombre_fichero_destino)


"""
Dado que la busqueda tarda mucho tiempo en cargar (entre 10 y 15 segundos) y la gran cantidad de datos se ha optado
por descargar los datos por meses y paralelizar la descarga utilizando multiprocessing. De esta manera se lanzan
12 navegadores en paralelo cada uno para descargar la información de un mes del año
Para ejecutar este proceso habrá que evaluar si las caracteristicas hardware (memoria y micro) del equipo soportan dicha 
carga de trabajo 
"""
if __name__ == '__main__':
    procesos = []
    for i in meses:
        # Creo un proceso
        t = multiprocessing.Process(target=recuperar_informacion_mes, args=[i, anio])
        # Lanzo el proceso
        t.start()
        procesos.append(t)
    # Para los procesos lanzados
    for proc in procesos:
        proc.join()
print("El proceso de descarga ha finalizado")