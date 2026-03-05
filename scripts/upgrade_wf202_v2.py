import requests, json

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MGVlYWVhZi0xNjI4LTQwY2YtYjJhOC04OWE3ZGNmMmQ3NGUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiOWM1ZTMzNzYtZTc1Yi00ZGZmLTk3ZGQtNGUyOTQyYjE0OGYwIiwiaWF0IjoxNzcyNzA0ODM5LCJleHAiOjE3NzUyNTAwMDB9.lobZs1JZbGZ-40qpMD4769omD1fmDk_LmcvGypvchw4"
BASE = "https://n8n-4d54.onrender.com/api/v1"

r = requests.get(f"{BASE}/workflows/iI3kYbrzbobvbklo", headers={"X-N8N-API-KEY": N8N_KEY})
wf = r.json()

PG_CRED = {"postgres": {"id": "vMUuOggCtBWX48Jg", "name": "Postgres account"}}

SQL_SEO_HEALTH = (
    "SELECT json_build_object("
    "'total_ticker_pages', (SELECT COUNT(*) FROM marketplace WHERE slug_suggestion IS NOT NULL),"
    "'with_ru_title', (SELECT COUNT(*) FROM marketplace WHERE slug_suggestion IS NOT NULL AND seo_data->'ru'->>'title' IS NOT NULL),"
    "'without_any_title', (SELECT COUNT(*) FROM marketplace WHERE slug_suggestion IS NOT NULL AND (seo_data IS NULL OR seo_data->'ru'->>'title' IS NULL)),"
    "'updated_today', (SELECT COUNT(*) FROM marketplace WHERE slug_suggestion IS NOT NULL AND updated_at > now() - interval '24h'),"
    "'updated_week', (SELECT COUNT(*) FROM marketplace WHERE slug_suggestion IS NOT NULL AND updated_at > now() - interval '7d')"
    ") as result"
)

SQL_TOP_MISSING = (
    "SELECT json_agg(t) as result FROM ("
    "SELECT slug_suggestion, ticker,"
    "seo_data->'ru'->>'title' as ru_title,"
    "seo_data->'en'->>'title' as en_title,"
    "updated_at::date as updated "
    "FROM marketplace "
    "WHERE slug_suggestion IS NOT NULL "
    "AND (seo_data IS NULL OR seo_data->'ru'->>'title' IS NULL) "
    "AND updated_at > now() - interval '7d' "
    "ORDER BY updated_at DESC LIMIT 10) t"
)

# 2 new PG nodes
new_nodes = [
    {
        "id": "pg1", "name": "PG SEO Health",
        "type": "n8n-nodes-base.postgres", "typeVersion": 2.5,
        "position": [900, 760],
        "parameters": {"operation": "executeQuery", "query": SQL_SEO_HEALTH, "options": {}},
        "credentials": PG_CRED
    },
    {
        "id": "pg2", "name": "PG Missing Titles",
        "type": "n8n-nodes-base.postgres", "typeVersion": 2.5,
        "position": [900, 960],
        "parameters": {"operation": "executeQuery", "query": SQL_TOP_MISSING, "options": {}},
        "credentials": PG_CRED
    }
]
wf['nodes'].extend(new_nodes)

