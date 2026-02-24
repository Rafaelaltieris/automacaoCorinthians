import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client

URL = "https://www.totalticket.com.br/novorizontino"
PALAVRA_CHAVE = "Nacional"

# 🔒 pegar do ambiente (Railway/Render/etc)
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")

# 🧠 controle anti-spam
alerta_enviado = False


def enviar_whatsapp():
    try:
        print("📱 Enviando WhatsApp via Twilio...")

        client = Client(TWILIO_SID, TWILIO_TOKEN)

        message = client.messages.create(
            from_="whatsapp:+14155238886",
            body="🔥 ALERTA: Saiu ingresso do jogo que você está monitorando!",
            to="whatsapp:+5514991478266",
        )

        print("✅ Mensagem enviada! SID:", message.sid)

    except Exception as e:
        print("❌ Erro ao enviar WhatsApp:", e)


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
        print("🔎 Acessando página...")
        driver.get(URL)

        time.sleep(6)

        eventos = driver.find_elements(By.CSS_SELECTOR, ".event-feed.latest")
        print(f"📋 Eventos encontrados: {len(eventos)}")

        for evento in eventos:
            try:
                nome_evt = evento.find_element(
                    By.CSS_SELECTOR, "ul.empresa_24"
                ).get_attribute("data-nome-evt")

                print(f"➡️ Evento: {nome_evt}")

                if PALAVRA_CHAVE.lower() in nome_evt.lower():
                    print("🔥 JOGO ENCONTRADO!")

                    if not alerta_enviado:
                        enviar_whatsapp()
                        alerta_enviado = True
                    else:
                        print("⚠️ Alerta já enviado anteriormente.")

                    return True

            except Exception as e:
                print("⚠️ Erro ao ler evento:", e)

        print("❌ Evento ainda não disponível.")
        alerta_enviado = False
        return False

    finally:
        driver.quit()


# 🔁 LOOP INFINITO (produção)
if __name__ == "__main__":
    while True:
        try:
            print("\n🔄 Nova verificação...")
            verificar_jogo()
        except Exception as e:
            print("💥 Erro no loop:", e)

        time.sleep(150)  # 2 minutos e meio