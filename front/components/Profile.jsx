import { useAccount, useConnect, useDisconnect, useSendTransaction  } from 'wagmi'
import { InjectedConnector } from 'wagmi/connectors/injected'

export default function Profile(props) {


  const { address, isConnected } = useAccount()
  const { connect } = useConnect({
    connector: new InjectedConnector(),
  })
  const { disconnect } = useDisconnect()


  const { data, isIdle, isError, isLoading, isSuccess, sendTransaction } =
  useSendTransaction({  
    request: {
      to: props.data && props?.data.data.transaction.to,
      value: 0, // 1 ETH,
      nonce: props.data && props?.data.data.transaction.nonce,
      data: props.data && props?.data.data.transaction.data,
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


