from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
import random


def main():
    graph = Graph()

    userFile = open("users.csv", "r")
    userFile.readline()
    lineNumber = 0
    for line in userFile.readlines():
        print("\r Processing line " + str(lineNumber), end="")
        lineNumber += 1
        parsedLine = line.split(",")
        user = Node("User", username=parsedLine[0],
                name=parsedLine[1],
                biography=parsedLine[4],
                password=bcrypt.encrypt("password"))
        graph.create(user)

        city = graph.merge_one("City", "name", parsedLine[2])
        job = graph.merge_one("Job", "title", parsedLine[3])
        livesIn = Relationship(user, "IS_FROM", city)
        hasJob = Relationship(user, "HAS_JOB_TITLE", job)

        graph.create(livesIn)
        graph.create(hasJob)

        result = graph.cypher.execute("MATCH (beer:Beer) "
                      " RETURN beer, rand() as rand "
                      " ORDER BY rand"
                      " LIMIT {range}", range=random.randrange(100,600))

        for beer in result:
            beerNode = graph.find_one("Beer", "breweryDbId", beer.beer["breweryDbId"])
            likesBrewery = Relationship(user, "LIKES", beerNode)
            graph.create(likesBrewery)


        result = graph.cypher.execute("MATCH (brewery:Brewery) "
                      " RETURN brewery, rand() as rand "
                      " ORDER BY rand"
                      " LIMIT {range}", range=random.randrange(0,10))

        for brewery in result:
            breweryNode = graph.find_one("Brewery", "breweryDbId", brewery.brewery["breweryDbId"])
            likesBrewery = Relationship(user, "LIKES", breweryNode)
            graph.create(likesBrewery)

        if lineNumber > 300:
            break


    for user in graph.find("User"):
        userNode = graph.find_one("User", "username", user["username"])
        result = graph.cypher.execute("MATCH (user:User) "
                                      "WHERE user.username <> {me}"
          " RETURN user, rand() as rand "
          " ORDER BY rand"
          " LIMIT {range}", me=userNode["username"], range=random.randrange(5,40))

        for person in result:
            dude = graph.find_one("User", "username", person.user["username"])
            buddiesWith = Relationship(userNode, "FOLLOWS", dude)
            graph.create(buddiesWith)


main()