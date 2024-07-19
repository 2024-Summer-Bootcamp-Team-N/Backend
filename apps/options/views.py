from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.info.models import GeneratedURL
from .models import RoomInfo, RoomDetailInfo
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
import time
import environ
import os
from pathlib import Path

from .serializers import RoomDetailInfoSerializer

logger = logging.getLogger(__name__)
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR,'.env'))
# 환경변수 로드
disable_blink_features = env('DISABLE_BLINK_FEATURES')
exclude_switches = env('EXCLUDE_SWITCHES')
use_automation_extension = env('USE_AUTOMATION_EXTENSION')
user_agent = env('USER_AGENT')

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저 헤드리스 모드로 실행
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--ignore-ssl-errors=yes")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument(disable_blink_features)
    chrome_options.add_experimental_option("excludeSwitches", [exclude_switches])
    chrome_options.add_experimental_option('useAutomationExtension', use_automation_extension.lower() == 'true')
    chrome_options.add_argument(f"user-agent={user_agent}")

    chrome_options.binary_location = "/usr/bin/chromium"  # 크로미움 경로

    # Chrome WebDriver 설정
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

class GenerateAndCrawlView(APIView):
    def get(self, request, *args, **kwargs):
        driver = setup_driver()
        try:
            # 최신 생성된 GeneratedURL 레코드 가져오기
            url_record = GeneratedURL.objects.order_by('-id').first()
            if not url_record:
                return Response({"error": "URL 레코드를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            url = url_record.url

            # Chrome 옵션 설정

            new_entries = []  # 새로운 엔트리를 저장할 리스트

            try:
                # URL로 이동
                driver.get(url)
                logger.info(f"다음 URL로 이동: {url}")

                while True:
                    # 특정 요소가 로드될 때까지 대기
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "styled__Price-sc-1lx6b5d-4"))
                    )

                    # 가격, 방 정보, 링크를 저장할 리스트
                    price_list = driver.find_elements(By.CLASS_NAME, "styled__Price-sc-1lx6b5d-4")
                    room_info_list = driver.find_elements(By.CLASS_NAME, "styled__RoomInfo-sc-1lx6b5d-6")
                    link_list = driver.find_elements(By.CLASS_NAME, "styled__RoomLink-sc-1lx6b5d-0")

                    # 데이터베이스에 저장 및 새로운 엔트리에 추가
                    num_records = min(len(price_list), len(room_info_list), len(link_list))
                    for idx in range(num_records):
                        new_entry = RoomInfo(
                            price=price_list[idx].text,
                            room_info=room_info_list[idx].text,
                            link=link_list[idx].get_attribute('href')
                        )
                        new_entry.save()
                        new_entries.append(new_entry)

                    # 다음 페이지 버튼 클릭하기
                    try:
                        # 현재 페이지 버튼 찾기
                        current_page_button = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "styled__PageBtn-d24fjp-2.cbZgbl"))
                        )

                        # 다음 페이지 버튼 찾기
                        next_page_button = current_page_button.find_element(By.XPATH, "./following-sibling::button[@class='styled__PageBtn-d24fjp-2 caslEP']")

                        # 다음 페이지로 이동
                        if next_page_button:
                            next_page_button.click()
                            time.sleep(0.1)  # 페이지 로딩 시간을 고려하여 잠시 대기
                        else:
                            break  # 다음 페이지 버튼이 없으면 루프 종료

                    except Exception as e:
                        break  # 다음 페이지 버튼을 찾을 수 없으면 루프를 종료

                # Response에 반환할 데이터 구성
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
                    "new_room_info_count": len(serialized_data),  # 새로 추가된 RoomInfo 객체 수
                }

                return Response(response_data, status=status.HTTP_200_OK)

            finally:
                driver.quit()

        except Exception as e:
            logger.error(f"크롤링 중 오류 발생: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from selenium.webdriver.common.by import By

def find_element_text(driver, header_text):
    try:
        # 요소가 로드될 때까지 기다리기
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.XPATH, f"//section[@data-scroll-spy-element='info']//li[div[@class='styled__ListHeader-ialnoa-6 jJKkgc']/h1[text()='{header_text}']]/div[@class='styled__ListContent-ialnoa-7 iMduqg']/p")))

        # 전체 텍스트 가져오기
        full_text = element.text
        # span 태그의 텍스트 부분 제거
        span_elements = element.find_elements(By.TAG_NAME, 'span')
        for span in span_elements:
            full_text = full_text.replace(span.text, '')

        return full_text.strip()
    except Exception as e:
        # 에러 로그 기록
        logger.error(f"Error finding info element with header '{header_text}': {str(e)}")
        return '-'

