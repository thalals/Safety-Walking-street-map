from collections import namedtuple
import collections
from math import *
import math
from queue import PriorityQueue

import hexgrid
import morton   #hexgrid package - pip install morton-py..? already installe during installation hexgrid-py

from .models import *

Point = collections.namedtuple("Point", ["x", "y"])


# 축 좌표(q,r) -> Cube 좌표 (x,y,z) -> 맨허튼 거리
Cube = namedtuple('Cube',['x','y','z']) #NameTuple 과 nametuple이 차이는...?

def axial_to_cube(hex):
    x = hex.q
    z = hex.r
    y = -x-z
    return Cube(x, y, z)


def hex_distance (a, b) :   #type  a,b : hex -> return ac, bc : cube
    ac = axial_to_cube (a) 
    bc = axial_to_cube (b) 
    
    return cube_distance (ac, bc)


def cube_distance (a, b) : 
    return (abs (a.x-b.x) + abs (a.y-b.y) + abs (a.z-b.z)) / 2

#H(x) : 현재 위치에서 목적지 까지의 거리
def Heuristic(a, b) :   
    # type : (Hex(q,r), Hex(q,r))
    dx = a.q - b.q
    dy = a.r - b.r

    if dx == dy :
        return abs(dx + dy)
    else :
        return max(abs(dx), abs(dy))

#현재 까지 이동한 거리
def G_cost() :
    cost =0
    return cost

# Time Complexity는 H에 따라 다르다.
# O(b^d), where d = depth, b = 각 노드의 하위 요소 수
# heapque를 이용하면 길을 출력할 때 reverse를 안해도 됨

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

        self.cost = 0       

    def __eq__(self, other):
        return self.position == other.position

def GiveCost(startX,startY,endX,endY) :
    #-----------------return hex corner ---------------------
    center=hexgrid.Point((float(startX)+float(endX))/2,(float(startY)+float(endY))/2)   #중앙
    rate = 110.574 / (111.320 * math.cos(37.55582994870823 * math.pi / 180))   #서울의 중앙을 잡고, 경도값에 대한 비율     
    grid = hexgrid.Grid(hexgrid.OrientationFlat, center, Point(rate*0.00010,0.00010), morton.Morton(2, 32)) #Point : hexgrid Size
    sPoint=grid.hex_at(Point(float(startX),float(startY)))      # hex_at : point to hex -> 출발지 Point -> hex좌표
    ePoint=grid.hex_at(Point(float(endX),float(endY)))          #목적지
    map_size=max(abs(sPoint.q),abs(sPoint.r))   #열col(q) 행row(r)
    real_hexMap_size = map_size+5   #ex) 21 (q,r)이 가지는 최대 절대값

    #------------------범위 계산-----------------------------------#
    #mapsize의 최대 범위 -> ex) mapsize +5 (아래의 neighbor 범위)
    #type : tuple
    LeftCorner = (grid.hex_center(hexgrid.Hex(-(real_hexMap_size),0)).x ,grid.hex_center(hexgrid.Hex(0,-(real_hexMap_size))).y)
    RightCorner = (grid.hex_center(hexgrid.Hex((real_hexMap_size),0)).x ,grid.hex_center(hexgrid.Hex(0,(real_hexMap_size))).y)

    endx = RightCorner[0]
    endy = RightCorner[1]

    startx = LeftCorner[0]
    starty = LeftCorner[1]

    # 범위의 양수 계산을 위해 변수 startx,endx / starty,endy 초기화
    if(endx>startx) :
        temp = endx
        endx = startx
        startx = temp
    if(endy>starty) :
        temp = endy
        endy = starty
        starty = temp

    #-----------------------DB data load------------------------------#
    loadpoint = Loadpoint.objects.filter(lon__range=(endx,startx),lat__range=(endy,starty)).order_by('lat')
    lamp = Lamp.objects.filter(lon__range=(endx,startx),lat__range=(endy,starty)).order_by('lat')

    print("가로등 개수 : ",len(lamp))
    print("실포 포인트 개수 : ", len(loadpoint))
    
    #---------------------- hex 좌표 계산-------------------------------#
    #return center extends neighbor : hex list(헥스좌표)
    neighbor=[]
    neighbor =grid.hex_neighbors(grid.hex_at(center),real_hexMap_size) #hex_neighbor : type(Hex, int) -> list
    neighbor.append(grid.hex_at(center))

    HexCostlist = {}
    #item : 각각의 hex좌표
    for item in neighbor:
        item_hexCorner = grid.hex_corners(item)
        
        cost =0
        for lamp_point in lamp :           
            if(hexgrid.point_in_geometry(Point(lamp_point.lon, lamp_point.lat),item_hexCorner)) :  # type: (Point, list) -> bool
                cost+=1
                # lamp.remove(lamp_point)
                break;

        for load_point in loadpoint :           
            if(hexgrid.point_in_geometry(Point(load_point.lon, load_point.lat),item_hexCorner)) :  # type: (Point, list) -> bool
                cost+=1
                # lamp.remove(lamp_point)
                break;         
        HexCostlist[item] = cost     #key :hex, value : cost

    return HexCostlist, real_hexMap_size

