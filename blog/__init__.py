from .views import app
from .models import graph


def create_uniqueness_constraint(label, property):
    query = "CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
    query = query.format(label=label, property=property)
    graph.cypher.execute(query)


create_uniqueness_constraint("User", "username")
create_uniqueness_constraint("Beer", "id")
create_uniqueness_constraint("Review", "id")
create_uniqueness_constraint("City", "name")
create_uniqueness_constraint("Job", "title")
