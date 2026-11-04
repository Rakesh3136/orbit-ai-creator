from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
import secrets
from urllib.parse import urlparse

from orbit.learning.feedback import LearningMemory


_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ORBIT Owner Control Centre</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#10141c;color:#edf2fa}
body{max-width:1100px;margin:0 auto;padding:24px}h1{margin-bottom:4px}.muted{color:#9eacc0}
.panel{background:#1a2230;border:1px solid #303d50;border-radius:14px;padding:18px;margin:18px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.metric{font-size:1.7rem;font-weight:700}.item{border-top:1px solid #344155;padding:16px 0}
label{display:block;margin:10px 0 5px}input,select,textarea{box-sizing:border-box;width:100%;padding:10px;border-radius:8px;border:1px solid #53647b;background:#111925;color:#fff}
textarea{min-height:72px}button{background:#80b7ff;color:#07111e;border:0;border-radius:8px;padding:10px 15px;font-weight:700;cursor:pointer}
button:disabled{opacity:.5}small{color:#aebbd0}.row{display:flex;gap:12px;flex-wrap:wrap}.row>*{flex:1}
.status{margin-left:8px;color:#a8dfb5}
</style></head><body>
<h1>ORBIT Owner Control Centre</h1><div class="muted">Local-only review desk · feedback stays on this machine</div>
<section class="panel"><h2>Agent performance</h2><div id="metrics" class="cards"></div><div class="row"><div><label for="agent">Agent</label><select id="agent"></select></div><div><label for="task">Task type (optional)</label><input id="task" placeholder="e.g. script"></div></div><button id="refresh">Refresh dashboard</button></section>
<section class="panel"><h2>Outputs awaiting review</h2><div id="queue" class="muted">Loading…</div></section>
<section class="panel"><h2>Recent owner reviews</h2><div id="reviews" class="muted">Loading…</div></section>
<script>
const token=__TOKEN__;
const $=id=>document.getElementById(id);
const esc=s=>String(s??"");
async function get(path){const r=await fetch(path);if(!r.ok)throw Error(await r.text());return r.json()}
function el(tag,text,cls){const n=document.createElement(tag);n.textContent=text;if(cls)n.className=cls;return n}
async function load(){
 const [queue,reviews]=await Promise.all([get('/api/queue'),get('/api/reviews')]);
 $('queue').replaceChildren(); $('reviews').replaceChildren();
 const agents=[...new Set(queue.items.map(x=>x.agent).concat(reviews.items.map(x=>x.agent)))].sort();
 $('agent').replaceChildren(...agents.map(a=>{const o=document.createElement('option');o.value=a;o.textContent=a;return o}));
 if(!agents.length)$('agent').append(el('option','No agent data'));
 if(!queue.items.length)$('queue').append(el('p','No outputs are currently awaiting review.','muted'));
 for(const item of queue.items){
  const box=el('article','', 'item');
  box.append(el('h3','#'+item.id+' · '+item.agent+' / '+item.task_type));
  box.append(el('p','Automatic quality score: '+item.overall.toFixed(1)+' / 100 · '+JSON.stringify(item.scores)));
  if(item.feedback)box.append(el('p','Pipeline notes: '+item.feedback));
  const form=document.createElement('form');
  const rating=document.createElement('select');rating.required=true;
  for(let n=1;n<=5;n++){const o=document.createElement('option');o.value=n;o.textContent=n+' / 5';rating.append(o)}
  const correction=document.createElement('textarea');correction.placeholder='What should the agent correct?';
  const lesson=document.createElement('textarea');lesson.placeholder='Reusable lesson (optional)';
  const scope=document.createElement('select');
  for(const v of ['network','channel']){const o=document.createElement('option');o.value=v;o.textContent=v;scope.append(o)}
  const scopeId=document.createElement('input');scopeId.value='default';scopeId.placeholder='Network/channel ID';
  const approve=document.createElement('input');approve.type='checkbox';
  const approveLabel=el('label','Approve this lesson for future matching tasks');approveLabel.prepend(approve);
  const submit=el('button','Save review');submit.type='submit';
  for(const [label,node] of [['Rating',rating],['Correction',correction],['Lesson',lesson],['Scope',scope],['Scope ID',scopeId]]){form.append(el('label',label));form.append(node)}
  form.append(approveLabel,submit);
  const status=el('span','');
  form.onsubmit=async ev=>{ev.preventDefault();submit.disabled=true;try{
   const r=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json','X-ORBIT-Token':token},body:JSON.stringify({evaluation_id:item.id,rating:Number(rating.value),correction:correction.value,lesson:lesson.value,scope_type:scope.value,scope_id:scopeId.value,approve_lesson:approve.checked})});
   const data=await r.json();if(!r.ok)throw Error(data.error||'Could not save review');status.textContent='Saved';await load();
  }catch(e){status.textContent=e.message;submit.disabled=false}};
  form.append(status);box.append(form);$('queue').append(box);
 }
 if(!reviews.items.length)$('reviews').append(el('p','No owner reviews recorded yet.','muted'));
 for(const r of reviews.items){const box=el('div','', 'item');box.append(el('strong','#'+r.id+' · evaluation #'+r.evaluation_id+' · '+r.rating+'/5'));box.append(el('p','Scope: '+r.scope_type+':'+r.scope_id+' · lesson approved: '+r.lesson_approved));if(r.correction)box.append(el('p','Correction: '+r.correction));if(r.lesson)box.append(el('p','Lesson: '+r.lesson));box.append(el('small','Provenance: '+r.provenance));$('reviews').append(box)}
 await metrics();
}
async function metrics(){const agent=$('agent').value;if(!agent){$('metrics').textContent='No evaluation data yet';return}
 const task=$('task').value;const data=await get('/api/performance?agent='+encodeURIComponent(agent)+'&task_type='+encodeURIComponent(task));
 $('metrics').replaceChildren(...[['Tasks',data.tasks],['Average score',data.average_score],['Passed',data.passed]].map(([k,v])=>{const d=el('div','','panel');d.append(el('div',k,'muted'),el('div',String(v),'metric'));return d}));
}
$('refresh').onclick=()=>load().catch(e=>{$('queue').textContent=e.message});
$('agent').onchange=()=>metrics().catch(e=>{$('metrics').textContent=e.message});
$('task').onchange=()=>metrics().catch(e=>{$('metrics').textContent=e.message});
load().catch(e=>{$('queue').textContent=e.message});
</script></body></html>"""


def _json(handler: BaseHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def serve(host: str = "127.0.0.1", port: int = 8765, db_path: str = "data/orbit-learning.sqlite3") -> None:
    if host not in {"localhost", "127.0.0.1", "::1"}:
        try:
            if not ipaddress.ip_address(host).is_loopback:
                raise ValueError("Dashboard must bind to a loopback address only.")
        except ValueError as exc:
            raise ValueError("Dashboard must bind to localhost/loopback only.") from exc

    memory = LearningMemory(db_path)
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        server_version = "ORBITLocalDashboard/1.0"

        def log_message(self, fmt: str, *args: object) -> None:
            return

        def _safe_host(self) -> bool:
            host_header = self.headers.get("Host", "").split(":", 1)[0].strip("[]").lower()
            return host_header in {"localhost", "127.0.0.1", "::1"}

        def do_GET(self) -> None:
            if not self._safe_host():
                _json(self, {"error": "Invalid Host header"}, 403)
                return
            path = urlparse(self.path)
            if path.path == "/":
                body = _PAGE.replace("__TOKEN__", json.dumps(token)).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            elif path.path == "/api/queue":
                items = memory.review_queue(limit=100)
                _json(self, {"items": [item.__dict__ for item in items]})
            elif path.path == "/api/reviews":
                items = memory.reviews(limit=50)
                _json(self, {"items": [item.__dict__ for item in items]})
            elif path.path == "/api/performance":
                from urllib.parse import parse_qs
                query = parse_qs(path.query)
                agent = query.get("agent", [""])[0]
                if not agent:
                    _json(self, {"error": "agent is required"}, 400)
                    return
                task = query.get("task_type", [""])[0] or None
                _json(self, memory.performance(agent, task))
            else:
                _json(self, {"error": "Not found"}, 404)

        def do_POST(self) -> None:
            if not self._safe_host():
                _json(self, {"error": "Invalid Host header"}, 403)
                return
            origin = self.headers.get("Origin")
            if origin and urlparse(origin).hostname not in {"localhost", "127.0.0.1", "::1"}:
                _json(self, {"error": "Cross-origin requests are not allowed"}, 403)
                return
            if self.headers.get("X-ORBIT-Token") != token:
                _json(self, {"error": "Missing or invalid local session token"}, 403)
                return
            if self.path != "/api/review":
                _json(self, {"error": "Not found"}, 404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 65536:
                    raise ValueError("Request body must be between 1 and 65536 bytes.")
                payload = json.loads(self.rfile.read(length))
                review_id = memory.submit_review(
                    evaluation_id=int(payload["evaluation_id"]),
                    rating=int(payload["rating"]),
                    correction=str(payload.get("correction", ""))[:10000],
                    lesson=str(payload.get("lesson", ""))[:10000],
                    scope_type=str(payload.get("scope_type", "network")),
                    scope_id=str(payload.get("scope_id", "default"))[:200],
                    provenance="owner:local-dashboard",
                    approve_lesson=bool(payload.get("approve_lesson", False)),
                )
                _json(self, {"review_id": review_id, "saved": True}, 201)
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
                _json(self, {"error": str(exc)}, 400)

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"ORBIT dashboard running at http://{host}:{port}")
    print("Local only. Keep this terminal open; press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nStopping ORBIT dashboard.")
    finally:
        server.server_close()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run the local ORBIT owner feedback dashboard.")
    parser.add_argument("--host", default="127.0.0.1", help="loopback address only (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", default="data/orbit-learning.sqlite3")
    args = parser.parse_args()
    serve(args.host, args.port, args.db)


if __name__ == "__main__":
    main()
