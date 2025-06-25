from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

# === DINA UPPGIFTER HÄR ===
EMAIL = "din@email.se"
PASSWORD = "dittlösenord"
LOGIN_URL = "https://apps.el-kretsen.se/ElcopiaLevportal/CheckSignIn?ReturnUrl=%2fElcopiaLevportal%2fSignOut.aspx"
LOAD_URL = "https://apps.el-kretsen.se/ElcopiaLevportal/MainPage.aspx/loadUserControl"

# === STARTA SELENIUM OCH LOGGA IN ===
options = Options()
options.add_argument("--headless")  # Kör utan fönster
options.add_argument("--disable-gpu")
service = Service()
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.presence_of_element_located((By.ID, "txtUName")))
    password_input = driver.find_element(By.ID, "txtPass")
    login_button = driver.find_element(By.ID, "Button1")

    username_input.send_keys(EMAIL)
    password_input.send_keys(PASSWORD)
    login_button.click()

    time.sleep(5)  # Vänta på att inloggning slutförs
    


    # === EXTRAHERA COOKIES ===
    cookies = driver.get_cookies()
    
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

finally:
    driver.quit()

# === GÖR POST-ANROP TILL loadUserControl ===
headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://apps.el-kretsen.se/ElcopiaLevportal/MainPage.aspx"
}
payload = {"inControl": "InleveranserFB.ascx", "inParam": ""}

response = session.post(LOAD_URL, json=payload, headers=headers)
print("Statuskod:", response.status_code)
print("Svarstyp:", response.headers.get("Content-Type"))
print("Svar (första 500 tecken):")
print(response.text[:500])

html_data = response.json()["d"]

# === PARSA HTML-TABELLEN ===
soup = BeautifulSoup(html_data, "html.parser")
table = soup.find("table", {"id": "ctl00_tableInleveranserFb"})

headers = [th.get_text(strip=True) for th in table.find_all("th")]
rows = []
for tr in table.find_all("tr")[1:]:
    cells = [td.get_text(strip=True) for td in tr.find_all("td")]
    if cells:
        rows.append(cells)

df = pd.DataFrame(rows, columns=headers)

# === SPARA SOM EXCEL ===
df.to_excel("inleveranser.xlsx", index=False)
print("✅ Tabellen har sparats som 'inleveranser.xlsx'.")
