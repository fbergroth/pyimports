import ast
from collections import namedtuple
from token import DEDENT, INDENT, NEWLINE, NAME
from tokenize import tokenize, ENCODING, NL
from keyword import iskeyword

_Token = namedtuple('_Token', 'type string')


def _linewise_tokens(readline):
    level = 0
    tokens = []
    for _token in tokenize(readline):
        token = _Token(_token[0], _token[1])
        if token.type == INDENT:
            level += 1
        elif token.type == DEDENT:
            level -= 1
        elif token.type in (ENCODING, NL) and not tokens:  # strip preceding NLs
            continue
        elif level == 0:
            tokens.append(token)
            if token.type == NEWLINE:
                yield tokens
                tokens = []

    # In case source does not end with a newline
    if tokens:
        yield tokens


def _parse_names(tokens, include_imports):
    if tokens[0].type != NAME:
        return []

    name = tokens[0].string
    if name in ('def', 'class') and \
       len(tokens) >= 2 and tokens[1].type == NAME:
        return [tokens[1].string]

    # TODO: handle star imports
    if name in ('from', 'import') and include_imports:
        source = ' '.join(t.string for t in tokens)
        node = ast.parse(source).body[0]
        return [n.asname or n.name.split('.')[0]
                for n in node.names]

    if not iskeyword(name) and not name.startswith('_'):
        return [name]

    return []


def extract_names(readline, include_imports):
    return {name
            for tokens in _linewise_tokens(readline)
            for name in _parse_names(tokens, include_imports)}
