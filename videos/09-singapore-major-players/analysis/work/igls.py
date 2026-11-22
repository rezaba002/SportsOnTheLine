"""IGLs of the Major teams from the saved Liquipedia team pages -> research/igls.json
Active squad: {{Person|...|id=X|...|igl=y}} inside the first {{Squad|status=active}} block.
Fallback: the infobox line |igl=... [[X]]."""
import glob, json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
out = {}
for f in sorted(glob.glob(os.path.join(ROOT, "research", "liquipedia", "*.wiki"))):
    t = open(f, encoding="utf-8").read()
    team = os.path.basename(f)[:-5].replace("_", " ")
    igl, src = [], None
    m = re.search(r"\{\{Squad\|status=active(?!\|type=staff).*?(?=\{\{Squad\|)", t, re.S)
    if m:
        for p in re.findall(r"\{\{Person\|([^{}]*(?:\{\{[^{}]*\}\}[^{}]*)*)\}\}", m.group(0)):
            if re.search(r"\|\s*igl\s*=\s*y", p):
                pid = re.search(r"\|\s*id\s*=\s*([^|}\n]+)", p)
                if pid: igl.append(pid.group(1).strip()); src = "squad"
    if not igl:
        ib = re.search(r"^\|igl=(.*)$", t, re.M)
        if ib:
            igl = [x.split("|")[-1].strip() for x in re.findall(r"\[\[([^\]]+)\]\]", ib.group(1))]; src = "infobox"
    out[team] = {"igl": igl, "source": src}
    print(f"{team:>20}: {igl} ({src})")
json.dump(out, open(os.path.join(ROOT, "research", "igls.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
