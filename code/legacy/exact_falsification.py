import itertools, json, math, random, heapq, argparse
from pathlib import Path
from collections import defaultdict


def noncross(a,b,c,d,n):
    if len({a,b,c,d})<4: return True
    def between(x,a,b):
        # clockwise strictly from a to b on labels 0..n-1
        return 0 < ((x-a)%n) < ((b-a)%n)
    return not (between(c,a,b) != between(d,a,b) and between(a,c,d) != between(b,c,d))


def diagonals(n):
    out=[]
    for i in range(n):
        for j in range(i+1,n):
            if (j-i)%n in (1,n-1) or (i==0 and j==n-1):
                continue
            out.append((i,j))
    return out


def noncrossing_sets(n, exact_size=None):
    ds=diagonals(n)
    for mask in range(1<<len(ds)):
        if exact_size is not None and mask.bit_count()!=exact_size: continue
        S=[ds[i] for i in range(len(ds)) if (mask>>i)&1]
        ok=True
        for i in range(len(S)):
            for j in range(i):
                if not noncross(*S[i],*S[j],n): ok=False; break
            if not ok: break
        if ok: yield S


def polygon_graph(n, ds):
    es={(i,(i+1)%n) if i<(i+1)%n else ((i+1)%n,i) for i in range(n)}
    es=set()
    for i in range(n):
        a,b=i,(i+1)%n
        es.add(tuple(sorted((a,b))))
    for e in ds: es.add(tuple(sorted(e)))
    return n, sorted(es)


def templates():
    # (name, n, edges, boundary order)
    out=[]
    # 2x3 grid: 0 1 2 / 3 4 5; boundary 0,1,2,5,4,3
    es=[]
    for i in range(2):
        for j in range(3):
            u=3*i+j
            if j+1<3: es.append((u,u+1))
            if i+1<2: es.append((u,u+3))
    out.append(("grid_2x3",6,sorted(set(tuple(sorted(e)) for e in es)),[0,1,2,5,4,3]))
    # triangulated 2x3
    es2=list(es)+[(0,4),(1,5)]
    out.append(("tri_grid_2x3",6,sorted(set(tuple(sorted(e)) for e in es2)),[0,1,2,5,4,3]))
    # wheel on outer 5-cycle + center 5
    es3=[]
    for i in range(5):
        es3.append(tuple(sorted((i,(i+1)%5))))
        es3.append((i,5))
    out.append(("wheel_5",6,sorted(set(es3)),list(range(5))))
    return out


def encode_weights(edges, bases):
    M=1<<(len(edges)+2)
    return {e: bases[i]*M + (1<<i) for i,e in enumerate(edges)}, M


def adj_from(n, edges, w, skip=None):
    a=[[] for _ in range(n)]
    for e in edges:
        if skip is not None and e==skip: continue
        u,v=e; z=w[e]
        a[u].append((v,z)); a[v].append((u,z))
    return a


def dijkstra(n, adj, s):
    inf=None
    d=[inf]*n; p=[-1]*n
    d[s]=0; pq=[(0,s)]
    while pq:
        du,u=heapq.heappop(pq)
        if d[u]!=du: continue
        for v,w in adj[u]:
            nd=du+w
            if d[v] is None or nd<d[v]:
                d[v]=nd; p[v]=u; heapq.heappush(pq,(nd,v))
    return d,p


def path_edges(parent,s,t):
    out=set(); x=t
    while x!=s:
        y=parent[x]
        if y<0: return None
        out.add(tuple(sorted((x,y)))); x=y
    return out


def cyclic_interval_indices(mask):
    k=len(mask); c=sum(mask)
    if c==0: return []
    if c==k: return [list(range(k))]
    starts=[i for i in range(k) if mask[i] and not mask[(i-1)%k]]
    out=[]
    for st in starts:
        cur=[]; i=st
        while mask[i]:
            cur.append(i); i=(i+1)%k
            if i==st: break
        out.append(cur)
    return out


def peak_unimodal(vals):
    signs=[]
    for a,b in zip(vals,vals[1:]):
        if b>a: signs.append(1)
        elif b<a: signs.append(-1)
    down=False
    for x in signs:
        if x<0: down=True
        elif down and x>0: return False
    return True


def forbidden_score(vals):
    signs=[]
    for a,b in zip(vals,vals[1:]):
        if b>a: signs.append(1)
        elif b<a: signs.append(-1)
    seen_down=False; score=0
    for x in signs:
        if x<0: seen_down=True
        elif x>0 and seen_down: score+=1
    turns=sum(signs[i]!=signs[i-1] for i in range(1,len(signs)))
    return (score,turns,len(vals))


