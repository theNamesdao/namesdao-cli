# Namesdao

Send XCH to a name. Find out more at [Namesdao.org](https://namesdao.org).

## Usage

Sample usage:
```sh
$ python3 namesdao.py wallet send $address -a $amount -m $fee
$ python3 namesdao.py wallet send hellobilly.xch -a 0.000000000001 -m 0.000000000002
$ python3 namesdao.py wallet resolve $address
```

Options:
  - First argument is the address to send the XCH  [required]
  - `-a, --amount TEXT`               How much chia to send, in XCH  [required]
  - `-e, --memo TEXT`                 Additional memo for the transaction
  - `-m, --fee TEXT`                  Set the fees for the transaction, in XCH [required]
  - `-M, --Fee TEXT`                  Set the fees for the transaction, in mojos [takes precedence over --fee]
  - `-y, --yes`                       Execute without asking for confirmation
  - `-h, --help`                      Show this message and exit.

## Requirements

Only [Python 3](https://www.python.org/downloads/) is required.
