UNISWAP_GET_POOLS = '''
query getToken($tokenid: ID!) {
  token(id: $tokenid) {
    id,
    symbol,
    name,
    whitelistPools (
        first: 1000,
        orderBy: liquidity,
        orderDirection: desc
    ) 
    {
        id,
        token0 { id, symbol, name },
        token1 { id, symbol, name },
        liquidity,
        feeTier,
        totalValueLockedToken0,
        totalValueLockedToken1
    }
  }
}
'''