def evaluate_instance(n, edges, boundary, bases, check_support=True):
    w,M=encode_weights(edges,bases)
    adj=adj_from(n,edges,w)
    sp=[dijkstra(n,adj,s) for s in boundary]
    tested=0; counter=None; maxscore=(0,0,0); support_fail=0; interval_fail=0
    for e in edges:
        adjdel=adj_from(n,edges,w,skip=e)
        dels=[dijkstra(n,adjdel,s)[0] for s in boundary]
        if check_support:
            w2=dict(w); w2[e]+=M
            adj2=adj_from(n,edges,w2)
            d2=[dijkstra(n,adj2,s)[0] for s in boundary]
        for si,s in enumerate(boundary):
            d0,par=sp[si]
            masks=[]
            for t in boundary:
                pe=path_edges(par,s,t)
                masks.append(pe is not None and e in pe)
            ints=cyclic_interval_indices(masks)
            if len(ints)>1: interval_fail+=1
            if check_support:
                for tj,t in enumerate(boundary):
                    actual=d2[si][t] is not None and d0[t] is not None and d2[si][t]>d0[t]
                    if actual!=masks[tj]: support_fail+=1
            if len(ints)==1 and len(ints[0])>=3:
                vals=[]; ok=True
                for idx in ints[0]:
                    t=boundary[idx]
                    if dels[si][t] is None: ok=False; break
                    vals.append(dels[si][t]-d0[t])
                if ok:
                    tested+=1
                    sc=forbidden_score(vals)
                    if sc>maxscore: maxscore=sc
                    if not peak_unimodal(vals):
                        counter={"edge":e,"source":s,"targets":[boundary[i] for i in ints[0]],"slacks":vals,"score":sc}
                        return tested,counter,maxscore,support_fail,interval_fail
    return tested,counter,maxscore,support_fail,interval_fail


