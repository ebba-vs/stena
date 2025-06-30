from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# === DINA UPPGIFTER HÄR ===
EMAIL = "joel.silemo@stenarecycling.se"
PASSWORD = "Huddingefragg123"
LOGIN_URL = "https://apps.el-kretsen.se/ElcopiaLevportal/CheckSignIn?ReturnUrl=%2fElcopiaLevportal%2fSignOut.aspx"

# === STARTA SELENIUM ===
options = Options()
options.add_argument("--start-maximized")
service = Service()
driver = webdriver.Chrome(service=service, options=options)
3 files to stena repo"try:
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 10)

    # === FYLL I FORMULÄRET ===
    username_input = wait.until(EC.presence_of_element_located((By.ID, "txtUName")))
    password_input = driver.find_element(By.ID, "txtPass")
    login_button = driver.find_element(By.ID, "Button1")

    username_input.send_keys(EMAIL)
    password_input.send_keys(PASSWORD)
    login_button.click()

    # === VÄNTA OCH BEKRÄFTA INLOGGNING ===
    time.sleep(5)

    # Kontrollera om ett element som bara finns efter inloggning är synligt
    try:
        wait.until(EC.presence_of_element_located((By.ID, "inleveranserFBpLiMenu")))  # exempel-ID
        print("✅ Inloggning lyckades!")
    except:
        print("⚠️ Inloggning misslyckades eller elementet hittades inte.")

    # Kommentera ut detta för att hålla webbläsaren öppen
    # driver.quit()
finally:
    print("done!")
