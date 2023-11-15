#!/usr/bin/python

from collections import namedtuple
import time
import sys

class Edge:
    def __init__(self, origin, destination, weight=1):
        self.origin = origin
        self.destination = destination
        self.weight = weight

    def __repr__(self):
        return "Edge: Origin: {0}, Destination: {1}, Weight: {2}".format(self.origin, self.destination, self.weight)


class Airport:
    def __init__(self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight =  0
        self.pageIndex = 0

    def __repr__(self):
        return f"{self.code}\t{self.pageIndex}\t{self.name}"


edgeList = []  # list of Edge
edgeHash = dict()  # hash of edge to ease the match
airportList = []  # list of Airport
airportHash = dict()  # hash key IATA code -> Airport

airportCodeSet = set() #This is for preprocessing the routes.txt.


def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r");
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5:
                raise Exception('not an IATA code')
            a.name = temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code = temp[4][1:-1]
            #Adding the uniqe airport codes.
            airportCodeSet.add(a.code)

        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")


def readRoutes(fd):
    print(f"Reading Routes file from {fd}")
    routesTxt = open(fd, "r")
    count = 0
    for line in routesTxt.readlines():
        try:
            temp = line.split(',')
            origin, destination = temp[2].strip(), temp[4].strip()
            if origin in airportCodeSet and destination in airportCodeSet:
                edge_key = (origin, destination)
                if edge_key in edgeHash:
                    # Increment weight for existing edge
                    edgeHash[edge_key].weight += 1
                else:
                    # Create new edge and add it to edgeHash
                    e = Edge(origin, destination)
                    edgeList.append(e)
                    edgeHash[edge_key] = e
                    count += 1

                # Add the edge to the origin airport's routes and update outweight
                if origin in airportHash:
                    airportHash[origin].routes.append(edgeHash[edge_key])
                    airportHash[origin].outweight += 1  # Increment the outweight

        except Exception as e:
            print(f"Error processing line: {line}, Error: {e}")

    routesTxt.close()
    print(f"There were {count} unique routes added.")


#TODO This is the big problem.
def computePageRanks(damping=0.85, max_iterations=100, tol=1e-6, sum_tol=1e-6):
    n = len(airportHash)
    if n == 0:
        return 0  # Return early if there are no airports

    P = {airport: 1.0 / n for airport in airportHash}

    for iteration in range(max_iterations):
        Q = {airport: 0 for airport in airportHash}
        dangling_sum = sum(P[airport] for airport in airportHash if airportHash[airport].outweight == 0) / n

        for airport_code in airportHash:
            airport = airportHash[airport_code]
            for edge in airport.routes:
                destination = edge.destination
                if destination in airportHash:
                    Q[destination] += damping * P[airport_code] * edge.weight / airport.outweight

        teleport = (1 - damping) / n
        Q = {airport: teleport + dangling_sum + damping * Q[airport] for airport in airportHash}

        # Adjusted check for sum of PageRank elements
        if abs(sum(Q.values()) - 1) > sum_tol:
            print("Sum of PageRank elements deviates significantly from 1")
            print(sum(Q.values()))

        delta = sum(abs(P[airport] - Q[airport]) for airport in airportHash)
        P = Q
        if delta < tol:
            break

    for airport in airportHash:
        airportHash[airport].pageIndex = P[airport]

    return iteration + 1



def outputPageRanks():
    # Extract PageRank and airport name pairs
    pageRankPairs = [(airportHash[airport].pageIndex, airportHash[airport].name) for airport in airportHash]

    # Sort pairs by PageRank in descending order
    pageRankPairs.sort(reverse=True, key=lambda x: x[0])

    # Writing the sorted pairs to a file
    with open("PageRanksOutput.txt", "w") as file:
        for pageRank, name in pageRankPairs:
            file.write(f"{pageRank}\t{name}\n")

    print("PageRanks written to PageRanksOutput.txt")

def filter_routes(routes_file, airportCodeSet):
    with open(routes_file, "r") as file:
        lines = file.readlines()

    temp_file = "temp_routes.txt"
    removed_count = 0  # Counter for removed routes

    with open(temp_file, "w") as file:
        for line in lines:
            parts = line.split(',')
            origin_code, destination_code = parts[2], parts[4]

            if origin_code in airportCodeSet and destination_code in airportCodeSet:
                file.write(line)
            else:
                removed_count += 1  # Increment counter for each removed route

    import os
    os.replace(temp_file, routes_file)

    return removed_count


def main(argv=None):
    readAirports("airports.txt")
    print(airportList)#debug
    print(airportHash)#debug

    #preprocessing the routes.txt file because of course
    removed_routes_count = filter_routes("routes.txt",airportCodeSet)
    print(f"Number of routes removed: {removed_routes_count}") #528 routes were removed in the first run.

    readRoutes("routes.txt")
    print(edgeList)
    print(edgeHash)


    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2 - time1)


if __name__ == "__main__":
    sys.exit(main())
