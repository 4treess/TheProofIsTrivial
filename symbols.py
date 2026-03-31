# all used operateors are defined below so the symbols used may be changed in the future
# no symbols should be hard-coded
_add = '+'
_subt = '-'
_neg = '~'
_pos = '+'
_mul = '*'
_div = '/'
_not = '⌐'
_and = '⋀'
_or = '⋁'
_dvds = '|'
_cngrnt = '≡'
_mod = '%'
_if = '→'
_iff = '↔'
_lbr = '('
_rbr = ')'
_eq = '='
_neq = '≠'
_lt = '<'
_gt = '>'
_ge = '≥'
_le = '≤'

# raw string containing all defined symbols for Operators and implications
validOps = r'' + _add + '\\' + _subt + _neg + _pos + _mul + _div + _not + _and + _or + _dvds + _cngrnt + _mod + _lbr + _rbr + _eq + _neq + _lt + _gt + _ge + _le
validIfs = r'' + _if + _iff
unaryOps = [_not, _neg]

# OPERATOR PRECEDENCE
precedence = {
#    _lbr: 9, _rbr: 9,
    _not: 8,
    _neg: 7, _pos: 7,
    _mul: 6, _div: 6, _mod: 6,
    _add: 5, _subt: 5,
    _dvds: 4, _cngrnt: 4, _eq: 4,
    _and: 3,
    _or: 2,
    _if: 1,
    _iff: 0
}

# OPERATOR ASSOCIATIVITY
#   l = LEFT ie 5 + 4 + 3 calculate left to right
#   r = RIGHT
#   n = NONE
associativity = {
    _add: 'l',
    _subt: 'l',
    _neg: 'r',
    _pos: 'r',
    _mul: 'l',
    _div: 'l',
    _not: 'r',
    _and: 'l',
    _or: 'l',
    _dvds: 'n',
    _cngrnt: 'n',
    _mod: 'l',
    _if: 'r',
    _iff: 'r',
    _mod: 'l'
}