import { useAccount, useConnect, useDisconnect, useSendTransaction  } from 'wagmi'
import { InjectedConnector } from 'wagmi/connectors/injected'

export default function Profile() {
  const { address, isConnected } = useAccount()
  const { connect } = useConnect({
    connector: new InjectedConnector(),
  })
  const { disconnect } = useDisconnect()


  const { data, isIdle, isError, isLoading, isSuccess, sendTransaction } =
  useSendTransaction({
    request: {
      to: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
      value: 0, // 1 ETH,
      nonce: 54,
      data: '0x38ed17390000000000000000000000000000000000000000000000004563918244f4000000000000000000000000000000000000000000000000000043a77aabd007800000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000707a7e9606b0e1547d7f8401d92222430c3483990000000000000000000000000000000000000000000000000000000062dd4f850000000000000000000000000000000000000000000000000000000000000003000000000000000000000000514910771af9ca656af840dff83e8264ecf986ca000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000d533a949740bb3306d119cc777fa900ba034cd52',
      gasPrice: 20,
      gasLimit: 200,
    },
  })



  if (isConnected)
    return (
      <div>
        Connected to {address}<br></br>
        <button class="mt-6 mb-6 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={() => disconnect()}>Disconnect</button>
        <br></br>
        <button disabled={isLoading} class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={() => sendTransaction()}>Send test transaction</button> 
        {isLoading && <div>Check Wallet</div>}
        {isSuccess && <div>Transaction: {JSON.stringify(data)}</div>}
        {isError && <div>Error sending transaction</div>}
      </div>
    )
  return <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={() => connect()}>Connect Wallet</button>
} 


