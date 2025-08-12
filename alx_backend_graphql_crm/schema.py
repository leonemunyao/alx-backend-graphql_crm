import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(CRMQuery, graphene.ObjectType):
    """
    Extend the CRM Query with additional fields if needed.
    """
    pass


class Mutation(CRMMutation, graphene.ObjectType):
    """
    Extend the CRM Mutation with additional fields if needed.
    """
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
