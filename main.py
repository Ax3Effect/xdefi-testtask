from typing import Union
import asyncio

from fastapi import FastAPI
from graphene import ObjectType, List, String, Int, Schema, Field
import graphene

from starlette.applications import Starlette
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
import json

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


class TokenQuery(ObjectType):
    token_list = None
    get_tokenlist = List(TokenType)
    get_pairslist = List(Pairs)

    async def resolve_get_tokenlist(self, info):
        return uni.token_list

    async def resolve_get_pairslist(self, info):
        data = (await uni.get_available_pools('0xc00e94cb662c3520282e6f5717214004a7f26888'))['token']['whitelistPools']
        return data


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


schema = graphene.Schema(query=TokenQuery, )
app.mount("/graphql", GraphQLApp(schema, on_get=make_graphiql_handler()))