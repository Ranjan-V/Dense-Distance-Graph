#!/usr/bin/env python3
import heapq, json
from pathlib import Path


def add_edge(adj,u,v,w):
    adj[u].append((v,w)); adj[v].append((u,w))


def dijkstra_count(adj, src, banned=None):
    n=len(adj); inf=10**30
    d=[inf]*n; c=[0]*n
    d[src]=0; c[src]=1
    pq=[(0,src)]
    while pq:
        du,u=heapq.heappop(pq)
        if du!=d[u]: continue
        for v,w in adj[u]:
            if banned is not None and ((u,v)==banned or (v,u)==banned):
                continue
            nd=du+w
            if nd<d[v]:
                d[v]=nd; c[v]=c[u]; heapq.heappush(pq,(nd,v))
            elif nd==d[v]:
                c[v]+=c[u]
    return d,c


def instance(m):
    # Boundary order: s=0, v=1, t_i=i+1 (i=1..m).
    k=m+2; r=k*k; A=3*m+2
    adj=[[] for _ in range(r)]
    add_edge(adj,0,1,1)             # e=(s,v)
    for x in range(1,m+1):          # v-t1-...-tm
        add_edge(adj,x,x+1,1)
    add_edge(adj,m+1,0,A)           # closing facial edge
    # Attach a unit-weight tree path at v outside the designated cycle face.
    prev=1
    for x in range(k,r):
        add_edge(adj,prev,x,1); prev=x
    return adj,k,r,A


def check(m):
    adj,k,r,A=instance(m)
    # Global uniqueness in P: all pairs have exactly one shortest path.
    for s in range(r):
        _,cnt=dijkstra_count(adj,s)
        if any(x!=1 for x in cnt):
            raise AssertionError((m,'nonunique',s,max(cnt)))
    d0,_=dijkstra_count(adj,0)
    dq,_=dijkstra_count(adj,0,banned=(0,1))
    boundary=list(range(k))
    expected=[4*m+1] + [4*m+1-2*i for i in range(1,m+1)]
    slack=[dq[t]-d0[t] for t in boundary[1:]]
    if slack!=expected:
        raise AssertionError((m,'slack',slack,expected))
    if len(set(slack))!=k-1:
        raise AssertionError((m,'distinct',slack))
    if not all(slack[i]>slack[i+1] for i in range(len(slack)-1)):
        raise AssertionError((m,'not-strictly-decreasing',slack))
    delta=4*m+2
    # Build updated graph by changing e from 1 to 1+delta.
    adjp=[lst[:] for lst in adj]
    for u,v in [(0,1),(1,0)]:
        for j,(x,w) in enumerate(adjp[u]):
            if x==v:
                adjp[u][j]=(x,1+delta)
                break
    dp,_=dijkstra_count(adjp,0)
    corr=[dp[t]-d0[t] for t in boundary[1:]]
    if corr!=slack:
        raise AssertionError((m,'correction',corr,slack))
    return {
        'm':m,'k':k,'r':r,'A':A,'delta':delta,
        'affected_targets':k-1,'distinct_corrections':len(set(corr)),
        'first_correction':corr[0],'last_correction':corr[-1]
    }

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--out', default=None, help='Output JSON path')
    args=ap.parse_args()
    rows=[check(m) for m in range(1,31)]
    out={
        'status':'PASS',
        'arithmetic':'exact integers',
        'checked_m_range':[1,30],
        'checked_k_range':[3,32],
        'instances':len(rows),
        'checks':rows
    }
    path=Path(args.out) if args.out else Path(__file__).resolve().parent.parent.parent/'raw_data'/'constant_patch_lower_bound_check.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','arithmetic','checked_m_range','checked_k_range','instances']},indent=2))

if __name__ == '__main__':
    main()
