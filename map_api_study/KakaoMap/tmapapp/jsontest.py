import json
    

#경기 라인 json 파일 보기
# with를 이용해 파일을 연다.

coordinates_Array = [] #전체
coordinates_part = [] # 고속도로와 대로를 제거한 길

def jsonShow_Gline():
    #with와 json 모듈을 이용해 Json파일 불러오기
    with open('static/json/Gline_result_data.geojson', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
        #json의 key로 접근
        #json_line : json 객체를 가지는 Array
        json_line = json_data['features']

        for a in json_line:
            if(a['properties']['ROA_CLS_SE']=='3' or a['properties']['ROA_CLS_SE']=='4' ):     #고속도로와 대로 제거
                coordinates_part.append(a['geometry']['coordinates'])

            coordinates_Array.append(a['geometry']['coordinates'])

    print("경기도 전체 라인\n첫번째 배열 : ",coordinates_Array[0])
    print("전체 길이 : ",len(coordinates_Array))

    print("고속도로, 대로 제거 라인\n첫번째 배열 : ",coordinates_part[0])
    print("제거 라인 길이 : ",len(coordinates_part))

jsonShow_Gline()



