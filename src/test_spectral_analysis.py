from math import sqrt

import numpy as np
from scipy.sparse import csr_matrix

from spectral_analysis import (
    build_sparse_adjacency_matrix,
    build_combinatorial_laplacian,
    build_symmetric_normalized_laplacian,
)

from spectral_eigen_analysis import (
    compute_smallest_eigenpairs,
    reordering,
    count_zero_eigenvalues,
    eigenpair_residuals,
    extract_fiedler_pair,
)


AdjacencyList = list[set[int]]


def test_chain_graph() -> None:
    """
    Test graph:

        0 -- 1 -- 2
    """
    adjacency: AdjacencyList = [
        {1},
        {0, 2},
        {1},
    ]

    A: csr_matrix = build_sparse_adjacency_matrix(adjacency)
    L: csr_matrix = build_combinatorial_laplacian(adjacency)
    L_sym: csr_matrix = build_symmetric_normalized_laplacian(adjacency)

    expected_A: np.ndarray = np.array(
        [
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
        ]
    )

    expected_L: np.ndarray = np.array(
        [
            [1.0, -1.0, 0.0],
            [-1.0, 2.0, -1.0],
            [0.0, -1.0, 1.0],
        ]
    )

    expected_L_sym: np.ndarray = np.array(
        [
            [1.0, -1.0 / sqrt(2.0), 0.0],
            [-1.0 / sqrt(2.0), 1.0, -1.0 / sqrt(2.0)],
            [0.0, -1.0 / sqrt(2.0), 1.0],
        ]
    )

    print("=== Chain graph ===")

    print("A:")
    print(A.toarray())

    print("L:")
    print(L.toarray())

    print("L_sym:")
    print(L_sym.toarray())

    assert A.shape == (3, 3)
    assert L.shape == (3, 3)
    assert L_sym.shape == (3, 3)

    assert A.nnz == 4

    assert np.allclose(A.toarray(), expected_A)
    assert np.allclose(L.toarray(), expected_L)
    assert np.allclose(L_sym.toarray(), expected_L_sym)

    assert np.allclose(A.toarray(), A.T.toarray())
    assert np.allclose(L.toarray(), L.T.toarray())
    assert np.allclose(L_sym.toarray(), L_sym.T.toarray())

    ones: np.ndarray = np.ones(3)
    assert np.allclose(L @ ones, np.zeros(3))

    print("Chain graph test passed.\n")


def test_isolated_vertex() -> None:
    """
    Test graph:

        0 -- 1      2

    Vertex 2 is isolated.
    """
    adjacency: AdjacencyList = [
        {1},
        {0},
        set(),
    ]

    A: csr_matrix = build_sparse_adjacency_matrix(adjacency)
    L: csr_matrix = build_combinatorial_laplacian(adjacency)
    L_sym: csr_matrix = build_symmetric_normalized_laplacian(adjacency)

    expected_A: np.ndarray = np.array(
        [
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
        ]
    )

    expected_L: np.ndarray = np.array(
        [
            [1.0, -1.0, 0.0],
            [-1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],
        ]
    )

    expected_L_sym: np.ndarray = np.array(
        [
            [1.0, -1.0, 0.0],
            [-1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],
        ]
    )

    print("=== Graph with isolated vertex ===")

    print("A:")
    print(A.toarray())

    print("L:")
    print(L.toarray())

    print("L_sym:")
    print(L_sym.toarray())

    assert A.nnz == 2

    assert np.allclose(A.toarray(), expected_A)
    assert np.allclose(L.toarray(), expected_L)
    assert np.allclose(L_sym.toarray(), expected_L_sym)

    assert np.allclose(L_sym.toarray()[2, :], np.zeros(3))
    assert np.allclose(L_sym.toarray()[:, 2], np.zeros(3))

    ones: np.ndarray = np.ones(3)
    assert np.allclose(L @ ones, np.zeros(3))

    print("Isolated vertex test passed.\n")


