UNISWAP_GET_POOLS = '''
query getToken($tokenid: ID!) {
  token(id: $tokenid) {
    symbol,
    name,
    whitelistPools (
        first: 1000,
        orderBy: liquidity,
        orderDirection: desc
    ) 
    {
        id,
        token0 { id, symbol },
        token1 { id, symbol },
        liquidity,
        feeTier,
        totalValueLockedToken0,
        totalValueLockedToken1
    }
  }
}
'''
