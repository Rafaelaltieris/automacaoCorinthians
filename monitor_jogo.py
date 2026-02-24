import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from twilio.rest import Client

print("🚀 Script iniciado", flush=True)

URL = "https://www.totalticket.com.br/novorizontino"
PALAVRA_CHAVE = "Nacional"

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")

alerta_enviado = False


def enviar_whatsapp():
    try:
        if not TWILIO_SID or not TWILIO_TOKEN:
            print("❌ Credenciais Twilio não configuradas.", flush=True)
            return

        client = Client(TWILIO_SID, TWILIO_TOKEN)

        message = client.messages.create(
            from_="whatsapp:+14155238886",
            body="🔥 ALERTA: Saiu ingresso do jogo que você está monitorando!",
            to="whatsapp:+5514991478266",
        )

        print(f"✅ WhatsApp enviado: {message.sid}", flush=True)

    except Exception as e:
        print(f"❌ Erro WhatsApp: {e}", flush=True)


def criar_driver():
    try:
        print("🧠 Iniciando Chrome...", flush=True)

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")

        chrome_options.binary_location = "/usr/bin/chromium"

        service = Service("/usr/bin/chromedriver")

        driver = webdriver.Chrome(service=service, options=chrome_options)

        print("✅ Chrome iniciado", flush=True)
        return driver

    except Exception as e:
        print(f"💥 Erro ao iniciar Chrome: {e}", flush=True)
        raise


def verificar_jogo():
    global alerta_enviado
    driver = None

    try:
        driver = criar_driver()

        print("🌐 Acessando página...", flush=True)
        driver.get(URL)

        time.sleep(12)

        eventos = driver.find_elements(By.XPATH, "//div[contains(@class,'event-feed')]")
        print(f"📋 Eventos encontrados: {len(eventos)}", flush=True)

        for evento in eventos:
            try:
                texto_evento = evento.text
                print(f"➡️ Evento texto: {texto_evento}", flush=True)

                if PALAVRA_CHAVE.lower() in texto_evento.lower():
                    print("🔥 JOGO ENCONTRADO!", flush=True)

                    if not alerta_enviado:
                        enviar_whatsapp()
                        alerta_enviado = True
                    else:
                        print("⚠️ Alerta já enviado.", flush=True)

                    return True

            except Exception as e:
                print(f"⚠️ Erro ao ler evento: {e}", flush=True)

        alerta_enviado = False
        print("❌ Evento ainda não disponível.", flush=True)
        return False

    except Exception as e:
        print(f"💥 Erro geral: {e}", flush=True)

    finally:
        if driver:
            driver.quit()
            print("🧹 Chrome fechado", flush=True)


if __name__ == "__main__":
    print("🚀 Monitor iniciado...", flush=True)

    while True:
        try:
            print("\n🔄 Nova verificação...", flush=True)
            verificar_jogo()
        except Exception as e:
            print(f"💥 Erro no loop: {e}", flush=True)

        time.sleep(120)