# ── Updated Prepare JS ──────────────────────────────────────────
PREPARE_JS = """
// GA4
var ga4 = $('GA4 Data').first().json;
var channels = {};
var ga4rows = (ga4.rows || []);
for (var i = 0; i < ga4rows.length; i++) {
  var d = ga4rows[i].dimensionValues || [];
  var m = ga4rows[i].metricValues || [];
  var ch = (d[0] && d[0].value) ? d[0].value : 'Other';
  channels[ch] = {
    s: parseInt((m[0]&&m[0].value)?m[0].value:0),
    c: parseFloat((m[1]&&m[1].value)?m[1].value:0),
    r: parseFloat((m[2]&&m[2].value)?m[2].value:0)
  };
}
var ts=0, tr=0;
for (var k in channels) { ts+=channels[k].s; tr+=channels[k].r; }
var org = channels['Organic Search'] || {s:0,r:0,c:0};

// GSC
var gRows = ($('GSC Queries').first().json.rows || []);
var tc=0, ti=0, wp=0;
for (var j=0; j<gRows.length; j++) { tc+=gRows[j].clicks; ti+=gRows[j].impressions; wp+=gRows[j].position*gRows[j].impressions; }
var avgP = ti>0 ? (wp/ti).toFixed(1) : '0';
var tq='';
for (var q=0; q<Math.min(12,gRows.length); q++) {
  var rq=gRows[q];
  tq+=rq.keys[0]+'|c:'+rq.clicks+' i:'+rq.impressions+' p:'+rq.position.toFixed(1)+' ctr:'+(rq.ctr*100).toFixed(1)+'%\\n';
}

var gPRows = ($('GSC Pages').first().json.rows || []);
var tPages='', opp='';
for (var p=0; p<gPRows.length; p++) {
  var pr=gPRows[p];
  var url=pr.keys[0].replace('https://gaming-goods.ru','');
  var tag=url.indexOf('/t/')===0?'[t]':url.indexOf('/marketplace/')===0?'[mp]':'[/]';
  tPages+=tag+url+'|i:'+pr.impressions+' c:'+pr.clicks+' p:'+pr.position.toFixed(1)+' ctr:'+(pr.ctr*100).toFixed(1)+'%\\n';
  if (pr.impressions>50 && pr.ctr<0.05 && pr.position<20) {
    opp+=tag+url+'|i:'+pr.impressions+' c:'+pr.clicks+' p:'+pr.position.toFixed(1)+' ctr:'+(pr.ctr*100).toFixed(1)+'%\\n';
  }
}

// Yandex
var ymData = ($('YM Data').first().json.data || []);
var ymT=0, ymO=0, ymD=0;
for (var y=0; y<ymData.length; y++) {
  var v=Math.round(ymData[y].metrics[0]);
  ymT+=v;
  var src=(ymData[y].dimensions[0].name||'');
  if (src.indexOf('Search')!==-1) ymO+=v;
  if (src.indexOf('Direct')!==-1) ymD+=v;
}

// PostgreSQL SEO Health
var pgHealth = {};
var pgMissing = [];
try {
  var h = $('PG SEO Health').first().json;
  pgHealth = h.result || h;
} catch(e) { pgHealth = {error: String(e)}; }
try {
  var mv = $('PG Missing Titles').first().json;
  pgMissing = mv.result || [];
} catch(e) { pgMissing = []; }

var totalT   = pgHealth.total_ticker_pages || 0;
var withTitle = pgHealth.with_ru_title || 0;
var noTitle  = pgHealth.without_any_title || 0;
var titlePct = totalT > 0 ? Math.round(withTitle/totalT*100) : 0;
var updToday = pgHealth.updated_today || 0;
var updWeek  = pgHealth.updated_week  || 0;

var missingList = '';
for (var mi=0; mi<Math.min(5,pgMissing.length); mi++) {
  var item = pgMissing[mi];
  missingList += '/t/'+(item.slug_suggestion||'?')+'|ticker:'+(item.ticker||'?')+(item.ru_title?'':'|NO_TITLE')+'\\n';
}

// Canonical conflict: same slug in /t/ AND /marketplace/ in GSC
var tInGsc=[], mpInGsc=[];
for (var pi=0; pi<gPRows.length; pi++) {
  var u=gPRows[pi].keys[0].replace('https://gaming-goods.ru','');
  if (u.indexOf('/t/')===0) tInGsc.push({url:u, imp:gPRows[pi].impressions, pos:gPRows[pi].position});
  if (u.indexOf('/marketplace/')===0) mpInGsc.push({url:u, imp:gPRows[pi].impressions, pos:gPRows[pi].position});
}
var conflicts='';
for (var ti2=0; ti2<tInGsc.length; ti2++) {
  var slug2=tInGsc[ti2].url.replace('/t/','').split('-')[0];
  for (var mi2=0; mi2<mpInGsc.length; mi2++) {
    if (mpInGsc[mi2].url.indexOf(slug2)!==-1) {
      conflicts+=tInGsc[ti2].url+'(p:'+tInGsc[ti2].pos.toFixed(1)+') vs '+mpInGsc[mi2].url+'(p:'+mpInGsc[mi2].pos.toFixed(1)+')\\n';
    }
  }
}

var jwtData = $('JWT').first().json;
var today = jwtData.end_date;

var userText =
  'Date:'+today+
  '\\nGA4: sessions='+ts+' organic='+org.s+' conv='+org.c.toFixed(0)+' rev_eur='+tr.toFixed(0)+
  '\\nGSC: clicks='+tc+' impressions='+ti+' avgPos='+avgP+
  '\\nTop queries:\\n'+tq+
  '\\nGSC pages ([t]=exchange [mp]=marketplace):\\n'+tPages+
  '\\nLow CTR opportunities:\\n'+(opp||'none')+
  '\\nYandex: visits='+ymT+' organic='+ymO+' direct='+ymD+
  '\\n\\n=== DB SEO HEALTH ==='+
  '\\n/t/ pages: total='+totalT+' with_ru_title='+withTitle+'('+titlePct+'%) no_title='+noTitle+
  '\\nupdated_today='+updToday+' updated_week='+updWeek+
  '\\nRecent pages missing title:\\n'+(missingList||'none')+
  '\\nCanonical conflicts (both /t/ and /marketplace/ in GSC):\\n'+(conflicts||'none detected');

return [{json: {today: today, user_text: userText}}];
"""

