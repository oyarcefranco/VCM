"""Construye el dashboard HTML final desde el JSON de métricas + JS."""
import json, os

B = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"

# Leer datos JSON
with open(os.path.join(B, "dashboard_vcm_data.json"), 'r', encoding='utf-8') as f:
    jd = f.read()

# Leer JS parts
with open(os.path.join(B, "dashboard_part1.js"), 'r', encoding='utf-8') as f:
    js1 = f.read()
with open(os.path.join(B, "dashboard_part2.js"), 'r', encoding='utf-8') as f:
    js2 = f.read()

CSS = """*{margin:0;padding:0;box-sizing:border-box}
:root{--p:#003366;--pl:#0a4d8c;--pd:#001f3f;--a:#0077cc;--a2:#00a6fb;--bg:#f0f2f5;--c:#fff;--t:#1a1a2e;--t2:#64748b;--t3:#94a3b8;--ok:#22c55e;--bd:#e2e8f0;--sh:0 4px 24px rgba(0,51,102,.07);--r:14px}
body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--t)}
.hd{background:linear-gradient(135deg,var(--pd) 0%,var(--p) 50%,var(--pl) 100%);color:#fff;padding:24px 40px;display:flex;align-items:center;gap:24px}
.hd .logo{width:56px;height:56px;border-radius:12px;display:grid;place-items:center;font-size:10px;color:rgba(255,255,255,.5);flex-shrink:0;overflow:hidden}
.hd .logo img{width:100%;height:100%;object-fit:contain}
.hd h1{font-size:15px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;opacity:.95}
.hd h2{font-size:13px;font-weight:400;opacity:.7;margin-top:6px;max-width:900px;line-height:1.5}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:24px 40px;background:linear-gradient(180deg,#fff 0%,var(--bg) 100%)}
.kpis h3{grid-column:1/-1;font-size:13px;color:var(--t2);font-weight:600;letter-spacing:.5px;text-transform:uppercase}
.kc{background:#fff;border-radius:var(--r);padding:20px;text-align:center;border:1px solid var(--bd);box-shadow:var(--sh);transition:transform .2s}
.kc:hover{transform:translateY(-3px)}
.kv{font-size:32px;font-weight:800;background:linear-gradient(135deg,var(--p),var(--a));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.kl{font-size:10px;color:var(--t3);font-weight:600;margin-top:6px;text-transform:uppercase;letter-spacing:.5px}
.fb{display:flex;gap:14px;padding:16px 40px;background:#fff;border-bottom:1px solid var(--bd);position:sticky;top:0;z-index:100;align-items:flex-end;flex-wrap:wrap}
.fg{display:flex;flex-direction:column;gap:4px}
.fg label{font-size:10px;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:.8px}
.fg select{padding:8px 12px;border:1px solid var(--bd);border-radius:10px;font-size:12px;font-family:inherit;background:#fff;min-width:150px;cursor:pointer;transition:border .2s}
.fg select:focus{outline:none;border-color:var(--a);box-shadow:0 0 0 3px rgba(0,119,204,.1)}
.cbtn{padding:8px 16px;border:1px solid var(--bd);border-radius:10px;font-size:11px;font-family:inherit;font-weight:600;cursor:pointer;background:#fff;color:var(--t2);transition:all .2s}
.cbtn:hover{border-color:var(--a);color:var(--a)}
.tabs{display:flex;gap:2px;padding:0 40px;background:#fff;border-bottom:1px solid var(--bd);overflow-x:auto}
.tb{padding:14px 22px;border:none;background:transparent;font-family:inherit;font-size:12px;font-weight:600;color:var(--t3);cursor:pointer;border-bottom:3px solid transparent;transition:all .2s;white-space:nowrap}
.tb:hover{color:var(--p)}
.tb.on{color:var(--p);border-bottom-color:var(--a)}
.tc{display:none;padding:28px 40px;animation:fi .3s ease}
.tc.on{display:block}
@keyframes fi{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.sd{background:#fff;border-radius:var(--r);padding:24px;margin-bottom:24px;border-left:4px solid var(--a);box-shadow:var(--sh)}
.sd h3{font-size:17px;color:var(--p);margin-bottom:10px;font-weight:700}
.sd p{font-size:13px;color:var(--t2);line-height:1.7}
.sd .tip{font-size:12px;color:var(--a);margin-top:10px;font-style:italic}
.cc{background:#fff;border-radius:var(--r);padding:24px;margin-bottom:24px;box-shadow:var(--sh)}
.ch{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:10px}
.ct{font-size:16px;font-weight:700;color:var(--p)}
.cn{font-size:12px;color:var(--t3);font-weight:500;margin-left:12px}
.ca{display:flex;gap:8px;align-items:center}
.tg{padding:7px 16px;border:1.5px solid var(--bd);border-radius:10px;font-size:11px;font-family:inherit;font-weight:600;cursor:pointer;transition:all .15s;background:#fff;color:var(--t2)}
.tg.on{background:var(--p);color:#fff;border-color:var(--p)}
.dl{padding:7px 12px;border:1.5px solid var(--bd);border-radius:10px;font-size:11px;cursor:pointer;background:#fff;color:var(--t2);transition:all .15s;font-family:inherit}
.dl:hover{background:var(--a);color:#fff;border-color:var(--a)}
.pills{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:18px}
.pill{padding:5px 14px;border-radius:20px;font-size:11px;cursor:pointer;border:1.5px solid var(--bd);background:#fff;color:var(--t2);transition:all .12s;font-family:inherit;font-weight:500}
.pill.on{background:var(--p);color:#fff;border-color:var(--p)}
.pill:hover{border-color:var(--a)}
.dc{background:#fff;border-radius:var(--r);margin-bottom:14px;box-shadow:var(--sh);overflow:hidden}
.dh{padding:18px 24px;background:linear-gradient(135deg,var(--p),var(--pl));color:#fff;cursor:pointer;display:flex;justify-content:space-between;align-items:center}
.dh h4{font-size:14px;font-weight:600}
.dh .ar{transition:transform .3s;font-size:12px}
.dh .ar.op{transform:rotate(180deg)}
.db{padding:20px 24px;display:none}
.db.op{display:block}
.db p{font-size:13px;color:var(--t2);margin-bottom:14px;line-height:1.6}
.dt{width:100%;border-collapse:collapse;font-size:12px}
.dt th{background:var(--bg);padding:10px 14px;text-align:left;font-weight:600;color:var(--t2);border-bottom:2px solid var(--bd)}
.dt td{padding:10px 14px;border-bottom:1px solid var(--bd)}
.dt tr:hover td{background:#f8fafc}
.ig{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-bottom:24px}
canvas{max-height:520px}
@media(max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}.fb{flex-direction:column}.tc{padding:16px}.tabs{padding:0 16px}}"""

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Dashboard VcM — Encuestas Estudiantes 2021-2025</title>
<meta name="description" content="Dashboard interactivo de resultados de la Encuesta de estudiantes participantes en Proyectos Colaborativos de Vinculación con el Medio, Universidad San Sebastián 2021-2025.">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<style>{CSS}</style>
</head>
<body>

