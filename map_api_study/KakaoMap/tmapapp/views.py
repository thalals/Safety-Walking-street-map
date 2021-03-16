from django.http.response import HttpResponse
from django.shortcuts import render
import json

from shapely import *
from shapely.geometry import *
from shapely.ops import unary_union
from shapely.validation import explain_validity
from plpygis import Geometry

import math
import hexgrid # han : pip install hexgrid-py
from .Astar import *

# Create your views here.
def thome(reqeust):
    return render (reqeust, "thome.html")

def pathFinder(request): #위험지역 받는 함수
    global startX,startY,endX,endY,startGu,endGu
    gu_list=['종로구','중구','용산구','성동구','광진구',
    '동대문구','중랑구','성북구','강북구','도봉구',
    '노원구','은평구','서대문구','마포구','양천구',
    '강서구','구로구','금천구','영등포구','동작구',
    '관악구','서초구','강남구','송파구','강동구',]
    loc_list=[]
    if request.method=="POST":
        startPoint=request.POST.get('start')
        endPoint=request.POST.get('end')
        startX=request.POST.get('startX')
        startY=request.POST.get('startY')
        endX=request.POST.get('endX')
        endY=request.POST.get('endY')
        for find_gu in gu_list:
            if find_gu in startPoint:
                startGu=find_gu
            else:
                pass
            if find_gu in endPoint:
                endGu=find_gu
            else:
                pass
        female_start=Female2.objects.filter(female2_crime_type="전체_전체",gu=startGu).all()
        female_end=Female2.objects.filter(female2_crime_type="전체_전체",gu=endGu).all()
        female_total=female_start.union(female_end,all=False)
        for loc in female_total:
            gis= Geometry(loc.female2_crime_loc.hex()[8:])
            contain_coordinate=shape(gis.geojson)
            crime_location={"type":"Feature","geometry":gis.geojson}
            loc_list.append(crime_location)
    pistes = {"type":"FeatureCollection","features":loc_list}
    return HttpResponse(json.dumps({'result':pistes}),content_type="application/json")

def normalPath(request):
    global gu_coordinate,startX,startY,endX,endY
    pointlist=[]
    polyline=[]
    line=""
    count=0
    if request.method=="POST":
        pistes=request.POST.get('draw')
        pist=pistes.split(",")
        for p in pist:
            if (pist.index(p)%2==0):
                x=p
                y=pist[pist.index(p)+1]
                point=[float(y),float(x)]
                pointlist.append(point)

        
    crime_location={"type":"Feature","geometry":{"type":"LineString","coordinates":pointlist}}
  
    pistes = {"type":"FeatureCollection","features":[crime_location]}
    return HttpResponse(json.dumps({'pistes':pistes}),content_type="application/json")

def aStar(request):
    global startGu,endGu
    center=hexgrid.Point((float(startX)+float(endX))/2,(float(startY)+float(endY))/2)
    rate = 110.574 / (111.320 * math.cos(37.55582994870823 * math.pi / 180))
    grid = hexgrid.Grid(hexgrid.OrientationFlat, center, Point(rate*0.00015,0.00015), morton.Morton(2, 32))
    sPoint=grid.hex_at(Point(float(startX),float(startY)))
    ePoint=grid.hex_at(Point(float(endX),float(endY)))
    map_size=max(abs(sPoint.q),abs(sPoint.r))
    road1=Roadtohexgrid.objects.filter(is_danger=1,hexgrid_gu=startGu).all()
    road2=Roadtohexgrid.objects.filter(is_danger=1,hexgrid_gu=endGu).all()
    total_road=road1.union(road2,all=False)
    wall1=Roadtohexgrid.objects.filter(is_danger=0,hexgrid_gu=startGu).all()
    wall2=Roadtohexgrid.objects.filter(is_danger=0,hexgrid_gu=endGu).all()
    total_wall=wall1.union(wall2,all=False)
    wh=GridWithWeights(layout_flat,Point(rate*0.00015,0.00015),center,map_size+5)
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