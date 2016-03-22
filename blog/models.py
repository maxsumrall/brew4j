from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from datetime import datetime
import os
import uuid

graph = Graph()

def all_styles():
    query = """
    MATCH (style:Style)
    RETURN style
    """
    return graph.cypher.execute(query)


class User:
    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one("User", "username", self.username)
        return user

    def findBeer(self, beerId):
        beer = graph.find_one("Beer", "breweryDbId", beerId)
        return beer

    def register(self, password):
        if not self.find():
            user = Node("User", username=self.username, password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False

    def add_review(self, text, beerName):
        user = self.find()
        beer = self.findBeer(beerName)
        post = Node(
            "Review",
            id=str(uuid.uuid4()),
            text=text,
            timestamp=timestamp(),
            date=date()
        )

        rel = Relationship(user, "PUBLISHED", post)
        rel2 = Relationship(post, "REVIEW_OF", beer)
        graph.create(rel)
        graph.create(rel2)

    def like_beer(self, beer_id):
        user = self.find()
        post = graph.find_one("Beer", "id", beer_id)
        graph.create_unique(Relationship(user, "LIKE", post))

    def get_recent_reviews(self):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(review:Review)-[:REVIEW_OF]->(beer:Beer)
        WHERE user.username = {username}
        RETURN review, beer
        ORDER BY review.timestamp DESC LIMIT 5
        """

        return graph.cypher.execute(query, username=self.username)

    def get_friends(self):
        query = """
        MATCH (user:User)-[:FOLLOWS]->(person:User)-[:HAS_JOB_TITLE]->(job:Job)
        MATCH (person:User)-[:IS_FROM]->(city:City)
        WHERE user.username = {username}
        RETURN person, job, city
        """

        return graph.cypher.execute(query, username=self.username)

    def get_similar_users(self):
        # Find three users who are most similar to the logged-in user
        # based on tags they've both blogged about.
        query = """
        MATCH (you:User)-[:PUBLISHED]->(:Review)-[:REVIEW_OF]->(beer:Beer),
              (they:User)-[:PUBLISHED]->(:Review)-[:REVIEW_OF]-(beer:Beer)
        WHERE you.username = {username} AND you <> they
        WITH they, COLLECT(DISTINCT beer.name) AS beers, COUNT(DISTINCT beer) AS len
        ORDER BY len DESC LIMIT 3
        RETURN they.username AS similar_user, beers
        """

        return graph.cypher.execute(query, username=self.username)

    def get_commonality_of_user(self, other):
        # Find how many of the logged-in user's posts the other user
        # has liked and which tags they've both blogged about.
        query = """
        MATCH (they:User {username: {they} })
        MATCH (you:User {username: {you} })
        OPTIONAL MATCH (they)-[:LIKE]->(beer:Beer)<-[:LIKE]-(you)
        OPTIONAL MATCH (they)-[:PUBLISHED]->(:Post)<-[:Style]-(style:Style),
                       (you)-[:PUBLISHED]->(:Post)<-[:Style]-(style)
        RETURN COUNT(DISTINCT beer) AS likes, COLLECT(DISTINCT beer.name) AS beers
        """

        return graph.cypher.execute(query, they=other.username, you=self.username)[0]


def get_todays_recent_reviews():
    query = """
    MATCH (user:User)-[:PUBLISHED]->(review:Review)-[:REVIEW_OF]->(beer:Beer)
    WHERE review.date = {today}
    RETURN user.username AS username, review, beer
    ORDER BY review.timestamp DESC LIMIT 5
    """

    return graph.cypher.execute(query, today=date())


def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()


def date():
    return datetime.now().strftime('%Y-%m-%d')
