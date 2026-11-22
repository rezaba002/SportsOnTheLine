import re,sys
def conv(fn):
    lines=open(fn,encoding='utf8').read().splitlines(); out=[]; t=None; last=''
    for l in lines:
        m=re.match(r'(\d\d):(\d\d):(\d\d)\.\d+ -->',l)
        if m: t=f"{int(m.group(1))*60+int(m.group(2))}:{m.group(3)}"; continue
        txt=re.sub(r'<[^>]+>','',l).strip()
        if not txt or txt==last or txt.startswith(('WEBVTT','Kind:','Language:')): continue
        out.append(f"[{t}] {txt}"); last=txt
    # dedupe rolling captions
    res=[];prev=''
    for o in out:
        body=o.split('] ',1)[1]
        if body in prev: continue
        res.append(o); prev=body
    return res
for fn in sys.argv[1:]:
    r=conv(fn); open(fn.replace('.en.vtt','.txt'),'w',encoding='utf8').write('\n'.join(r)); print(fn,len(r))
