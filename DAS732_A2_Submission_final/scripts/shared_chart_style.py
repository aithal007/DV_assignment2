"""shared chart style and marching squares algorithm."""
from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

root = Path(__file__).resolve().parents[1]


# gaussian density on [0,100] with boundary reflections at 0 and 100
def reflected_kde(values: np.ndarray, grid: np.ndarray, bandwidth: float = 6.0) -> np.ndarray:
    def kernel(points):
        z = (grid[:, None] - points[None, :]) / bandwidth
        return np.exp(-0.5 * z * z).sum(axis=1)
    normalizer = len(values) * bandwidth * np.sqrt(2 * np.pi)
    return (kernel(values) + kernel(-values) + kernel(200 - values)) / normalizer


# 16-case marching squares lookup
_cases = {
    0: [], 1: [(3, 0)], 2: [(0, 1)], 3: [(3, 1)], 4: [(1, 2)],
    6: [(0, 2)], 7: [(3, 2)], 8: [(2, 3)], 9: [(0, 2)], 11: [(1, 2)],
    12: [(3, 1)], 13: [(0, 1)], 14: [(3, 0)], 15: [],
}
_edges = ((0, 1), (1, 2), (2, 3), (3, 0))


# compute line segments inside single grid cell
def cell_segments(
    xy: np.ndarray, values: np.ndarray, level: float
) -> list[np.ndarray]:
    values = np.asarray(values, dtype=float)
    if not np.isfinite(values).all():
        return []
    case = sum((int(v > level) << k) for k, v in enumerate(values))
    if case == 5:
        pairs = [(0, 1), (2, 3)] if values.mean() > level else [(3, 0), (1, 2)]
    elif case == 10:
        pairs = [(3, 0), (1, 2)] if values.mean() > level else [(0, 1), (2, 3)]
    else:
        pairs = _cases[case]

    def crossing(edge: int) -> np.ndarray:
        a, b = _edges[edge]
        fraction = (level - values[a]) / (values[b] - values[a])
        return xy[a] + fraction * (xy[b] - xy[a])

    return [
        np.array([crossing(a), crossing(b)])
        for a, b in pairs
        if np.linalg.norm(crossing(a) - crossing(b)) > 1e-12
    ]


# extract contour segments for 2d grid
def segments(
    x: np.ndarray, y: np.ndarray, z: np.ndarray, level: float
) -> np.ndarray:
    x, y, z = np.asarray(x), np.asarray(y), np.asarray(z)
    if z.shape != (len(y), len(x)):
        raise ValueError("grid shape mismatch")
    answer = []
    for i in range(len(y) - 1):
        for j in range(len(x) - 1):
            v = z[[i, i, i + 1, i + 1], [j, j + 1, j + 1, j]]
            xy = np.array(
                [[x[j], y[i]], [x[j + 1], y[i]], [x[j + 1], y[i + 1]], [x[j], y[i + 1]]]
            )
            answer.extend(cell_segments(xy, v, level))
    return np.array(answer).reshape(-1, 2, 2)


# canonical representation for segment set comparison
def canonical(lines: np.ndarray, decimals: int = 8) -> set:
    result: set = set()
    for line in lines:
        for a, b in zip(line[:-1], line[1:]):
            if np.linalg.norm(a - b) > 1e-12:
                result.add(
                    tuple(
                        sorted(
                            (tuple(np.round(a, decimals)), tuple(np.round(b, decimals)))
                        )
                    )
                )
    return result


# unit test for marching squares cases against contourpy
def validate_marching_squares(
    x: np.ndarray, y: np.ndarray, z: np.ndarray, levels: list[float]
) -> dict:
    import contourpy  # noqa: PLC0415

    xy = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    count = 0
    for case in range(16):
        for magnitude in [0.5, 2.0]:
            values = np.array([magnitude if case & (1 << k) else -1.0 for k in range(4)])
            grid = values[[0, 1, 3, 2]].reshape(2, 2)
            ours = cell_segments(xy, values, 0)
            ref = contourpy.contour_generator(
                x=[0.0, 1.0], y=[0.0, 1.0], z=grid,
                name="serial", corner_mask=False,
            ).lines(0)
            assert canonical(ours) == canonical(ref), (case, magnitude)
            count += 1

    comparisons = []
    generator = contourpy.contour_generator(
        x=x, y=y, z=np.ma.masked_invalid(z), name="serial", corner_mask=False
    )
    for level in levels:
        ours = segments(x, y, z, level)
        a = canonical(ours)
        b = canonical(generator.lines(level))
        assert a == b, (level, len(a - b), len(b - a))
        comparisons.append(
            dict(level_C=float(level), segments=len(a), identical_quantized_segments=True)
        )
    assert not len(segments([0, 1], [0, 1], np.full((2, 2), np.nan), 0))
    return dict(
        status="PASS",
        synthetic_case_checks=count,
        masked_cells_skipped=True,
        coordinate_tolerance_degrees=1e-8,
        real_grid=comparisons,
    )


# approved figure metadata mapping
def apply_approved_changes(figures: list, why: dict, more: dict, captions: dict) -> None:
    by = {f["figure"]: f for f in figures}
    changes = {
        4: dict(
            path="output/pcp_changes/pcp_changes.png",
            title="Similar internet gains, different infrastructure changes.",
            extension_key="paired_change_pcp",
            question="Do countries with similar gains in internet use also have similar changes in their telecom indicators?",
            encoding="Each line connects one country's four changes from 2015 to 2020.",
            rationale="Parallel coordinates connect four changes across the full matched sample.",
            interpretation="Highlighted countries show widely varying infrastructure shifts.",
            note="Selected gain range is descriptive.",
            takeaway="Similar internet progress does not describe one common infrastructure history.",
            caption="Paired 2015-2020 changes for 175 countries with highlighted selections.",
        ),
        5: dict(
            path="output/internet_revision/pcp_gentle_bundles.png",
            title="Gentle bundles reveal different country profiles.",
            extension_key="gentle_pcp",
            question="Do countries with high internet use share the same infrastructure profile?",
            encoding="Each curve is one of the 175 countries in 2020 grouped by adoption band.",
            rationale="Parallel coordinates with 35% curve bundling.",
            interpretation="High adoption includes wide broadband and mobile variation.",
            note="Adoption bands are descriptive comparison groups.",
            takeaway="Adoption label hides diverse infrastructure combinations.",
            caption="175 matched country profiles in 2020 with 35% curve bundling.",
        ),
    }
    for n, c in changes.items():
        if n in by:
            f = by[n]
            f.update(
                path=c["path"],
                title=c["title"],
                extension_key=c["extension_key"],
                caption=c["caption"],
                explanation=[
                    c["question"],
                    c["encoding"],
                    c["rationale"],
                    c.get("note", ""),
                    c["takeaway"],
                ],
                detailed_interpretation=c["interpretation"],
            )
            why[n] = c["rationale"]
            more[n] = c["interpretation"]
            captions[n] = c["caption"]
