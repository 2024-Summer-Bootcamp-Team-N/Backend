# your_app/tasks.py

from celery import shared_task
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
from .models import RoomInfo
from ..info.models import GeneratedURL
import logging
import environ
import os
from pathlib import Path

logger = logging.getLogger(__name__)
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

disable_blink_features = env('DISABLE_BLINK_FEATURES')
exclude_switches = env('EXCLUDE_SWITCHES')
use_automation_extension = env('USE_AUTOMATION_EXTENSION')
user_agent = env('USER_AGENT')

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--ignore-ssl-errors=yes")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument(disable_blink_features)
    chrome_options.add_experimental_option("excludeSwitches", [exclude_switches])
    chrome_options.add_experimental_option('useAutomationExtension', use_automation_extension.lower() == 'true')
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.binary_location = "/usr/bin/chromium"

    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def get_total_pages(driver, url):
    driver.get(url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "styled__Price-sc-1lx6b5d-4"))
    )

    # 총 페이지 수를 추출하는 로직
    pagination_elements = driver.find_elements(By.CSS_SELECTOR, ".pagination .page-link")
    if pagination_elements:
        last_page_number = pagination_elements[-1].text
        try:
            total_pages = int(last_page_number)
        except ValueError:
            total_pages = 1  # 숫자로 변환할 수 없는 경우 기본값 1
    else:
        total_pages = 1  # 페이지 네이션 요소가 없는 경우 기본값 1

    return total_pages

def crawl_page(url, page_num):
    driver = setup_driver()
    try:
        driver.get(f"{url}?page={page_num}")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "styled__Price-sc-1lx6b5d-4"))
        )

        price_list = driver.find_elements(By.CLASS_NAME, "styled__Price-sc-1lx6b5d-4")
        room_info_list = driver.find_elements(By.CLASS_NAME, "styled__RoomInfo-sc-1lx6b5d-6")
        link_list = driver.find_elements(By.CLASS_NAME, "styled__RoomLink-sc-1lx6b5d-0")

        entries = []
        num_records = min(len(price_list), len(room_info_list), len(link_list))
        for idx in range(num_records):
            new_entry = RoomInfo(
                price=price_list[idx].text,
                room_info=room_info_list[idx].text,
                link=link_list[idx].get_attribute('href')
            )
            new_entry.save()
            entries.append(new_entry)

        # 화면 캡처 저장
        screenshot_path = f'/app/screenshots/page_{page_num}.png'
        driver.save_screenshot(screenshot_path)
        logger.info(f"스크린샷 저장: {screenshot_path}")

        return entries
    finally:
        driver.quit()

@shared_task
def crawl_latest_url():
    try:
        url_record = GeneratedURL.objects.order_by('-id').first()
        if not url_record:
            return {"error": "URL 레코드를 찾을 수 없습니다."}

        url = url_record.url

        driver = setup_driver()
        total_pages = get_total_pages(driver, url)
        driver.quit()

        new_entries = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(crawl_page, url, page) for page in range(1, total_pages + 1)]
            for future in futures:
                result = future.result()
                if result:
                    new_entries.extend(result)

        serialized_data = [
            {
                "id": entry.id,
                "price": entry.price,
                "room_info": entry.room_info,
                "link": entry.link
            }
            for entry in new_entries
        ]
        response_data = {
            "new_room_info_list": serialized_data,
            "new_room_info_count": len(serialized_data),
        }

        return response_data

    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {str(e)}")
        return {"error": str(e)}