def test_chain_graph_eigenpairs() -> None:
    """
    Stage 3 eigenpair test:

        0 -- 1 -- 2

    Connected graph:
    zero eigenvalue multiplicity should be 1.
    """
    adjacency: AdjacencyList = [
        {1},
        {0, 2},
        {1},
    ]

    L_sym: csr_matrix = build_symmetric_normalized_laplacian(adjacency)

    eigenpairs: tuple[np.ndarray, np.ndarray] = compute_smallest_eigenpairs(
        L_sym,
        k=2,
    )

    eigenpairs = reordering(eigenpairs)

    eigenvalues, eigenvectors = eigenpairs

    residuals: list[float] = eigenpair_residuals(
        L_sym,
        eigenpairs,
    )

    print("=== Chain graph eigenpairs ===")

    print("Eigenvalues:")
    print(eigenvalues)

    print("Eigenpair residuals:")
    print(residuals)

    assert eigenvalues.shape == (2,)
    assert eigenvectors.shape == (3, 2)

    assert eigenvalues[0] <= eigenvalues[1]

    assert count_zero_eigenvalues(eigenpairs) == 1

    for residual in residuals:
        assert residual < 1e-8

    print("Chain graph eigenpair test passed.\n")


def test_disconnected_graph_eigenpairs() -> None:
    """
    Stage 3 zero eigenvalue test:

        0 -- 1      2 -- 3

    Two connected components:
    zero eigenvalue multiplicity should be 2.
    """
    adjacency: AdjacencyList = [
        {1},
        {0},
        {3},
        {2},
    ]

    L_sym: csr_matrix = build_symmetric_normalized_laplacian(adjacency)

    eigenpairs: tuple[np.ndarray, np.ndarray] = compute_smallest_eigenpairs(
        L_sym,
        k=3,
    )

    eigenpairs = reordering(eigenpairs)

    eigenvalues, eigenvectors = eigenpairs

    residuals: list[float] = eigenpair_residuals(
        L_sym,
        eigenpairs,
    )

    print("=== Disconnected graph eigenpairs ===")

    print("Eigenvalues:")
    print(eigenvalues)

    print("Eigenpair residuals:")
    print(residuals)

    assert eigenvalues.shape == (3,)
    assert eigenvectors.shape == (4, 3)

    assert eigenvalues[0] <= eigenvalues[1] <= eigenvalues[2]

    assert count_zero_eigenvalues(eigenpairs) == 2

    for residual in residuals:
        assert residual < 1e-8

    print("Disconnected graph eigenpair test passed.\n")


def test_extract_fiedler_pair_connected() -> None:
    """
    Test graph:

        0 -- 1 -- 2

    Connected graph:
    Fiedler value should be 1.
    """
    adjacency: AdjacencyList = [
        {1},
        {0, 2},
        {1},
    ]

    L_sym: csr_matrix = build_symmetric_normalized_laplacian(adjacency)

    eigenpairs: tuple[np.ndarray, np.ndarray] = compute_smallest_eigenpairs(
        L_sym,
        k=2,
    )

    eigenpairs = reordering(eigenpairs)

    fiedler_value, fiedler_vector = extract_fiedler_pair(eigenpairs)

    print("=== Fiedler pair: connected chain ===")

    print("Fiedler value:")
    print(fiedler_value)

    print("Fiedler vector:")
    print(fiedler_vector)

    assert abs(fiedler_value - 1.0) < 1e-8

    assert fiedler_vector.shape == (3,)

    residual: np.ndarray = (
        L_sym @ fiedler_vector
        - fiedler_value * fiedler_vector
    )

    acc: float = 0.0

    for e in residual:
        acc += e * e

    residual_norm: float = float(np.sqrt(acc))

    print("Fiedler residual:")
    print(residual_norm)

    assert residual_norm < 1e-8

    print("Connected Fiedler pair test passed.\n")


def test_extract_fiedler_pair_disconnected() -> None:
    """
    Test graph:

        0 -- 1      2 -- 3

    Disconnected graph:
    extract_fiedler_pair should reject it.
    """
    adjacency: AdjacencyList = [
        {1},
        {0},
        {3},
        {2},
    ]

    L_sym: csr_matrix = build_symmetric_normalized_laplacian(adjacency)

    eigenpairs: tuple[np.ndarray, np.ndarray] = compute_smallest_eigenpairs(
        L_sym,
        k=3,
    )

    eigenpairs = reordering(eigenpairs)

    print("=== Fiedler pair: disconnected graph ===")

    try:
        extract_fiedler_pair(eigenpairs)

    except ValueError:
        print("Disconnected graph correctly rejected.\n")
        return

    raise AssertionError(
        "Disconnected graph should not produce a Fiedler pair."
    )

def main() -> None:
    test_chain_graph()
    test_isolated_vertex()

    test_chain_graph_eigenpairs()
    test_disconnected_graph_eigenpairs()

    test_extract_fiedler_pair_connected()
    test_extract_fiedler_pair_disconnected()

    print("All Stage 2 and Stage 3 spectral tests passed.")
if __name__ == "__main__":
    main()