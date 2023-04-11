import json
from serializers import MusicSerializer

fn = "a1.json"

with open(fn) as f:
    data = json.load(f)
    for x in data['songs']:
        print(x)