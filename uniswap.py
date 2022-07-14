from queries import UNISWAP_GET_POOLS
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

import asyncio
import requests
import json

UNISWAP_SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

class UniswapConnect:
    def __init__(self):
        with open("./tokenlists/ethereum.json") as tokens:
            self.token_list = json.load(tokens)

    def get_address_data(self, address):
        for token in self.token_list:
            #print(token)
            if token['address'].lower() == address.lower():
                return token
        return None
    
    async def process_pool_pairs(self, address):
        data = await self.get_available_pools(address)

        source_symbol = data['token']['symbol']
        destinations = []
        for pool in data['token']['whitelistPools']:
            # ignore pairs with no liquidity
            if int(pool['liquidity']) < 10000:
                continue
            
            if source_symbol == pool['token0']['symbol']:
                destination_data = pool['token1']
            elif source_symbol == pool['token1']['symbol']:
                destination_data = pool['token0']
            
            if not destination_data:
                continue
            
            destinations.append(destination_data)
        return destinations

    
    async def send_uniswap_request(self, gql_query, variables={}):
        transport = AIOHTTPTransport(url=UNISWAP_SUBGRAPH_URL)
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql(gql_query)
        result = await client.execute_async(query, variable_values=variables)
        return result

    async def get_available_pools(self, address):
        token_data = self.get_address_data(address)
        if token_data:
            query = gql(UNISWAP_GET_POOLS)
            token_id = str(token_data['address'].lower())
            result = (await self.send_uniswap_request(UNISWAP_GET_POOLS, {'tokenid': token_id}))
            return result

async def test():
    a = await UniswapConnect().process_pool_pairs('0x6B175474E89094C44Da98b954EedeAC495271d0F')
    print(a)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()

