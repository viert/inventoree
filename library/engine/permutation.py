import string


class InvalidPattern(Exception):
    pass

lw = list(string.ascii_lowercase)
up = list(string.ascii_uppercase)
nums = list(string.digits)


def succ(s):
    """Ruby String.succ implementation"""
    def get_alphabeth(sym):
        if sym.isupper(): return up
        if sym.islower(): return lw
        if sym.isdigit(): return nums
        return None

    def symbol_succ(sym):
        """Returns the next symbol in alphabeth, the carry flag and the alphabeth"""
        alphabeth = get_alphabeth(sym)
        if alphabeth is None:
            return None, None, None
        i = alphabeth.index(sym) + 1
        if i == len(alphabeth):
            carry = True
            i = 0
        else:
            carry = False
        return alphabeth[i], carry, alphabeth

    sym_list = list(s)[::-1]
    if len(sym_list) == 0:
        return ""
    i = 0
    while True:
        sym = sym_list[i]

        new_sym, carry, current_alphabeth = symbol_succ(sym)
        if new_sym is None:
            raise ValueError("Wrong alphabeth")

        sym_list[i] = new_sym
        if not carry:
            break
        i += 1
        if len(sym_list) == i:
            if current_alphabeth is nums:
                sym_list.append(current_alphabeth[1])
            else:
                sym_list.append(current_alphabeth[0])
            break

    return "".join(sym_list[::-1])


def sequence(fr, to, exclude=False):
    """
    Ruby-like string range generator
    ================================
    Ruby's 'a0'..'e4' equals to sequence('a0', 'e4')
    use @exclude parameter to exclude the last element (@to) from the generated sequence
    """
    while fr is not None and fr != to and len(fr) <= len(to):
        yield fr
        fr = succ(fr)
    if fr == to and not exclude:
        yield fr


def expand_single_pattern(pattern):
    import re
    single_expr = re.compile('([0-9a-zA-Z]+)\-([0-9a-zA-Z]+)')

    if pattern.startswith('[') and pattern.endswith(']'):
        pattern = pattern[1:-1]

    tokens = pattern.split(',')
    for token in tokens:
        corners = single_expr.search(token)
        if corners is None:
            yield token
        else:
            for item in sequence(*corners.groups()):
                yield item


def get_braces_indices(pattern):
    stack = list()
    indices = []
    current_index = []
    for ind, sym in enumerate(pattern):
        if sym == '[':
            stack.append(True)
            current_index.append(ind)
        elif sym == ']':
            try:
                stack.pop()
            except IndexError:
                raise InvalidPattern('Closing brace without opening one')
            current_index.append(ind)
        if len(current_index) == 2:
            if len(stack) != 0:
                raise InvalidPattern('Nested patterns are not allowed')
            indices.append(current_index)
            current_index = []
    if len(stack) > 0:
        raise InvalidPattern('Closing brace is absent')
    return indices


def expand_pattern(pattern):
    indices = get_braces_indices(pattern)
    if len(indices) == 0:
        yield pattern
        return
    fr, to = indices[0]
    for token in expand_single_pattern(pattern[fr+1:to]):
        for result in expand_pattern(pattern[:fr] + token + pattern[to+1:]):
            yield result


def expand_pattern_with_vars(pattern, vars=[]):
    indices = get_braces_indices(pattern)
    if len(indices) == 0:
        yield pattern, [pattern] + vars
        return
    fr, to = indices[0]
    for token in expand_single_pattern(pattern[fr+1:to]):
        for result in expand_pattern_with_vars(pattern[:fr] + token + pattern[to+1:], vars + [token]):
            yield result


def apply_vars(pattern, vars):
    for i, v in enumerate(vars):
        pattern = pattern.replace("$%d" % i, v)
    return pattern
