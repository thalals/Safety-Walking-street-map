import pymysql
import json
def insertsql_from_json():
    # connection 정보

    # 접속
    # 비밀번호가 포함되어 있기 때문에 보통 config파일에서 key값으로 부른다.
    conn = pymysql.connect(
        host = "localhost", 	 #ex) '127.0.0.1'
        port=3306,
        user = "root", 		 #ex) root
        password = "1234",
        database = "safemap",
        charset = 'utf8'
    )
    # Cursor Object 가져오기
    curs = conn.cursor()

    check_number =0;
    try :    
        #geoJson 가져오기
        with open('static/json/AvailableLoadData.json', encoding='utf-8') as json_file:
            json_data = json.load(json_file)
            #json의 key로 접근
            #json_line : json 객체를 가지는 Array
            json_line = json_data['geometries']

            # print(len(json_line))
            # a =[]
            count=0;
            while(check_number!=len(json_line)) :
                print(check_number)

                lon1 = json_line[check_number]['coordinates'][0]
                lat1 = json_line[check_number]['coordinates'][1]
                check_number+=1

                lon2 = json_line[check_number]['coordinates'][0]
                lat2 = json_line[check_number]['coordinates'][1]
                check_number+=1

                lon3 = json_line[check_number]['coordinates'][0]
                lat3 = json_line[check_number]['coordinates'][1]
                check_number+=1

                lon4 = json_line[check_number]['coordinates'][0]
                lat4 = json_line[check_number]['coordinates'][1]
                check_number+=1

                sql = "INSERT INTO loadpoint(lat, lon) VALUES (%s, %s), (%s, %s), (%s, %s), (%s, %s)"
                val = (float(lat1), float(lon1), float(lat2), float(lon2), float(lat3), float(lon3), float(lat4), float(lon4))

                curs.execute(sql, val)
            conn.commit()
            # for a in json_line:
            #     lon = a['coordinates'][0]
            #     lat = a['coordinates'][1]

            #     sql = "INSERT INTO loadpoint(lat, lon) VALUES (%s, %s)"
            #     val = (float(lat), float(lon))

            #     curs.execute(sql, val)
            #     print(check_number)
            #     check_number+=1

            # conn.commit()
    finally :
        conn.close()


    print("record inserted")

insertsql_from_json()

def json_test():
    #geoJson 가져오기
    with open('static/json/AvailableLoadData.json', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
        #json의 key로 접근
        #json_line : json 객체를 가지는 Array
        json_line = json_data['geometries']
        
        for a in json_line:
            lat = a['coordinates'][0]
            lon = a['coordinates'][1]

            print(lat)

#json_test()
