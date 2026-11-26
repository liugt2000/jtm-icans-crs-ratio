import csv
import time

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import splu

t0 = time.time()
edges = set()
with open("data/omnipath_interactions_20261116.tsv", encoding="utf-8", errors="replace") as fh:
    for row in csv.DictReader(fh, delimiter="\t"):
        if row["entity_type_source"] != "protein" or row["entity_type_target"] != "protein":
            continue
        a, b = row["source_genesymbol"].strip(), row["target_genesymbol"].strip()
        if a and b and a != b:
            edges.add((a, b))
            edges.add((b, a))
print("load", round(time.time() - t0, 2), len(edges))

nodes = sorted({x for e in edges for x in e})
idx = {n: i for i, n in enumerate(nodes)}
A = sp.coo_matrix((np.ones(len(edges)),
                   ([idx[a] for a, b in edges], [idx[b] for a, b in edges])),
                  shape=(len(nodes),) * 2)
A = sp.csr_matrix(A)
A.data[:] = 1.0
deg = np.asarray(A.sum(1)).ravel()
WT = (sp.diags(1.0 / deg) @ A).T.tocsr()

t0 = time.time()
M = (sp.identity(A.shape[0], format="lil") - 0.7 * WT).tocsr()
M = M.astype(np.float64)
print("build", round(time.time() - t0, 2), M.nnz)
t0 = time.time()
lu = splu(M.tocoo().tocsr().tocsc() if False else M)
print("factor", round(time.time() - t0, 2))

p0 = np.zeros(A.shape[0])
p0[:30] = 1 / 30
t0 = time.time()
for _ in range(50):
    p = lu.solve(p0)
print("50 solves", round(time.time() - t0, 3))
