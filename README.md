# `eth-monitor-extradata`

A simple `web3.py` script to monitor `extradata` field in Ethereum blocks for "votes".
ProgPoW votes in this particular example.

Does not handle ommers yet! This skews stats, attributing the hashing power of those
producing an uncle to those including it as one.

## License

"MIT". See `LICENSE.txt`.
