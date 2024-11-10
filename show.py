import platform
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchDriverException

"""
Dieses Script öffnet einen Browser und scrollt durch einen Forum-Thread. 
Dabei wird ein Overlay mit einem Text angezeigt und einige Elemente ausgeblendet.
"""
current_os = platform.system()

# WebDriver konfigurieren
chrome_options = Options()
chrome_options.add_argument("--start-fullscreen")
# chrome_options.add_argument("--start-maximized")  # Startet im Vollbildmodus
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Entfernt das "ferngesteuert"-Banner
chrome_options.add_experimental_option("useAutomationExtension", False)

# chrome_options.add_argument('--headless')
if current_os == "Windows":
    service = Service('./chromedriver.exe')
elif current_os == "Linux":
    service = Service('./chromedriver')

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
except NoSuchDriverException as e:
    print("Chromedriver nicht gefunden (https://chromedriver.chromium.org/downloads)")
    exit(1)

def main():
    overlay_content = '<h1 style="color: white; margin: 20px; text-align:center;">Technik-AG - heute live in Raum 0.06</h1>'

    overlay_html = f"""
        var overlay = document.createElement('div');
        overlay.innerHTML = '{overlay_content}';
        overlay.style.position = 'fixed';
        overlay.style.bottom = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '70px';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        overlay.style.color = 'white';
        overlay.style.zIndex = '1000';
        document.body.appendChild(overlay);
    """

    driver.get("https://forum.szas.org/t/-/4779")
    time.sleep(1)

    driver.execute_script(overlay_html)

    # cookies akzeptieren
    click_element(".cc-compliance")
    click_element(".btn-sidebar-toggle") 

    hide_elements([".timeline-container", ".post-avatar",".login-button",".sidebar-wrapper"])

    set_zoom_level(2)

    try:
        smooth_scroll_to_end(driver, pause_time=0.0005, scroll_speed=1)
    except Exception as e:
        pass

def set_zoom_level(zoom_level):
    zoom_level = zoom_level*100
    driver.execute_script(f"document.body.style.zoom = '{zoom_level}%';")

def click_element(selector, by=By.CSS_SELECTOR):
    try:
        element = driver.find_element(by, selector)
        element.click()
    except Exception as e:
        print("Element nicht gefunden oder konnte nicht angeklickt werden:", e)

def params(**kwargs):
    return json.dumps(kwargs)


def bounding_client_rect(selector, by=By.CSS_SELECTOR):
    try:
        element = driver.find_element(by, selector)
        return element.rect
    except Exception as e:
        return None

def is_element_in_viewport(selector, by=By.CSS_SELECTOR):
    try:
        element = driver.find_element(by, selector)
        return driver.execute_script("var rect = arguments[0].getBoundingClientRect(); return (rect.top >= 0 && rect.bottom <= window.innerHeight);", element)
    except Exception as e:
        return False

# Funktion zum Scrollen mit einstellbarer Geschwindigkeit
def smooth_scroll_to_end(driver, pause_time=1, scroll_speed=300, max_scroll_attempts=50, page_height = 1200, slow = 100, forever = True):
    scroll_attempts = 0
    last_height = driver.execute_script("return window.pageYOffset")

    while scroll_attempts < max_scroll_attempts:

        y_offset = driver.execute_script("return window.pageYOffset")

        speed = scroll_speed
        if y_offset % page_height > slow:
            speed = 15*scroll_speed
        

        driver.execute_script(f"window.scrollBy({params(top=speed,left=0,behavior = "smooth")});")
        time.sleep(pause_time)

        if is_element_in_viewport(".topic-footer-main-buttons"):
            time.sleep(2)
            if forever:
                driver.execute_script(f"window.scrollTo(0,0);")
            else:
                break

        new_height = driver.execute_script("return window.pageYOffset")

        # print(scroll_attempts, last_height, new_height, y_offset)
        if new_height == last_height:
            if scroll_attempts > 10:
                break
        else:
            scroll_attempts = 0 

        last_height = new_height
        scroll_attempts += 1

def hide_elements(css_selectors):
    for selector in css_selectors:
        driver.execute_script(f"document.querySelectorAll('{selector}').forEach(el => el.style.display = 'none');")

main()

driver.quit()



