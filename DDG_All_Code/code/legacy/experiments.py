import argparse, csv, math, random, statistics, time
from pathlib import Path
from collections import defaultdict

import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

TOL = 1e-8


def add_unique_weights(G, seed, base=1.0, spread=1.0):
    rng = random.Random(seed)
    for idx, (u, v) in enumerate(G.edges()):
        # Continuous random perturbation makes ties probability zero in our experiments.
        G[u][v]["weight"] = base + spread * rng.random() + 1e-9 * (idx + 1)


def boundary_cycle(m, n):
    b = []
    for j in range(n): b.append((0, j))
    for i in range(1, m): b.append((i, n - 1))
    for j in range(n - 2, -1, -1): b.append((m - 1, j))
    for i in range(m - 2, 0, -1): b.append((i, 0))
    return b


def make_grid(m, seed, triangulated=False, road=False):
    G = nx.Graph()
    for i in range(m):
        for j in range(m):
            G.add_node((i, j))
    for i in range(m):
        for j in range(m):
            if i + 1 < m: G.add_edge((i, j), (i + 1, j))
            if j + 1 < m: G.add_edge((i, j), (i, j + 1))
            if triangulated and i + 1 < m and j + 1 < m:
                # Alternate diagonal orientation to avoid an overly regular metric.
                if (i + j) % 2 == 0:
                    G.add_edge((i, j), (i + 1, j + 1))
                else:
                    G.add_edge((i + 1, j), (i, j + 1))
    bd = boundary_cycle(m, m)
    add_unique_weights(G, seed * 1009 + 17, base=0.8, spread=1.4)
    if road:
        rng = random.Random(seed * 2027 + 91)
        bdedges = {frozenset((bd[i], bd[(i + 1) % len(bd)])) for i in range(len(bd))}
        candidates = [e for e in G.edges() if frozenset(e) not in bdedges]
        rng.shuffle(candidates)
        # Delete a modest fraction of interior edges while preserving connectivity.
        target = max(1, int(0.18 * len(candidates)))
        removed = 0
        for e in candidates:
            if removed >= target: break
            w = G[e[0]][e[1]]["weight"]
            G.remove_edge(*e)
            if nx.is_connected(G):
                removed += 1
            else:
                G.add_edge(*e, weight=w)
    return G, bd



def make_random_planar(m, seed):
    # A Delaunay triangulation with k=4m-4 designated outer-face vertices
    # and r=m^2 total vertices. All outer vertices are placed on a convex circle.
    k = 4 * m - 4
    r = m * m
    rng = np.random.default_rng(seed * 4099 + 31)
    ang = np.linspace(0.0, 2.0 * np.pi, k, endpoint=False)
    outer = np.c_[np.cos(ang), np.sin(ang)]
    q = r - k
    rad = np.sqrt(rng.random(q)) * 0.78
    ia = rng.random(q) * 2.0 * np.pi
    inner = np.c_[rad * np.cos(ia), rad * np.sin(ia)]
    pts = np.vstack([outer, inner])
    tri = Delaunay(pts, qhull_options="QJ")
    G = nx.Graph()
    for i in range(r): G.add_node(i)
    for face in tri.simplices:
        a,b,c = map(int, face)
        G.add_edge(a,b); G.add_edge(b,c); G.add_edge(c,a)
    add_unique_weights(G, seed * 8191 + 73, base=0.7, spread=1.6)
    return G, list(range(k))


def boundary_dist_paths(G, bd):
    dist = []
    paths = []
    for s in bd:
        d, p = nx.single_source_dijkstra(G, s, weight="weight")
        dist.append(d)
        paths.append(p)
    D = np.array([[dist[i][t] for t in bd] for i in range(len(bd))], dtype=float)
    return D, dist, paths


def boundary_dist_only(G, bd):
    dist = []
    for s in bd:
        d = nx.single_source_dijkstra_path_length(G, s, weight="weight")
        dist.append(d)
    return np.array([[dist[i][t] for t in bd] for i in range(len(bd))], dtype=float)


def path_uses_edge(path, edgekey):
    return any(frozenset((path[i], path[i + 1])) == edgekey for i in range(len(path) - 1))


def support_from_paths(paths, bd, e):
    k = len(bd)
    ek = frozenset(e)
    M = np.zeros((k, k), dtype=bool)
    for i in range(k):
        for j, t in enumerate(bd):
            if i == j: continue
            if path_uses_edge(paths[i][t], ek):
                M[i, j] = True
    return M


