#!/usr/bin/env python3
"""
Custom JSON Encoder
Provides custom JSON encoding for complex application-specific objects.
"""

import json
from dataclasses import is_dataclass, asdict
from datetime import datetime
import numpy as np

class CustomJSONEncoder(json.JSONEncoder):
    """
    A custom JSON encoder that can handle application-specific objects
    like dataclasses, datetime objects, and numpy data types.
    """
    def default(self, obj):
        """
        Override the default method to handle custom objects.
        """
        # For dataclasses, convert them to dictionaries
        if is_dataclass(obj):
            return asdict(obj)
            
        # For datetime objects, convert them to ISO format string
        if isinstance(obj, datetime):
            return obj.isoformat()

        # For numpy types, convert them to native Python types
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)

        # Let the base class default method raise the TypeError for other types
        return super().default(obj) 