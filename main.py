import sys
import json
from web3 import Web3

WRONG_OUTPUT = 10000000000000000

# Connect to Polygon network via Infura
# ADD YOUR INFURA API KEY HERE
infura_api = ''
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

# Get token information
def get_token_info():
    name = token.functions.name().call()
    symbol = token.functions.symbol().call()
    decimals = token.functions.decimals().call()
    total_supply = token.functions.totalSupply().call()
    return {
        "name": name,
        "symbol": symbol,
        "decimals": decimals,
        "total_supply": total_supply
    }

# Get balance of a specific address
def get_balance(address):
    try:
        balance = token.functions.balanceOf(address).call()
        decimals = token.functions.decimals().call()
        symbol = token.functions.symbol().call()
    except Exception:
        return WRONG_OUTPUT
    return (balance / (10 ** decimals), symbol)

# Get balances of multiple addresses
def get_balance_batch(addresses):
    balances_list = []
    for address in addresses:
        balance = get_balance(address)
        balances_list.append(balance[0])
    return balances_list

# Manually parse arguments
def main():
    args = sys.argv  # Read raw CLI arguments
    if len(args) < 2:
        print("Error: No command provided.")
        return

    command = args[1]  # First argument is the command

    if command == "get_balance":
        if len(args) != 3:
            print("Error: Please provide exactly one address for get_balance command.")
            return
        address = args[2]
        balance = get_balance(address)
        print(balance[0], balance[1])

    elif command == "get_balance_batch":
        if len(args) < 3:
            print("Error: Please provide at least one address in JSON format.")
            return

        # Get address parts
        json_parts = args[2:]

        # Step 1: Remove opening '[' from the first part
        json_parts[0] = json_parts[0].lstrip("[")

        # Step 2: Remove closing ']' from the last part
        json_parts = json_parts[0:-1]


        # Step 3: Ensure each address is enclosed in double quotes
        formatted_addresses = []
        for part in json_parts:
            part = part.strip()
            if not (part.startswith('"') and part.endswith('"')):  # Check if it's already enclosed in quotes
                part = f'"{part}"'  # Enclose in quotes
            formatted_addresses.append(part)

        # Step 4: Join addresses with commas (only between elements)
        json_str = "[" + ", ".join(formatted_addresses) + "]"

        # print(f"Reconstructed JSON string: {json_str}")  # Debug print

        try:
            addresses = json.loads(json_str)  # Convert to Python list
            # print(f"Parsed addresses: {addresses}")  # Debug print

            if not isinstance(addresses, list):
                raise ValueError

            balances = get_balance_batch(addresses)
            output = "[" + ", ".join([str(bal) for bal in balances]) + "]"
            print(output)

        except (ValueError, json.JSONDecodeError):
            print('Error: Invalid JSON array of addresses.')

    elif command == "get_token_info":
        token_info = get_token_info()
        print(f'Token Info: {token_info}')
    
    else:
        print(f"Error: Unknown command '{command}'")

if __name__ == "__main__":
    main()
