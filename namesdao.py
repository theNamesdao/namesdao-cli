# Namesdao-cli
#  Sample imlementation of using the Namesdao secondary cache to resolve Namesdao names for sending XCH
#   to a Namesdao .xch wallet
#
# Organization: Namedao, https://www.namesdao.org/
#
# Note: This is only a sample implementation using the secondary cache, which is not updated reliably. Wallets and Infrastructure Providers should
# index the primary storage on the Chia Blockchain, per NDIP-0001
#
# TODOs:
#  check with primary record (on chia blockchain) to confirm before sending
#  add pytest unit tests
#
# contact @theNamesdao or @BenAtreidesVing on Twitter if you'd like bounty commissions to upgrade this code, thank you!
#
#
# Copyright 2022 Namesdao
# Use permitted under the MIT Open Source License
#
#  Usage:
'''
        Sample usage:
        $ python3 namesdao.py name register $name $destaddress --cloak -a 0.018
        $ python3 namesdao.py name register _nameToRegister.xch _MyExistingName.xch --cloak -a 0.018
        $ python3 namesdao.py name register ___nameToRegister.xch xchaddresstoregister --cloak -a 0.000000000001 -m 0.0000000001
        $ python3 namesdao.py name register ___nameToRegister.xch xchaddresstoregister -a 0.000000000001 -m 0.0000000001
        $ python3 namesdao.py wallet send $address -a $amount -m $fee
        $ python3 namesdao.py wallet send hellobilly.xch -a 0.000000000001 -m 0.000000000002
        $ python3 namesdao.py wallet resolve $address

        Options:
          First argument is the address to send the XCH  [required]
          -a, --amount TEXT               How much chia to send, in XCH  [required]
          -e, --memo TEXT                 Additional memo for the transaction
          -k, --cloak                     Encrypt memo
          -m, --fee TEXT                  Set the fees for the transaction, in XCH (optional, default value 1 mojo)
          -M, --Fee TEXT                  Set the fees for the transaction, in mojos [takes precedence over --fee]
          -y, --yes                       Execute without asking for confirmation
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
from urllib.error import HTTPError, URLError
from urllib.parse import quote
import subprocess
import time
import hashlib
import os
import base64

RECIPIENT_ADDRESS = 'xch1jhye8dmkhree0zr8t09rlzm9cc82mhuqtp5tlmsj4kuqvs69s2wsl90su4'
RECIPIENT_FINGERPRINT = '2A06D252B6B804C837E2BA2D2B3A61F48A54276C'
RECIPIENT_PUBKEY = b'''-----BEGIN PGP PUBLIC KEY BLOCK-----

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
evFFqsVLe8jB1LlsYrQJ
=tDO1
-----END PGP PUBLIC KEY BLOCK-----'''


INCLUDE_SALT = True


def encrypt(message):
    '''Encrypt a message using gpg'''

    import io
    import gpg

    ptext = io.BytesIO(message)
    c = gpg.Context()
    c.armor = True

    try:
        recipient = c.get_key(RECIPIENT_FINGERPRINT)
    except gpg.errors.KeyNotFound:
        c.key_import(RECIPIENT_PUBKEY)
        recipient = c.get_key(RECIPIENT_FINGERPRINT)

    ctext = c.encrypt(
        recipients=[recipient],
        plaintext=ptext,
        always_trust=True,
        sign=False,
    )[0]

    return ctext.decode('utf-8')


def verify(message, signature):
    '''Verify a signature using gpg'''

    import io
    import gpg

    c = gpg.Context()

    try:
        key = c.get_key(RECIPIENT_FINGERPRINT)
    except gpg.errors.KeyNotFound:
        c.key_import(RECIPIENT_PUBKEY)
        key = c.get_key(RECIPIENT_FINGERPRINT)

    message_buffer = io.BytesIO(message)
    signature_buffer = io.BytesIO(signature)

    try:
        c.verify(
            message_buffer,
            signature=signature_buffer,
            verify=[key],
        )
    except (gpg.errors.BadSignatures, gpg.errors.MissingSignatures):
        return False

    return True


def sanitize_address(address):
    '''Make sure address is safe input for a shell command.'''
    if re.match(r'^[a-z0-9]{62}$', address):
        return address


def sanitize_number(number):
    '''Turn input that's supposed to be a (12 decimal digit) number into a number, or give error. '''
    try:
        num = int(number)
    except:
        return
    return number


