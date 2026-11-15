"""Stage B, second subject (plan item 76): configuration model and oracle for Python's configparser module
(CPython 3.13 Lib/configparser.py, copied to docs/item76/configparser_original.py). A test is one parser
configuration run on every text in CORPUS. It fails if the parsed sections and options, the value returned by get()
for every option (or the exception type it raises), the written output, or the exception raised by read_string()
differ from the unmodified module. configparser's constructor rejects no option combination, so the model is
unconstrained."""
import io, json

PARAMS = {
    "delimiters": ["eq_colon", "eq", "colon"],
    "comment_prefixes": ["hash_semi", "hash"],
    "inline_comment_prefixes": ["none", "semi", "hash"],
    "strict": ["T", "F"],
    "empty_lines_in_values": ["T", "F"],
    "allow_no_value": ["T", "F"],
    "interpolation": ["basic", "extended", "none"],
    "default_section": ["DEFAULT", "common"],
    "allow_unnamed_section": ["T", "F"],
    "optionxform": ["lower", "keep"],
}
DELIM = {"eq_colon": ("=", ":"), "eq": ("=",), "colon": (":",)}
COMMENT = {"hash_semi": ("#", ";"), "hash": ("#",)}
INLINE = {"none": None, "semi": (";",), "hash": ("#",)}

CORPUS = [
    "[server]\nhost = example.org\nport: 8080\n; comment\n# another\nName = Mixed Case ; trailing note\n",
    "[DEFAULT]\nbase = /srv\n[paths]\nroot = %(base)s/root\nlog = ${base}/log\nraw = 100%% sure\n",
    "[multi]\nkey = line one\n  line two\n\n  line four after blank\nother = x\n",
    "[dup]\na = 1\na = 2\n[dup]\nb = 3\n",
    "[flags]\nenable_feature\nverbose = yes\n# x = commented\n",
    "top = level value\n[after]\nk = v\n",
    "[common]\nshared = s\n[ref]\nuse = ${common:shared} and %(shared)s\nhash = a # b ; c\n",
]

def make(module, cfg):
    interp = {"basic": module.BasicInterpolation(), "extended": module.ExtendedInterpolation(), "none": None}
    p = module.ConfigParser(delimiters=DELIM[cfg["delimiters"]], comment_prefixes=COMMENT[cfg["comment_prefixes"]],
                            inline_comment_prefixes=INLINE[cfg["inline_comment_prefixes"]], strict=cfg["strict"] == "T",
                            empty_lines_in_values=cfg["empty_lines_in_values"] == "T",
                            allow_no_value=cfg["allow_no_value"] == "T", interpolation=interp[cfg["interpolation"]],
                            default_section=cfg["default_section"],
                            allow_unnamed_section=cfg["allow_unnamed_section"] == "T")
    if cfg["optionxform"] == "keep":
        p.optionxform = str
    return p

def behaviour(module, cfg):
    out = []
    for text in CORPUS:
        try:
            p = make(module, cfg)
            p.read_string(text)
            secs = []
            for s in p.sections():
                vals = []
                for o in p.options(s):
                    try:
                        vals.append((o, p.get(s, o)))
                    except Exception as e:
                        vals.append((o, "EXC:" + type(e).__name__))
                secs.append((repr(s), tuple(vals)))
            buf = io.StringIO()
            try:
                p.write(buf)
                written = buf.getvalue()
            except Exception as e:
                written = "EXC:" + type(e).__name__
            out.append((tuple(secs), written))
        except Exception as e:
            out.append(("EXC", type(e).__name__))
    return out

def write_model(path):
    json.dump({"parameters": PARAMS, "forbidden": []}, open(path, "w"), indent=1)
