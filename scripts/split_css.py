#!/usr/bin/env python3
"""Split the monolithic stylesheet into base + one file per active theme.

Source of truth is ``styles/business_connect.src.css`` (the full monolith). This
writes the *served* files:

  osduo_business_connect/public/css/business_connect.css   (base, all pages)
  osduo_business_connect/public/css/theme-<name>.css        (loaded only on pages
                                                             using that theme)

Why it is safe:
  * A rule is moved into a theme file only when EVERY selector in its selector
    list is tokened to that one theme (.bc-template-<t>, .bc-hero-<t>, .bc-<t>-).
    Any selector list that touches no theme, or more than one, stays in base, so
    a shared rule can never be taken away from another theme.
  * Theme selectors (.bc-template-X / .bc-hero-X) are strictly MORE specific than
    the shared base selectors they refine, so loading base-then-theme preserves
    the cascade regardless of source-order across the two files.
  * The split is verified: base + all themes re-parse to exactly the original rule
    set (every selector/declaration present once), and nothing is emitted for a
    theme that references a different theme.

Comments are dropped from the generated files (the readable, commented source is
styles/business_connect.src.css). Re-run after editing the source.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SRC = os.path.join(ROOT, "styles", "business_connect.src.css")
OUTDIR = os.path.join(ROOT, "osduo_business_connect", "public", "css")

THEMES = {
    "modern": ["bc-template-modern", "bc-hero-modern", "bc-modern-"],
    "professional": ["bc-template-professional", "bc-hero-professional", "bc-prof-", "bc-hero-prof-"],
    "minimal": ["bc-template-minimal", "bc-hero-minimal", "bc-minimal-"],
    "classic": ["bc-template-classic", "bc-hero-classic", "bc-classic-"],
    "luxury": ["bc-template-luxury", "bc-hero-luxury", "bc-luxury-"],
    "creative": ["bc-template-creative", "bc-hero-creative", "bc-creative-"],
}

HEADER = "/* GENERATED — do not edit. Source: styles/business_connect.src.css\n   Regenerate: python3 scripts/split_css.py */\n"


def _skip_comment(s, i):
    if s[i : i + 2] == "/*":
        j = s.find("*/", i + 2)
        return (j + 2) if j != -1 else len(s)
    return i


def _match_block(s, open_i):
    """Given index of the '{' opening a block, return index just past its '}'."""
    depth = 0
    i = open_i
    while i < len(s):
        i = _skip_comment(s, i)
        if i >= len(s):
            break
        c = s[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced braces")


def parse(css):
    """Return a list of nodes: ('rule', selector, body) | ('atrule', prelude, children) | ('stmt', text)."""
    i = 0
    nodes = []
    n = len(css)
    while i < n:
        i = _skip_comment(css, i)
        while i < n and css[i].isspace():
            i += 1
            i = _skip_comment(css, i)
        if i >= n:
            break
        if css[i] == "@":
            # prelude up to '{' or ';'
            j = i
            while j < n and css[j] not in "{;":
                j += 1
            prelude = css[i:j].strip()
            if j >= n:
                break
            if css[j] == ";":
                nodes.append(("stmt", css[i : j + 1]))
                i = j + 1
            else:  # '{' block
                end = _match_block(css, j)
                children = parse(css[j + 1 : end - 1])
                nodes.append(("atrule", prelude, children))
                i = end
        else:
            # selector runs up to the next '{' (rule) or ';' (stray statement),
            # skipping comments; braces/parens are not part of a selector here.
            k = i
            while k < n:
                if css[k : k + 2] == "/*":
                    k = _skip_comment(css, k)
                    continue
                if css[k] in "{;":
                    break
                k += 1
            sel = css[i:k].strip()
            if k < n and css[k] == "{":
                end = _match_block(css, k)
                body = css[k + 1 : end - 1]
                nodes.append(("rule", sel, body.strip()))
                i = end
            else:
                nodes.append(("stmt", css[i : min(k + 1, n)].strip()))
                i = k + 1
    return nodes


def _selectors(sel):
    # split a selector list on commas not inside parens/brackets
    parts, depth, buf = [], 0, ""
    for ch in sel:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return [p for p in parts if p]


def classify(sel):
    hits = {t for t, toks in THEMES.items() if any(tok in sel for tok in toks)}
    # require EVERY selector to hit the same single theme; else base (conservative)
    if len(hits) != 1:
        return None
    theme = next(iter(hits))
    for one in _selectors(sel):
        if not any(tok in one for tok in THEMES[theme]):
            return None
    return theme


def _render(nodes, dest):
    """Render the nodes destined for `dest` ('base' or a theme name)."""
    out = []
    for node in nodes:
        kind = node[0]
        if kind == "rule":
            _, sel, body = node
            target = classify(sel)
            target = "base" if target is None else target
            if target == dest:
                out.append(f"{sel} {{\n{body}\n}}")
        elif kind == "stmt":
            if dest == "base":  # @charset/@import etc. are global
                out.append(node[1])
        elif kind == "atrule":
            _, prelude, children = node
            inner = _render(children, dest)
            if inner:
                out.append(f"{prelude} {{\n" + "\n\n".join(inner) + "\n}")
    return out


def _leaf_rules(nodes):
    leaves = []
    for node in nodes:
        if node[0] == "rule":
            leaves.append((node[1], node[2]))
        elif node[0] == "atrule":
            leaves.extend(_leaf_rules(node[2]))
    return leaves


def _norm(sel, body):
    norm_sel = " ".join(sel.split())
    decls = sorted(" ".join(d.split()) for d in re.split(r";(?![^()]*\))", body) if d.strip())
    return (norm_sel, tuple(decls))


def main():
    src = open(SRC).read()
    tree = parse(src)
    all_leaves = _leaf_rules(tree)

    outputs = {"base": _render(tree, "base")}
    for t in THEMES:
        outputs[t] = _render(tree, t)

    # ---- verification ----
    src_keys = sorted(_norm(s, b) for s, b in all_leaves)
    out_leaves = []
    for _dest, blocks in outputs.items():
        text = "\n\n".join(blocks)
        reparsed = _leaf_rules(parse(text))
        out_leaves.extend(reparsed)
    out_keys = sorted(_norm(s, b) for s, b in out_leaves)
    if src_keys != out_keys:
        missing = set(src_keys) - set(out_keys)
        extra = set(out_keys) - set(src_keys)
        sys.exit(
            f"COVERAGE FAIL: {len(missing)} missing, {len(extra)} extra\n"
            f"missing={list(missing)[:5]}\nextra={list(extra)[:5]}"
        )

    # no theme file may reference a different theme's tokens
    for t in THEMES:
        text = "\n".join(outputs[t])
        for other, toks in THEMES.items():
            if other == t:
                continue
            for tok in toks:
                pattern = rf"\b{re.escape(tok)}\b"
                # a shared 'bc-hero-' prefix collision is caught only via exact other-theme tokens
                if re.search(pattern, text):
                    sys.exit(f"theme-{t}.css references {tok} (from theme {other})")

    # ---- write ----
    def write(path, blocks):
        with open(path, "w") as f:
            f.write(HEADER + "\n\n".join(blocks).strip() + "\n")

    write(os.path.join(OUTDIR, "business_connect.css"), outputs["base"])
    counts = {"base": len(_leaf_rules(parse("\n".join(outputs["base"]))))}
    for t in THEMES:
        write(os.path.join(OUTDIR, f"theme-{t}.css"), outputs[t])
        counts[t] = len(_leaf_rules(parse("\n".join(outputs[t]))))
    total = sum(counts.values())
    print("original rules:", len(all_leaves), "| emitted:", total, "| verified equal")
    for k, v in counts.items():
        print(f"  {k:14} {v} rules")


if __name__ == "__main__":
    main()
