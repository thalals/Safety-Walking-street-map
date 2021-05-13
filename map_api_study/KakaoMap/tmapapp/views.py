import re
from django.http.response import HttpResponse
from django.shortcuts import render
import json

from numpy import polyint
from .models import *

from shapely import *
from shapely.geometry import *
from shapely.ops import unary_union
from shapely.validation import explain_validity
from plpygis import Geometry

import math
import hexgrid # han : pip install hexgrid-py
import morton   #hexgrid package - pip install morton-py..? already installe during installation hexgrid-py

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
    '관악구','서초구','강남구','송파구','강동구','부평구','소하동','일직동',]
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
    # print(pistes)
    # print(startGu)
    # print(endGu)
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
                y=pist[(pist.index(p))+1] #lng
                point=[float(y),float(x)]
                pointlist.append(point)

        
    crime_location={"type":"Feature","geometry":{"type":"LineString","coordinates":pointlist}}
  
    pistes = {"type":"FeatureCollection","features":[crime_location]}   #경로 정보
    return HttpResponse(json.dumps({'pistes':pistes}),content_type="application/json")

#그리드 그려보자
def gird_draw(request):
    #-----------------return hex corner ---------------------
    center=hexgrid.Point((float(startX)+float(endX))/2,(float(startY)+float(endY))/2)   #중앙
    rate = 110.574 / (111.320 * math.cos(37.55582994870823 * math.pi / 180))   #서울의 중앙을 잡고, 경도값에 대한 비율     
    grid = hexgrid.Grid(hexgrid.OrientationFlat, center, Point(rate*0.00015,0.00015), morton.Morton(2, 32)) #Point = Size
    sPoint=grid.hex_at(Point(float(startX),float(startY)))      # hex_at : point to hex -> 출발지 Point -> hex좌표
    ePoint=grid.hex_at(Point(float(endX),float(endY)))          #목적지
    map_size=max(abs(sPoint.q),abs(sPoint.r))   #열col(q) 행row(r)
    
    
    #return center extends neighbor : hex list
    neighbor=[]
    neighbor =grid.hex_neighbors(grid.hex_at(center),map_size+5) #hex_neighbor : type(Hex, int) -> list

    print("hexgrid 개수 : ",len(neighbor))
    #test make hex to corner
    cornerlist = []
    for item in neighbor:
        cornerlist.append(grid.hex_corners(item))


    polylist =[]
    for hex in cornerlist:
      for corner in hex :
        polylist.append(corner)

    print("hexgrid 꼭지점 개수 : ",len(polylist))

    hex_line={"type":"Feature","geometry":{"type":"LineString","coordinates":polylist}}
    hex_polygon = {"type":"FeatureCollection","features":[hex_line]}

    # print(hex_polygon)
    #------------------return lamp data --------------------    
    endx = endX
    startx = startX
    endy = endY
    starty = startY

    #범위의 양수 계산을 위해 변수 startx,endx / starty,endy 초기화
    if(endX>startX) :
        endx = startX
        startx = endX
    if(endY>startY) :
        endy = startY
        starty = endY

    
    lamp = Lamp.objects.filter(lon__range=(endx,startx),lat__range=(endy,starty)).order_by('lat')
    # lamp.order_by('lon')
    print("가로등 개수 : ",len(lamp))

    plist=[]

    for l in lamp :
        # print(l.lon)
        point=[float(l.lon),float(l.lat)]
        plist.append(point)

    
    lamp_location={"type":"Feature","geometry":{"type":"Point","coordinates":plist}}
    pistes = {"type":"FeatureCollection","features":[lamp_location]}
    
    #print(pistes)
    #print(pistes['features'][0]['geometry']['coordinates']) #point Array
    return HttpResponse(json.dumps({'pistes' : pistes, 'hex_polygon':hex_polygon}),content_type="application/json") #python to json


#hexgrid : 16진수 그리드
def aStar(request):
    # global startGu
    # global endGu   #global 전역변수
    print(startGu)
    print(endGu)
    center=hexgrid.Point((float(startX)+float(endX))/2,(float(startY)+float(endY))/2)   #중앙
    rate = 110.574 / (111.320 * math.cos(37.55582994870823 * math.pi / 180))   #서울의 중앙을 잡고, 경도값에 대한 비율     
    grid = hexgrid.Grid(hexgrid.OrientationFlat, center, Point(rate*0.00015,0.00015), morton.Morton(2, 32)) #Point = Size
    sPoint=grid.hex_at(Point(float(startX),float(startY)))      # hex_at : point to hex -> 출발지 Point -> hex좌표
    ePoint=grid.hex_at(Point(float(endX),float(endY)))          #목적지
    map_size=max(abs(sPoint.q),abs(sPoint.r))   #열col(q) 행row(r)

    print(center)
    print(sPoint)
    print(ePoint)
    print(grid)
    print(map_size)

    #return center extends neighbor : hex list
    neighbor=[]
    neighbor =grid.hex_neighbors(grid.hex_at(center),1) #hex_neighbor : type(Hex, int) -> list

    print(len(neighbor))

    #test make region
    regionlist =[]

    for ne in neighbor :
        regionlist.append(grid._make_region(grid.hex_corners(ne)))
    
    print(len(regionlist))
    # for region in regionlist :
    #     print(region.hexes)


    #test make hex to corner
    cornerlist = []
    for item in neighbor:
        cornerlist.append(grid.hex_corners(item))

    # item:list (안에 6개의 corner)
    # print(cornerlist)
    # for item in cornerlist:
    #     print(item)
    #     print()
        
        

    # for a in region :
    #     print(region)

    # for a in neighbor :
    #     print(a)
    
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