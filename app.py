from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import xml.etree.ElementTree as ET
import requests
import streamlit as st
import googlemaps

gmaps = googlemaps.Client(key='AIzaSyDzp93kH-G8ygGQGIfc97ljgpQQwWFkXqQ')


title="<h1 style='text-align: center;'>🚑응급실 삐용삐용🚑</h1>"
st.markdown(title, unsafe_allow_html=True)
with st.form("recommendation_form"):
    st.write("소요 시간 예측을 위해 나이와 성별을 기입해주세요.")
    age = st.number_input('Age',min_value=2, max_value=120, step=1)
    gender = st.radio('Gender',('Male','Female'))
    submitted = st.form_submit_button("생성")

import folium
from streamlit_folium import st_folium, folium_static

if submitted:
    # st.write(current_location)
    lat = "37.503316"
    lon = "127.041683"
    reverse_geocode_result = gmaps.reverse_geocode((lat, lon), language='ko')
    datas =[item['formatted_address'] for item in reverse_geocode_result]
    
        # folium 지도 생성
        #m = folium.Map(location=[lat, lon], zoom_start=18)
        #folium.Marker([lat, lon], popup='Your Location').add_to(m)
    
        # folium_static을 사용하여 folium 맵을 Streamlit 앱에 표시
        #folium_static(m)
    
    es = Elasticsearch(cloud_id="ABC-JYPE:dXMtd2VzdC0yLmF3cy5mb3VuZC5pbzo0NDMkNzllZmQ3YTY0YWQxNDgzMDhjZDQzYWVmYTQ3Zjg0NzQkOTU5MWQwOWM4MmFjNDUyMDhhMDU1MTc1YmVlNDY5NDM=", api_key="eHJocEpJNEJ6T0c4TnY3aHY1Qk06ZEFYN1hFVjhTa3FwRTV4aE9KWVhkdw==")
    
    # 거리 쿼리를 위한 중심 좌표
    latitude = 37.503316
    longitude = 127.041683
    
    s = Search(using=es, index="hospital") \
        .query("match_all") \
        .sort({
            "_geo_distance": {
                "location": {
                    "lat": latitude,
                    "lon": longitude
                },
                "order": "asc",  # 가장 가까운 것부터 오름차순으로 정렬
                "unit": "m"  # 거리 단위를 미터로 설정
            }
        })
    
    response = s.execute()
    
        
    if response:
        st.header("병원 안내")
        hospitals = [hit['DUTYNAME'] for hit in response]
        selected_hospitals = st.selectbox("병원 선택", hospitals)
        for hit in response:
            dlat_l = [(hit['location']['lat'])]
            dlon_l = [(hit['location']['lon'])]
            if hit['DUTYNAME'] == selected_hospitals:
                st.subheader("병원 정보")
                dlat = str(hit['location']['lat'])
                dlon = str(hit['location']['lon'])
                # print(dlat_l)
                # print(dlon_l)
                        # folium 지도 생성
                m = folium.Map(location=[dlat, dlon], zoom_start=18)
                folium.Marker([dlat, dlon], popup='Your Location').add_to(m)
            
                # folium_static을 사용하여 folium 맵을 Streamlit 앱에 표시
                #folium_static(m)
                
                print(hit['DUTYADDR'])
                
                google_maps_url = f"https://www.google.com/maps/embed/v1/directions?key=AIzaSyDzp93kH-G8ygGQGIfc97ljgpQQwWFkXqQ&origin=37.5003316,127.041683&destination={dlat},{dlon}"
                st.write(f'<iframe width="600" height="450" frameborder="0" style="border:4" src="{google_maps_url}" allowfullscreen></iframe>', unsafe_allow_html=True)
                #출발지, 도착지, 거리, 소요시간 계산 api
                response = requests.get(f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&mode=transit&origins=37.503316,127.041683&destinations={dlat},{dlon}&region=KR&key=AIzaSyDzp93kH-G8ygGQGIfc97ljgpQQwWFkXqQ")
                data = response.json()
                # st.write(data) #전체 걸리는 시간을 초로 나타낸 것
                st.markdown(f"**연락처: {hit['DUTYTEL3']}")
                st.write("출발지 : " + datas[0])
                st.write(f"주소: {hit['DUTYADDR']}")
                distance_text = data['rows'][0]['elements'][0]['distance']['text']
                duration_text = data['rows'][0]['elements'][0]['duration']['text']
                st.write("거리 : " + distance_text)
                st.write("소요 시간 : " + duration_text)
                st.write(f"진료: {hit['DUTYINF']}")
                
                url = 'http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire'
                params ={'serviceKey' : 'HcMdtdccBIhT9uUdi4wT33I6TXJ5Nx6NDOWrAbYQ5XlqQUqCo%2B3q%2BSCa8suCLPnx%2FLyjfvLnAS1lZGpk869cPA%3D%3D', 'STAGE1' : '서울특별시', 'STAGE2' : hit['DUTYADDR'].split(' ')[1], 'pageNo' : '1', 'numOfRows' : '10'}
                print(params)
                response1 = requests.get(url, params=params)
                print(response1)
    
                #XML 파싱
                root = ET.fromstring(response1.content)
                print(f">>>>>>>>>>>>>>> ${root}")
                
                answer = []
                # 각 item에서 hvec, dutyName, dutyTel3 추출
                for item in root.findall('.//item'):
                    lists = []
                    hvec = item.find('hvec').text
                    lists.append(hvec)
                    duty_name = item.find('dutyName').text
                    lists.append(duty_name)
                    duty_tel3 = item.find('dutyTel3').text
                    lists.append(duty_tel3)
                    hv4 = item.find('hv4')
                    lists.append(hv4)
                    hv5 = item.find('hv5')
                    lists.append(hv5)
                    hv31 = item.find('hv31')
                    hv33 = item.find('hv33')
                    hv36 = item.find('hv36')
                    hv37 = item.find('hv37')
                    answer.append(lists)
                print(answer)
                for i in range(len(list(answer))):
                    if answer[i][1] == hit['DUTYNAME']:
                        
                        st.write(f'현재 병상 수: {str(answer[i][0])}')
    
                  #  for i in range(len(new_data)):
                   #     if duty_name == new_data['duty_name']:
                    #        st.write(new_data['hv4'][i])
                     #       st.write(new_data['hv5'][i])
    
                            
               
                    print(hit.meta.id, hit.DUTYNAME, hit.meta.score)
