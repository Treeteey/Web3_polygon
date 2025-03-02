# Web3_polygon

## Project Description

This project is a Python-based application that interacts with the Polygon blockchain network. It provides various functionalities to interact with ERC20 token contracts, including fetching token balances, retrieving token information, and identifying top token holders. The project leverages Web3.py to connect to the Polygon network and interact with smart contracts.

## Features

- **Get Token Balance**: Retrieve the balance of a specific address for a given ERC20 token.
- **Get Token Information**: Fetch details about the token, such as its name, symbol, decimals, and total supply.
- **Get Balances of Multiple Addresses**: Retrieve the balances of multiple addresses for a given ERC20 token.
- **Get Top Token Holders**: Identify the top N addresses by balance for a given ERC20 token.

## Installation

1. Clone the repository:
   ```sh
   git clone git@github.com:<YourUsername>/<YourRepository>.git
   cd <YourRepository>
   ```

2. `cd Web3_polygon`
3. `pip install -r requirements.txt`


## Commands

1. Get balance of address:
   
   - input: `py main.py get_balance 0x51f1774249Fc2B0C2603542Ac6184Ae1d048351d`
   - output: `0.01 TBY` OR `10000000000000000` if cant fetch data
  
2. Get balance of several addresses:
   
   - Input: `py main.py get_balance_batch ["0x51f1774249Fc2B0C2603542Ac6184Ae1d048351d", "0x4830AF4aB9cd9E381602aE50f71AE481a7727f7C"]`
   - Output: `[0.01, 0.01]` OR `[10000000000000000, 10000000000000000]`
  
3. Get Top N token holders. This function searches for browser that can open url `https://polygonscan.com/accounts`. Launches browser, then downloads `.csv` tables in current directory in `top_accounts/` and process them.

    - Input: `py main.py get_top {N}`  (N max is 10000)
    - Output: `[(address_top_1, balance_top_1), (address_top_2, balance_top_2), (address_top_3, balance_top_3), ..., (address_top_N, balance_top_N)]`

4. Get token info.

    - Input: `py main.py  get_token_info 0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0`
    - Output: `{'name': 'Storage Gastoken V3', 'symbol': 'TBY', 'decimals': 18, 'total_supply': 9761593039690880466978}`