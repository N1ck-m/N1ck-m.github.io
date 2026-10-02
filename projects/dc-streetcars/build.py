import pathlib,re,json
p=pathlib.Path(__file__).resolve().parent;s=(p/'legacy/index.html').read_text()
draft=json.loads((p/'legacy/dcsc-draft-20260930.json').read_text())
match=re.search(r'(<script[^>]*id="d-lines"[^>]*>)(.*?)(</script>)',s,re.S)
d=json.loads(match[2]);d['version']='dcsc-profile-v2-sep30';d['model']={'nodes':draft['n'],'ways':[dict(id=x[0],nodes=x[1],tags=x[2],u=x[3]) for x in draft['w']],'relations':[dict(id=x[0],kind=x[1],line=x[2],tags=x[3],members=x[4]) for x in draft['r']]}
for r in d['model']['relations']:
 r['meta']={'status':'provisional','researchIds':[d['lines'][r['line']]['id']] if r['line'] is not None else []}
 if 'railway:traction' in r['tags']:r['tags']['streetcar:traction']=r['tags']['railway:traction']
s=s[:match.start(2)]+json.dumps(d,separators=(',',':'))+s[match.end(2):]
s=s.replace("const KEY='dcsc-model-v1'","const KEY='dcsc-model-v2'")
s=s.replace('  MODEL.nodes.clear();MODEL.ways.clear();MODEL.rels.clear();',"  MODEL.meta={schema:2,baseline:'cb278c36c1e2',migration:'Claude September 30 draft'};MODEL.nodes.clear();MODEL.ways.clear();MODEL.rels.clear();",1)
s=s.replace('members:r.members.map(m=>({...m}))','members:r.members.map(m=>({...m})),meta:JSON.parse(JSON.stringify(r.meta||{status:\'provisional\'}))',1)
s=s.replace('u:w.u?w.u.map(x=>x.slice()):null','u:null,meta:{geometryStatus:\'osm-derived\',sources:[]}',1)
start=s.index('  function snapshot()');end=s.index('  function persist()',start)
s=s[:start]+"  function snapshot(){return JSON.stringify(DCProfile.archive(MODEL,changed,DATA.version));}\n  function restore(s){changed=DCProfile.restore(MODEL,s);}\n"+s[end:]
s=s.replace('const ok=fn(); if(ok===false) return;',"const prior=new Set(DCProfile.validate(MODEL).filter(x=>x.sev==='error').map(x=>x.code+':'+x.type+':'+x.id+':'+x.msg));let ok;try{ok=fn();const introduced=DCProfile.validate(MODEL).find(x=>x.sev==='error'&&!prior.has(x.code+':'+x.type+':'+x.id+':'+x.msg));if(introduced)throw Error(introduced.msg);if(ok===false){restore(before);return;}}catch(e){restore(before);sel=selNow;rebuild();status(e.message);return;} ")
s=s.replace('if(!mw.u) mw.u=deriveUsers','mw.u=deriveUsers')
s=s.replace('return [n.lat,n.lon];}); if(p.length<2)', 'return n?[n.lat,n.lon]:null;}).filter(Boolean); if(p.length<2)')
s=s.replace('persist(); rebuild(); status(label);',"MODEL.meta={...MODEL.meta,audit:[...(MODEL.meta?.audit||[]),{at:new Date().toISOString(),label,category:/^(Historical|Split physical)/.test(label)?'historical transition':'correction or research edit'}].slice(-1000)};persist(); rebuild(); status(label);")
# Keep legacy corridor editing away from passenger service states.
s=s.replace("r.kind==='route'&&r.line===li&&r.tags.start_date","r.kind==='route'&&r.tags['public_transport:version']!=='2'&&r.line===li&&r.tags.start_date")
s=s.replace("r.kind==='route'&&r.line===li&&!r.members.length","r.kind==='route'&&r.tags['public_transport:version']!=='2'&&r.line===li&&!r.members.length")
s=s.replace("r.kind==='chronology'&&r.line===li","r.kind==='chronology'&&!r.meta?.serviceId&&r.line===li")
s=s.replace('Lines using this track','Research corridors using this track')
s=s.replace("Adds or removes this track in the line\\'s dated routes","Edits provisional research associations in the corridor\\'s dated records")
# Every numeric boundary display conversion respects month/day precision.
s=re.sub(r'''(?<![\w'"\)\]])\+([a-zA-Z][\w.]*)\.tags\.(start_date|end_date)''',r'DCProfile.number(\1.tags.\2)',s)
s=s.replace("r.members.map(m=>m.ref).sort(),r.tags.operator||'',r.tags['railway:traction']||'',r.tags.ref||''", "DCProfile.stateKey(r)")
s=s.replace("operator:tmpl?tmpl.tags.operator:''","operator:''")
# Keep ordered occurrences; sorting may only reorder chronology dates.
a=s.index('  function sortMembers(r)');b=s.index('\n  function ',a+15)
s=s[:a]+"  function sortMembers(r){if(r.kind==='chronology')r.members.sort((a,b)=>DCProfile.number(MODEL.rels.get(a.ref)?.tags.start_date)-DCProfile.number(MODEL.rels.get(b.ref)?.tags.start_date));else if(r.tags['public_transport:version']==='2')DCProfile.path(MODEL,r);}\n"+s[b:]
a=s.index('  function split(nid,ways)');b=s.index('  function sameMembership',a)
s=s[:a]+"  function split(nid,ways){act('Split track and every route occurrence',()=>ways.forEach(w=>DCProfile.splitWay(MODEL,w.id,nid)));}\n"+s[b:]
a=s.index('  function combine(a,b,shared)');b=s.index('  function mergeCandidates',a)
s=s[:a]+"  function combine(a,b,shared){return DCProfile.combineWays(MODEL,a.id,b.id,shared);}\n"+s[b:]
a=s.index('  function validate()');s=s[:a]+s[a:].replace('  function validate(){','  function legacyValidate(){',1)
# Legacy validation UI now reports formal errors and separate evidence blockers.
s=s.replace('  function legacyValidate(){','  function validate(){return DCProfile.validate(MODEL).concat(DCProfile.crossings(MODEL));}\n  function legacyValidate(){',1)
s=s.replace("{railway:'tram',gauge:'1435'}","{railway:'tram'}")
s=s.replace("const iss=validate(); const el=$('edInspector');","const iss=validate(); const el=$('edInspector');")
s=s.replace("'<ul class=\"ed-list\">'+iss.slice(0,200)","'<p class=\"note\">'+iss.filter(x=>x.sev==='error').length+' structural errors; '+iss.filter(x=>x.sev==='blocker').length+' publication blockers; '+iss.filter(x=>x.sev==='warning').length+' review warnings. Showing up to 200 issues.</p><ul class=\"ed-list\">'+iss.slice(0,200)")
s=s.replace("$('edExport').onclick=exportXml","$('edExport').onclick=exportPanel")
s=s.replace('<button type="button" class="btn" id="edExport">Export .osm</button>','<button type="button" class="btn" id="edExport">Export / import</button><button type="button" class="btn" id="edServices">Services &amp; evidence</button>')
s=s.replace("  // wire the toolbar",(p/'workbench.js').read_text()+"\n  $('edServices').onclick=servicePanel;\n  // wire the toolbar")
s=s.replace("  let stale=null;", "  let stale=null;")
s=s.replace('https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js','vendor/leaflet/leaflet.js').replace('https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css','vendor/leaflet/leaflet.css')
s=s.replace("</head>",'<script>'+ (p/'temporal.js').read_text()+'</script>\n</head>')
# Expose stable, read/write test and integration API; editor commands retain undo boundaries.
s=s.replace('const editBtn=document.getElementById',"window.DCStreetcars={model:MODEL,profile:DCProfile,editor:Ed};\nconst editBtn=document.getElementById")
s=s.replace('return {renderEdit,refresh,mapClick', 'return {servicePanel,exportPanel,snapshot,restore,act,rebuild,doUndo,doRedo,renderEdit,refresh,mapClick')
# Exact-date inspection and a service-only overlay; the research map remains the default.
s=s.replace('<input type="range" id="slider"','<label style="font-size:12px">Inspect date <input type="date" id="viewDate" value="1917-01-01" min="1862-01-01" max="1962-12-31"></label><label style="font-size:12px"><input type="checkbox" id="serviceView"> Verified services only</label><input type="range" id="slider"')
s=s.replace("document.getElementById('year').textContent=year;","document.getElementById('year').textContent=Math.floor(year);")
s=s.replace("document.getElementById('dockYear').textContent=year;","document.getElementById('dockYear').textContent=Math.floor(year);")
s=s.replace("document.getElementById('nLines').textContent=nByYear[year];","document.getElementById('nLines').textContent=new Set(WAYS.flatMap(w=>wayActive(w,year).filter(i=>i>=0))).size;")
s=s.replace("document.getElementById('nKm').textContent=Math.round(kmByYear[year]);","document.getElementById('nKm').textContent=Math.round(WAYS.reduce((sum,w)=>sum+(wayActive(w,year).length?w.km:0),0));")
s=s.replace("function wayActive(w,y){return", "function wayActive(w,y){if(document.getElementById('serviceView').checked){const routes=[...MODEL.rels.values()].filter(r=>r.tags['public_transport:version']==='2'&&r.meta?.status==='verified'&&DCProfile.number(r.tags.start_date)<=y&&y<DCProfile.number(r.tags.end_date)&&r.members.some(m=>m.type==='way'&&m.ref===w.id));return routes.length?[...new Set(routes.map(r=>r.line??-1))]:[];}return")
s=s.replace("slider.addEventListener('input',()=>setYear(+slider.value));", "slider.addEventListener('input',()=>{document.getElementById('viewDate').value=slider.value+'-01-01';setYear(+slider.value);});\ndocument.getElementById('viewDate').onchange=e=>{try{const y=DCProfile.number(e.target.value);if(!Number.isFinite(y))throw Error('Invalid date');year=y;render();}catch(error){e.target.setCustomValidity(error.message);e.target.reportValidity();}};\ndocument.getElementById('serviceView').onchange=()=>render();")
s=s.replace("if(sel.type==='relation'){const r=MODEL.rels.get(sel.ids[0]); if(r) r.members.forEach(m=>{if(m.type==='way')relWays.add(m.ref);});}", "if(sel.type==='relation'){const visited=new Set();const descend=id=>{if(visited.has(id))return;visited.add(id);const r=MODEL.rels.get(id);if(r)r.members.forEach(m=>{if(m.type==='way')relWays.add(m.ref);else if(m.type==='relation')descend(m.ref);});};descend(sel.ids[0]);}")

(p/'index.html').write_text(s)
(p/'exports/dcsc-project-v2.json').write_text(json.dumps({'schema':2,'base':d['version'],'meta':{'schema':2,'baseline':'cb278c36c1e2','migration':'Sep30 Claude draft, preserved research corridors'},'n':[x+[{}] for x in draft['n']],'w':[x+[{'geometryStatus':'osm-derived','sources':[]}] for x in draft['w']],'r':[[r['id'],r['kind'],r['line'],r['tags'],r['members'],r['meta']] for r in d['model']['relations']],'c':0},indent=2))
