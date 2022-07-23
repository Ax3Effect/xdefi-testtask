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
        return destinations, data['token']
    
    async def find_optimal_route(self, from_address, to_address):
        print("From address: {} To address: {}".format(from_address, to_address))

        try:
            destinations1, data1 = await self.process_pool_pairs(from_address)
            destinations2, data2 = await self.process_pool_pairs(to_address)
        except TypeError:
            return []

        already_found = False
        print("-----------> {}".format(data1))
        # simplify
        destinations_list1 = []
        for destination in destinations1:
            if destination['symbol'] == data2['symbol']:
                # already found 1-1 swap
                already_found = True
                #print("{} -> {}".format(data1['name'], data2['name']))
                break
            destinations_list1.append(destination['symbol'])

        if not already_found:
            destinations_list2 = []
            for destination in destinations2:
                destinations_list2.append(destination['symbol'])
            
            print("Pools for {}: {}".format(data1['symbol'], destinations_list1))
            print("Pools for {}: {}".format(data2['symbol'], destinations_list2))

            common_swaps = list(set(destinations_list1).intersection(destinations_list2))
            #print(common_swaps)
            print("{} -> {} -> {}".format(data1['name'], common_swaps, data2['name']))
        else:
            print("{} -> {} (direct swap)".format(data1['name'], data2['name']))
            common_swaps = None


        result = [{
            'from_id': data1['id'],
            'from_symbol': data1['symbol'],
            'from_name': data1['name'],
            'to_id': data2['id'],
            'to_symbol': data2['symbol'],
            'to_name': data2['name'],
            'side_id': next(item for item in destinations1 if item["symbol"] == side)['id'],
            'side_symbol': next(item for item in destinations1 if item["symbol"] == side)['symbol'],
            'side_name': next(item for item in destinations1 if item["symbol"] == side)['name']
        } for side in common_swaps]

        return result


    
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
    a = await UniswapConnect().find_optimal_route('0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0', '0xBB0E17EF65F82Ab018d8EDd776e8DD940327B28b')
    print(a)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()

