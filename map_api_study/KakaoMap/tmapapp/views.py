from django.shortcuts import render

# Create your views here.
def thome(reqeust):
    return render (reqeust, "thome.html")

def pathfinder(reqeust):
    return render (reqeust, "thome.html")

def normalPath(reqeust):
    return render (reqeust, "thome.html")

def aStar(reqeust):
    return render (reqeust, "thome.html")

def tsample(reqeust):
    return render (reqeust, "tsample.html")