"""Plan item 85: a real, historical bug run through the Stage B pipeline.
Usage: python3 -I scripts/stageb/realbug.py --subject tw|cp --buggy BUGGY.py --fixed FIXED.py --out OUT.jsonl
       [--extra-text TEXT ...]
The fixed source (the commit that fixed the bug) is the reference and the buggy source (its parent) is the program
under test. A test (one valid configuration) fails if its behaviour on the input corpus differs between the two, using
the same behaviour() as items 75 and 76. --extra-text appends inputs to the corpus, for example the project's own
regression-test input; runs that use it must say so. Writes one line in the mutants.jsonl format (id 0), so
tw_evaluate.py, controls.py and tw_shapes.py can be used unchanged."""
import json, os, sys, types
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, ROOT)
from cla_harness.io import load_model
from cla_harness.core import valid_configurations

args = sys.argv[1:]
opt = lambda k: args[args.index(k) + 1]
subject = opt("--subject")
extras = [args[i + 1] for i, a in enumerate(args) if a == "--extra-text"]
if subject == "tw":
    import tw_model as model_mod
    model_path = os.path.join(ROOT, "docs/item75/textwrap_model.json")
else:
    import cp_model as model_mod
    model_path = os.path.join(ROOT, "docs/item76/configparser_model.json")
model_mod.CORPUS = list(model_mod.CORPUS) + extras

def load(path, name):
    mod = types.ModuleType(name)
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), mod.__dict__)
    return mod

buggy, fixed = load(opt("--buggy"), "buggy"), load(opt("--fixed"), "fixed")
configs = valid_configurations(*load_model(model_path))
failing = [k for k, c in enumerate(configs) if model_mod.behaviour(buggy, c) != model_mod.behaviour(fixed, c)]
row = {"id": 0, "operator": "real", "line": None, "status": "ok", "n_fail": len(failing), "failing": failing,
       "extra_texts": extras}
with open(opt("--out"), "w") as f:
    f.write(json.dumps(row) + "\n")
print(json.dumps({"subject": subject, "configs": len(configs), "n_fail": len(failing), "extra_texts": len(extras)}))
