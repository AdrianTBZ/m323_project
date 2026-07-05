# M323 Mini Projekt — Static Site Generator

Markdown → HTML converter implemented in Python using functional programming principles.

## Usage

```bash
# Basic conversion
python main.py example.md output.html
```

## Functional Programming Concepts

| Concept | Where in code|
|---|---|
| Pure Functions | `parse_line`, `parse_inline`, `render_line`, `convert` — no side effects |
| Immutable Data | tuples used everywhere instead of lists |
| Recursion | `group_lists` calls itself on the remaining tokens |
| Pattern Matching | `match/case` in `parse_line` and `render_line` |
| Map / Filter | `map(parse_line, lines)`, `map(render_line, grouped)`, `filter(...)` in `convert` |
| Higher-Order Functions | `apply_rule` is passed into `functools.reduce` over `INLINE_RULES` |
| Isolated Side-Effects | only `read_file`, `write_file`, and `run` touch I/O |

## Project Structure

```
markdown_html/
├── converter.py   # Core logic (pure functions + isolated I/O)
├── main.py        # CLI entry point
├── tests.py       # Unit tests
├── example.md     # Demo Markdown file
├── style.css      # Demo CSS
└── README.md      # This file
```

---

## AI Usage Documentation

*(Required by assignment AI-Guidelines)*

| Prompt used | Model |
|---|---|
| Asked to write pytest tests covering all grading criteria | claude-sonnet-4-6 |
| Asked to write a example.md | claude-sonnet-4-6 |
| Asked to write README.md | claude-sonnet-4-6 |
| Made sections in converter.py | claude-sonnet-4-6 |