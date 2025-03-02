import sys
import json
import get_balance
from get_top import get_top, get_top_with_transactions
from const import POLYGONSCAN_API_KEY


def command_get_balance(args):
    """Handles the 'get_balance' command."""
    if len(args) != 3:
        print("Error: Please provide exactly one address for get_balance command.")
        return
    address = args[2]
    balance = get_balance.get_balance(address)
    print(balance[0], balance[1])


def command_get_balance_batch(args):
    """Handles the 'get_balance_batch' command."""
    if len(args) < 3:
        print("Error: Please provide at least one address in JSON format.")
        return

    json_parts = args[2:]
    json_parts[0] = json_parts[0].lstrip("[")
    json_parts = json_parts[:-1]  # Remove last element
    # json_parts[-1] = json_parts[-1].rstrip("]")

    formatted_addresses = []
    for part in json_parts:
        part = part.strip()
        if not (part.startswith('"') and part.endswith('"')):  # Ensure quotes
            part = f'"{part}"'
        formatted_addresses.append(part)

    json_str = "[" + ", ".join(formatted_addresses) + "]"

    try:
        addresses = json.loads(json_str)
        if not isinstance(addresses, list):
            raise ValueError

        balances = get_balance.get_balance_batch(addresses)
        output = "[" + ", ".join([str(bal) for bal in balances]) + "]"
        print(output)

    except (ValueError, json.JSONDecodeError):
        print("Error: Invalid JSON array of addresses.")


def command_get_top(args):
    """Handles the 'get_top' command."""
    if len(args) != 3:
        print("Error: Please provide exactly one number for get_top command.")
        return

    try:
        N = int(args[2])
        top_accounts = get_top(N)
        print(top_accounts)
    except ValueError:
        print("Error: Invalid number provided for get_top command.")


def command_get_token_info(args):
    """Handles the 'get_token_info' command."""
    if len(args) != 3:
        print("Error: Please provide exactly one token contract address for get_token_info command.")
        return
    token_info = get_balance.get_token_info(args[2])
    print(token_info)

def command_get_top_with_transactions(args):
    """Handles the 'get_top_with_transactions' command."""
    if len(args) != 3:
        print("Error: Please provide exactly one number for get_top_with_transactions command.")
        return

    try:
        N = int(args[2])
        top_accounts = get_top_with_transactions(N)
        print(top_accounts)
    except ValueError:
        print("Error: Invalid number provided for get_top_with_transactions command.")


def main():
    """Main function to handle command-line arguments."""
    args = sys.argv
    if len(args) < 2:
        print("Error: No command provided.")
        return

    command = args[1]

    command_handlers = {
        "get_balance": command_get_balance,
        "get_balance_batch": command_get_balance_batch,
        "get_top": command_get_top,
        "get_token_info": command_get_token_info,
        "get_top_with_transactions": command_get_top_with_transactions,
    }

    if command in command_handlers:
        command_handlers[command](args)
    else:
        print(f"Error: Unknown command '{command}'")


if __name__ == "__main__":
    main()
