from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import re
import requests
import os
from apps.entry.models import Regions, Residences, Types, Options
from .models import GeneratedURL
def parse_number(value):
    """ 문자열로 입력된 숫자를 정수로 변환, '억'과 '만원' 단위를 처리 """
    value = value.replace('억', '0000').replace('만원', '')
    return str(int(re.sub(r'[^0-9]', '', value)))

def get_location(address):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + address
    headers = {"Authorization": "KakaoAK " + os.getenv("KAKAO_AK")}
    response = requests.get(url, headers=headers)
    api_json = response.json()
    if api_json['documents']:
        address_info = api_json['documents'][0]['address']
        crd = {"lat": str(address_info['y']), "lng": str(address_info['x'])}
        address_name = address_info['address_name']
        return crd
    return None

class URLGenerator(APIView):
    def get(self, request):
        try:
            region = Regions.objects.order_by('-id').first()
            residence = Residences.objects.order_by('-id').first()
            types = Types.objects.order_by('-id').first()
            options = Options.objects.order_by('-id').first()

            if not residence:
                return Response({"error": "거주 형태가 선택되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

            if residence.apartment:
                base_url = "https://dabangapp.com/map/apt?"
            elif residence.officetel:
                base_url = "https://dabangapp.com/map/officetel?"
            elif residence.house:
                base_url = "https://dabangapp.com/map/house?"
            elif residence.onetwo:
                base_url = "https://dabangapp.com/map/onetwo?"
            else:
                return Response({"error": "거주 형태가 선택되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

            params = []

            if types.LEASE:
                params.append('sellingTypeList=%5B%22LEASE%22%5D')
                params.append(f'depositRangeMax={parse_number(types.depositRangeMax)}')
            if types.MONTHLY_RENT:
                params.append('sellingTypeList=%5B%22MONTHLY_RENT%22%5D')
                params.append(f'depositRangeMax={parse_number(types.depositRangeMax)}')
                params.append(f'priceRangeMax={parse_number(types.priceRangeMax)}')

            if options.canParking:
                params.append('canParking=true')
            if options.hasElevator:
                params.append('hasElevator=true')
            if options.parkingNumRangeMin > 0:
                params.append(f'parkingNumRangeMin={options.parkingNumRangeMin}')
            if options.roomCount > 0:
                room_count_map = {
                    1: "ONE_ROOM",
                    2: "TWO_ROOM",
                    3: "THREE_ROOM",
                    4: "FOUR_ROOM",
                }
                if options.roomCount in room_count_map:
                    params.append(f'roomCount={room_count_map[options.roomCount]}')
            if options.isShortLease:
                params.append('isShortLease=true')
            if options.isDivision:
                params.append('isDivision=true')
            if options.isDuplex:
                params.append('isDuplex=true')

            url = base_url + "&".join(params)
            url += f'&m_lat={region.latitude}&m_lng={region.longitude}&m_zoom=16'

            GeneratedURL.objects.create(url=url)

            return Response({"url": url}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)