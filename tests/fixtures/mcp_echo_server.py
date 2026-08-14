from __future__ import annotations
import json, sys

TOOLS = [
    {"name":"echo","description":"Return supplied text","inputSchema":{"type":"object","properties":{"text":{"type":"string"}}}},
    {"name":"mutate","description":"Qualification-only mutating tool","inputSchema":{"type":"object"}},
]

for line in sys.stdin:
    if not line.strip():
        continue
    msg=json.loads(line)
    method=msg.get('method')
    if method=='notifications/initialized':
        continue
    ident=msg.get('id')
    if method=='initialize':
        result={"protocolVersion":"2025-06-18","capabilities":{"tools":{}},"serverInfo":{"name":"grox-a5-qualification","version":"1"}}
    elif method=='tools/list':
        result={"tools":TOOLS}
    elif method=='tools/call':
        name=msg.get('params',{}).get('name')
        args=msg.get('params',{}).get('arguments') or {}
        if name=='echo':
            result={"content":[{"type":"text","text":str(args.get('text',''))}],"isError":False}
        elif name=='mutate':
            result={"content":[{"type":"text","text":"mutated"}],"isError":False}
        else:
            sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":ident,"error":{"code":-32601,"message":"unknown tool"}})+'\n'); sys.stdout.flush(); continue
    else:
        sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":ident,"error":{"code":-32601,"message":"unknown method"}})+'\n'); sys.stdout.flush(); continue
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":ident,"result":result})+'\n'); sys.stdout.flush()
