# execute as sudo python3 app.py inside a tmux session

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, request
import requests
import locale
import pytz
from twilio.twiml.messaging_response import MessagingResponse
 
app = Flask(__name__)
 
@app.route("/wa")
def wa_hello():
    return "Hello, World!"
 
@app.route("/wasms", methods=['POST'])
def wa_sms_reply():
    """Respond to incoming calls with a report of COVID."""
    # Fetch the message
    locale.setlocale(locale.LC_ALL, 'es_CL.utf8')
    msg = request.form.get('Body').lower() # Reading the message from the whatsapp
 
    print("msg-->",msg)
    resp = MessagingResponse()
    reply=resp.message()
    # Create reply

  # Returns the current Santiago date
    tz = pytz.timezone('America/Santiago')
    date = datetime.now(tz)
    datem1 = date - timedelta(days=1)

    date_str = date.strftime("%Y-%m-%d")
    datem1_str = datem1.strftime("%Y-%m-%d")

    def reportecovid(date, datem1):
        dateformatted = datetime.strptime(date, '%Y-%m-%d')
        dateformatted = dateformatted.strftime("%A %d-%m-%Y")  
        dataTotal = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto4/" + date + "-CasosConfirmados-totalRegional.csv",index_col=0)
        dataTotalayer = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto4/" + datem1 + "-CasosConfirmados-totalRegional.csv",index_col=0)
        dataPCR = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto17/PCREstablecimiento.csv", index_col=0)
        dataCamasCrit = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto20/NumeroVentiladores.csv", index_col=0)
        dataPos = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto49/Positividad_Diaria_Media.csv", index_col=0)
        string_data = "Reporte COVID 🦠 del día " + dateformatted + "\n\n• Casos nuevos: " + locale.format_string('%.0f', dataTotal.loc['Total', 'Casos nuevos totales'], True) + "\n• Casos activos: " + locale.format_string('%.0f', dataTotal.loc['Total', 'Casos activos confirmados'], True) + "\n• Fallecidos hoy: " + locale.format_string('%.0f', dataTotal.loc['Total', 'Fallecidos totales']-dataTotalayer.loc['Total', 'Fallecidos totales'], True) + "\n• Fallecidos total: " + locale.format_string('%.0f', dataTotal.loc['Total', 'Fallecidos totales'], True) + "\n• Exámenes PCR último día: " + locale.format_string('%.0f', dataPCR.loc['Total informados ultimo dia',date], True) + "\n• Exámenes PCR total: " + locale.format_string('%.0f', dataPCR.loc['Total realizados',date], True) + "\n• Camas críticas disponibles: " + locale.format_string('%.0f', dataCamasCrit.loc['disponibles',date], True) + "\n• Positividad PCR: " + locale.format_string('%.2f', dataPos.loc['positividad pcr',date]*100, True) + "%"
        return string_data
    
    response = requests.get("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto4/" + date_str + "-CasosConfirmados-totalRegional.csv")

    if response.status_code == 200:
       bodystring = reportecovid(date_str,datem1_str)
    
    else: 
       i=0
       while response.status_code != 200:
          i+=1
          date = datetime.now(tz) - timedelta(days=i)
          datem1 = date - timedelta(days=1)
          date_str = date.strftime("%Y-%m-%d")
          datem1_str = datem1.strftime("%Y-%m-%d")
          response = requests.get("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto4/" + date_str + "-CasosConfirmados-totalRegional.csv")  


    bodystring = "El reporte COVID de hoy no está disponible aún. El último reporte disponible es el del día " + date.strftime("%A %d-%m-%Y") + ".\n\n" + reportecovid(date_str,datem1_str)


    # Text response
    if msg == "reporte":
       #reply.body("¡Holis! 😄")
       reply.body(bodystring)
 
    # # Image response
    # elif msg == "image":
    #    reply.media('https://i.kym-cdn.com/photos/images/newsfeed/000/319/137/bf3.jpg',caption="jj ccp")
    # # Audio response
    # elif msg == "audio":
    #    reply.media('http://www.largesound.com/ashborytour/sound/brobob.mp3')
    # # Video response
    # elif msg == "video":
    #    reply.media('https://www.appsloveworld.com/wp-content/uploads/2018/10/640.mp4')
    
    # # File response   
    # elif msg == "file":
    #    reply.media('http://www.africau.edu/images/default/sample.pdf')
       
    # # resp = MessagingResponse()
    # # resp.message("You said: {}".format(msg))
    else:
        reply.body("""Escribe la palabra "reporte" para obtener el reporte COVID de hoy""")
 
    return str(resp)
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
