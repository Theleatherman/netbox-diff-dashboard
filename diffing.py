import json
from deepdiff import DeepDiff

def compare_snapshots(current, previous):
    return DeepDiff(previous, current, ignore_order=True)

def diff_to_json(diff):
    return json.dumps(diff, indent=2)
