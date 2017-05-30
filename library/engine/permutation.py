import string

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