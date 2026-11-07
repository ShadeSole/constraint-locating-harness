"""Stage B (plan item 75): configuration model and oracle for Python's textwrap module (CPython 3.13 Lib/textwrap.py,
copied to docs/item75/textwrap_original.py). A test is one TextWrapper configuration run on every text in CORPUS;
it fails if wrap() or fill() output, or the exception raised, differs from the unmodified module."""
import json, os

PARAMS = {
    "width": ["5", "12", "30"],
    "expand_tabs": ["T", "F"],
    "replace_whitespace": ["T", "F"],
    "drop_whitespace": ["T", "F"],
    "break_long_words": ["T", "F"],
    "break_on_hyphens": ["T", "F"],
    "fix_sentence_endings": ["T", "F"],
    "max_lines": ["none", "1", "3"],
    "placeholder": ["long", "short"],
    "indent": ["none", "init", "sub", "both"],
}
PLACEHOLDER = {"long": " [...]", "short": " .."}
INDENT = {"none": ("", ""), "init": ("> ", ""), "sub": ("", "  "), "both": ("> ", "  ")}

CORPUS = [
    "The quick brown fox jumps over the lazy dog.  Then it rests. Mr. Smith agrees!",
    "Tabs\there\tand\tthere, with   multiple   spaces and a trailing space ",
    "A well-known, state-of-the-art, hyphen-heavy sentence about re-entrant e-mail.",
    "Supercalifragilisticexpialidocious antidisestablishmentarianism is long.",
    "Line one.\nLine two has\ttabs.\r\nLine three?  Yes!  Done.",
    "short",
    "   leading spaces and words that wrap across several lines of output text here   ",
]

def kwargs(cfg):
    ini, sub = INDENT[cfg["indent"]]
    return dict(width=int(cfg["width"]), expand_tabs=cfg["expand_tabs"] == "T", tabsize=4,
                replace_whitespace=cfg["replace_whitespace"] == "T", drop_whitespace=cfg["drop_whitespace"] == "T",
                break_long_words=cfg["break_long_words"] == "T", break_on_hyphens=cfg["break_on_hyphens"] == "T",
                fix_sentence_endings=cfg["fix_sentence_endings"] == "T",
                max_lines=None if cfg["max_lines"] == "none" else int(cfg["max_lines"]),
                placeholder=PLACEHOLDER[cfg["placeholder"]], initial_indent=ini, subsequent_indent=sub)

def behaviour(module, cfg):
    out = []
    for text in CORPUS:
        try:
            w = module.TextWrapper(**kwargs(cfg))
            out.append((tuple(w.wrap(text)), w.fill(text)))
        except Exception as e:  # a mutant may crash: that is a failure if the original does not
            out.append(("EXC", type(e).__name__))
    return out

def all_configs():
    keys = list(PARAMS)
    res = [{}]
    for k in keys:
        res = [dict(c, **{k: v}) for c in res for v in PARAMS[k]]
    return res

def write_model(path, original):
    """Forbidden combinations = configurations the ORIGINAL module rejects with ValueError, written as full
    assignments of the parameters involved in its validity rule (width, max_lines, placeholder, indent)."""
    forbidden = set()
    for c in all_configs():
        try:
            original.TextWrapper(**kwargs(c)).wrap(CORPUS[0])
        except ValueError:
            forbidden.add(tuple((k, c[k]) for k in ("width", "max_lines", "placeholder", "indent")))
    json.dump({"parameters": PARAMS, "forbidden": [dict(f) for f in sorted(forbidden)]}, open(path, "w"), indent=1)
    return len(forbidden)
