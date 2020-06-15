import importlib.metadata as ilmd
import json

eps = ilmd.entry_points().get('flake8.extension', {})

d = {ep.name: {'module': (val := ep.value.partition(":"))[0], 'function': val[2]} for ep in eps}

print(json.dumps(d))

