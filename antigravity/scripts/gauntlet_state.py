#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from datetime import datetime,timezone

def now(): return datetime.now(timezone.utc).isoformat()
def load(p): return json.loads(Path(p).read_text())
def save(p,o):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(o,indent=2)+'\n'); t.replace(p)
def main():
 a=argparse.ArgumentParser(); a.add_argument('--path',default='.gauntlet/state.json'); s=a.add_subparsers(dest='cmd',required=True)
 x=s.add_parser('init'); x.add_argument('--task',required=True); x.add_argument('--max-iterations',type=int,default=4); x.add_argument('--min-score',type=float,default=.90)
 s.add_parser('show'); x=s.add_parser('round'); x.add_argument('--score',type=float,required=True); x.add_argument('--verdict',choices=['PASS','REVISE','FAIL','BEST_EFFORT'],required=True); x.add_argument('--blocking-issue',action='append',default=[])
 z=a.parse_args(); p=Path(z.path)
 if z.cmd=='init': save(p,{'task':z.task,'iteration':0,'max_iterations':z.max_iterations,'minimum_judge_score':z.min_score,'history':[],'verdict':'RUNNING','created_at':now(),'updated_at':now()}); print(p)
 elif z.cmd=='show': print(json.dumps(load(p),indent=2))
 else:
  o=load(p); o['iteration']+=1; r={'iteration':o['iteration'],'judge_score':z.score,'verdict':z.verdict,'blocking_issues':z.blocking_issue,'timestamp':now()}; o['history'].append(r); o['verdict']=z.verdict; o['updated_at']=now(); save(p,o); print(json.dumps(r,indent=2))
if __name__=='__main__': main()
