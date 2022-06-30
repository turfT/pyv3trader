# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import List

# Pip
from jsoncodable import JSONCodable

# Local
from .function_result import FunctionResult

# -------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------- class: AggregateResult ---------------------------------------------------- #

class AggregateResult(JSONCodable):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        block_number: int,
        # blocktimestamp:int,
        results: List[FunctionResult]
    ):
        self.block_number = block_number
        # self.blocktimestamp = blocktimestamp
        self.results = results


# -------------------------------------------------------------------------------------------------------------------------------- #