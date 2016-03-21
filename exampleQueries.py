from py2neo import Graph, Node, Relationship, authenticate


def main():
    graph = Graph()
    cypher = graph.cypher

    example_brewery = "Bierbrouwerij De Koningshoeven"
    example_username = "juditlindahl"

    # Simple questions:

    print("all beer from a given brewery")
    result = cypher.execute(""" MATCH (beer:Beer)-[:PRODUCED_BY]->(brewery:Brewery {name: {breweryName}} )
                             RETURN beer
                              LIMIT 5""", {"breweryName": example_brewery})

    for beer in result:
        print(beer)

    print("all beer where ABV = 3.5")
    result = cypher.execute(""" MATCH (beer:Beer)-[:HAS_ABV]->(abv:Abv)
                             WHERE abv.abv = 3.5
                             RETURN beer
                             LIMIT 5 """)

    for beer in result:
        print(beer)

    print("all beer where IBU > 100")
    result = cypher.execute(""" MATCH (beer:Beer)-[:HAS_IBU]->(ibu:Ibu)
                             WHERE ibu.ibu > 100.0
                             RETURN beer
                             LIMIT 5 """)
    for beer in result:
        print(beer)

    print("Brewery with the most beer with an IBU over 80")
    result = cypher.execute(""" MATCH (brewery:Brewery)<-[:PRODUCED_BY]-(beer:Beer)-[:HAS_IBU]->(ibu:Ibu)
                             WHERE ibu.ibu > 80
                             RETURN brewery.name, count(distinct beer) as frequency
                             ORDER BY frequency DESC
                             LIMIT 5""")
    for brewery in result:
        print(brewery)

    print("Which brewery has the most 2% beers?")
    result = cypher.execute("""MATCH (abv:Abv {abv: {abv}})<-[:HAS_ABV]-(beer:Beer)-[:PRODUCED_BY]->(brewery:Brewery)
                            RETURN count(brewery) AS counts, brewery
                            ORDER BY counts DESC
                            LIMIT 1""", {"abv": 2})
    for brewery in result:
        print(brewery)

    # Social Networking:
    #
    # Recommended follows:

    print("Which users like the same breweries I do?")
    result = cypher.execute("""
        MATCH (me:User {username: {username}})-[:LIKES]->(brewery:Brewery)<-[:LIKES]-(person:User)
        RETURN person.name, count(*) AS counts
        ORDER BY counts DESC
        LIMIT 2
        """, {"username": example_username})
    for row in result:
        print(row)

    print("Which users that I don't already follow like the same breweries I do?")
    result = cypher.execute("""
        MATCH (me:User {username: {username}})-[:LIKES]->(brewery:Brewery)<-[:LIKES]-(person:User)
        WHERE NOT (me)-[:follows]->(person)
        RETURN person.name, count(*) AS counts
        ORDER BY counts DESC
        LIMIT 2
        """, {"username": example_username})
    for row in result:
        print(row)

    print("Which users like the same beers I do?")
    result = cypher.execute("""
        MATCH (me:User {username: {username}})-[:LIKES]->(beer:Beer)<-[:LIKES]-(person:User)
        RETURN person.name, count(*) AS counts
        ORDER BY counts DESC
        LIMIT 2
        """, {"username": example_username})
    for row in result:
        print(row)

    print("Which users have the most overlapping likes with mine?")
    result = cypher.execute("""
        MATCH (me:User {username: {username}})-[:LIKES]->(thing)<-[:LIKES]-(person:User)
        RETURN person.name, count(*) AS counts
        ORDER BY counts DESC
        LIMIT 2
        """, {"username": example_username})
    for row in result:
        print(row)

    print("What breweries do I like?")
    result = cypher.execute("""
        MATCH (me:User {username: {username}})-[:LIKES]->(brewery:Brewery)
        RETURN brewery """, {"username": example_username})
    for row in result:
        print(row)

    print("Inferr which are my favourite breweries")
    result = cypher.execute("""
        MATCH (me:User {username: {username}})-[:LIKES]->(beer:Beer)-[:PRODUCED_BY]-(brewery:Brewery)
        RETURN brewery, count(*) AS counts
        ORDER BY counts DESC
        LIMIT 2""", {"username": example_username})
    for row in result:
        print(row)

    print("Which breweries might I want to try?")
    result = cypher.execute("""
    MATCH (me:User {username: {username}})-[:FOLLOWS]->(person:User)-[:LIKES]->(brewery:Brewery)
    WHERE NOT (me)-[:LIKES]->(brewery)
    RETURN brewery, count(brewery) AS counts
    ORDER BY counts DESC
    LIMIT 2""", {"username": example_username})

    for row in result:
        print(row)

    print("Which beers am I most likely to like based on who I follow?")
    result = cypher.execute("""
    MATCH (me:User {username: {username}})-[:FOLLOWS]->(person:User)-[:LIKES]->(beer:Beer)
    WHERE NOT (me)-[:LIKES]->(beer)
    RETURN beer, count(beer) AS counts
    ORDER BY counts DESC
    LIMIT 2""", {"username": example_username})

    for row in result:
        print(row)

    print("Which beers am I most likely to like based on who I follow and what brewery they like?")
    result = cypher.execute("""
    MATCH (me:User {username: {username}})-[:FOLLOWS]->(person:User)-[:LIKES]->(brewery:Brewery)<-[:PRODUCED_BY]-(beer:Beer)
    WHERE NOT (me)-[:LIKES]->(beer)
    RETURN beer, count(beer) AS counts
    ORDER BY counts DESC
    LIMIT 2""", {"username": example_username})

    for row in result:
        print(row)


main()
