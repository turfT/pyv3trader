from enum import Enum

from pyv3trader.utils.types import onchainTxType

MINT_KECCAK = "0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde"
SWAP_KECCAK = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
BURN_KECCAK = "0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c"
COLLECT_KECCAK = "0x70935338e69775456a85ddef226c395fb668b63fa0115f5f20610b388e6ca9c0"

INCREASE_LIQUIDITY = "0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f"
DECREASE_LIQUIDITY = "0x26f6a048ee9138f2c0ce266f322cb99228e8d619ae2bff30c67f8dcf9d2377b4"
COLLECT = "0x40d0efd1a53d60ecbf40971b9daf7dc90178c3aadc7aab1765632738fa8b8f01"

PROXY_CONTRACT_ADDRESS = "0xc36442b4a4522e871399cd717abdd847ab11fe88"

type_dict = {
    MINT_KECCAK: onchainTxType.MINT,
    SWAP_KECCAK: onchainTxType.SWAP,
    BURN_KECCAK: onchainTxType.BURN,
    COLLECT_KECCAK: onchainTxType.COLLECT
}
