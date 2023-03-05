import json

import numpy as np


class BaseEncoder(json.JSONEncoder):
    """
    This class provides necessary methods to encode incompatible JSON types
    """

    def default(self, o):
        # numpy integer
        if isinstance(o, np.integer):
            return int(o)

        # numpy float
        elif isinstance(o, np.floating):
            return float(o)

        # numpy array
        elif isinstance(o, np.ndarray):
            return o.tolist()

        return super().default(o)