<div class="hd">
  <div class="logo"><!-- LOGO: reemplazar con <img src="URL_LOGO"> --></div>
  <div>
    <h1>Universidad San Sebasti&aacute;n</h1>
    <h2>Reporte de resultados de la Encuesta de estudiantes participantes en Proyectos Colaborativos 2021-2025 y Modelo de Evaluaci&oacute;n VcM</h2>
  </div>
</div>

<div class="kpis">
  <h3>Cifras globales destacadas (2021-2025)</h3>
  <div class="kc"><div class="kv" id="kN">-</div><div class="kl">Estudiantes encuestados</div></div>
  <div class="kc"><div class="kv" id="kR">-</div><div class="kl">&Iacute;ndice de recomendaci&oacute;n global</div></div>
  <div class="kc"><div class="kv" id="kS">-</div><div class="kl">Impacto positivo en formaci&oacute;n (T2B)</div></div>
  <div class="kc"><div class="kv" id="kE">-</div><div class="kl">Expectativas cumplidas (T2B)</div></div>
</div>

<div class="fb">
  <div class="fg"><label>A&ntilde;o</label><select id="fY" multiple></select></div>
  <div class="fg"><label>Sede</label><select id="fS" multiple></select></div>
  <div class="fg"><label>Carrera</label><select id="fC" multiple></select></div>
  <button class="cbtn" onclick="resetF()">Limpiar filtros</button>
</div>

<div class="tabs">
  <button class="tb on" onclick="go('imp')">Importancia Aspectos</button>
  <button class="tb" onclick="go('hab')">Desarrollo Habilidades</button>
  <button class="tb" onclick="go('ind')">Indicadores Clave</button>
  <button class="tb" onclick="go('val')">Valores Sebastianos</button>
  <button class="tb" onclick="go('evo')">Evoluci&oacute;n</button>
  <button class="tb" onclick="go('dim')">Modelo Evaluaci&oacute;n VcM</button>
</div>

<div id="Timp" class="tc on"></div>
<div id="Thab" class="tc"></div>
<div id="Tind" class="tc"></div>
<div id="Tval" class="tc"></div>
<div id="Tevo" class="tc"></div>
<div id="Tdim" class="tc"></div>

<script>
const D = {jd};
</script>
<script>
{js1}
</script>
<script>
{js2}
</script>
</body>
</html>"""

out_path = os.path.join(B, "dashboard_vcm_final.html")
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

sz = os.path.getsize(out_path) / (1024 * 1024)
print(f"[OK] Dashboard construido: {sz:.2f} MB")
print(f"   JS Part1: {len(js1)} chars | JS Part2: {len(js2)} chars")
print(f"   JSON data: {len(jd)} chars")
