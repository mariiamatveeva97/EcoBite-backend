import json, sys

def fix(node):
    if isinstance(node, list):
        return [fix(x) for x in node]
    if not isinstance(node, dict):
        return node
    node = {k: fix(v) for k, v in node.items()}
    if "anyOf" in node:
        opts = node["anyOf"]
        non_null = [o for o in opts if o != {"type": "null"}]
        if len(non_null) != len(opts):
            del node["anyOf"]
            if len(non_null) == 1:
                only = non_null[0]
                if "$ref" in only:
                    node["allOf"] = [only]
                else:
                    for k, v in only.items():
                        node.setdefault(k, v)
            else:
                node["anyOf"] = non_null
            node["nullable"] = True
    for ex, base in (("exclusiveMinimum", "minimum"), ("exclusiveMaximum", "maximum")):
        if ex in node and not isinstance(node[ex], bool):
            node[base] = node[ex]
            node[ex] = True
    return node

src, dst = sys.argv[1], sys.argv[2]
spec = fix(json.load(open(src, encoding="utf-8")))
spec["openapi"] = "3.0.3"
json.dump(spec, open(dst, "w"), indent=2)
print("ok")
