# Namesdao

Register a Namesdao .xch name or send XCH to a Namesdao .xch name. Find out more at [Namesdao.org](https://www.namesdao.org).

## Usage

Sample usage:
```sh
$ python3 namesdao.py name register ___nameToRegister.xch xchaddresstoregister --cloak -a 0.000000000001 -m 0.0000000001
$ python3 namesdao.py name register ___nameToRegister.xch xchaddresstoregister -a 0.000000000001 -m 0.0000000001
$ python3 namesdao.py wallet send $address -a $amount -m $fee
$ python3 namesdao.py wallet send hellobilly.xch -a 0.000000000001 -m 0.000000000002
$ python3 namesdao.py wallet resolve $address
```

Options:
  - First argument is the address to send the XCH  [required]
  - `-a, --amount TEXT`               How much chia to send, in XCH  [required]
  - `-e, --memo TEXT`                 Additional memo for the transaction
  - `-k, --cloak`                     Encrypt memo
  - `-m, --fee TEXT`                  Set the fees for the transaction, in XCH [required]
  - `-M, --Fee TEXT`                  Set the fees for the transaction, in mojos [takes precedence over --fee]
  - `-y, --yes`                       Execute without asking for confirmation
  - `-h, --help`                      Show this message and exit.

## Requirements

[Python 3](https://www.python.org/downloads/) is required.

To use cloaked registrations, you will need to install GPG for Python:

On Ubuntu: `sudo apt install python3-gpg`

See [here](https://wiki.python.org/moin/GnuPrivacyGuard) for other operating systems.


## Cloaked registrations

Cloaked registrations encrypt part of the request to prevent others from watching the name you request in the Chia mempool, and trying to
register the name before you.

The `--cloak` flag encrypts the memo so that your name is protected from being seen by others before its registration is confirmed.


## Troubleshooting

You can fix the following warning message:

```
/usr/lib/python3/dist-packages/requests/__init__.py:89: RequestsDependencyWarning: urllib3 (1.26.11) or chardet (3.0.4) doesn't match a supported version!
  warnings.warn("urllib3 ({}) or chardet ({}) doesn't match a supported "
```

by running:

```
$ pip3 install --upgrade requests
```

## License

MIT Licence. See LICENSE for details.