def deterministic_patterns(m, count):
    pats=[]
    # fixed structured assignments plus deterministic pseudo-random bit patterns
    pats.append(tuple([1]*m)); pats.append(tuple([2]*m))
    pats.append(tuple(1+(i%2) for i in range(m)))
    pats.append(tuple(1+((i//2)%2) for i in range(m)))
    rng=random.Random(314159+m)
    while len(pats)<count:
        x=tuple(1+rng.randrange(2) for _ in range(m))
        if x not in pats: pats.append(x)
    return pats[:count]


def exhaustive_campaign():
    total_instances=0; rows=0; support_fail=0; interval_fail=0; maxscore=(0,0,0); counter=None
    classes=defaultdict(lambda:{"instances":0,"rows":0})
    support_budget=256; support_checked=0
    # Exhaust all noncrossing-diagonal outerplanar topologies on n<=5;
    # use a deterministic battery of 16 integer weight assignments per topology.
    for n in (4,5):
        for ds in noncrossing_sets(n):
            _,edges=polygon_graph(n,ds)
            for bases in deterministic_patterns(len(edges),16):
                total_instances+=1; classes["outerplanar_all_topologies_n<=5"]["instances"]+=1
                chk=support_budget>0
                t,c,sc,sf,iv=evaluate_instance(n,edges,list(range(n)),bases,check_support=chk)
                if chk: support_budget-=1; support_checked+=1
                rows+=t; classes["outerplanar_all_topologies_n<=5"]["rows"]+=t; support_fail+=sf; interval_fail+=iv; maxscore=max(maxscore,sc)
                if c: return locals()
    # Exhaust all maximal outerplanar topologies on n=6; 64 deterministic integer assignments each.
    n=6
    for ds in noncrossing_sets(n, exact_size=n-3):
        _,edges=polygon_graph(n,ds)
        for bases in deterministic_patterns(len(edges),64):
            total_instances+=1; classes["maximal_outerplanar_all_topologies_n6"]["instances"]+=1
            chk=support_budget>0
            t,c,sc,sf,iv=evaluate_instance(n,edges,list(range(n)),bases,check_support=chk)
            if chk: support_budget-=1; support_checked+=1
            rows+=t; classes["maximal_outerplanar_all_topologies_n6"]["rows"]+=t; support_fail+=sf; interval_fail+=iv; maxscore=max(maxscore,sc)
            if c: return locals()
    # For three embedded planar templates, exhaust every {1,2} base-weight assignment.
    for name,n,edges,bd in templates():
        for bases in itertools.product((1,2), repeat=len(edges)):
            total_instances+=1; classes[name]["instances"]+=1
            chk=support_budget>0
            t,c,sc,sf,iv=evaluate_instance(n,edges,bd,bases,check_support=chk)
            if chk: support_budget-=1; support_checked+=1
            rows+=t; classes[name]["rows"]+=t; support_fail+=sf; interval_fail+=iv; maxscore=max(maxscore,sc)
            if c: return locals()
    return locals()

def random_triangulated_grid(m=5):
    n=m*m; edges=[]
    for i in range(m):
        for j in range(m):
            u=i*m+j
            if i+1<m: edges.append(tuple(sorted((u,(i+1)*m+j))))
            if j+1<m: edges.append(tuple(sorted((u,i*m+j+1))))
            if i+1<m and j+1<m:
                if (i+j)%2==0: edges.append(tuple(sorted((u,(i+1)*m+j+1))))
                else: edges.append(tuple(sorted((i*m+j+1,(i+1)*m+j))))
    bd=[]
    for j in range(m): bd.append(j)
    for i in range(1,m): bd.append(i*m+m-1)
    for j in range(m-2,-1,-1): bd.append((m-1)*m+j)
    for i in range(m-2,0,-1): bd.append(i*m)
    return n,sorted(set(edges)),bd


def annealing_campaign(restarts=5,steps=80,seed=9917):
    rng=random.Random(seed); n,edges,bd=random_triangulated_grid(4)
    best={"score":[0,0,0],"bases":None,"counterexample":None,"evaluations":0}
    for rr in range(restarts):
        bases=[rng.randint(1,12) for _ in edges]
        t,c,sc,_,_=evaluate_instance(n,edges,bd,bases,check_support=False); best["evaluations"]+=1
        cur=sc
        if sc>tuple(best["score"]): best.update(score=list(sc),bases=list(bases),counterexample=c)
        if c: return best
        temp=3.0
        for it in range(steps):
            nb=list(bases)
            # mutate 1-3 edge base weights
            for _ in range(1+rng.randrange(3)):
                idx=rng.randrange(len(nb)); nb[idx]=max(1,min(20,nb[idx]+rng.choice((-3,-2,-1,1,2,3))))
            t,c,sc,_,_=evaluate_instance(n,edges,bd,nb,check_support=False); best["evaluations"]+=1
            if c:
                best.update(score=list(sc),bases=nb,counterexample=c); return best
            gain=(sc[0]-cur[0])*20+(sc[1]-cur[1])*3+(sc[2]-cur[2])*0.02
            if gain>=0 or rng.random()<math.exp(gain/max(temp,1e-6)):
                bases=nb; cur=sc
            temp*=0.985
            if sc>tuple(best["score"]): best.update(score=list(sc),bases=list(nb),counterexample=None)
    return best


def exact_kernel_validation(seed=777):
    rng=random.Random(seed); n,edges,bd=random_triangulated_grid(7)
    base=[rng.randint(1,50) for _ in edges]; w,M=encode_weights(edges,base)
    total=0; fail=0
    for q in (1,2,4):
        F=rng.sample(edges,q); fset=set(F)
        Hedges=[e for e in edges if e not in fset]
        Hadj=adj_from(n,Hedges,w)
        terminals=set(bd)
        for e in F: terminals.update(e)
        dm={s:dijkstra(n,Hadj,s)[0] for s in terminals}
        endpoints=sorted(set(x for e in F for x in e))
        for _ in range(270):
            cw={e:(rng.randint(1,80)*M + (1<<edges.index(e))) for e in F}
            curw=dict(w); curw.update(cw)
            full=adj_from(n,edges,curw)
            s,t=rng.sample(bd,2)
            fd=dijkstra(n,full,s)[0][t]
            U=[]
            for x in [s,t]+endpoints:
                if x not in U: U.append(x)
            idx={x:i for i,x in enumerate(U)}
            kadj=[[] for _ in U]
            for i,u in enumerate(U):
                for j in range(i+1,len(U)):
                    v=U[j]; z=dm[u][v]
                    if z is not None:
                        kadj[i].append((j,z)); kadj[j].append((i,z))
            for e in F:
                u,v=e; i=idx[u]; j=idx[v]; z=cw[e]
                kadj[i].append((j,z)); kadj[j].append((i,z))
            kd=dijkstra(len(U),kadj,idx[s])[0][idx[t]]
            total+=1
            if kd!=fd: fail+=1
    return {"queries":total,"failures":fail}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="Output JSON path")
    args=ap.parse_args()
    out=Path(args.out) if args.out else Path(__file__).resolve().parent.parent.parent/"raw_data"/"exact_falsification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    ex=exhaustive_campaign()
    ann=annealing_campaign()
    ker=exact_kernel_validation()
    result={
        "arithmetic":"exact Python integers; primary integer weights with deterministic subset-unique perturbations",
        "exhaustive_instances":ex["total_instances"],
        "exhaustive_slack_rows":ex["rows"],
        "support_checked_instances":ex["support_checked"],
        "support_failures":ex["support_fail"],
        "interval_failures":ex["interval_fail"],
        "max_forbidden_score":list(ex["maxscore"]),
        "counterexample":ex["counter"],
        "classes":dict(ex["classes"]),
        "annealing":ann,
        "active_kernel_exact":ker,
    }
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
