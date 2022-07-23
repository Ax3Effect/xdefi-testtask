from typing import Union
import asyncio
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from graphene import ObjectType, List, String, Int, Schema, Field
from graphene.types import generic
import graphene

from starlette.applications import Starlette
from starlette_graphene3 import GraphQLApp, make_graphiql_handler

from uniswap import UniswapConnect

app = FastAPI()
uni = UniswapConnect()

origins = [
    'http://localhost:3000',
    'http://localhost:8000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# issues:
# https://github.com/Uniswap/v3-subgraph/issues/120


class TokenType(ObjectType):
    address = String()
    symbol = String()
    name = String()
    decimals = Int()
    chainId = String()
    logoURI = String()
    coingeckoId = String()

class Token(ObjectType):
    id = String()
    symbol = String()

class Pairs(ObjectType):
    id = String()
    token0 = Field(Token)
    token1 = Field(Token)
    liquidity = String()
    feeTier = String()


'''
class Route(ObjectType):
    class Meta:
        interfaces = (BaseRoute, )
'''

async def resolve_routes(data, info):
    data = (await uni.find_optimal_route(data.from_address, data.to_address))
    return data


class Route(ObjectType):
    from_id = String(required=True)
    from_symbol = String(required=True)
    from_name = String(required=True)
    to_id = String(required=True)
    to_symbol = String(required=True)
    to_name = String(required=True)
    side_id = String(required=True)
    side_symbol = String(required=True)
    side_name = String(required=True)
    result = generic.GenericScalar(resolver=resolve_routes)


class Query(ObjectType):
    token = List(TokenType)
    pairs = List(Pairs)
    routes = List(Route, args={'from': String(), 'to': String()})
 
    async def resolve_token(self, info):
        return uni.token_list

    async def resolve_pairs(self, info, address):
        data = (await uni.get_available_pools(address)['token']['whitelistPools'])
        return data
    
    async def resolve_routes(self, info, **kwargs):
        from_address = kwargs.get('from')
        to_address = kwargs.get('to')
        data = (await uni.find_optimal_route(from_address, to_address))
        return data

class RouteInput(graphene.InputObjectType):
    from_address = graphene.String(required=True)
    to_address = graphene.String(required=True)
    
class CreateRoute(graphene.Mutation):
    class Arguments:
        address = RouteInput(required=True)

    route = graphene.Field(lambda: Route)

    def mutate(root, info, address=None):
        data = (uni.find_optimal_route(address.from_address, to_address=address.to_address))
        print(data)
        route = Route(from_address=address.from_address, to_address=address.to_address)
        return CreateRoute(route=route)

class Person(graphene.ObjectType):
    name = graphene.String()
    age = graphene.Int()

# We must define a query for our schema
class Mutations(graphene.ObjectType):
    person = graphene.Field(Person)


class PersonInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    age = graphene.Int(required=True)

class CreatePerson(graphene.Mutation):
    class Arguments:
        person_data = PersonInput(required=True)

    person = graphene.Field(Person)

    def mutate(root, info, person_data=None):
        person = Person(
            name=person_data.name,
            age=person_data.age
        )
        return CreatePerson(person=person)

class MyMutations(graphene.ObjectType):
    create_route = CreateRoute.Field()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


schema = graphene.Schema(query=Query, mutation=MyMutations, )
app.mount("/graphql", GraphQLApp(schema, on_get=make_graphiql_handler()))