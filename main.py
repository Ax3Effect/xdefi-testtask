from typing import Union
import asyncio

from fastapi import FastAPI
from graphene import ObjectType, List, String, Int, Schema
import graphene

from starlette.applications import Starlette
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
import json

app = FastAPI()

class TokenType(ObjectType):
    address = String()
    symbol = String()
    name = String()
    decimals = Int()
    chainId = String()
    logoURI = String()
    coingeckoId = String()


class TokenQuery(ObjectType):
    token_list = None
    get_tokenlist = List(TokenType)
    async def resolve_get_tokenlist(self, info):
        with open("./tokenlists/ethereum.json") as courses:
            token_list = json.load(courses)
        return token_list


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


schema = graphene.Schema(query=TokenQuery, )
app.mount("/graphql", GraphQLApp(schema, on_get=make_graphiql_handler()))