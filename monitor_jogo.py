import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client

URL = "https://www.totalticket.com.br/novorizontino"
PALAVRA_CHAVE = "Corinthians"

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")

alerta_enviado = False


def enviar_whatsapp():
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)

        message = client.messages.create(
            from_="whatsapp:+14155238886",
            body="🔥 ALERTA: Saiu ingresso do jogo que você está monitorando!",
            to="whatsapp:+5514991478266",
        )

        print("✅ WhatsApp enviado:", message.sid)

    except Exception as e:
        print("❌ Erro WhatsApp:", e)


def criar_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def verificar_jogo():
    global alerta_enviado

    driver = criar_driver()

    try:
        driver.get(URL)
        time.sleep(6)

        eventos = driver.find_elements(By.CSS_SELECTOR, ".event-feed.latest")

        for evento in eventos:
            nome_evt = evento.find_element(
                By.CSS_SELECTOR, "ul.empresa_24"
            ).get_attribute("data-nome-evt")

            print("Evento:", nome_evt)

            if PALAVRA_CHAVE.lower() in nome_evt.lower():
                if not alerta_enviado:
                    enviar_whatsapp()
                    alerta_enviado = True
                return True

        alerta_enviado = False
        return False

    finally:
        driver.quit()


if __name__ == "__main__":
    while True:
        print("🔄 Verificando...")
        verificar_jogo()
        time.sleep(120)