def cyclic_intervals(mask):
    a = list(bool(x) for x in mask)
    k = len(a)
    s = sum(a)
    if s == 0:
        return []
    if s == k:
        return [(0, k - 1)]
    starts = [i for i in range(k) if a[i] and not a[(i - 1) % k]]
    out = []
    for st in starts:
        en = st
        while a[(en + 1) % k] and (en + 1) % k != st:
            en = (en + 1) % k
        out.append((st, en))
    return out


def cyclic_values(vals, mask):
    ints = cyclic_intervals(mask)
    if len(ints) != 1:
        return []
    st, en = ints[0]
    k = len(mask)
    out = []
    i = st
    while True:
        out.append(float(vals[i]))
        if i == en:
            break
        i = (i + 1) % k
    return out


def sign_pattern(seq, tol=1e-7):
    signs = []
    for a, b in zip(seq, seq[1:]):
        d = b - a
        if abs(d) <= tol:
            continue
        signs.append(1 if d > 0 else -1)
    return signs


def sign_turns(seq, tol=1e-7):
    signs = sign_pattern(seq, tol)
    return sum(signs[i] != signs[i - 1] for i in range(1, len(signs)))


def peak_unimodal(seq, tol=1e-7):
    # Nondecreasing followed by nonincreasing, allowing either phase to be empty.
    signs = sign_pattern(seq, tol)
    seen_down = False
    for s in signs:
        if s < 0:
            seen_down = True
        elif seen_down and s > 0:
            return False
    return True


def candidate_edges(G, bd, paths):
    used = defaultdict(int)
    bdset = set(bd)
    for pmap in paths:
        for t in bd:
            p = pmap[t]
            for i in range(len(p) - 1):
                e = tuple(sorted((p[i], p[i + 1]), key=repr))
                used[e] += 1
    c = []
    for e, cnt in used.items():
        # Prefer an edge that is not itself an outer boundary edge.
        if e[0] in bdset and e[1] in bdset:
            # Adjacent boundary vertices may still be useful, but deprioritize.
            score = cnt * 0.2
        else:
            score = cnt
        c.append((score, cnt, e))
    c.sort(reverse=True, key=lambda x: (x[0], x[1]))
    return [e for _, _, e in c]


