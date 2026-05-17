"""Genera JSON de dimensiones e inyecta en dashboard_vcm.html"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, json, os

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"
DIM = os.path.join(BASE, "metricas_dimensiones.xlsx")
HTML = os.path.join(BASE, "dashboard_vcm.html")

dim_desc = {
    'Dim_1': {'t': 'Despliegue territorial y articulacion con el entorno', 'd': 'Observar el nivel de cobertura territorial, el alcance del despliegue institucional y la capacidad de articulacion con actores relevantes del entorno.'},
    'Dim_2': {'t': 'Sostenibilidad y reputacion del vinculo con el entorno', 'd': 'Observar la capacidad institucional para sostener relaciones de colaboracion con actores del entorno en el tiempo, asi como la valoracion y reconocimiento que dichos actores desarrollan respecto de la VcM.'},
    'Dim_5': {'t': 'Resultados formativos en estudiantes', 'd': 'Observar la contribucion de la VcM al desarrollo formativo de los estudiantes, considerando el fortalecimiento de competencias disciplinares y transversales.'},
    'Dim_6': {'t': 'Desarrollo academico y fortalecimiento de la practica docente', 'd': 'Observar el fortalecimiento del desarrollo academico, la innovacion en la practica docente y la consolidacion del rol del academico en el marco de la VcM.'},
    'Dim_7': {'t': 'Generacion de conocimiento', 'd': 'Observar la capacidad de la VcM para contribuir a la generacion y difusion de conocimiento academico y disciplinar.'},
    'Dim_8': {'t': 'Pertinencia territorial y conexion con el entorno', 'd': 'Evaluar el despliegue institucional asociado al desarrollo territorial y la capacidad de la universidad para vincularse con las necesidades del entorno relevante.'},
    'Dim_9': {'t': 'Valoracion y contribucion territorial de la VcM', 'd': 'Evaluar la valoracion que actores externos realizan respecto de la calidad y contribucion de las iniciativas de VcM.'},
    'Dim_10': {'t': 'Capacidades institucionales de la VcM', 'd': 'Observar el nivel de desarrollo y consolidacion de las capacidades institucionales destinadas a sostener la implementacion de la VcM.'},
    'Dim_11': {'t': 'Gestion y desempeno de la VcM', 'd': 'Observar el nivel de cumplimiento, seguimiento y desempeno de las iniciativas y mecanismos institucionales asociados a la VcM.'},
    'Dim_12': {'t': 'Recursos e inversion en VcM', 'd': 'Observar el nivel de recursos humanos, financieros, tecnologicos y organizacionales destinados al desarrollo de la VcM.'}
}

xls = pd.ExcelFile(DIM)
dims = {}
for s in xls.sheet_names:
    df = pd.read_excel(xls, s)
    yc = [c for c in df.columns if c != 'Indicador']
    inds = []
    for _, r in df.iterrows():
        ind = {'nombre': str(r['Indicador'])}
        for y in yc:
            v = r[y]
            if pd.isna(v) or str(v).strip() in ['-', 'S/I', '']:
                ind[str(y)] = None
            else:
                sv = str(v).replace('\xa0', '').strip()
                try:
                    if '%' in sv:
                        fv = float(sv.replace('%', '').replace(',', '.').strip())
                        ind[str(y)] = round(fv / 100, 4) if fv > 1 else round(fv, 4)
                    else:
                        fv = float(sv.replace(',', '.'))
                        if 0 < fv < 1:
                            ind[str(y)] = round(fv, 4)
                        else:
                            ind[str(y)] = int(fv) if fv == int(fv) else round(fv, 2)
                except:
                    ind[str(y)] = sv
        inds.append(ind)
    info = dim_desc.get(s, {'t': s, 'd': ''})
    dims[s] = {'titulo': info['t'], 'descripcion': info['d'], 'anios': [str(c) for c in yc], 'indicadores': inds}

dims_json = json.dumps(dims, ensure_ascii=False)
print(f"Dimensions JSON: {len(dims_json)} chars, {len(dims)} dimensions")

# Read the HTML
with open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace the external link tab with a real button tab
old_tab = '''      <a href="dashboard_vcm_dim5.html" class="nav-btn"
        style="background: #e84393; color: #fff; text-decoration: none;">Modelo de Evaluaci\u00f3n VcM: Dimensi\u00f3n 5</a>'''
new_tab = '''      <button class="nav-btn" onclick="showSection('dim')">Modelo de Evaluaci\u00f3n VcM</button>'''

if old_tab in html:
    html = html.replace(old_tab, new_tab)
    print("[OK] Replaced external link with tab button")
else:
    print("[WARN] Could not find old tab link, trying alternate...")
    # Try a simpler match
    if 'dashboard_vcm_dim5.html' in html:
        import re
        html = re.sub(r'<a href="dashboard_vcm_dim5\.html"[^>]*>[^<]*</a>', 
                       '<button class="nav-btn" onclick="showSection(\'dim\')">Modelo de Evaluaci\u00f3n VcM</button>', html)
        print("[OK] Replaced via regex")

# 2. Add the dimensions section before </div> (closing container)
# Find the closing of sec-trend
dim_section = '''
    <div id="sec-dim" class="section hidden">
      <div class="section-title">Modelo de Evaluaci&oacute;n VcM</div>
      <div class="section-sub">Dimensiones del Modelo de Evaluaci&oacute;n de Vinculaci&oacute;n con el Medio de la Universidad San Sebasti&aacute;n. Cada dimensi&oacute;n incluye indicadores cuantitativos y cualitativos para evaluar el impacto institucional.</div>
      <div id="dim-content"></div>
    </div>'''

# Insert before </div>\n  <script>
insert_marker = '  </div>\n  <script>'
if insert_marker in html:
    html = html.replace(insert_marker, dim_section + '\n  </div>\n  <script>', 1)
    print("[OK] Inserted dimensions section")

# 3. Add dimensions data and render function before closing </script>
# Find the last </script> before </body>
dim_js = '''

    // === DIMENSIONS DATA ===
    var DIM_DATA = ''' + dims_json + ''';

    function buildDimensions() {
      var container = document.getElementById('dim-content');
      if (!container) return;
      var h = '';
      var dimOrder = ['Dim_1','Dim_2','Dim_5','Dim_6','Dim_7','Dim_8','Dim_9','Dim_10','Dim_11','Dim_12'];
      dimOrder.forEach(function(dk) {
        var d = DIM_DATA[dk];
        if (!d) return;
        var num = dk.replace('Dim_','');
        h += '<div style="margin-bottom:24px;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden">';
        h += '<div onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display===\\'none\\'?\\'block\\':\\'none\\';this.querySelector(\\'.dim-arrow\\').textContent=this.nextElementSibling.style.display===\\'none\\'?\\'\\u25B6\\':\\'\\u25BC\\'" style="background:#1b365d;color:#fff;padding:16px 20px;cursor:pointer;display:flex;justify-content:space-between;align-items:center">';
        h += '<div><strong>Dimensi\\u00f3n ' + num + ':</strong> ' + d.titulo + '</div>';
        h += '<span class="dim-arrow" style="font-size:14px">\\u25B6</span></div>';
        h += '<div style="display:none;padding:20px">';
        h += '<p style="font-size:13px;color:#666;margin-bottom:16px;font-style:italic">' + d.descripcion + '</p>';
        h += '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:13px">';
        h += '<thead><tr style="background:#f1f5f9"><th style="text-align:left;padding:10px 12px;border-bottom:2px solid #1b365d;min-width:300px">Indicador</th>';
        d.anios.forEach(function(a) { h += '<th style="text-align:center;padding:10px 12px;border-bottom:2px solid #1b365d;min-width:80px">' + a + '</th>'; });
        h += '</tr></thead><tbody>';
        d.indicadores.forEach(function(ind, idx) {
          var bg = idx % 2 === 0 ? '#fff' : '#f8fafc';
          h += '<tr style="background:' + bg + '">';
          h += '<td style="padding:10px 12px;border-bottom:1px solid #eee">' + ind.nombre + '</td>';
          d.anios.forEach(function(a) {
            var v = ind[a];
            if (v === null || v === undefined) {
              h += '<td style="text-align:center;padding:10px 12px;border-bottom:1px solid #eee;color:#94a3b8;font-style:italic">S/I</td>';
            } else if (typeof v === 'number' && v > 0 && v < 1) {
              h += '<td style="text-align:center;padding:10px 12px;border-bottom:1px solid #eee;font-weight:600">' + (v * 100).toFixed(1).replace('.',',') + '%</td>';
            } else {
              var formatted = typeof v === 'number' ? v.toLocaleString('es-CL') : v;
              h += '<td style="text-align:center;padding:10px 12px;border-bottom:1px solid #eee;font-weight:600">' + formatted + '</td>';
            }
          });
          h += '</tr>';
        });
        h += '</tbody></table></div></div></div>';
      });
      container.innerHTML = h;
    }
'''

# Insert before the closing of the first <script> block
# Find the position after init() call and before </script>
js_insert = '    function buildTrends() {'
if js_insert in html:
    html = html.replace(js_insert, dim_js + '\n    function buildTrends() {')
    print("[OK] Inserted dimensions JS")

# 4. Add buildDimensions() call to init()
old_init_calls = '''      buildSection('val', DATA.valores, 'Valor Sebastiano', '% de Estudiantes');
      buildTrends();
      buildValImp04();'''
new_init_calls = '''      buildSection('val', DATA.valores, 'Valor Sebastiano', '% de Estudiantes');
      buildTrends();
      buildValImp04();
      buildDimensions();'''

if old_init_calls in html:
    html = html.replace(old_init_calls, new_init_calls)
    print("[OK] Added buildDimensions() to init()")

# Write
with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

sz = os.path.getsize(HTML) / 1024
print(f"\n[DONE] dashboard_vcm.html: {sz:.1f} KB")
