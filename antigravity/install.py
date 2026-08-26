#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,shutil,subprocess
from pathlib import Path

NAME='gauntlet-loop'; SRC=Path(__file__).resolve().parent

def patch(dest):
    p=dest/'mcp_config.json'; o=json.loads(p.read_text()); o['mcpServers']['gauntlet-router']['args']=[str((dest/'servers/gauntlet_mcp.py').resolve())]; p.write_text(json.dumps(o,indent=2)+'\n')

def install(dest):
    if dest.exists(): shutil.rmtree(dest)
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(SRC,dest,ignore=shutil.ignore_patterns('*.zip','__pycache__','.git','.DS_Store'))
    patch(dest)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--workspace',help='Install into <workspace>/.agents/plugins/gauntlet-loop'); args=ap.parse_args()
    if args.workspace: dest=Path(args.workspace).expanduser().resolve()/'.agents/plugins'/NAME; scope='workspace'
    else: dest=Path.home()/'.gemini/antigravity-cli/plugins'/NAME; scope='global'
    install(dest); print(f'Installed {NAME} ({scope}) -> {dest}'); print(f'MCP server -> {dest/"servers/gauntlet_mcp.py"}')
    agy=shutil.which('agy')
    if agy:
        try:
            r=subprocess.run([agy,'plugin','list'],capture_output=True,text=True,timeout=20); print('\nAntigravity plugin discovery:'); print((r.stdout or r.stderr).strip()[:4000])
        except Exception as e: print(f"\nCould not run 'agy plugin list': {e}")
    else: print("\n'agy' not found on PATH. Restart Antigravity/CLI and use /skills, /agents, /mcp to verify discovery.")
    print('\nUse: /gauntlet-loop <task>'); print('Provider check: /gauntlet-providers')
if __name__=='__main__': main()
