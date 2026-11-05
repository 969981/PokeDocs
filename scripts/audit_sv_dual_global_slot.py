#!/usr/bin/env python3
"""Proof of root-level _ENV[C] key equality for SV 95 dual-evidence classes.

Requires the user's original SV 4.0.0 main.blua and Lua54 parser; neither
is uploaded. Structural bytecode proof, NOT runtime object identity or name recovery.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import re
from collections import defaultdict, Counter
from pathlib import Path

EXPECTED_MAIN_SHA = 'c1a4f4e2625912cf0b739a642a79ba3357df0557a544b92da22a6cb139de2815'
ROW = re.compile(r'^0x([A-Fa-f0-9]{16})(?:\s+(.*))?$')

def load_parser(path: Path):
    spec = importlib.util.spec_from_file_location('sv_lua54_native', path)
    if spec is None or spec.loader is None:
        raise ValueError('Unable to import Lua54 parser')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_tsv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))

def load_unknown(path: Path):
    result = set()
    for lineno, raw in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        if not raw.strip():
            continue
        m = ROW.fullmatch(raw.strip())
        if m is None:
            raise ValueError(f'Malformed Hashlist at line {lineno}')
        if not (m.group(2) or '').strip():
            result.add('C' + m.group(1).upper())
    return result

def verify_global(I, K, cls, pc):
    op = I[pc:pc+5]
    if len(op) != 5 or tuple(x[0] for x in op) != ('GETUPVAL','LOADK','MOVE','CALL','SETTABLE'):
        return False, None
    a = op[0][1]
    valid = (op[0][2] == 0 and op[1][1] == a + 1 and
             op[1][5] < len(K) and K[op[1][5]] == cls.encode() and
             op[2][1] == a + 2 and op[3][1] == a + 2 and
             op[3][2] == 1 and op[3][3] == 2 and
             op[4][1:4] == (a, a+1, a+2))
    return valid, (op[2][2] if valid else None)

def verify_static(I, K, root, row):
    pc = int(row['root_pc'])
    op = I[pc-1:pc+5]
    if len(op) != 6 or tuple(x[0] for x in op) != ('GETUPVAL','LOADK','GETTABLE','LOADK','CLOSURE','SETTABLE'):
        return False
    a = op[0][1]
    return (op[0][2] == 0 and op[1][1] == a+1 and
            op[1][5] < len(K) and K[op[1][5]] == row['class_hash'].encode() and
            op[2][1:4] == (a,a,a+1) and op[3][1] == a+1 and
            op[3][5] < len(K) and K[op[3][5]] == row['s_field_hash'].encode() and
            op[4][1] == a+2 and int(row['closure_child_index']) == op[4][5] and
            op[4][5] < len(root['children']) and
            root['children'][op[4][5]] == int(row['closure_proto_id']) and
            op[5][1:4] == (a,a+1,a+2))

def run(main: Path, parser: Path, static: Path, registrations: Path, hashlist: Path):
    raw = main.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_MAIN_SHA:
        raise ValueError(f'Unexpected original main.blua SHA256 {digest}')
    core = load_parser(parser)
    obj = core.Lua54(raw)
    obj.parse()
    root = obj.protos[0]
    I = core.instructions(raw, root)
    K = root['constants']
    unknown = load_unknown(hashlist)
    s = load_tsv(static)
    g = load_tsv(registrations)
    by_s, by_g = defaultdict(list), defaultdict(list)
    for row in s: by_s[row['class_hash']].append(row)
    for row in g: by_g[row['class_hash']].append(row)
    chosen = sorted(set(by_s) & set(by_g) & unknown)
    if len(chosen) != 95:
        raise ValueError(f'Current 95 C baseline changed: {len(chosen)}')
    result, failures = [], []
    for cls in chosen:
        gr, sr = by_g[cls], by_s[cls]
        valid_g, factory = [], []
        for row in gr:
            ok, register = verify_global(I,K,cls,int(row['root_pc'])) if row['source']=='main' else (False,None)
            valid_g.append(ok); factory.append(register)
        valid_s = [verify_static(I,K,root,row) if row['source']=='main' else False for row in sr]
        if not all(valid_g) or not all(valid_s):failures.append(cls)
        result.append({'class_hash':cls,'global_root_pc':';'.join(x['root_pc'] for x in gr),
            'static_root_pcs':';'.join(x['root_pc'] for x in sr),
            'global_slot_writes_verified':sum(valid_g),'global_slot_writes_total':len(gr),
            'static_slot_reads_verified':sum(valid_s),'static_slot_reads_total':len(sr),
            'factory_registers':';'.join(map(str,factory)),
            'same_root_upvalue_slot_verified':all(valid_g) and all(valid_s),
            'runtime_same_object_confirmed':False,'original_name_confirmed':False})
    return {'version':'SV 4.0.0', 'sha256_main':digest,
        'classes':len(chosen), 'global_writes_verified':sum(r['global_slot_writes_verified'] for r in result),
        'global_writes_total':sum(r['global_slot_writes_total'] for r in result),
        'static_reads_verified':sum(r['static_slot_reads_verified'] for r in result),
        'static_reads_total':sum(r['static_slot_reads_total'] for r in result),
        'factory_registers':dict(Counter(reg for r in result for reg in r['factory_registers'].split(';'))),
        'root_factory_proto_created_at_pc49':I[49][0]=='CLOSURE' and I[49][1]==15,
        'failed_classes':failures, 'confirmed_original_names':0,
        'runtime_receiver_identity_confirmed':0,
        'boundary':'Same root _ENV upvalue/key, not proven unchanged table value across intervening calls.'}, result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main',type=Path,required=True)
    ap.add_argument('--parser',type=Path,required=True)
    ap.add_argument('--static',type=Path,required=True)
    ap.add_argument('--registrations',type=Path,required=True)
    ap.add_argument('--hashlist',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    summary, rows=run(args.main,args.parser,args.static,args.registrations,args.hashlist)
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'sv-95-global-slot-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (args.out/'sv-95-global-slot-audit.tsv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys(),delimiter='\t',lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
