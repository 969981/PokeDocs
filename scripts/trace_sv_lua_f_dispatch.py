#!/usr/bin/env python3
"""Trace original Lua 5.4 F fields, receiver origins, and static SELF->CALL paths.

Reads native bytecode without running it. A static dispatch path is not proof
that the path was executed or that its dynamically selected callee is known.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
from collections import Counter
from pathlib import Path
from trace_sv_lua_c2f import AssignmentReader, opcode, reg_a, reg_b, reg_c
from inspect_sv_blua import load_hashlists

GETUPVAL, GETTABUP, GETI, GETFIELD = 9, 11, 13, 14
SETFIELD, SELF, CALL, CLOSURE, JMP, EQK = 18, 20, 68, 79, 56, 60
LOADK, MOVE, VARARG = 3, 0, 80
BRANCHES = {56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 73, 74, 75, 77}
TERMINATORS = {69, 70, 71, 72}


def const_key(word, constants):
    op = opcode(word)
    if op in (11, 14) or (op == 20 and ((word >> 15) & 1)):
        return constants.get(reg_c(word))
    if op in (15, 18):
        return constants.get(reg_b(word))
    return None


def writes_register(word, register):
    """Conservative Lua 5.4 register-kill test, including variable CALL results."""
    op, a, b, c = opcode(word), reg_a(word), reg_b(word), reg_c(word)
    single = {0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 19, 21, 22, 23,
              24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
              39, 40, 41, 42, 43, 44, 45, 49, 50, 51, 52, 53, 67, 79}
    if op in single:
        return register == a
    if op == 8:
        return a <= register <= a+b
    if op == SELF:
        return register == a or register == a+1
    if op in (CALL, VARARG):
        return register >= a if c == 0 else a <= register < a+c-1
    if op in (73, 74):
        return a <= register <= a+3
    if op in (76, 77):
        return a <= register <= a+max(c+3, 3)
    if op == 81:
        return True
    return False


def last_writer(code, pc, reg):
    """Only use a straight-line predecessor; no fabricated CFG phi nodes."""
    for prev in range(pc-1, -1, -1):
        if writes_register(code[prev], reg):
            if any(opcode(x) in BRANCHES | TERMINATORS for x in code[prev+1:pc]):
                return None, 'UNKNOWN_CONTROL_FLOW'
            return prev, 'DIRECT_PREDECESSOR'
    return None, 'NO_WRITER'


def origin(code, pc, reg, constants, nparams, depth=0):
    if depth > 6:
        return {'kind':'UNKNOWN_DEPTH','register':reg}
    prev, status = last_writer(code, pc, reg)
    if status == 'UNKNOWN_CONTROL_FLOW':
        return {'kind':status,'register':reg}
    if prev is None:
        return ({'kind':'FORMAL_PARAMETER','register':reg,'parameter_index':reg}
                if reg < nparams else {'kind':'UNDEFINED_OR_INHERITED','register':reg})
    word = code[prev]
    op, a, b, c = opcode(word), reg_a(word), reg_b(word), reg_c(word)
    meta = {'writer_pc':prev,'register':reg}
    if op == MOVE:
        return {'kind':'MOVE',**meta,'source':origin(code,prev,b,constants,nparams,depth+1)}
    if op == GETI:
        return {'kind':'INDEXED_TABLE',**meta,'index':c,
                'table':origin(code,prev,b,constants,nparams,depth+1)}
    if op == GETFIELD:
        return {'kind':'NAMED_FIELD',**meta,
                'key':(constants.get(c) or b'').decode('ascii','replace'),
                'table':origin(code,prev,b,constants,nparams,depth+1)}
    if op == GETUPVAL:
        return {'kind':'UPVALUE',**meta,'upvalue_index':b}
    if op == GETTABUP:
        return {'kind':'UPVALUE_FIELD',**meta,'upvalue_index':b,
                'key':(constants.get(c) or b'').decode('ascii','replace')}
    if op == SELF:
        return {'kind':'SELF_METHOD_OR_RECEIVER',**meta}
    if op == CALL:
        return {'kind':'CALL_RESULT_UNRESOLVED',**meta,'func_reg':a,'arg_B':b,'result_C':c}
    if op == LOADK:
        idx = (word >> 15) & 131071
        return {'kind':'CONSTANT',**meta,'constant_index':idx,
                'string':(constants.get(idx) or b'').decode('ascii','replace')}
    if op == VARARG:
        return {'kind':'VARARG_VALUE',**meta}
    if op == CLOSURE:
        return {'kind':'CLOSURE',**meta,'child_index':(word >> 15)&131071}
    if op == 19:
        return {'kind':'LOCAL_NEW_TABLE',**meta}
    if op == 8:
        return {'kind':'NIL',**meta}
    return {'kind':'UNKNOWN_PRODUCER_OPCODE',**meta,'opcode':op}


def call_after_self(code, pc, dest, max_span=12):
    """Require SAME callee register and no intervening write/branch/termination."""
    for cp in range(pc+1, min(len(code), pc+max_span+1)):
        word, op = code[cp], opcode(code[cp])
        if op in BRANCHES | TERMINATORS:
            return None
        if op == CALL and reg_a(word) == dest:
            if reg_b(word) < 2:
                return None
            return {'call_pc':cp,'callee_reg':dest,'argument_B':reg_b(word),
                    'return_C':reg_c(word),'distance':cp-pc,'self_register':dest+1}
        if writes_register(word,dest) or writes_register(word,dest+1):
            return None
    return None


def get_header(reader, offset):
    saved = reader.pos
    try:
        reader.pos = offset
        reader.lua_string(); reader.integer(); reader.integer()
        return reader.byte(), reader.byte(), reader.byte()
    finally:
        reader.pos = saved


class FDispatchReader(AssignmentReader):
    def __init__(self, file, unknown_f):
        super().__init__(file)
        self.target_unknown_f = set(unknown_f)
        self.field_sites = []

    def trace(self, offset, ncode, constants, children, nup, proto, proto_offset):
        super().trace(offset, ncode, constants, children, nup, proto, proto_offset)
        if not any(re.fullmatch(rb'F[0-9A-F]{16}', s) and
                   int(s[1:], 16) in self.target_unknown_f
                   for s in constants.values() if s):
            return
        nparams, _, _ = get_header(self,proto_offset)
        code = struct.unpack_from(f'<{ncode}I',self.data,offset)
        for pc,word in enumerate(code):
            op = opcode(word)
            if op not in (GETFIELD,SETFIELD,SELF):
                continue
            key = const_key(word, constants)
            if not key or not re.fullmatch(rb'F[0-9A-F]{16}',key):
                continue
            if int(key[1:],16) not in self.target_unknown_f:
                continue
            base_reg = reg_b(word) if op in (GETFIELD,SELF) else reg_a(word)
            row = {'file':self.file.name,'proto':proto,'pc':pc,
                   'byte_offset':offset+pc*4,
                   'opcode':{GETFIELD:'GETFIELD',SETFIELD:'SETFIELD',SELF:'SELF'}[op],
                   'hash':'0x'+key[1:].decode('ascii'),
                   'receiver_reg':base_reg,
                   'receiver_origin':origin(code,pc,base_reg,constants,nparams),
                   'nparams':nparams,
                   'constant_index':reg_c(word) if op in (GETFIELD,SELF) else reg_b(word)}
            if op == SETFIELD:
                row['value_origin'] = (origin(code,pc,reg_c(word),constants,nparams)
                       if not ((word>>15)&1) else
                       {'kind':'CONSTANT','constant_index':reg_c(word)})
            if op == GETFIELD:
                row['getfield_destination'] = reg_a(word)
            if op == SELF:
                row['call'] = call_after_self(code,pc,reg_a(word))
                row['preceding_guard_getfield_pc'] = None
                row['guard_jmp_pc'] = None
                row['guard_jump_target_pc'] = None
                if row['call']:
                    for gp in range(max(0,pc-6),pc):
                        if gp+3 != pc:
                            continue
                        g,cond,jmp = code[gp],code[gp+1],code[gp+2]
                        target = gp+3 + ((jmp>>7) - ((1<<25)-1)//2)
                        if (opcode(g)==GETFIELD and reg_b(g)==base_reg and
                            const_key(g,constants)==key and
                            opcode(cond)==60 and reg_a(cond)==reg_a(g) and
                            opcode(jmp)==JMP and
                            target==row['call']['call_pc']+1):
                            row['preceding_guard_getfield_pc']=gp
                            row['guard_jmp_pc']=gp+2
                            row['guard_jump_target_pc']=target
            self.field_sites.append(row)

    def analyze(self):
        original = self.scan_assignments()
        owners = {(x['file'],x['closure_proto']):x for x in self.assignments}
        for row in self.field_sites:
            owner=owners.get((row['file'],row['proto']))
            row['containing_method'] = (
                {'class_hash':owner['class_hash'],
                 'method_hash':owner['function_hash']}
                if owner else None)
        return original


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('files',nargs='+',type=Path)
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--game',choices=('SV','ZA'),default='SV')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    unknown,_=load_hashlists(a.repo,a.game)
    sites,files=[],[]
    for f in a.files:
        r=FDispatchReader(f,unknown['F'])
        files.append(r.analyze())
        sites.extend(r.field_sites)
        print(f'{f.name}: {len(r.field_sites)} unknown F field sites')
    opcounts=Counter(x['opcode'] for x in sites)
    selfs=[x for x in sites if x['opcode']=='SELF']
    report={'source':'original user Library Lua5.4 files, not executed',
            'version_limit':'Lua 5.4 header cannot authenticate game version',
            'files':files,'unmapped_F_in_hashlist':len(unknown['F']),
            'opcodes':dict(opcounts),'field_sites':len(sites),
            'distinct_F':len({x['hash'] for x in sites}),
            'static_SELF_to_CALL':sum(x['call'] is not None for x in selfs),
            'guarded_SELF_to_CALL':sum(x['preceding_guard_getfield_pc'] is not None for x in selfs),
            'all_SELF_receivers_are_unchanged_first_parameter':all(
                x['receiver_reg']==0 and
                x['receiver_origin']['kind']=='FORMAL_PARAMETER' for x in selfs),
            'evidence':'STATIC_LUA54_FIELD_DISPATCH_NOT_RUNTIME_EXECUTION',
            'limitation':'No target closure or original F name is proven by SELF/CALL alone.',
            'records':sites}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('files','records')},ensure_ascii=False))


if __name__=='__main__':
    main()
