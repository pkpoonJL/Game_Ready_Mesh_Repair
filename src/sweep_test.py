import numpy as np
from spectral_analysis import build_symmetric_normalized_laplacian
from spectral_eigen_analysis import (
    compute_smallest_eigenpairs,
    reordering,
    extract_fiedler_pair,
)

from spectral_sweep_analysis import (
    build_fiedler_ordering,
    generate_sweep_candidates,
    compute_candidate_conductance,
    find_best_sweep_cut,
    extract_cut_edges,
)


def test_stage4_weak_bridge() -> None:
    """
    Graph:

        0
       / \
      1---2
          |
          3
         / \
        4---5

    Expected weak bridge:
        (2, 3)
    """

    adjacency: list[set[int]] = [
        {1, 2},        # 0
        {0, 2},        # 1
        {0, 1, 3},     # 2
        {2, 4, 5},     # 3
        {3, 5},        # 4
        {3, 4},        # 5
    ]

    print("=== Stage 4 weak bridge test ===")

    # Step 1: build normalized Laplacian
    L_sym = build_symmetric_normalized_laplacian(adjacency)

    # Step 2: compute low eigenpairs
    eigenpairs = compute_smallest_eigenpairs(
        L_sym,
        k=3,
    )

    eigenpairs = reordering(eigenpairs)

    print("Eigenvalues:")
    print(eigenpairs[0])

    # Step 3: extract Fiedler pair
    fiedler_value, fiedler_vector = extract_fiedler_pair(eigenpairs)

    print("\nFiedler value:")
    print(fiedler_value)

    print("Fiedler vector:")
    print(fiedler_vector)

    # Step 4: build Fiedler ordering
    ordering: list[int] = build_fiedler_ordering(fiedler_vector)

    print("\nFiedler ordering:")
    print(ordering)

    # Step 5: generate sweep candidates
    candidates: list[set[int]] = generate_sweep_candidates(ordering)

    print("\nSweep candidates:")

    for candidate in candidates:
        phi: float = compute_candidate_conductance(
            candidate,
            adjacency,
        )

        print(
            candidate,
            "conductance =",
            phi,
        )

    # Step 6: find best sweep cut
    best_candidate, best_phi = find_best_sweep_cut(
        candidates,
        adjacency,
    )

    print("\nBest candidate:")
    print(best_candidate)

    print("Best conductance:")
    print(best_phi)

    # Step 7: extract cut edges
    cut_edges: list[tuple[int, int]] = extract_cut_edges(
        best_candidate,
        adjacency,
    )

    print("Cut edges:")
    print(cut_edges)

    # The graph should be separated into:
    # {0,1,2} and {3,4,5}

    expected_left: set[int] = {0, 1, 2}
    expected_right: set[int] = {3, 4, 5}

    all_vertices: set[int] = set(range(6))

    complement: set[int] = all_vertices - best_candidate

    assert (
        best_candidate == expected_left
        and complement == expected_right
    ) or (
        best_candidate == expected_right
        and complement == expected_left
    )

    # Depending on Fiedler vector sign,
    # the cut edge can be represented as (2,3) or (3,2).

    assert len(cut_edges) == 1

    u, v = cut_edges[0]

    assert {u, v} == {2, 3}

    print("\nStage 4 weak bridge test passed.")


if __name__ == "__main__":
    test_stage4_weak_bridge()