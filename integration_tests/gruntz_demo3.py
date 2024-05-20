from lpython import S, str
from sympy import Symbol, Pow, sin, oo, pi, E, Mul, Add

def mrv(e: S, x: S) -> list[S]:
    """
    Calculate the MRV set of the expression.

    Examples
    ========

    >>> mrv(log(x - log(x))/log(x), x)
    {x}

    """

    if e == x:
        list1: list[S] = [x]
        return list1
    if e.func == Mul or e.func == Add:
        a: S = e.args[0]
        b: S = e.args[1]
        ans1: list[S] = mrv(a, x)
        ans2: list[S] = mrv(b, x)
        return mrv_max(mrv(a, x), mrv(b, x), x)
    if e.func == Pow:
        base: S = e.args[0]
        list3: list[S] = mrv(base, x)
        return list3
    if e.is_Function:
        return reduce(lambda a, b: mrv_max(a, b, x), (mrv(a, x) for a in e.args))
    raise NotImplementedError(f"Can't calculate the MRV of {e}.")

def mrv_max(f: list[S], g: list[S], x: S) -> list[S]:
    """Compute the maximum of two MRV sets.

    Examples
    ========

    >>> mrv_max({log(x)}, {x**5}, x)
    {x**5}

    """

    if len(f) == 0:
        return g
    elif len(g) == 0:
        return f
    else:
        return f | g

def rewrite(e: S, x: S, w: S) -> S:
    """
    Rewrites the expression in terms of the MRV subexpression.

    Parameters
    ==========

    e : Expr
        an expression
    x : Symbol
        variable of the `e`
    w : Symbol
        The symbol which is going to be used for substitution in place
        of the MRV in `x` subexpression.

    Returns
    =======

    The rewritten expression

    Examples
    ========

    >>> rewrite(exp(x)*log(x), x, y)
    (log(x)/y, -x)

    """
    pass


def sign(e: S) -> S:
    """
    Returns the complex sign of an expression:

    Explanation
    ===========

    If the expression is real the sign will be:

        * $1$ if expression is positive
        * $0$ if expression is equal to zero
        * $-1$ if expression is negative
    """

    if e.is_positive:
        return S(1)
    elif e == S(0):
        return S(0)
    else:
        return S(-1)

def signinf(e: S, x : S) -> S:
    """
    Determine sign of the expression at the infinity.

    Returns
    =======

    {1, 0, -1}
        One or minus one, if `e > 0` or `e < 0` for `x` sufficiently
        large and zero if `e` is *constantly* zero for `x\to\infty`.

    """

    if not e.has(x):
        return sign(e)
    if e == x:
        return S(1)
    if e.func == Pow:
        base: S = e.args[0]
        if signinf(base, x) == S(1):
            return S(1)

def mrv_leadterm(e: S, x: S) -> list[S]:
    """
    Compute the leading term of the series.

    Returns
    =======

    tuple
        The leading term `c_0 w^{e_0}` of the series of `e` in terms
        of the most rapidly varying subexpression `w` in form of
        the pair ``(c0, e0)`` of Expr.

    Examples
    ========

    >>> leadterm(1/exp(-x + exp(-x)) - exp(x), x)
    (-1, 0)

    """

    #w = Dummy('w', real=True, positive=True)
    w: S = Symbol('w')
    #e = rewrite(e, x, w)
    coeff_exp_list: list[S] = [S(2), S(3)]
    #return e.leadterm(w)
    return coeff_exp_list

def limitinf(e: S, x: S) -> S:
    """
    Compute the limit of the expression at the infinity.

    Examples
    ========

    >>> limitinf(exp(x)*(exp(1/x - exp(-x)) - exp(1/x)), x)
    -1

    """

    if not e.has(x):
        return e
    
    coeff_exp_list: list[S] = mrv_leadterm(e, x)
    c0: S = coeff_exp_list[0]
    e0: S = coeff_exp_list[1]
    sig: S = signinf(e0, x)
    if sig == S(1):
        return S(0)
    if sig == S(-1):
        return signinf(c0, x) * oo
    if sig == S(0):
        return limitinf(c0, x)
    raise NotImplementedError(f'Result depends on the sign of {sig}.')

def gruntz(e: S, z: S, z0: S, dir: str ="+") -> S:
    """
    Compute the limit of e(z) at the point z0 using the Gruntz algorithm.

    Explanation
    ===========

    ``z0`` can be any expression, including oo and -oo.

    For ``dir="+"`` (default) it calculates the limit from the right
    (z->z0+) and for ``dir="-"`` the limit from the left (z->z0-). For infinite z0
    (oo or -oo), the dir argument does not matter.

    This algorithm is fully described in the module docstring in the gruntz.py
    file. It relies heavily on the series expansion. Most frequently, gruntz()
    is only used if the faster limit() function (which uses heuristics) fails.
    """

    e0: S
    if str(dir) == "-":
        e0 = e.subs(z, z0 - S(1)/z)
    elif str(dir) == "+":
        e0 = e.subs(z, z0 + S(1)/z)
    else:
        raise NotImplementedError("dir must be '+' or '-'")

    r: S = limitinf(e0, z)
    return r

# test
def test():
    x: S = Symbol('x')
    ans: S = gruntz(sin(x)/x, x, S(0), "+")
    print(ans)

test()