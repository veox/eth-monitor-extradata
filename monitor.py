#!/usr/bin/env python
# Monitor `extradata` field in Ethereum blocks (canonical and linked ommers)
# for ProgPoW preference signal.
#
# Based on example: https://web3py.readthedocs.io/en/stable/filters.html#synchronous        

from pprint import pprint as pp
import time

from eth_utils import (
    to_hex,
    to_text,
)
from web3.auto import w3


# scan this many bytes at most
MAX_SCAN = 16


def detect_progpow_vote(extradata, nbytes=MAX_SCAN):
    try:
        scan = to_text(extradata[:nbytes])
    except UnicodeDecodeError as err:
        # print('Error while detecting vote!')
        # pp(err.args)
        badpos = err.args[2]
        # second pass, more constrained
        return detect_progpow_vote(extradata, nbytes=badpos)

    choices = ['PPYE', 'PPNO', 'PPDC', 'PPWK']
    votes = [choice for choice in choices if choice in scan]

    if len(votes) > 1:
        vote = 'JERK'
    elif len(votes) == 1:
        vote = votes[0]
    else: # len(votes) == 0
        vote = 'NONE'

    return vote, nbytes

def handle_new_block(blockhash, recursive_call=False, ommertext=None):
    if not ommertext:
        if not recursive_call:
            ommertext = '│'
        else:
            ommertext = '┝'

    block = w3.eth.getBlock(blockhash)

    blocknum = block['number']
    extradata = block['extraData']
    ommers = block['uncles']
    parent = block['parentHash']

    vote, safechars = detect_progpow_vote(extradata)

    try:
        extratext = to_text(extradata[:safechars])
    except UnicodeDecodeError as err:
        # print('Error while preparing extratext!')
        # pp(err.args)
        extratext = ''

    # NOTE: handling (printing) ommers before printing non-ommer block info
    # (so that ommers are printed first)
    if not recursive_call:
        if len(ommers) > 0:
            # handle ommers of this block
            for ommer_blockhash in ommers:
                handle_new_block(ommer_blockhash, recursive_call=True)
            # also print (possibly re-print!..) parent
            handle_new_block(parent, recursive_call=True, ommertext='╞')

    print(blocknum, len(ommers), ommertext, to_hex(blockhash), vote, extratext)

    return

def loop_event_handler(event_filter, event_handler=pp, poll_interval=2):
    while True:
        for event in event_filter.get_new_entries():
            event_handler(event)
        time.sleep(poll_interval)

    return

def main():
    block_filter = w3.eth.filter('latest')
    loop_event_handler(block_filter, event_handler=handle_new_block)

    return

if __name__ == '__main__':
    main()