def sequential_experiment(family, m, seed, updates, rng_seed):
    if family == "grid":
        G, bd = make_grid(m, seed, triangulated=False, road=False)
    elif family == "triangulated":
        G, bd = make_grid(m, seed, triangulated=True, road=False)
    elif family == "road":
        G, bd = make_grid(m, seed, triangulated=False, road=True)
    elif family == "random_planar":
        G, bd = make_random_planar(m, seed)
    elif family == "adversarial":
        G, bd = make_grid(m, seed, triangulated=True, road=False)
    else:
        raise ValueError(family)

    rng = random.Random(rng_seed)
    rows = []
    slack_examples = []

    for step in range(updates):
        D0, _, paths = boundary_dist_paths(G, bd)
        cand = candidate_edges(G, bd, paths)
        if not cand:
            break
        # Bias toward highly used edges but vary across updates.
        pool = cand[:max(3, min(len(cand), max(8, len(cand)//3)))]
        if family == "adversarial":
            # Choose the currently used edge whose support has the richest row-interval staircase.
            # This is an adversarial update-selection rule, not a claim of worst-case optimality.
            best = None
            for ce in pool:
                cm = support_from_paths(paths, bd, ce)
                shapes = set()
                for ii in range(len(bd)):
                    ci = cyclic_intervals(cm[ii])
                    if ci: shapes.add(ci[0])
                score = (len(shapes), int(cm.sum()))
                if best is None or score > best[0]: best = (score, ce)
            e = best[1]
        else:
            e = rng.choice(pool)
        oldw = G[e[0]][e[1]]["weight"]
        pred = support_from_paths(paths, bd, e)

        H = G.copy()
        H.remove_edge(*e)
        if nx.is_connected(H):
            Dav = boundary_dist_only(H, bd)
        else:
            # Infinite replacement distance where disconnected. Our graph families are usually 2-edge-connected.
            Dav = np.full_like(D0, np.inf)
            for i, s in enumerate(bd):
                d = nx.single_source_dijkstra_path_length(H, s, weight="weight")
                for j, t in enumerate(bd):
                    if t in d: Dav[i, j] = d[t]

        delta = oldw * rng.uniform(0.12, 0.85) + rng.uniform(0.03, 0.2)
        G[e[0]][e[1]]["weight"] = oldw + delta
        D1 = boundary_dist_only(G, bd)
        actual = np.abs(D1 - D0) > TOL
        support_ok = bool(np.array_equal(pred, actual))

        interval_counts = [len(cyclic_intervals(actual[i])) for i in range(len(bd))]
        active_rows = sum(c > 0 for c in interval_counts)
        interval_viol = sum(c > 1 for c in interval_counts)
        changed = int(actual.sum())
        desc = active_rows
        unique_ints = set()
        bitonic_tested = 0
        bitonic_viol = 0
        unimodal_peak_viol = 0
        max_turn = 0
        local_best = None
        for i in range(len(bd)):
            ints = cyclic_intervals(actual[i])
            if ints:
                unique_ints.add(ints[0])
            if len(ints) == 1:
                slack = Dav[i] - D0[i]
                seq = cyclic_values(slack, actual[i])
                if len(seq) >= 3 and np.all(np.isfinite(seq)):
                    bitonic_tested += 1
                    tr = sign_turns(seq)
                    max_turn = max(max_turn, tr)
                    if tr > 1:
                        bitonic_viol += 1
                    if not peak_unimodal(seq):
                        unimodal_peak_viol += 1
                    if local_best is None or (len(seq), tr) > (len(local_best[0]), local_best[1]):
                        local_best = (seq, tr, i)
        if local_best is not None:
            slack_examples.append((len(local_best[0]), local_best[1], family, m, seed, step, e, local_best[2], local_best[0]))

        rows.append({
            "family": family,
            "m": m,
            "r": G.number_of_nodes(),
            "k": len(bd),
            "seed": seed,
            "step": step,
            "edge": repr(e),
            "old_weight": oldw,
            "delta": delta,
            "changed_entries": changed,
            "active_row_descriptors": desc,
            "compression_ratio": (changed / desc) if desc else 0.0,
            "max_cyclic_intervals_per_row": max(interval_counts) if interval_counts else 0,
            "interval_violations": interval_viol,
            "support_equivalence": support_ok,
            "unique_row_interval_shapes": len(unique_ints),
            "bitonic_rows_tested": bitonic_tested,
            "bitonic_violations": bitonic_viol,
            "unimodal_peak_violations": unimodal_peak_viol,
            "max_slack_sign_turns": max_turn,
        })
    return rows, slack_examples


def active_kernel_precompute(G, bd, F):
    H = G.copy()
    for e in F:
        if H.has_edge(*e): H.remove_edge(*e)
    U = []
    for u, v in F:
        if u not in U: U.append(u)
        if v not in U: U.append(v)
    X = list(bd)
    for u in U:
        if u not in X: X.append(u)
    dm = {}
    for s in X:
        dm[s] = nx.single_source_dijkstra_path_length(H, s, weight="weight")
    return H, U, dm


def kernel_query(s, t, U, dm, F, current_weights):
    nodes = [s, t] + [u for u in U if u not in (s, t)]
    n = len(nodes)
    idx = {u:i for i,u in enumerate(nodes)}
    # Dense Dijkstra on metric closure of G-F, augmented with active F edges.
    dist = [math.inf] * n
    used = [False] * n
    dist[idx[s]] = 0.0
    fad = defaultdict(list)
    for e, w in zip(F, current_weights):
        a, b = e
        fad[a].append((b, w)); fad[b].append((a, w))
    for _ in range(n):
        uidx = -1; best = math.inf
        for i in range(n):
            if not used[i] and dist[i] < best:
                best = dist[i]; uidx = i
        if uidx < 0: break
        if nodes[uidx] == t: return best
        used[uidx] = True
        u = nodes[uidx]
        # Static complete metric edges.
        du = dm[u]
        for j, v in enumerate(nodes):
            if used[j] or v == u: continue
            w = du.get(v, math.inf)
            nv = best + w
            if nv < dist[j]: dist[j] = nv
        # Dynamic active edges.
        for v, w in fad.get(u, []):
            if v not in idx: continue
            j = idx[v]
            nv = best + w
            if nv < dist[j]: dist[j] = nv
    return dist[idx[t]]


def validate_active_kernel(outdir):
    rng = random.Random(77123)
    records = []
    for m in (7, 9, 11):
        G, bd = make_grid(m, 100 + m, triangulated=True, road=False)
        all_edges = list(G.edges())
        bdset = set(bd)
        internal = [e for e in all_edges if not (e[0] in bdset and e[1] in bdset)]
        for q in (1, 2, 4):
            F = rng.sample(internal, q)
            basew = [G[e[0]][e[1]]["weight"] for e in F]
            H, U, dm = active_kernel_precompute(G, bd, F)
            errs = []
            kernel_times = []
            full_times = []
            trials = 90
            for z in range(trials):
                cw = [max(0.05, w * rng.uniform(0.45, 2.1)) for w in basew]
                for e, w in zip(F, cw): G[e[0]][e[1]]["weight"] = w
                s, t = rng.sample(bd, 2)
                ta = time.perf_counter()
                kd = kernel_query(s, t, U, dm, F, cw)
                tb = time.perf_counter()
                fd = nx.shortest_path_length(G, s, t, weight="weight")
                tc = time.perf_counter()
                errs.append(abs(kd - fd))
                kernel_times.append(tb-ta)
                full_times.append(tc-tb)
            for e, w in zip(F, basew): G[e[0]][e[1]]["weight"] = w
            records.append({
                "m": m, "r": G.number_of_nodes(), "k": len(bd), "q": q,
                "queries": trials, "max_abs_error": max(errs),
                "mean_kernel_query_us": 1e6 * statistics.mean(kernel_times),
                "mean_full_dijkstra_us": 1e6 * statistics.mean(full_times),
            })
    df = pd.DataFrame(records)
    df.to_csv(outdir / "data" / "active_kernel_validation.csv", index=False)
    return df


def benchmark_single_edge(outdir):
    rng = random.Random(8801)
    rec = []
    for m in (6, 8, 10, 12, 14):
        G, bd = make_grid(m, 400 + m, triangulated=True, road=False)
        D0, _, paths = boundary_dist_paths(G, bd)
        e = candidate_edges(G, bd, paths)[0]
        oldw = G[e[0]][e[1]]["weight"]
        F = [e]
        _, U, dm = active_kernel_precompute(G, bd, F)
        # Time a batch of oracle update+query operations.
        nops = 3000
        t0 = time.perf_counter()
        chk = 0.0
        for _ in range(nops):
            w = oldw * rng.uniform(0.5, 2.0)
            s, t = rng.sample(bd, 2)
            chk += kernel_query(s, t, U, dm, F, [w])
        t1 = time.perf_counter()
        oracle_us = 1e6 * (t1 - t0) / nops
        # Full DDG recomputation after each of a few weight changes.
        trials = 8
        ts = []
        for _ in range(trials):
            G[e[0]][e[1]]["weight"] = oldw * rng.uniform(0.5, 2.0)
            a = time.perf_counter()
            _ = boundary_dist_only(G, bd)
            b = time.perf_counter()
            ts.append(b-a)
        G[e[0]][e[1]]["weight"] = oldw
        rec.append({
            "m":m, "r":G.number_of_nodes(), "k":len(bd),
            "oracle_update_plus_query_us":oracle_us,
            "full_ddg_recompute_ms":1000*statistics.mean(ts),
            "empirical_ratio":(1000*statistics.mean(ts))/(oracle_us/1000),
            "checksum":chk,
        })
    df = pd.DataFrame(rec)
    df.to_csv(outdir / "data" / "single_edge_benchmark.csv", index=False)
    return df


def make_figures(outdir, df, ak, bench, slack_examples):
    figdir = outdir / "figures"
    # Figure 1: changed entries vs descriptors scaling.
    agg = df.groupby(["family","r","k"], as_index=False).agg(
        changed_entries=("changed_entries","median"),
        descriptors=("active_row_descriptors","median"),
        compression_ratio=("compression_ratio","median"),
        unique_shapes=("unique_row_interval_shapes","median"),
    )
    fig, ax = plt.subplots(figsize=(6.2,4.0))
    for family, g in agg.groupby("family"):
        g=g.sort_values("r")
        ax.plot(g["r"], g["changed_entries"], marker="o", label=f"{family}: changed DDG entries")
        ax.plot(g["r"], g["descriptors"], marker="x", linestyle="--", label=f"{family}: row intervals")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("piece size r")
    ax.set_ylabel("median count per update")
    ax.set_title("Value changes can be dense while support stays O(sqrt(r))")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout(); fig.savefig(figdir/"support_scaling.pdf", bbox_inches="tight"); fig.savefig(figdir/"support_scaling.png", dpi=220, bbox_inches="tight"); plt.close(fig)

    # Figure 2: empirical support compression ratio.
    fig, ax = plt.subplots(figsize=(6.2,3.8))
    families = list(agg["family"].unique())
    for family, g in agg.groupby("family"):
        g=g.sort_values("r")
        ax.plot(g["r"], g["compression_ratio"], marker="o", label=family)
    ax.set_xlabel("piece size r"); ax.set_ylabel("median changed entries / interval descriptors")
    ax.set_title("Empirical structural compression of the changed-entry support")
    ax.grid(True, alpha=0.25); ax.legend()
    fig.tight_layout(); fig.savefig(figdir/"compression_ratio.pdf", bbox_inches="tight"); fig.savefig(figdir/"compression_ratio.png", dpi=220, bbox_inches="tight"); plt.close(fig)

    # Figure 3: one longest replacement-slack sequence from the real run.
    if slack_examples:
        ex = sorted(slack_examples, reverse=True, key=lambda x:(x[0],-x[1]))[0]
        seq=ex[-1]
        pd.DataFrame({"position": list(range(len(seq))), "replacement_slack": seq}).to_csv(outdir/"data"/"slack_profile_example.csv", index=False)
        (outdir/"data"/"slack_profile_metadata.json").write_text(__import__("json").dumps({"family": ex[2], "m": ex[3], "seed": ex[4], "length": len(seq), "sign_turns": ex[1]}, indent=2)+"\n")
        fig, ax = plt.subplots(figsize=(6.2,3.6))
        ax.plot(range(len(seq)), seq, marker="o")
        ax.set_xlabel("boundary position within affected cyclic interval")
        ax.set_ylabel("replacement slack rho_e(s,t)")
        ax.set_title(f"Observed replacement-slack profile ({ex[2]}, r={ex[3]**2}, length={len(seq)})")
        ax.grid(True, alpha=0.25)
        fig.tight_layout(); fig.savefig(figdir/"slack_profile.pdf", bbox_inches="tight"); fig.savefig(figdir/"slack_profile.png", dpi=220, bbox_inches="tight"); plt.close(fig)

    # Figure 4: benchmark on a log scale.
    fig, ax = plt.subplots(figsize=(6.2,3.8))
    ax.plot(bench["r"], bench["full_ddg_recompute_ms"]*1000, marker="o", label="full DDG rematerialization")
    ax.plot(bench["r"], bench["oracle_update_plus_query_us"], marker="s", label="single-active-edge oracle")
    ax.set_yscale("log")
    ax.set_xlabel("piece size r"); ax.set_ylabel("microseconds (Python prototype)")
    ax.set_title("Prototype cost: rematerialization vs implicit edge-weight oracle")
    ax.grid(True, which="both", alpha=0.25); ax.legend()
    fig.tight_layout(); fig.savefig(figdir/"runtime_benchmark.pdf", bbox_inches="tight"); fig.savefig(figdir/"runtime_benchmark.png", dpi=220, bbox_inches="tight"); plt.close(fig)

    agg.to_csv(outdir/"data"/"support_scaling_summary.csv", index=False)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    ap.add_argument("--quick", action="store_true")
    args=ap.parse_args()
    outdir=Path(args.out)
    (outdir/"data").mkdir(parents=True, exist_ok=True)
    (outdir/"figures").mkdir(parents=True, exist_ok=True)

    sizes=(6,8,10,12) if not args.quick else (6,8)
    seeds=(0,1) if not args.quick else (0,)
    updates=6 if not args.quick else 2
    allrows=[]; examples=[]
    start=time.perf_counter()
    for family in ("grid","triangulated","road","random_planar","adversarial"):
        for m in sizes:
            for seed in seeds:
                rows, ex = sequential_experiment(family,m,seed,updates, rng_seed=31337+100*m+17*seed+len(family))
                allrows.extend(rows); examples.extend(ex)
                print(f"done {family} m={m} seed={seed}: {len(rows)} updates", flush=True)
    df=pd.DataFrame(allrows)
    df.to_csv(outdir/"data"/"sequential_updates.csv", index=False)
    ak=validate_active_kernel(outdir)
    bench=benchmark_single_edge(outdir)
    make_figures(outdir,df,ak,bench,examples)

    report={
        "updates":int(len(df)),
        "support_equivalence_failures":int((~df["support_equivalence"]).sum()),
        "interval_violations":int(df["interval_violations"].sum()),
        "bitonic_rows_tested":int(df["bitonic_rows_tested"].sum()),
        "bitonic_violations":int(df["bitonic_violations"].sum()),
        "unimodal_peak_violations":int(df["unimodal_peak_violations"].sum()),
        "max_slack_sign_turns":int(df["max_slack_sign_turns"].max()),
        "changed_entries_total":int(df["changed_entries"].sum()),
        "active_descriptors_total":int(df["active_row_descriptors"].sum()),
        "max_compression_ratio":float(df["compression_ratio"].max()),
        "median_compression_ratio":float(df.loc[df["active_row_descriptors"]>0,"compression_ratio"].median()),
        "active_kernel_queries":int(ak["queries"].sum()),
        "active_kernel_max_abs_error":float(ak["max_abs_error"].max()),
        "runtime_seconds":float(time.perf_counter()-start),
    }
    import json
    (outdir/"data"/"run_summary.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__ == "__main__":
    main()