def aStar(start,end, startX,startY,endX,endY) :
    #-----------------return hex corner ---------------------
    center=hexgrid.Point((float(startX)+float(endX))/2,(float(startY)+float(endY))/2)   #중앙
    rate = 110.574 / (111.320 * math.cos(37.55582994870823 * math.pi / 180))   #서울의 중앙을 잡고, 경도값에 대한 비율     
    grid = hexgrid.Grid(hexgrid.OrientationFlat, center, Point(rate*0.00010,0.00010), morton.Morton(2, 32)) #Point : hexgrid Size
    sPoint=grid.hex_at(Point(float(startX),float(startY)))      # hex_at : point to hex -> 출발지 Point -> hex좌표
    ePoint=grid.hex_at(Point(float(endX),float(endY)))          #목적지
    map_size=max(abs(sPoint.q),abs(sPoint.r))   #열col(q) 행row(r)
    
    
    #------------------------- 시작
    HexCostDict , mapsize = GiveCost(startX,startY,endX,endY)
    #startNode 와 endNode 초기화
    startNode = Node(None, start)
    endNode = Node(None, end)

    #openList, closeList 초기화
    openList = []   #방문중이거나, 방문 할 곳
    closeList = []  #더 나은 위치를 찾은 곳(이미 방문)

    #openList에 시작 노드 추가
    openList.append(startNode)

    #endNode를 찾을 때까지 실행
    while openList :
        
        #현재 노드 지정
        currentNode = openList[0]
        currentIdx = 0

        #이미 같은 노드가 openList에 있고, f값이 더 크면
        #currentNode를 openList안에 있는 값으로 교체
        for index, item in enumerate(openList) :
            if item.f < currentNode.f :
                currentNode = item
                currentIdx = index

        
        #openList에서 제거하고 closedList에 추가
        openList.pop(currentIdx)
        closeList.append(currentNode)


        #현재 노드가 목적지면 current.position 추가하고
        # current 부모 노드로 이동
        if currentNode == endNode :
            path = []
            current = currentNode

            while current is not None :
                path.append(current.position)
                current = current.parent    
            return path[::-1] #reverse

        children = []

        #인접한 좌표 체크
        # neighbor -> 범위, cost(갈 수 잇는 길인지) 체크
        neighbor = grid.hex_neighbors(currentNode.position,1)

        for newPosition in neighbor :
            if HexCostDict.get(newPosition) :
                TileCost = HexCostDict[newPosition]
            else : continue

            #범위 탈추한 거
            if abs(newPosition.q) >= mapsize or abs(newPosition.r) >= mapsize :
                continue

            #갈수 없는길
            if TileCost == 0 :
                continue

            new_node = Node(currentNode, newPosition)
            new_node.cost = int(TileCost)
            children.append(new_node)   

        #자식들 모두 loop
        for child in children :

            #자식이 closeList에 있으면 pass
            if child in closeList:
                continue

            #f,g,h 값 업데이트
            child.g = int(currentNode.g) +1      #현재까지 오는 비용
            child.h = int(Heuristic(child.position, end))    #목적지까지의 추정비용

            # child.f = child.g + child.h 
            child.f = child.g + child.h - (child.cost)      #TileCost의 값을 추가해줌

            # 자식이 openList에 있고, g값이 더 크면 continue(돌아서 온 경우)
            for openNode in openList :
                if(child == openNode and child.g > openNode.g) :
                    continue
            
            # print('openList에 다시 들어가는거 : ',child)
            openList.append(child)
            # print(openList)


def Go_astar(startHex, endHex,sx,sy,ex,ey) :  # type(hex, hex)

    startX = sx
    startY = sy
    endX = ex
    endY = ey

    path = aStar(startHex,endHex,sx,sy,ex,ey)

    print("경로 구간 : ",path)
    return path

    
