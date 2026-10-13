"""Load a YAML file: PyYAML when it is installed, else a parser for the subset specs.yaml uses
(nested mappings, lists of scalars or mappings, '...' and "..." strings, # comments)."""
import re


def load(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        import yaml
    except ImportError:
        return parse(text)
    return yaml.safe_load(text)


def parse(text):
    lines = []
    for raw in text.splitlines():
        stripped = _strip_comment(raw).rstrip()
        if stripped.strip():
            lines.append((len(stripped) - len(stripped.lstrip()), stripped.strip()))
    value, _ = _block(lines, 0, lines[0][0])
    return value


def _strip_comment(line):
    quote = None
    for i, ch in enumerate(line):
        if quote:
            quote = None if ch == quote else quote
        elif ch in "'\"":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] == " "):
            return line[:i]
    return line


def _block(lines, i, indent):
    if lines[i][1].startswith("- "):
        return _list(lines, i, indent)
    return _mapping(lines, i, indent)


def _list(lines, i, indent):
    items = []
    while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
        # "- key: v" becomes a mapping whose keys sit two columns right of the dash
        lines[i] = (indent + 2, lines[i][1][2:])
        if re.match(r"[\w.-]+:(\s|$)", lines[i][1]):
            item, i = _mapping(lines, i, indent + 2)
        else:
            item, i = _scalar(lines[i][1]), i + 1
        items.append(item)
    return items, i


def _mapping(lines, i, indent):
    result = {}
    while i < len(lines) and lines[i][0] == indent:
        key, _, rest = lines[i][1].partition(":")
        rest = rest.strip()
        i += 1
        if rest:
            result[key] = _scalar(rest)
        elif i < len(lines) and (lines[i][0] > indent or lines[i][1].startswith("- ") and lines[i][0] == indent):
            result[key], i = _block(lines, i, lines[i][0])
        else:
            result[key] = None
    return result, i


def _scalar(text):
    if text[0] == "'" and text[-1] == "'":
        return text[1:-1].replace("''", "'")
    if text[0] == '"' and text[-1] == '"':
        return text[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return {"null": None, "~": None, "true": True, "false": False}.get(text, text)
