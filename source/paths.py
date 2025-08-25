import os
from pprint import pprint

_SOURCE = os.path.dirname(__file__)
_BASE = os.path.dirname(_SOURCE)
_ASSETS = os.path.join(_BASE, "assets")


def _load_assets(root):
    assets = {}
    for dirpath, _, filenames in os.walk(root):
        relpath = os.path.relpath(dirpath, root)
        node = assets
        if relpath != ".":
            for part in relpath.split(os.sep):
                node.setdefault(part, {})
                node = node[part]
        for name in filenames:
            stem, _ = os.path.splitext(name)
            node[stem] = os.path.join(dirpath, name)
    return assets


paths = _load_assets(_ASSETS)
