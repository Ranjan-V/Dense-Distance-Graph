from pathlib import Path
import argparse
import importlib.util, random, json
import networkx as nx
import numpy as np
spec=importlib.util.spec_from_file_location('ex', str(Path(__file__).with_name('experiments.py')))
ex=importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)

def outerplanar(k, seed):
    rng=random.Random(seed)
    G=nx.Graph(); G.add_nodes_from(range(k))
    for i in range(k): G.add_edge(i,(i+1)%k)
    def rec(poly):
        if len(poly)<=3: return
        j=rng.randint(2,len(poly)-2)
        G.add_edge(poly[0],poly[j])
        rec(poly[:j+1]); rec([poly[0]]+poly[j:])
    rec(list(range(k)))
    ex.add_unique_weights(G, seed*104729+97, base=.2, spread=4.0)
    return G,list(range(k))

def check(G,bd,max_edges=None):
    D,_,paths=ex.boundary_dist_paths(G,bd)
    cand=ex.candidate_edges(G,bd,paths)
    if max_edges is not None: cand=cand[:max_edges]
    rows=0
    for e in cand:
        M=ex.support_from_paths(paths,bd,e)
        H=G.copy(); H.remove_edge(*e)
        if not nx.is_connected(H): continue
        Dav=ex.boundary_dist_only(H,bd)
        for i in range(len(bd)):
            ints=ex.cyclic_intervals(M[i])
            if len(ints)>1:
                return rows, {'type':'interval','edge':repr(e),'row':i,'ints':ints}
            if len(ints)!=1: continue
            seq=ex.cyclic_values(Dav[i]-D[i],M[i])
            if len(seq)<3 or not np.all(np.isfinite(seq)): continue
            rows += 1
            if not ex.peak_unimodal(seq):
                return rows, {'type':'unimodal','edge':repr(e),'row':i,'seq':seq,'turns':ex.sign_turns(seq)}
    return rows,None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="Output JSON path")
    args=ap.parse_args()
    total={'graphs':0,'rows_tested':0,'counterexample':None}
    # Outerplanar families with diverse sizes/weights.
    for seed in range(300):
        k=[12,16,20,24,32][seed%5]
        G,bd=outerplanar(k, 5000+seed)
        r,ce=check(G,bd,max_edges=20)
        total['graphs']+=1; total['rows_tested']+=r
        if ce:
            ce.update(family='outerplanar',seed=seed,k=k); total['counterexample']=ce; break
    # Delaunay one-hole planar pieces if none found.
    if total['counterexample'] is None:
        for seed in range(100):
            m=[6,7,8,9][seed%4]
            G,bd=ex.make_random_planar(m,6000+seed)
            r,ce=check(G,bd,max_edges=12)
            total['graphs']+=1; total['rows_tested']+=r
            if ce:
                ce.update(family='random_planar',seed=seed,m=m); total['counterexample']=ce; break
    out=Path(args.out) if args.out else Path(__file__).resolve().parent.parent.parent/'raw_data'/'extended_stress.json'; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(total,indent=2)+'\n')
    print(json.dumps(total,indent=2))
if __name__=='__main__': main()
