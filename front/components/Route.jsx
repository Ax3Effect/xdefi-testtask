/* This example requires Tailwind CSS v2.0+ */
import { CheckCircleIcon, ChevronRightIcon, MailIcon, ArrowRightIcon } from '@heroicons/react/solid'

export default function Route(props) {

    const data = props.data
    const handleTransaction = props.handleTransaction

    return (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
            {data.map((token) => (
            <li key={token.fromId}>
                <a className="block hover:bg-gray-50">
                <div className="flex items-center px-4 py-4 sm:px-6">
                    <div className="min-w-0 flex-1 flex items-center">
                    <div className="flex-shrink-0">
                    </div>
                    <div className="min-w-0 flex-1 px-4 md:grid md:grid-cols-2 md:gap-4">
                        <div>
                        <p className="text-sm font-medium text-indigo-600 truncate">{token.fromSymbol} ({token.fromName}) 
                        <ArrowRightIcon className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" aria-hidden="true" />
                        {token.sideSymbol} ({token.sideName})
                        <ArrowRightIcon className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" aria-hidden="true" />
                        {token.toSymbol} ({token.toName})
                        </p>
                        <p className="mt-2 flex items-center text-sm text-gray-500">
                            
                            <span className="truncate">{token.fromSymbol}: {token.fromPrice}$ | {token.toSymbol}: {token.toPrice}$</span>
                        </p>
                        </div>
                        <div className="hidden md:block">
                        <div>
                            <p className="text-sm text-gray-900">
                            </p>
                            <p className="mt-2 flex items-center text-sm text-gray-500">
                            </p>
                            <button class='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded' onClick={() => handleTransaction(token.routeId)}>Set</button>
                        </div>
                        </div>
                    </div>
                    </div>
                    <div>
                    <ChevronRightIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                    </div>
                </div>
                </a>
            </li>
            ))}
        </ul>
        </div>
    )
}
