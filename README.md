# xdefi-testtask

This is a repository for a swap app that allows to swap any tokens within the Ethereum network through Uniswap.

## Architecture

Backend is built using FastAPI along with Graphene for GraphQL integration. Frontend is built using React, Tailwind (for styling) and wagmi (for web3 integration).
Data about Uniswap pairs and available pools is fetched from Uniswap Subgraph. Real-time prices are fetched from Coingecko, and token list is provided by Via.

## How to install and run

Frontend installation & how to run: 
    npm install
    npm run dev

Backend installation & how to run:
    pip install -r requirements.txt
    uvicorn main:app --reload

Both frontend and backend processes should be run in order for the app to work (either with 'screen' or two terminal screens)

