from django.http.response import HttpResponse
from django.shortcuts import render
import json
from .models import *

from shapely import *
from shapely.geometry import *
from shapely.ops import unary_union
from shapely.validation import explain_validity
from plpygis import Geometry

import math
import hexgrid # han : pip install hexgrid-py
import morton   #hexgrid package - pip install morton-py..?

from .Astar import *

import folium   #지도데이터 시각화
from folium.features import CustomIcon

import geocoder
#import geojson
import geodaisy.converters as convert
#import geog
g = geocoder.ip('me')   #현재 내위치

# Create your views here.
def thome(reqeust):
    return render (reqeust, "thome.html")

def pathSetting(request):
    map = folium.Map(location=g.latlng,zoom_start=15, width='100%', height='30%',)
    maps=map._repr_html_()  #지도를 템플릿에 삽입하기위해 iframe이 있는 문자열로 반환 
    api_key="l7xxa033eab75a3a4ab38dd11a74fb8b87c6"
    return render(request,'thome.html',{'map':maps,'api_key':api_key})

def pathFinder(request): #위험지역 받는 함수
    global startX,startY,endX,endY,startGu,endGu
    gu_list=['종로구','중구','용산구','성동구','광진구',
    '동대문구','중랑구','성북구','강북구','도봉구',
    '노원구','은평구','서대문구','마포구','양천구',
    '강서구','구로구','금천구','영등포구','동작구',
    '관악구','서초구','강남구','송파구','강동구','부평구',]
    loc_list=[]
    if request.method=="POST":
        startPoint=request.POST.get('start')
        endPoint=request.POST.get('end')
        startX=request.POST.get('startX')
        startY=request.POST.get('startY')
        endX=request.POST.get('endX')
        endY=request.POST.get('endY')
        for find_gu in gu_list:
            if find_gu in startPoint:   #출발지 나 목적지가 gu_list에 있다면
                startGu=find_gu
            else:
                pass
            if find_gu in endPoint:
                endGu=find_gu
            else:
                pass
        # female_start=Female2.objects.filter(female2_crime_type="전체_전체",gu=startGu).all()
        # female_end=Female2.objects.filter(female2_crime_type="전체_전체",gu=endGu).all()
        # female_total=female_start.union(female_end,all=False)
        # for loc in female_total:
        #     gis= Geometry(loc.female2_crime_loc.hex()[8:])
        #     contain_coordinate=shape(gis.geojson)
        #     crime_location={"type":"Feature","geometry":gis.geojson}
        #     loc_list.append(crime_location)
    pistes = {"type":"FeatureCollection","features":loc_list}   #geoJason data:loc_list
    return HttpResponse(json.dumps({'result':pistes}),content_type="application/json")  #json.dump : python -> json object

def normalPath(request):
    global gu_coordinate,startX,startY,endX,endY
    pointlist=[]
    polyline=[]
    line=""
    count=0
    if request.method=="POST":
        pistes=request.POST.get('draw') #경로 좌표 정보(Point, Line)
        pist=pistes.split(",")

        for p in pist:
            #pist.index(p) - p의 위치(index) 반환
            if (pist.index(p)%2==0):    #Point 일때
                x=p     #lat
                print(len(pist))
                print(pist.index(p))
                # print(pist)
                y=pist[(pist.index(p))+1] #lng
                point=[float(y),float(x)]
                pointlist.append(point)

        
    crime_location={"type":"Feature","geometry":{"type":"LineString","coordinates":pointlist}}
  
    pistes = {"type":"FeatureCollection","features":[crime_location]}   #경로 정보
    return HttpResponse(json.dumps({'pistes':pistes}),content_type="application/json")

#hexgrid : 16진수 그리드
def aStar(request):
    global startGu
    global endGu   #global 전역변수
    center=hexgrid.Point((float(startX)+float(endX))/2,(float(startY)+float(endY))/2)   #중앙
    rate = 110.574 / (111.320 * math.cos(37.55582994870823 * math.pi / 180))   #서울의 중앙을 잡고, 경도값에 대한 비율     
    grid = hexgrid.Grid(hexgrid.OrientationFlat, center, Point(rate*0.00015,0.00015), morton.Morton(2, 32)) #Point = Size
    sPoint=grid.hex_at(Point(float(startX),float(startY)))      #출발지 Point -> hex좌표
    ePoint=grid.hex_at(Point(float(endX),float(endY)))          #목적지
    map_size=max(abs(sPoint.q),abs(sPoint.r))   #열col(q) 행row(r)
    road1=Roadtohexgrid.objects.filter(is_danger=1,hexgrid_gu=startGu).all()
    road2=Roadtohexgrid.objects.filter(is_danger=1,hexgrid_gu=endGu).all()
    total_road=road1.union(road2,all=False) #road1, road2 union

    wall1=Roadtohexgrid.objects.filter(is_danger=0,hexgrid_gu=startGu).all()
    wall2=Roadtohexgrid.objects.filter(is_danger=0,hexgrid_gu=endGu).all()
    total_wall=wall1.union(wall2,all=False)

    wh=GridWithWeights(layout_flat,Point(rate*0.00015,0.00015),center,map_size+5)   #Astart.py gird Cost?
    for r in total_road:
        gis= Geometry(r.hexgrid_loc.hex()[8:])
        h=grid.hex_at(shape(gis.geojson))
        wh.weights[(h.q,h.r)]=1
    
    for w in total_wall:
        gis= Geometry(w.hexgrid_loc.hex()[8:])
        h=grid.hex_at(shape(gis.geojson))
        wh.weights[(h.q,h.r)]=200
    
    start, goal = (sPoint.q,sPoint.r), (ePoint.q,ePoint.r)
    came_from, cost_so_far = a_star_search(wh, start, goal)
    pointList=reconstruct_path(came_from, start=start, goal=goal)
    plist=[]
    for p in pointList:
        point=wh.hex_to_pixel(hexgrid.Hex(p[0],p[1]))
        plist.append([point.x,point.y])
    crime_location={"type":"Feature","geometry":{"type":"LineString","coordinates":plist}}
    pistes = {"type":"FeatureCollection","features":[crime_location]}
    
    return HttpResponse(json.dumps({'pistes':pistes}),content_type="application/json")


def tsample(reqeust):
    return render (reqeust, "tsample.html")