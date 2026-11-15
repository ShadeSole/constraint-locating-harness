"""Plan item 53: convert the Segall et al. models from the HHSA archive (Zenodo 10.5281/zenodo.581657,
folder segall_issta_11) into this repo's CASA loader format.
The archive's X_yue.cons files number (parameter, value) pairs from 1; load_casa_model numbers them from 0,
so every index is shifted down by one. A model without a .cons file gets an empty constraints file.
Usage: python3 scripts/item53_convert.py SRC_DIR OUT_DIR"""
import sys
from pathlib import Path
src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
for model in sorted(src.glob("*.model")):
    name = model.stem
    (out / f"{name}.model").write_text(model.read_text())
    cons = src / f"{name}_yue.cons"
    if not cons.exists():
        (out / f"{name}.constraints").write_text("")
        continue
    tokens = cons.read_text().split()
    res, pos = [tokens[0]], 1
    for _ in range(int(tokens[0])):
        k = int(tokens[pos]); res.append(tokens[pos]); pos += 1
        for _ in range(k):
            sign, idx = tokens[pos], int(tokens[pos + 1]); pos += 2
            if idx < 1:
                raise ValueError(f"{name}: index {idx} is not 1-based")
            res += [sign, str(idx - 1)]
    if pos != len(tokens):
        raise ValueError(f"{name}: unexpected extra content")
    (out / f"{name}.constraints").write_text(" ".join(res) + "\n")
    print(name, "converted")