def sanitize_number12dec(number):
    '''Turn input that's supposed to be a (12 decimal digit) number into a number, or give error. '''
    try:
        num = float(number)
    except:
        return
    return f'{num:.12f}'


def resolve(name):
    ''' Use the Namesdao name to get the XCH address it refers to. Look up name json file and return the address, which the file lists.'''

    # Normalize name
    name = name.lower()

    # Remove any permitted top-level suffix
    suffixes = ['.xch', '.chia']
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break

    # This is the URL from which the resolving data will be downloaded.
    urls = [
        f'https://namesdaolookup.xchstorage.com/{name}.json',
        f'https://storage1.xchstorage.cyou/names_lookup/{name}.json',
    ]
    signature_urls = [f'{u}.gpg' for u in urls]

    retries = 3
    url_idx = 0
    url = urls[url_idx]
    signature_url = signature_urls[url_idx]
    while retries > 0:
        try:
            request = Request(
                url,
                data=None,
            )
            response = urlopen(request)
        except HTTPError as err:
            code = err.getcode()
            if code in (403, 404):
                url_idx += 1
                if url_idx >= len(urls):
                    print('We don\'t currently have this address registered in our cache.')
                else:
                    url = urls[url_idx]
                    continue
            else:
                print('An error occurred while trying to resolve. Please try again.')
                print(f'Error was: {err}')
            return
        except URLError:
            retries -= 0 # TODO: subtract 1?
            if retries <= 0:
                print('An error occurred while trying to resolve. Please check your network connection and try again.')
                break
            else:
                time.sleep(1)
            continue

        # Now we try to download the signature file.
        signature_response = None
        try:
            request = Request(
                signature_url,
                data=None,
            )
            signature_response = urlopen(request)
        except HTTPError as err:
            code = err.getcode()
            if code in (403, 404):
                #print('WARNING: No signature.')
                pass
            else:
                print('An error occurred while trying to download the signature file. Please try again.')
                print(f'Error was: {err}')
        except URLError:
            print('An error occurred while trying to download the signature file. Please check your network connection and try again.')
        break

    message = response.read()
    data = json.loads(message.decode('utf-8'))
    if signature_response:
        signature = signature_response.read()
        if verify(message, signature):
            print('Verified signature')
        else:
            print('WARNING: Aborting due to invalid signature.')
            return
    return data['address']

def cmd_send_after_confirmation(safe_address, safe_amount, safe_fee, safe_memo):
    cmd = [
        'chia',
        'wallet',
        'send',
        '-t',
        safe_address,
        '-a',
        safe_amount,
        '-m',
        safe_fee,
        '--override',
    ]

    if safe_memo is not None:
        cmd.extend([
            '-e',
            safe_memo,
        ])

    subprocess.run(cmd)


class _Options:
    pass


