from complex_utils import (
    build_triangle_maximal_complexes,
    complete_to_edge_maximal,
    facets_to_inclusion_poset,
)
from dimension import sat_dimension
from functools import reduce
from itertools import combinations
from sage.all import Poset
from collections import defaultdict


def linext_to_relation(linext):
    return set(
        (linext[i], linext[j])
        for i in range(len(linext))
        for j in range(i + 1, len(linext))
    )


def log(msg, f):
    print(msg)
    f.write(msg + "\n")


# === Main Execution ===

output_path = "triangle_system_results.txt"
n = 9

with open(output_path, "w") as log_file:
    log(f"\n===== Edge-Maximal Linear Triangle Systems on {n} Vertices =====", log_file)

    vertices = list(range(1, n + 1))

    triangle_maximal = build_triangle_maximal_complexes(vertices)
    edge_maximal_systems = complete_to_edge_maximal(triangle_maximal, vertices)

    log(f"Total triangle-maximal systems: {len(triangle_maximal)}", log_file)
    log(f"Total edge-maximal systems: {len(edge_maximal_systems)}\n", log_file)

    all_verifications_passed = True
    high_dimension_systems = []

    for idx, (triangles, bare_edges) in enumerate(edge_maximal_systems, 1):
        log(f"System {idx}:", log_file)

        log(f"  Triangles: {sorted([tuple(sorted(t)) for t in triangles])}", log_file)
        log(f"  Bare Edges: {sorted([tuple(sorted(e)) for e in bare_edges])}", log_file)

        # Combine all facets (triangles + bare edges)
        facets = triangles + bare_edges

        try:
            P = facets_to_inclusion_poset(facets)
            dim, realizer = sat_dimension(P, certificate=True)
            log(f"  Dimension: {dim}", log_file)
            log("  Realizer:", log_file)
            for linext in realizer:
                readable = [sorted(list(e)) for e in linext]
                log(f"    {readable}", log_file)

            if dim > 4:
                high_dimension_systems.append(idx)

            # Verification step
            relations = [linext_to_relation(le) for le in realizer]
            intersection_relation = reduce(set.intersection, relations)

            reconstructed_poset = Poset(
                (list(P), intersection_relation), cover_relations=False
            )

            if reconstructed_poset == P:
                log("Verification passed!", log_file)
            else:
                log("Verification failed!", log_file)
                all_verifications_passed = False

            log("", log_file)
            log("-" * 50, log_file)
            log("", log_file)

        except Exception as e:
            log(f"  ❌ ERROR: {e}", log_file)

    if all_verifications_passed:
        log("All Verifications passed!", log_file)
    else:
        log("Some Verifications failed!", log_file)

    log("High Dimension Systems (dimension > 4):", log_file)
    for high_dim_idx in high_dimension_systems:
        log(f"  System {high_dim_idx}", log_file)

