from enum import Enum

from pyv3trader.utils.types import onchainTxType

MINT_KECCAK = "0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde"
SWAP_KECCAK = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
BURN_KECCAK = "0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c"




type_dict ={}
type_dict[MINT_KECCAK]= onchainTxType.MINT
type_dict[SWAP_KECCAK] = onchainTxType.SWAP
type_dict[BURN_KECCAK] = onchainTxType.BURN