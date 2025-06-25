from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# === DINA UPPGIFTER HÄR ===
EMAIL = "joel.silemo@stenarecycling.se"
PASSWORD = "Huddingefragg123"
LOGIN_URL = "https://apps.el-kretsen.se/ElcopiaLevportal/CheckSignIn?ReturnUrl=%2fElcopiaLevportal%2fSignOut.aspx"
MAIN_PAGE_URL = "https://apps.el-kretsen.se/ElcopiaLevportal/MainPage.aspx"

# === STARTA SELENIUM ===
options = Options()
options.add_argument("--start-maximized")
service = Service()  # ChromeDriver måste finnas i PATH
driver = webdriver.Chrome(service=service, options=options)



# === Kontrollera om vi redan är på MainPage ===
driver.get("https://apps.el-kretsen.se/ElcopiaLevportal/MainPage.aspx")
time.sleep(2)

if "MainPage.aspx" in driver.current_url and "Logga in" not in driver.page_source:
    print("Redan inloggad – hoppar över inloggning.")
    login = false
else:
    print("Inte inloggad – loggar in nu...")
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.presence_of_element_located((By.ID, "txtUName")))
    password_input = driver.find_element(By.ID, "txtPass")
    login_button = driver.find_element(By.ID, "Button1")
    username_input.send_keys(EMAIL)
    password_input.send_keys(PASSWORD)
    login_button.click()
    time.sleep(3)


    # === STEG 2: NAVIGERA TILL HUVUDSIDAN ===
   # wait.until(EC.url_contains("MainPage.aspx"))
   # driver.get(MAIN_PAGE_URL)
    
    time.sleep(3) # Vänta lite efter inloggning (ny kod)
    driver.get(MAIN_PAGE_URL) # ny kod

    time.sleep(3)

    # === STEG 3: LADDA INLEVERANSER VIA AJAX ===
    driver.execute_script("""
        fetch('/ElcopiaLevportal/MainPage.aspx/loadUserControl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({inControl: 'InleveranserFB.ascx', inParam: ''})
        }).then(response => response.text()).then(data => {
            document.body.innerHTML = data;
        });
    """)
    time.sleep(3)

    # === STEG 4: PARSA HTML-TABELLEN ===
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', {'id': 'ctl00_tableInleveranserFb'})

    headers = [th.get_text(strip=True) for th in table.find_all('th')]
    rows = []
    for tr in table.find_all('tr')[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all('td')]
        if cells:
            rows.append(cells)

    df = pd.DataFrame(rows, columns=headers)

    # === STEG 5: SPARA SOM EXCEL ===
    df.to_excel("inleveranser.xlsx", index=False)
    print(" Tabellen har sparats som 'inleveranser.xlsx'.")

    driver.quit()
