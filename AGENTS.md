# AGENTS.md

## Docstrings

Docstrings use reStructuredText (reST), the format Sphinx's autodoc expects.
Follow these conventions when writing or editing docstrings in this project:

- Wrap all docstrings in triple double-quotes (`"""`).
- Start with a single-line summary in the imperative mood (e.g. "Get all
  stations." not "Gets all stations." or "This function gets...").
- For exceptions, phrase the summary as "Raised when ...".
- Leave a blank line between the summary and any field list that follows.
- Document parameters, return values, and exceptions using reST field lists:
  - `:param name: description` — one per parameter, in signature order.
  - `:type name: type` — only needed when the type isn't already obvious
    from a type annotation Sphinx can resolve; include it for consistency
    in this codebase.
  - `:returns: description`
  - `:rtype: type`
  - `:raises ExceptionType: description of when it's raised` — one entry
    per exception type that can propagate out of the function.
- Document dataclass fields with `:ivar name: description` /
  `:vartype name: type` pairs in the class docstring, rather than
  commenting individual fields.
- Class-level constants (e.g. `Bixi.GRAPHQL_URL`) are documented the same
  way, with `:ivar:` / `:vartype:` in the class docstring.
- Keep descriptions concise — one or two sentences. Use `` `` for inline
  code (parameter names, literals) within prose.

### Example

```python
def rides(self, offset: int = 0) -> list[Ride]:
    """Get the current member's ride history.

    :param offset: Unix timestamp in milliseconds; only rides that
        started at or after this time are returned. Defaults to ``0``,
        which returns the full ride history.
    :type offset: int
    :returns: List of rides, most recent first.
    :rtype: list[Ride]
    :raises ValueError: If `offset` is negative.
    :raises BixiError: If the request to fetch rides fails.
    """
```

See [`bixi/bixi.py`](bixi/bixi.py) for more examples.
