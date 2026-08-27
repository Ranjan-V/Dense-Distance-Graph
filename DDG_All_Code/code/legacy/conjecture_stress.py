from pathlib import Path
import argparse
import importlib.util, random, json, math
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
    ex.add_unique_weights(G, seed*1237+11, base=.6, spread=2.0)
    return G,list(range(k))


def test_graph(G,bd,rng,max_edges):
    D,_,paths=ex.boundary_dist_paths(G,bd)
    cand=ex.candidate_edges(G,bd,paths)
    if len(cand)>max_edges:
        # Mix high-use and random candidates.
        top=cand[:max_edges//2]
        rest=cand[max_edges//2:]
        extra=rng.sample(rest,min(max_edges-len(top),len(rest))) if rest else []
        cand=top+extra
    tested=viol=rows=intervalviol=0
    worst_turn=0
    for e in cand:
        M=ex.support_from_paths(paths,bd,e)
        H=G.copy(); H.remove_edge(*e)
        if not nx.is_connected(H): continue
        Dav=ex.boundary_dist_only(H,bd)
        for i in range(len(bd)):
            ints=ex.cyclic_intervals(M[i])
            if len(ints)>1: intervalviol+=1
            if len(ints)!=1: continue
            seq=ex.cyclic_values(Dav[i]-D[i],M[i])
            if len(seq)<3 or not np.all(np.isfinite(seq)): continue
            rows+=1; tested+=1
            tr=ex.sign_turns(seq); worst_turn=max(worst_turn,tr)
            if not ex.peak_unimodal(seq):
                viol+=1
                return tested,viol,rows,intervalviol,worst_turn,(e,i,seq)
    return tested,viol,rows,intervalviol,worst_turn,None


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="Output JSON path")
    args=ap.parse_args()
    rng=random.Random(991)
    total={'graphs':0,'rows_tested':0,'unimodal_peak_violations':0,'interval_violations':0,'max_sign_turns':0}
    families=[]
    for seed in range(30):
        families.append(('random_planar',)+ex.make_random_planar(10,1000+seed))
    for seed in range(30):
        families.append(('outerplanar',)+outerplanar(40,2000+seed))
    for name,G,bd in families:
        t,v,r,iv,mt,ce=test_graph(G,bd,rng,15)
        total['graphs']+=1; total['rows_tested']+=r; total['unimodal_peak_violations']+=v; total['interval_violations']+=iv; total['max_sign_turns']=max(total['max_sign_turns'],mt)
        if ce:
            total['counterexample']={'family':name,'edge':repr(ce[0]),'row':ce[1],'seq':ce[2]}
            break
    out=Path(args.out) if args.out else Path(__file__).resolve().parent.parent.parent/'raw_data'/'conjecture_stress.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(total,indent=2)+'\n')
    print(json.dumps(total,indent=2))

if __name__=='__main__': main()
