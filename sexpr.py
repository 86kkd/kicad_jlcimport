"""S-expression builder for KiCad file output."""
from typing import Any, List, Union


class SExpr:
    """Builder for KiCad S-expression format."""

    def __init__(self, name: str):
        self.name = name
        self.items: List[Union[str, float, int, 'SExpr']] = []

    def add(self, *args: Any) -> 'SExpr':
        """Add raw items (strings, numbers, or nested SExpr)."""
        for arg in args:
            self.items.append(arg)
        return self

    def child(self, name: str) -> 'SExpr':
        """Create and add a child S-expression, returning it."""
        child = SExpr(name)
        self.items.append(child)
        return child

    def render(self, indent: int = 0) -> str:
        """Render to string with proper formatting."""
        parts = [f"({self.name}"]
        inline_items = []
        block_children = []

        for item in self.items:
            if isinstance(item, SExpr):
                rendered = item.render(indent + 1)
                if "\n" in rendered or len(rendered) > 80:
                    block_children.append(rendered)
                else:
                    inline_items.append(rendered)
            elif isinstance(item, float):
                inline_items.append(_format_float(item))
            elif isinstance(item, int):
                inline_items.append(str(item))
            elif isinstance(item, str):
                inline_items.append(_quote_if_needed(item))
            else:
                inline_items.append(str(item))

        if inline_items:
            parts.append(" " + " ".join(inline_items))

        if block_children:
            prefix = "  " * (indent + 1)
            parts.append("\n")
            for child in block_children:
                parts.append(prefix + child + "\n")
            parts.append("  " * indent + ")")
        else:
            parts.append(")")

        return "".join(parts)


def _format_float(value: float) -> str:
    """Format float with appropriate precision, stripping trailing zeros."""
    if value == int(value) and abs(value) < 1e10:
        return f"{int(value)}"
    formatted = f"{value:.6f}".rstrip("0").rstrip(".")
    return formatted


def _quote_if_needed(s: str) -> str:
    """Quote strings that contain spaces or special chars."""
    if not s:
        return '""'
    needs_quote = any(c in s for c in ' \t\n"()') or s[0].isdigit()
    if needs_quote:
        return f'"{s}"'
    return s


def node(name: str, *args: Any) -> SExpr:
    """Create an S-expression node with initial items."""
    s = SExpr(name)
    for arg in args:
        if isinstance(arg, SExpr):
            s.items.append(arg)
        else:
            s.items.append(arg)
    return s