SYSTEM = (
    "Ты SEO-агент gaming-goods.ru (Steam ключи, игровые товары). "
    "Структура URL: /t/{slug} = биржевая карточка (113K+ страниц), /marketplace/{slug} = конструктор. "
    "Правила анализа: "
    "1) Если no_title > 0 — это Приоритет 1 (причина 18K crawled-not-indexed). "
    "2) Canonical conflict = Google не знает что продвигать — называй конкретные URL. "
    "3) Если /marketplace/ опережает /t/ по позиции — это проблема. "
    "Каждый день: 1 инсайт + 1 конкретное действие с цифрами. "
    "6-10 строк. Русский язык. Тон инвестору."
)

CLAUDE_BODY = (
    '{"model":"claude-opus-4-5","max_tokens":500,'
    '"system":' + json.dumps(SYSTEM) + ','
    '"messages":[{"role":"user","content":"={{ $(\\"Prepare\\").first().json.user_text }}"}]}'
)

for n in wf['nodes']:
    if n['name'] == 'Prepare':
        n['parameters']['jsCode'] = PREPARE_JS
        print("  Prepare JS: updated")
    if n['name'] == 'Claude':
        n['parameters']['jsonBody'] = CLAUDE_BODY
        print("  Claude body: updated")

# New connection chain
wf['connections']['YM Data']            = {"main": [[{"node": "PG SEO Health",     "type": "main", "index": 0}]]}
wf['connections']['PG SEO Health']      = {"main": [[{"node": "PG Missing Titles", "type": "main", "index": 0}]]}
wf['connections']['PG Missing Titles']  = {"main": [[{"node": "Prepare",           "type": "main", "index": 0}]]}

patch = {
    'name': wf['name'], 'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': {'executionOrder': wf['settings'].get('executionOrder', 'v1')}
}

payload = json.dumps(patch, ensure_ascii=False).encode('utf-8')
print(f"Payload: {len(payload)/1024:.1f} KB")

resp = requests.put(f"{BASE}/workflows/iI3kYbrzbobvbklo",
    headers={"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"},
    data=payload)

print("Status:", resp.status_code)
if resp.status_code == 200:
    result = resp.json()
    print("WF-202 v2 DEPLOYED!")
    nodes = [n['name'] for n in result['nodes']]
    print("Nodes:", nodes)
    print("\nChain:")
    for k, v in result['connections'].items():
        targets = [c['node'] for lst in v.get('main', []) for c in lst]
        print(f"  {k} -> {targets}")
else:
    print("ERROR:", resp.text[:400])
