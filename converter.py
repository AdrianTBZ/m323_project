"""
Markdown to HTML Converter - M323 Mini Projekt

FP concepts:
- Pure Functions:    parse_line, parse_inline, render_line, convert
- Immutable data:    tuples instead of lists
- Recursion:         parse_inline_recursive
- Pattern Matching:  match/case in parse_line and render_line
- Map / Filter:      used in convert()
- HOF:               apply_rule() passed into functools.reduce
- Side-Effects:      isolated in read_file, write_file, run
"""

import re
import functools


# --- Side-Effects (I/O only here) ---

def read_file(path, encoding="utf-8"):
    with open(path, "r", encoding=encoding) as f:
        return f.read()

def write_file(path, content, encoding="utf-8"):
    with open(path, "w", encoding=encoding) as f:
        f.write(content)


# --- Inline formatting (HOF + reduce) ---

INLINE_RULES = (
    (r"!\[([^\]]*)\]\(([^)]+)\)", r'<img alt="\1" src="\2">'),
    (r"\[([^\]]+)\]\(([^)]+)\)",  r'<a href="\2">\1</a>'),
    (r"\*\*([^*]+)\*\*",          r"<strong>\1</strong>"),
    (r"\*([^*]+)\*",              r"<em>\1</em>"),
)

def apply_rule(text, rule):
    pattern, replacement = rule
    return re.sub(pattern, replacement, text)

def parse_inline(text):
    return functools.reduce(apply_rule, INLINE_RULES, text)


# --- Line parsing (pure, pattern matching) ---

def parse_line(line):
    match line:
        case s if re.match(r"^#{1,6} ", s):
            level = len(re.match(r"^(#+) ", s).group(1))
            return ("heading", level, s[level + 1:].strip())
        case s if re.match(r"^[-*+] ", s):
            return ("ul_item", s[2:].strip())
        case s if re.match(r"^\d+\. ", s):
            return ("ol_item", re.match(r"^\d+\. (.+)", s).group(1).strip())
        case "":
            return ("blank",)
        case _:
            return ("paragraph", line.strip())


# --- List grouping (pure, recursion) ---

def take_while(tokens, kind):
    i = 0
    while i < len(tokens) and tokens[i][0] == kind:
        i += 1
    return tokens[:i], tokens[i:]

def group_lists(tokens):
    if not tokens:
        return ()
    head, rest = tokens[0], tokens[1:]
    if head[0] == "ul_item":
        run, remainder = take_while(rest, "ul_item")
        return (("ul", (head[1],) + tuple(t[1] for t in run)),) + group_lists(remainder)
    if head[0] == "ol_item":
        run, remainder = take_while(rest, "ol_item")
        return (("ol", (head[1],) + tuple(t[1] for t in run)),) + group_lists(remainder)
    return (head,) + group_lists(rest)


# --- Rendering (pure, pattern matching) ---

def render_line(token):
    match token:
        case ("heading", level, text):
            return f"<h{level}>{parse_inline(text)}</h{level}>"
        case ("paragraph", text):
            return f"<p>{parse_inline(text)}</p>"
        case ("ul", items):
            lis = "".join(f"  <li>{parse_inline(i)}</li>\n" for i in items)
            return f"<ul>\n{lis}</ul>"
        case ("ol", items):
            lis = "".join(f"  <li>{parse_inline(i)}</li>\n" for i in items)
            return f"<ol>\n{lis}</ol>"
        case _:
            return ""

def build_html(body, css=None):
    style = f"  <style>\n{css}\n  </style>\n" if css else ""
    return f"<!DOCTYPE html>\n<html>\n<head>\n  <meta charset=\"UTF-8\">\n{style}</head>\n<body>\n{body}\n</body>\n</html>\n"


# --- Main pipeline (map + filter) ---

def convert(markdown, css=None):
    lines   = tuple(markdown.splitlines())
    tokens  = tuple(map(parse_line, lines))
    grouped = group_lists(tokens)
    parts   = tuple(map(render_line, grouped))
    body    = "\n".join(filter(lambda s: s, parts))
    return build_html(body, css)


# --- Entry point (side-effects here) ---

def run(input_path, output_path, css_path=None, input_encoding="utf-8", output_encoding="utf-8"):
    markdown = read_file(input_path, encoding=input_encoding)
    css      = read_file(css_path) if css_path else None
    html     = convert(markdown, css)
    write_file(output_path, html, encoding=output_encoding)
    print(f"Converted '{input_path}' -> '{output_path}'")