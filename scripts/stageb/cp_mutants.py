"""Stage B (plan item 76): generate single-point mutants of configparser parser and interpolation classes and run each on every valid
configuration. Standard mutation operators, applied to every eligible node inside class TextWrapper:
  ROR  swap a comparison operator (< <=, > >=, == !=, is / is not, in / not in)
  LCR  swap and / or
  UOI  remove a 'not'
  NEG  negate the test of an if / while / conditional expression
  CRP  replace a small integer constant c by c+1 and by c-1
Usage: python3 -I scripts/stageb/tw_mutants.py OUT.jsonl [--limit N]
Writes one line per mutant: id, operator, line, failing (sorted indices into the valid-configuration list),
n_fail, status (ok / timeout / compile_error). Baseline is the unmodified docs/item76/configparser_original.py."""
import ast, json, sys, os, signal, types, copy
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, ROOT)
import cp_model as tw_model
from cla_harness.io import load_model
from cla_harness.core import valid_configurations

SRC = open(os.path.join(ROOT, "docs/item76/configparser_original.py")).read()
TARGET = {"RawConfigParser", "ConfigParser", "BasicInterpolation", "ExtendedInterpolation", "SectionProxy"}
SWAP = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
        ast.Is: ast.IsNot, ast.IsNot: ast.Is, ast.In: ast.NotIn, ast.NotIn: ast.In}

def sites(tree):
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in TARGET]
    out = []
    for node in (x for cls in classes for x in ast.walk(cls)):
        if isinstance(node, ast.Compare):
            for k, op in enumerate(node.ops):
                if type(op) in SWAP:
                    out.append(("ROR", node, k))
        elif isinstance(node, ast.BoolOp):
            out.append(("LCR", node, None))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            out.append(("UOI", node, None))
        if isinstance(node, (ast.If, ast.While, ast.IfExp)):
            out.append(("NEG", node, None))
        if isinstance(node, ast.Constant) and type(node.value) is int and abs(node.value) <= 4:
            out.append(("CRP+", node, None)); out.append(("CRP-", node, None))
    return out

def mutant_source(i):
    tree = ast.parse(SRC)
    op, node, k = sites(tree)[i]
    line = node.lineno
    if op == "ROR":
        node.ops[k] = SWAP[type(node.ops[k])]()
    elif op == "LCR":
        node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
    elif op == "UOI":
        # replace 'not X' by 'X': rewrite parent field via a NodeTransformer
        class T(ast.NodeTransformer):
            def visit_UnaryOp(self, n):
                self.generic_visit(n)
                return n.operand if n is node else n
        tree = T().visit(tree)
    elif op == "NEG":
        node.test = ast.UnaryOp(op=ast.Not(), operand=node.test)
    elif op == "CRP+":
        node.value += 1
    elif op == "CRP-":
        node.value -= 1
    return op, line, ast.unparse(ast.fix_missing_locations(tree))

def load(src, name):
    mod = types.ModuleType(name)
    exec(compile(src, name, "exec"), mod.__dict__)
    return mod

params, forb = load_model(os.path.join(ROOT, "docs/item76/configparser_model.json"))
CONFIGS = valid_configurations(params, forb)
ORIG = load(SRC, "tw_orig")
BASE = None

def init():
    global BASE
    BASE = [tw_model.behaviour(ORIG, c) for c in CONFIGS]

class Timeout(Exception):
    pass

def handler(signum, frame):
    raise Timeout()

def run(i):
    try:
        op, line, src = mutant_source(i)
        mod = load(src, f"tw_m{i}")
    except Exception as e:
        return {"id": i, "status": "compile_error", "error": type(e).__name__}
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(120)
    try:
        failing = [k for k, c in enumerate(CONFIGS) if tw_model.behaviour(mod, c) != BASE[k]]
        status = "ok"
    except Timeout:
        failing, status = [], "timeout"
    finally:
        signal.alarm(0)
    return {"id": i, "operator": op, "line": line, "status": status, "n_fail": len(failing), "failing": failing}

def one(i):
    """Run a single mutant in this process (used by the isolated runner below)."""
    init()
    print(json.dumps(run(i)), flush=True)

def isolated(out, n, done):
    """Each mutant in its own process with a 1 GB address-space cap and a 180 s wall-clock limit, 4 at a time.
    A mutant that exceeds either is recorded as status timeout or memory (some mutants loop forever and grow lists)."""
    import subprocess, resource
    from concurrent.futures import ThreadPoolExecutor
    def limit():
        resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
    def go(i):
        try:
            r = subprocess.run([sys.executable, "-I", os.path.abspath(__file__), "--one", str(i)], capture_output=True,
                               text=True, timeout=180, preexec_fn=limit)
            line = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
            return json.loads(line) if line else {"id": i, "status": "memory" if "MemoryError" in r.stderr else "crashed"}
        except subprocess.TimeoutExpired:
            return {"id": i, "status": "timeout", "n_fail": 0, "failing": []}
    with ThreadPoolExecutor(4) as ex, open(out, "a") as f:
        for r in ex.map(go, [i for i in range(n) if i not in done]):
            f.write(json.dumps(r) + "\n"); f.flush()

if __name__ == "__main__" and "--one" in sys.argv:
    one(int(sys.argv[sys.argv.index("--one") + 1]))
    sys.exit(0)

if __name__ == "__main__" and "--isolated" in sys.argv:
    out = sys.argv[1]
    n = len(sites(ast.parse(SRC)))
    done = {json.loads(l)["id"] for l in open(out)} if os.path.exists(out) else set()
    print(f"{n} mutants, {len(done)} already done", file=sys.stderr)
    isolated(out, n, done)
    sys.exit(0)

if __name__ == "__main__":
    out = sys.argv[1]
    n = len(sites(ast.parse(SRC)))
    if "--limit" in sys.argv:
        n = min(n, int(sys.argv[sys.argv.index("--limit") + 1]))
    print(f"{n} mutants, {len(CONFIGS)} valid configurations", file=sys.stderr)
    with Pool(4, initializer=init) as pool, open(out, "w") as f:
        for r in pool.imap_unordered(run, range(n)):
            f.write(json.dumps(r) + "\n"); f.flush()
