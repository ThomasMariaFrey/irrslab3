#!/usr/bin/python

from collections import namedtuple
import numpy as np
import time
import sys

class Edge:
    def __init__ (self, origin=None):
        self.origin = origin
        self.weight = 1

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)
        
    ## write rest of code that you need for this class

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict() # not used for Pagerank
        self.outweight = 0

    def __repr__(self):
        return f"{self.code}\t{self.pageIndex}\t{self.name}"

edgeList = [] # list of Edge, not used for Pagerank
edgeHash = dict() # IATA code of origin airport -> dict that maps IATA code of the dest -> Edge from origin to dest
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r", encoding="utf8");
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5:
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
            if a.code in airportHash:
                raise Exception('duplicated AITA code')
        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            if a.code in airportHash:
                print('OHNO', cont, a.code)
            airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")




def add_edge(origin_code, destination_code):
    origin_ap = airportHash[origin_code]
    dest_ap = airportHash[destination_code]
    origin_ap.outweight += 1
    if origin_code not in edgeHash:
        e = Edge(origin_ap)
        edgeHash[origin_code] = {destination_code: e}
        edgeList.append(e)

        dest_ap.routeHash[origin_code] = e
        dest_ap.routes.append(e)
    else:
        origin_dict = edgeHash[origin_code]
        if destination_code in origin_dict:
            e = origin_dict[destination_code]
            origin_dict[destination_code].weight += 1
        else:
            e = Edge(origin_ap)
            origin_dict[destination_code] = e
            edgeList.append(e)

            dest_ap.routeHash[origin_code] = e
            dest_ap.routes.append(e)



def readRoutes(fd): # we are interested in fields 3 (3) origin and 5 (4) destination
    print("Reading Routes file from {fd}")
    routesTxt = open(fd, "r", encoding="utf8");
    cont = 0
    for line in routesTxt.readlines():
        # e = Edge()
        try:
            temp = line.split(',')
            origin = temp[2]
            destination = temp[4]
            if len(origin) != 3 or len(destination) != 3:
                raise Exception('not IATA codes')
            if origin not in airportHash or destination not in airportHash:
                raise Exception("undefined airport")
        except Exception as inst:
            pass
        else:
            cont += 1
            add_edge(origin, destination)
    routesTxt.close()

def computePageRanks():
    n = len(airportList)
    p = {a_code: 1/n for a_code in airportHash.keys()}
    print(sum(p.values()))
    quit()
    l_factor = 0.9
    for i in range(100):
        q = {a.code: l_factor*sum([p[e.origin.code]*e.weight/e.origin.outweight for e in a.routes]) + (1-l_factor)/n for a in airportList}
        p = q
        print(sum(p.values()))
    return p
    

    

    pass

def outputPageRanks():
    # write your code
    pass

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    # for a in airportList:
    #     ow1 = sum([e.weight for e in a.routes])
    #     ow2 = a.outweight
    #     if ow1 != ow2:
    #         print(ow1, ow2)
    # quit()
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    quit()
    outputPageRanks()
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2-time1)


if __name__ == "__main__":
    sys.exit(main())