def _cmd_send(name, address, options):
    # This is a shared method for processing operations that require sending chia.
    if options.Fee is not None:
        mojos = sanitize_number(options.Fee)
        if mojos is None:
            safe_fee = None
        else:
            safe_fee = str(int(mojos)*1e-12)
    elif options.fee is not None:
        safe_fee = sanitize_number12dec(options.fee)
        if safe_fee is None:
            mojos = None
        else:
            mojos = str(int(float(safe_fee)*1e12))
    else:
        safe_fee = '0.000000000001'
        mojos = '1'

    if options.amount is None:
        safe_amount = '0.000000000001'
    else:
        safe_amount = sanitize_number12dec(options.amount)

    if float(safe_amount) == 0:
        print('Please provide an amount higher than 0.000000000001 (10^-12) XCH')
        return

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

    memo = options.memo

    if memo and options.cloak:
        # We encrypt the memo here if the cloak flag was set.
        orig_memo = memo
        hash = hashlib.sha256()
        memo_payload = memo.encode('utf-8')
        if INCLUDE_SALT:
            # Here we append a secret to the memo_payload.
            memo_payload += b':' + base64.b64encode(os.urandom(20))
        encmemo = encrypt(memo_payload)
        safe_memo = ':register:' + quote(encmemo)
        print (f'Replaced {safe_memo} for {orig_memo}')
    elif memo:
        safe_memo = shlex.quote(memo)
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
        f"with {memo_txt} network transaction fee of {mojos} mojos? (Y/n)"
    )
    if input() in ('Y', 'Yes', 'yes', 'y'):
        cmd_send_after_confirmation(safe_address, safe_amount, safe_fee, safe_memo)


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
        '-k', '--cloak',
        action='store_true',
        help='Encrypt memo',
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

    try:
        name = args[0]
    except IndexError:
        print('Please provide a name, e.g. hello.xch')
        display_help()
        return
    # TODO: Improve help message re name/address. And give better error message in case no name is provided.
    address = sanitize_address(name)
    if not address:
        address = resolve(name)
        if address is None:
            return

    _cmd_send(name, address, options)


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


def cmd_register():
    parser = OptionParser()
    parser.add_option(
        '-a', '--amount',
        help='How much chia to send, in XCH [required]',
    )
    parser.add_option(
        '-k', '--cloak',
        action='store_true',
        help='Encrypt memo',
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
    try:
        name, address = args
    except ValueError:
        print('Please provide a name and a recipient address or name')
        print('Sample usage:')
        print('python namesdao.py name register ___nameToRegister.xch xchaddresstoregister -a 0.000000000001 -m 0.0000000001')
        print('python namesdao.py name register ___nameToRegister.xch xchaddresstoregister --cloak -a 0.000000000001 -m 0.0000000001')
        return

    memo = f'{name}:{address}'
    opts = _Options()
    opts.memo = memo
    opts.cloak = options.cloak
    opts.yes = options.yes
    opts.amount = options.amount
    opts.fee = options.fee
    opts.Fee = options.Fee
    _cmd_send('namesdao.xch', RECIPIENT_ADDRESS, opts)


# Used to point to the method to process the command
cmd_dict = {
    'wallet': {
        'send': cmd_send,
        'resolve': cmd_resolve,
    },
    'name': {
        'register': cmd_register,
    },
}


def display_help():
    print(
        "Sample usage:\n"
        "python namesdao.py wallet send $address -a $amount -m $fee\n"
        "python namesdao.py wallet send hellobilly.xch -a 0.000000000001 -m 0.000000000002\n"
        "python namesdao.py wallet resolve $address\n"
        "python namesdao.py name register ___nameToRegister.xch xchaddresstoregister -a 0.000000000001 -m 0.0000000001\n"
        "python namesdao.py name register ___nameToRegister.xch xchaddresstoregister --cloak -a 0.000000000001 -m 0.0000000001\n"
        "\n"
        "Options:\n"
        "  First argument is the address to send the XCH  [required]\n"
        "  -a, --amount TEXT               How much chia to send, in XCH  [required]\n"
        "  -e, --memo TEXT                 Additional memo for the transaction\n"
        "  -k, --cloak                     Encrypt memo\n"
        "  -m, --fee TEXT                  Set the fees for the transaction, in XCH\n"
        "  -M, --Fee TEXT                  Set the fees for the transaction, in mojos [takes precedence over --fee]\n"
        "  -y, --yes                       Execute without asking for confirmation\n"
        "  -h, --help                      Show this message and exit.\n"
    )

# processing starts here
def main():
    try:
        if sys.argv[1] not in ('wallet', 'name'):
            display_help()
            return
    except IndexError:
        display_help()
        return

    try:
        # see if we have a clear "send" or "resolve" command on the command line, if so proceed
        cmd = cmd_dict[sys.argv[1]][sys.argv[2]] # TODO test change of [1] to [2]
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
