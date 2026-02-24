import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from twilio.rest import Client

URL = "https://www.totalticket.com.br/novorizontino"
PALAVRA_CHAVE = "Nacional"

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")

alerta_enviado = False


def enviar_whatsapp():
    try:
        if not TWILIO_SID or not TWILIO_TOKEN:
            print("❌ Credenciais Twilio não configuradas.")
            return

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
    chrome_options = Options()

    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # caminhos padrão do Railway
    chrome_options.binary_location = "/usr/bin/chromium"

    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def verificar_jogo():
    global alerta_enviado
    driver = None

    try:
        driver = criar_driver()

        print("🌐 Acessando página...")
        driver.get(URL)

        time.sleep(8)  # tempo para JS carregar

        eventos = driver.find_elements(By.CSS_SELECTOR, ".event-feed.latest")
        print(f"📋 Eventos encontrados: {len(eventos)}")

        for evento in eventos:
            try:
                nome_evt = evento.find_element(
                    By.CSS_SELECTOR, "ul.empresa_24"
                ).get_attribute("data-nome-evt")

                print("➡️ Evento:", nome_evt)

                if PALAVRA_CHAVE.lower() in nome_evt.lower():
                    print("🔥 JOGO ENCONTRADO!")

                    if not alerta_enviado:
                        enviar_whatsapp()
                        alerta_enviado = True
                    else:
                        print("⚠️ Alerta já enviado.")

                    return True

            except Exception as e:
                print("⚠️ Erro ao ler evento:", e)

        alerta_enviado = False
        print("❌ Evento ainda não disponível.")
        return False

    except Exception as e:
        print("💥 Erro geral:", e)

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    print("🚀 Monitor iniciado...")

    while True:
        try:
            print("\n🔄 Nova verificação...")
            verificar_jogo()
        except Exception as e:
            print("💥 Erro no loop:", e)

        time.sleep(120)  # 2 minutos