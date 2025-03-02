import sys
import json
import get_balance 
from get_top import get_top


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
        balance = get_balance.get_balance(address)
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

            balances = get_balance.get_balance_batch(addresses)
            output = "[" + ", ".join([str(bal) for bal in balances]) + "]"
            print(output)

        except (ValueError, json.JSONDecodeError):
            print('Error: Invalid JSON array of addresses.')

    elif command == "get_token_info":
        token_info = get_balance.get_token_info()
        print(f'Token Info: {token_info}')
    
    elif command == "get_top":
        if len(args) != 3:
            print("Error: Please provide exactly one number for get_top command.")
            return
        N = int(args[2])
        top = get_top(N)
        print(top)
    
    else:
        print(f"Error: Unknown command '{command}'")

if __name__ == "__main__":
    main()
