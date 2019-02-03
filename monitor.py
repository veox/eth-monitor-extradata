#!/usr/bin/env python
# Monitor `extradata` field in ethereum blocks (canonical and linked ommers)
# for progpow preference signal.
#
# Based on example: https://web3py.readthedocs.io/en/stable/filters.html#synchronous        

from pprint import pprint as pp
import time

from eth_utils import (
    to_hex,
    to_text,
)
from web3.auto import w3


# scan this many characters at most
MAX_SCAN = 16


def detect_progpow_vote(extradata):
    try:
        scan = to_text(extradata[:MAX_SCAN])
    except UnicodeDecodeError as e:
        badpos = e.args[2]
        return 'CRAP', max(0, badpos - 1)

    choices = ['PPYE', 'PPNO', 'PPDC', 'PPWK']
    votes = [choice for choice in choices if choice in scan]

    if len(votes) > 1:
        vote = 'JERK'
    elif len(votes) == 1:
        vote = votes[0]
    else: # len(votes) == 0
        vote = 'NONE'

    return vote, MAX_SCAN

def handle_new_block(blockhash):
    block = w3.eth.getBlock(blockhash)
    blocknum = block['number']
    extradata = block['extraData']
    vote, safechars = detect_progpow_vote(extradata)

    extratext = to_text(extradata[:safechars])

    print(blocknum, to_hex(blockhash), vote, extratext)
    # TODO: inspect ommers

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
