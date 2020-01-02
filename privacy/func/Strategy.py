import numpy as np
from scipy import sparse


def gen_strategy_h2(dom_size): #hierarchical for 1D
    branching = 2
    strategy = build_hierarchical_sparse(dom_size, branching).tocsr()[1:]
    return strategy


# from ektelo/client/selection.py
def build_hierarchical_sparse(n, b):
    """Builds a sparsely represented (csr_matrix) hierarchical matrix
    with n columns and a branching factor of b.  Works even when n
    is not a power of b"""

    if n == 1:
        return sparse.csr_matrix([1.0])
    if n <= b:
        a = np.ones(n)
        b = sparse.identity(n, format='csr')
        return sparse.vstack([a, b])

    # n = mb + r where r < b
    # n = (m+1) r + m (b-r)
    # we need r hierarchical matrices with (m+1) cols
    # and (b-r) hierarchical matrices with m cols
    m, r = divmod(n, b)
    hier0 = build_hierarchical_sparse(m, b) # hierarchical matrix with m cols
    if r > 0:
        hier1 = build_hierarchical_sparse(m+1, b) # hierarchical matrix with (m+1) cols

    # sparse.hstack doesn't work when matrices have 0 cols
    def hstack(left, hier, right):
        if left.shape[1] > 0 and right.shape[1] > 0:
            return sparse.hstack([left, hier, right])
        elif left.shape[1] > 0:
            return sparse.hstack([left, hier])
        else:
            return sparse.hstack([hier, right])

    res = [np.ones(n)]
    for i in range(r):
        rows = hier1.shape[0]
        start = (m+1)*i
        end = start + m+1
        left = sparse.csr_matrix((rows, start))
        right = sparse.csr_matrix((rows, n-end))
        res.append(hstack(left, hier1, right))
    for i in range(r, b):
        # (m+1) r + m (b-r) = (m+1) r + m (b-i) + m (i-r)
        rows = hier0.shape[0]
        start = (m+1)*r + m*(i-r)
        end = start + m
        left = sparse.csr_matrix((rows, start))
        right = sparse.csr_matrix((rows, n-end))
        res.append(hstack(left, hier0, right))

    return sparse.vstack(res, format='csr')

