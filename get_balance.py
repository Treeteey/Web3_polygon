
from web3 import Web3
from const import WRONG_OUTPUT


def CreateToken():
    # Connect to Polygon network via Infura
    # ADD YOUR INFURA API KEY HERE
    infura_api = 'd63e86ddbad24ba99e54bbb90befdd64'
    infura_url = f'https://polygon-mainnet.infura.io/v3/{infura_api}'
    w3 = Web3(Web3.HTTPProvider(infura_url))

    # Token contract address
    contract_address = '0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0'
    checksum_address = Web3.to_checksum_address(contract_address)

    # Generic ERC20 ABI
    erc20_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
        }
    ]

    # Create contract instance
    token = w3.eth.contract(address=checksum_address, abi=erc20_abi)

    return token

# Get token information
def get_token_info(address):
    token = CreateToken()
    
    # Convert address to checksum format
    checksum_address = Web3.to_checksum_address(address)

    balance = token.functions.balanceOf(checksum_address).call()
    name = token.functions.name().call()
    symbol = token.functions.symbol().call()
    decimals = token.functions.decimals().call()
    total_supply = token.functions.totalSupply().call()

    return {
        "name": name,
        "symbol": symbol,
        "decimals": decimals,
        "total_supply": total_supply,
        # "balance": balance / (10 ** decimals)  # normalize balance
    }


# Get balance of a specific address
def get_balance(address):
    token = CreateToken()
    try:
        balance = token.functions.balanceOf(address).call()
        decimals = token.functions.decimals().call()
        symbol = token.functions.symbol().call()
    except Exception:
        return (WRONG_OUTPUT, "NOTOK")
    return (balance / (10 ** decimals), symbol)

# Get balances of multiple addresses
def get_balance_batch(addresses):
    balances_list = []
    # print(addresses)
    for address in addresses:
        balance = get_balance(address)
        balances_list.append(balance[0])
    return balances_list