class DetailedRoomInfoView(APIView):
    def get(self, request, room_id=None, *args, **kwargs):
        try:
            room = RoomInfo.objects.get(id=room_id)
            link = room.link

            driver = setup_driver()
            try:
                driver.get(link)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "styled__SubInfo-sc-1h4thfr-18"))
                )

                try:
                    location_element = driver.find_element(By.XPATH, "//li[@class='styled__SubInfo-sc-1h4thfr-18 etnpDk']//p[@class='title' and text()='위치']/following-sibling::p[@class='content']")
                    location_text = location_element.text
                except Exception as e:
                    logger.error(f"Error finding location: {str(e)}")
                    location_text = '-'

                try:
                    maintenance_fee_element = driver.find_element(By.CLASS_NAME, "styled__MaintenanceCostWrap-mttebe-2")
                    maintenance_fee_text = maintenance_fee_element.text
                except Exception as e:
                    logger.error(f"Error finding maintenance fee: {str(e)}")
                    maintenance_fee_text = '-'

                try:
                    price_section = driver.find_element(By.XPATH, "//section[@data-scroll-spy-element='price']")
                    parking_availability_header = price_section.find_element(By.XPATH,
                                                                             ".//div[@class='styled__ListHeader-mttebe-0 gfmTEV' and h1[text()='주차가능여부']]")
                    parking_availability_element = parking_availability_header.find_element(By.XPATH,
                                                                                            "./following-sibling::div[@class='styled__ListContent-mttebe-1 bQSaMO']/p")
                    parking_availability_text = parking_availability_element.text if parking_availability_element else '-'
                except Exception as e:
                    logger.error(f"Error finding parking availability: {str(e)}")
                    parking_availability_text = '-'



                # 크롤링할 항목들
                room_type_text = find_element_text(driver, '방종류')
                exclusive_overall_area_text = find_element_text(driver, '전용/공급면적')
                num_rooms_bathrooms_text = find_element_text(driver, '방 수/욕실 수')
                floor_building_floors_text = find_element_text(driver, '해당층/건물층')
                direction_text = find_element_text(driver, '방향')
                total_parking_spaces_text = find_element_text(driver, '총 주차대수')
                heating_type_text = find_element_text(driver, '난방종류')
                building_use_text = find_element_text(driver, '건축물용도')
                move_in_date_text = find_element_text(driver, '입주가능일')
                approval_date_text = find_element_text(driver, '사용승인일')
                initial_registration_date_text = find_element_text(driver, '최초등록일')

                # RoomDetailInfo 모델에 저장
                room_detail, created = RoomDetailInfo.objects.update_or_create(
                    room=room,
                    defaults={
                        'location': location_text,
                        'exclusive_overall_area': exclusive_overall_area_text,
                        'maintenance_fee': maintenance_fee_text,
                        'room_type': room_type_text,
                        'num_rooms_bathrooms': num_rooms_bathrooms_text,
                        'floor_building_floors': floor_building_floors_text,
                        'direction': direction_text,
                        'parking_availability': parking_availability_text,
                        'total_parking_spaces': total_parking_spaces_text,
                        'heating_type': heating_type_text,
                        'building_use': building_use_text,
                        'move_in_date': move_in_date_text,
                        'approval_date': approval_date_text,
                        'initial_registration_date': initial_registration_date_text
                    }
                )

                serializer = RoomDetailInfoSerializer(room_detail)
                response_data = {
                    "room_detail_info": serializer.data,
                }

                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"크롤링 중 오류 발생: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            finally:
                driver.quit()

        except RoomInfo.DoesNotExist:
            return Response({"error": "RoomInfo 레코드를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"크롤링 중 오류 발생: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)