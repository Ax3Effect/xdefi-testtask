from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_read_routes():
    value = '''query {
        routes(from: "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0", to: "0xBB0E17EF65F82Ab018d8EDd776e8DD940327B28b") {
            routeId,
            fromId,
            fromSymbol,
            fromName,
            fromPrice,
            toId,
            toName,
            toSymbol,
            toPrice,
            sideId,
            sideName,
            sideSymbol
        }
        }
    '''
    response = client.post("/graphql", data=value)
    assert response.json() == {
        "data": {
            "routes": [
            {
                "routeId": "30814e92-2eb2-4663-947b-7490c8ceb9f3",
                "fromId": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
                "fromSymbol": "MATIC",
                "fromName": "Matic Token",
                "fromPrice": "0.822245",
                "toId": "0xbb0e17ef65f82ab018d8edd776e8dd940327b28b",
                "toName": "Axie Infinity Shard",
                "toSymbol": "AXS",
                "toPrice": "15.89",
                "sideId": "0xdac17f958d2ee523a2206206994597c13d831ec7",
                "sideName": "Tether USD",
                "sideSymbol": "USDT"
            },
            {
                "routeId": "0e04d831-971d-421a-a7f4-ee4fd4fe36ac",
                "fromId": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
                "fromSymbol": "MATIC",
                "fromName": "Matic Token",
                "fromPrice": "0.822245",
                "toId": "0xbb0e17ef65f82ab018d8edd776e8dd940327b28b",
                "toName": "Axie Infinity Shard",
                "toSymbol": "AXS",
                "toPrice": "15.89",
                "sideId": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                "sideName": "Wrapped Ether",
                "sideSymbol": "WETH"
            }
            ]
        }
    }