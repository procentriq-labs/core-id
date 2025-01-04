from json import JSONEncoder
from dataclasses import is_dataclass, asdict
import base64

class EnhancedJSONEncoder(JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        elif type(o) == bytes:
                return "<bytes>"+base64.urlsafe_b64encode(o).decode('utf-8')
        return super().default(o)