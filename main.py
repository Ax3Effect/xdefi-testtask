from typing import Union
import asyncio
import json

from fastapi import FastAPI
from graphene import ObjectType, List, String, Int, Schema, Field
import graphene

from starlette.applications import Starlette
from starlette_graphene3 import GraphQLApp, make_graphiql_handler

from uniswap import UniswapConnect

app = FastAPI()
uni = UniswapConnect()

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
    from_address = String(required=True)
    to_address = String(required=True)
    result = String(resolver=resolve_routes)


class Query(ObjectType):
    token = List(TokenType)
    pairs = List(Pairs)
    routes = List(Route)

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
    
class CreateRoute(graphene.Mutation):
    class Arguments:
        from_address = graphene.String()
        to_address = graphene.String()
    
    ok = graphene.Boolean()
    route = graphene.Field(lambda: Route)

    def mutate(root, info, from_address, to_address):
        person = Route(from_address=from_address, to_address=to_address)
        ok = True
        return Mutation(route=route, ok=ok)


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