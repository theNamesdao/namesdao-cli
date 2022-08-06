# Namesdao-resolver
#  Sample imlementation of using the Namesdao secondary cache to resolve Namesdao names for sending XCH
#   to a Namesdao .xch wallet
#
# Copyright 2022 Namesdao
# Use permitted under the MIT Open Source License
#
#  Usage:
'''
        Sample usage:
        python namesdao.py wallet send $address -a $amount -m $fee
        python namesdao.py wallet send hellobilly.xch -a 0.000000000001 -m 0.000000000002
        python namesdao.py wallet resolve $address

        Options:
          First argument is the address to send the XCH  [required]
          -a, --amount TEXT               How much chia to send, in XCH  [required]
          -e, --memo TEXT                 Additional memo for the transaction
          -m, --fee TEXT                  Set the fees for the transaction, in XCH [required]
          -M, --Fee TEXT                  Set the fees for the transaction, in mojos [takes precedence over --fee]
          -h, --help                      Show this message and exit.
'''
#
# processing starts at main() at the bottom
#
from optparse import OptionParser
import sys
import json
import re
import shlex
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import subprocess



def sanitize_address(address):
    '''Make sure address is safe input for a shell command.'''
    if re.match(r'^[a-z0-9]{62}$', address):
        return address


def sanitize_number(number, _type=float):
    '''Turn input that's supposed to be a number into a number, or give error. '''
    try:
        num = _type(number)
    except:
        return
    return number


def resolve(name):
    ''' Use the Namesdao name to get the XCH address it refers to. Look up name json file and return the address, which the file lists.'''

    # Normalize name
    name = name.lower()

    # Remove any permitted top-level suffix
    suffixes = ['.xch', '.chia']
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]

    # This is the URL from which the resolving data will be downloaded.
    url = f'https://lookup.namesdao.org/{name}.json'

    try:
        request = Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
            },
        )
        response = urlopen(request)
    except HTTPError as err:
        code = err.getcode()
        if code == 404:
            print('We don\'t currently have this address registered in our cache.')
        else:
            print('An error occurred while trying to resolve. Please try again.')
            print(f'Error was: {err}')
        return

    data = json.loads(response.read().decode('utf-8'))
    return data['address']

def cmd_send_after_confirmation(safe_address, safe_amount, safe_fee, safe_memo):
    subprocess.run(
        [
            'chia',
            'wallet',
            'send',
            '-t',
            safe_address,
            '-a',
            safe_amount,
            '-m',
            safe_fee,
            '-e',
            safe_memo,
        ]
    )


def cmd_send():
    '''send command: Send XCH to the address that corresponds to the Namesdao name'''

    parser = OptionParser()
    parser.add_option(
        '-a', '--amount',
        help='How much chia to send, in XCH  [required]',
    )
    parser.add_option(
        '-e', '--memo',
        help='Additional memo for the transaction',
    )
    parser.add_option(
        '-m', '--fee',
        help='Set the fees for the transaction, in XCH',
    )
    parser.add_option(
        '-M', '--Fee',
        help='Set the fees for the transaction, in mojos [takes precedence over --fee]',
    )
    parser.add_option(
        '-y', '--yes',
        action='store_true',
        help='Execute without asking for confirmation',
    )
    options, args = parser.parse_args(sys.argv[3:])

    if options.help:
        display_help()
        return

    try:
        name = args[0]
    except IndexError:
        print('Please provide a name, e.g. hello.xch')
        display_help()
        return
    address = resolve(name)
    if options.amount is None:
        print('--amount in XCH is required') # TODO: Amount in XCH or mojos? Same for fee.
        display_help()
        return
    if options.Fee is not None:
        safe_fee = sanitize_number(options.Fee, _type=int)
    elif options.fee is not None:
        safe_fee = str(int(float(sanitize_number(options.fee))*1e12))
    else:
        safe_fee = '1'
    safe_amount = sanitize_number(options.amount)
    safe_address = sanitize_address(address)
    if options.fee is not None and safe_fee is None:
        if options.Fee is not None:
            print('Please use a number to indicate the network transaction fee (in mojos)')
        else:
            print('Please use a number to indicate the network transaction fee (in XCH)')
        return
    if safe_amount is None:
        print('Please use a number to indicate the amount of XCH to send')
        return
    if safe_address is None:
        print('Sorry, we don\'t have an address for that name.')
        return
    #print (f'Sending to address {safe_address}')

    if options.memo:
        safe_memo = shlex.quote(options.memo)
    else:
        safe_memo = None

    if options.yes:
        cmd_send_after_confirmation(safe_address, safe_amount, safe_fee, safe_memo)
        return

    if safe_memo:
        memo_txt = f'a memo of "{safe_memo}" and'
    else:
        memo_txt = ''

    print(
        "Welcome to Namesdao wallet send\n"
        "Namesdao, the Name Service for the Chia Blockchain\n"
        "\n"
        f"{name} maps to this XCH address: {safe_address}\n"
        #f"AIR token has asset id 824c71e37ac660006e03f7884561e7a124d930460ae1506a9c234c06ebc6aa1d"
        #f"and your current balance is: 10 AIR"
        "\n"
        f"Please confirm, send {safe_amount} XCH to {name},\n"
        f"with{memo_txt} network transaction fee of {safe_fee} mojos? (Y/n)"
    )
    cmd_send_after_confirmation(safe_address, safe_amount, safe_fee, safe_memo)

def cmd_resolve():
    '''resolve command: Show the XCH address for the given Namesdao name.

    We use this for simple testing.
    '''

    parser = OptionParser()
    options, args = parser.parse_args(sys.argv[3:])
    try:
        name = args[0]
    except IndexError:
        print('Please provide a name')
        display_help()
        return
    address = resolve(name)
    if address:
        print(address)

# Used to point to the method to process the command
cmd_dict = {
    'send': cmd_send,
    'resolve': cmd_resolve,
}


def display_help():
    print(
        "Sample usage:\n"
        "python namesdao.py wallet send $address -a $amount -m $fee\n"
        "python namesdao.py wallet send hellobilly.xch -a 0.000000000001 -m 0.000000000002\n"
        "python namesdao.py wallet resolve $address\n"
        "\n"
        "Options:\n"
        "  First argument is the address to send the XCH  [required]\n"
        "  -a, --amount TEXT               How much chia to send, in XCH  [required]\n"
        "  -e, --memo TEXT                 Additional memo for the transaction\n"
        "  -m, --fee TEXT                  Set the fees for the transaction, in XCH\n"
        "  -M, --Fee TEXT                  Set the fees for the transaction, in mojos [takes precedence over --fee]\n"
        "  -y, --yes                       Execute without asking for confirmation\n"
        "  -h, --help                      Show this message and exit.\n"
    )

# processing starts here
def main():
    try:
        if sys.argv[1] != 'wallet':
            display_help()
            return
    except IndexError:
        display_help()
        return

    try:
        # see if we have a clear "send" or "resolve" command on the command line, if so proceed
        cmd = cmd_dict[sys.argv[2]] # TODO test change of [1] to [2]
    except KeyError:
        display_help()
        return
    except IndexError:
        display_help()
        return
    # call the send or resolve method
    cmd()


if __name__ == '__main__':
    main()
