from queries import UNISWAP_GET_POOLS
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

import asyncio
import requests
import json
import time

from constants import UNISWAP_ABI
from web3 import Web3

UNISWAP_SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

class UniswapConnect:
    def __init__(self):
        with open("./tokenlists/ethereum.json") as tokens:
            self.token_list = json.load(tokens)

        uniswap_contract = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
        infura_url = 'https://mainnet.infura.io/v3/834f68489ebf4602a8eae94107f32d0e'
        self.w3 = Web3(Web3.HTTPProvider(infura_url))

        contract_addr = Web3.toChecksumAddress(uniswap_contract)
        self.contract = self.w3.eth.contract(contract_addr, abi=UNISWAP_ABI)


    def get_address_data(self, address):
        for token in self.token_list:
            #print(token)
            if token['address'].lower() == address.lower():
                return token
        return None
    
    async def get_price_from_coingecko(self, address):
        token_data = self.get_address_data(address)
        if token_data:
            coingeckoId = token_data['coingeckoId']
            url = "https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies=usd".format(coingeckoId)
            r = requests.get(url).json()
            price = r[coingeckoId]['usd']
            return price
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
        price_from_func = self.get_price_from_coingecko(from_address)
        price_to_func = self.get_price_from_coingecko(to_address)


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


        price_from = await price_from_func
        price_to = await price_to_func


        result = [{
            'from_id': data1['id'],
            'from_symbol': data1['symbol'],
            'from_name': data1['name'],
            'from_price': price_from,
            'to_id': data2['id'],
            'to_symbol': data2['symbol'],
            'to_name': data2['name'],
            'to_price': price_to,
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
            token_id = str(token_data['address'])
            result = (await self.send_uniswap_request(UNISWAP_GET_POOLS, {'tokenid': token_id.lower()}))
            return result
    
    async def get_swap_quote(self, input_amount, swap_path):
        input_amount_wei = Web3.toWei(input_amount, 'ether')
        swap_path_checksums = [Web3.toChecksumAddress(addr) for addr in swap_path]
        result_wei = self.contract.functions.getAmountsOut(input_amount_wei, swap_path_checksums).call()
        result = [Web3.fromWei(wei, 'ether') for wei in result_wei]
        
        return result

    async def build_transaction(self, account_address, input_quantity, swap_path):
        input_quantity_wei = Web3.toWei(input_quantity, 'ether')
        min_input_quantity_wei = int(int(input_quantity_wei) * 0.975)

        print("input_quantity_wei: {}, min_input_quantity_wei: {}".format(input_quantity_wei, min_input_quantity_wei))

        swap_path_checksums = [Web3.toChecksumAddress(addr) for addr in swap_path]

        deadline = int(time.time() + 60)
        fun = self.contract.functions.swapExactTokensForTokens(
            input_quantity_wei,
            min_input_quantity_wei,
            swap_path_checksums,
            account_address,
            deadline
        )
        tx = fun.build_transaction({
            'from': account_address,
            'nonce': self.w3.eth.getTransactionCount(account_address),
            'gasPrice': self.w3.toWei('20', 'gwei'),
            'gas': '0'
        })

        return tx

async def test():
    # LINK -> WETH -> CRV
    #a = await UniswapConnect().get_swap_quote(1, ['0x514910771AF9Ca656af840dff83E8264EcF986CA', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', '0xD533a949740bb3306d119CC777fa900bA034cd52', ])
    
    # BUILD
    a = await UniswapConnect().build_transaction('0x707a7E9606b0e1547d7F8401D92222430C348399', '5', ['0x514910771AF9Ca656af840dff83E8264EcF986CA', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', '0xD533a949740bb3306d119CC777fa900bA034cd52', ])


    #a = await UniswapConnect().find_optimal_route('0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0', '0xBB0E17EF65F82Ab018d8EDd776e8DD940327B28b')
    print(a)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()

