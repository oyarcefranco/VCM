"""
Upgrade dashboard: add interactive item toggles, sort controls, data labels.
"""
import re

filepath = r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_vcm.html'

with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. ADD NEW CSS before </style> ──
new_css = """
.item-controls{display:flex;gap:10px;align-items:center;margin-bottom:12px;flex-wrap:wrap}
.item-controls button{padding:5px 14px;border-radius:4px;border:1px solid #1b365d;background:#fff;color:#1b365d;cursor:pointer;font-size:12px;font-weight:700;transition:all .15s}
.item-controls button:hover{background:#1b365d;color:#fff}
.item-controls .sort-btn.active{background:#1b365d;color:#fff}
.item-chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:18px;max-height:120px;overflow-y:auto;padding:4px 0}
.item-chip{padding:5px 12px;border-radius:20px;border:1.5px solid #1b365d;background:#e8edf4;color:#1b365d;cursor:pointer;font-size:12px;font-weight:600;transition:all .15s;user-select:none;white-space:nowrap}
.item-chip.off{background:#f4f4f4;color:#bbb;border-color:#ddd;text-decoration:line-through}
.item-chip:hover{opacity:.8}
.item-count{font-size:12px;color:#888;font-weight:400;margin-left:6px}
"""
html = html.replace('</style>', new_css + '</style>')

# ── 2. ADD ITEM FILTER CONTAINERS in HTML sections ──
# For imp section
html = html.replace(
    '<div id="avail-imp" class="avail-note"></div>',
    '<div class="item-controls" id="ctrl-imp"></div>\n<div class="item-chips" id="chips-imp"></div>\n<div id="avail-imp" class="avail-note"></div>'
)
# For hab section
html = html.replace(
    '<div id="avail-hab" class="avail-note"></div>',
    '<div class="item-controls" id="ctrl-hab"></div>\n<div class="item-chips" id="chips-hab"></div>\n<div id="avail-hab" class="avail-note"></div>'
)
# For val section - add chips container before chart
html = html.replace(
    '<div class="chart-wrap"><canvas id="chart-val">',
    '<div class="item-controls" id="ctrl-val"></div>\n<div class="item-chips" id="chips-val"></div>\n<div class="chart-wrap"><canvas id="chart-val">'
)

# ── 3. REPLACE THE ENTIRE JS (from <script> to </script>) ──
# Extract the DATA= line (it's the huge inline data)
data_match = re.search(r'(DATA=\{.*?\};init\(\);)', html, re.DOTALL)
data_line = data_match.group(1) if data_match else ''

new_js = """<script>
const COLORS=['#1e4c9a','#7d4199','#009a74','#f37021','#f3a81a','#4c3c5c','#2a82c9','#e64d3d','#8c7a6b','#5c9d38'];
const YEAR_COLORS={2021:'#1e4c9a',2022:'#7d4199',2023:'#009a74',2024:'#f37021',2025:'#f3a81a'};
let charts={};
let DATA;
let sectionState={};

""" + data_line + """

function init(){
  buildSection('imp',DATA.importancia,'Indicador','Top_2_Box (%)');
  buildSection('hab',DATA.habilidades,'Indicador','Top_2_Box (%)');
  buildIndicadores();
  buildValoresSection();
  buildTrends();
}

function showSection(id){
  document.querySelectorAll('.section').forEach(s=>s.classList.add('hidden'));
  document.getElementById('sec-'+id).classList.remove('hidden');
  document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));
  event.target.classList.add('active');
}

/* ═══════ GENERIC SECTION BUILDER (imp, hab) ═══════ */
function buildSection(key,rawData,labelField,valueField){
  const years=[...new Set(rawData.map(r=>r['Año']))].sort();
  const items=[...new Set(rawData.map(r=>r[labelField]))];
  sectionState[key]={rawData,labelField,valueField,selectedYear:null,activeItems:new Set(items),sortBy:'default'};

  // Year buttons
  const yf=document.getElementById('yf-'+key);
  const allBtn=document.createElement('button');
  allBtn.className='year-btn active';allBtn.textContent='Todos';
  allBtn.onclick=()=>{sectionState[key].selectedYear=null;refreshSection(key)};
  yf.appendChild(allBtn);
  years.forEach(y=>{
    const b=document.createElement('button');b.className='year-btn';b.textContent=y;
    b.onclick=()=>{sectionState[key].selectedYear=y;refreshSection(key)};
    yf.appendChild(b);
  });

  // Control bar: Select All / None / Sort
  const ctrl=document.getElementById('ctrl-'+key);
  ctrl.innerHTML='<button onclick="toggleAll(\\''+key+'\\',true)">✓ Todos</button>'
    +'<button onclick="toggleAll(\\''+key+'\\',false)">✕ Ninguno</button>'
    +'<button class="sort-btn" id="sort-'+key+'" onclick="toggleSort(\\''+key+'\\')">↕ Ordenar por valor</button>'
    +'<span class="item-count" id="count-'+key+'"></span>';

  buildChips(key);
  refreshSection(key);
}

function buildChips(key){
  const st=sectionState[key];
  const container=document.getElementById('chips-'+key);
  container.innerHTML='';
  const items=[...new Set(st.rawData.map(r=>r[st.labelField]))];
  items.forEach(item=>{
    const chip=document.createElement('span');
    chip.className='item-chip'+(st.activeItems.has(item)?'':' off');
    chip.textContent=item;
    chip.onclick=()=>{
      if(st.activeItems.has(item)) st.activeItems.delete(item);
      else st.activeItems.add(item);
      chip.classList.toggle('off');
      updateCount(key);
      redrawChart(key);
    };
    container.appendChild(chip);
  });
  updateCount(key);
}

function updateCount(key){
  const st=sectionState[key];
  const total=[...new Set(st.rawData.map(r=>r[st.labelField]))].length;
  document.getElementById('count-'+key).textContent=st.activeItems.size+' de '+total+' seleccionados';
}

function toggleAll(key,on){
  const st=sectionState[key];
  const items=[...new Set(st.rawData.map(r=>r[st.labelField]))];
  if(on) items.forEach(i=>st.activeItems.add(i));
  else st.activeItems.clear();
  document.querySelectorAll('#chips-'+key+' .item-chip').forEach(c=>{
    if(on) c.classList.remove('off'); else c.classList.add('off');
  });
  updateCount(key);
  redrawChart(key);
}

function toggleSort(key){
  const st=sectionState[key];
  st.sortBy=st.sortBy==='value'?'default':'value';
  const btn=document.getElementById('sort-'+key);
  btn.classList.toggle('active',st.sortBy==='value');
  btn.textContent=st.sortBy==='value'?'↕ Orden original':'↕ Ordenar por valor';
  redrawChart(key);
}

function refreshSection(key){
  // Update year button states
  const st=sectionState[key];
  document.querySelectorAll('#yf-'+key+' .year-btn').forEach(b=>{
    if(st.selectedYear===null && b.textContent==='Todos') b.classList.add('active');
    else if(b.textContent==st.selectedYear) b.classList.add('active');
    else b.classList.remove('active');
  });

  // When year changes, reset active items to those available
  const allItems=[...new Set(st.rawData.map(r=>r[st.labelField]))];
  if(st.selectedYear!==null){
    const availItems=new Set(st.rawData.filter(r=>r['Año']===st.selectedYear).map(r=>r[st.labelField]));
    st.activeItems=new Set([...availItems]);
  } else {
    st.activeItems=new Set(allItems);
  }
  buildChips(key);
  redrawChart(key);
}

function redrawChart(key){
  const st=sectionState[key];
  const {rawData,labelField,valueField,selectedYear}=st;
  const years=[...new Set(rawData.map(r=>r['Año']))].sort();

  if(charts[key]) charts[key].destroy();
  const canvas=document.getElementById('chart-'+key);
  const availEl=document.getElementById('avail-'+key);

  if(selectedYear!==null){
    // SINGLE YEAR
    let filtered=rawData.filter(r=>r['Año']===selectedYear && st.activeItems.has(r[labelField]));
    if(st.sortBy==='value') filtered.sort((a,b)=>b[valueField]-a[valueField]);
    const labels=filtered.map(r=>r[labelField]);
    const values=filtered.map(r=>r[valueField]*100);

    // Availability note
    const allItems=[...new Set(rawData.map(r=>r[labelField]))];
    const yearItems=new Set(rawData.filter(r=>r['Año']===selectedYear).map(r=>r[labelField]));
    const missing=allItems.filter(i=>!yearItems.has(i));
    if(missing.length>0){
      availEl.innerHTML='<strong>No disponible en '+selectedYear+':</strong> '+missing.join(', ');
      availEl.style.display='inline-block';
    } else { availEl.style.display='none'; }

    canvas.style.maxHeight=Math.max(labels.length*44,150)+'px';
    charts[key]=new Chart(canvas,{
      type:'bar',
      data:{labels,datasets:[{
        data:values,
        backgroundColor:values.map(v=>v>=90?'#009a74':v>=80?'#1e4c9a':v>=70?'#f3a81a':'#e64d3d'),
        borderRadius:4,borderSkipped:false,barThickness:22
      }]},
      options:{
        indexAxis:'y',responsive:true,maintainAspectRatio:false,
        plugins:{legend:{display:false},
          tooltip:{callbacks:{label:c=>c.raw.toFixed(1)+'%'}}},
        scales:{
          x:{min:0,max:100,grid:{color:'#eaeaea'},ticks:{color:'#666666',callback:v=>v+'%'}},
          y:{grid:{display:false},ticks:{color:'#333333',font:{size:12}}}
        }
      }
    });
  } else {
    // ALL YEARS
    availEl.style.display='none';
    let items=[...st.activeItems];
    if(st.sortBy==='value'){
      items.sort((a,b)=>{
        const avgA=rawData.filter(r=>r[labelField]===a).reduce((s,r)=>s+r[valueField],0)/Math.max(1,rawData.filter(r=>r[labelField]===a).length);
        const avgB=rawData.filter(r=>r[labelField]===b).reduce((s,r)=>s+r[valueField],0)/Math.max(1,rawData.filter(r=>r[labelField]===b).length);
        return avgB-avgA;
      });
    }
    const datasets=years.map(y=>({
      label:y.toString(),
      data:items.map(item=>{
        const m=rawData.find(r=>r[labelField]===item&&r['Año']===y);
        return m?(m[valueField]*100):null;
      }),
      backgroundColor:YEAR_COLORS[y]+'cc',
      borderRadius:3,borderSkipped:false,barThickness:14
    }));
    canvas.style.maxHeight=Math.max(items.length*55,200)+'px';
    charts[key]=new Chart(canvas,{
      type:'bar',
      data:{labels:items,datasets},
      options:{
        indexAxis:'y',responsive:true,maintainAspectRatio:false,
        plugins:{legend:{position:'top',labels:{color:'#333333',usePointStyle:true,pointStyle:'circle',font:{size:11}}},
          tooltip:{callbacks:{label:c=>c.dataset.label+': '+(c.raw?c.raw.toFixed(1)+'%':'Sin dato')}}},
        scales:{
          x:{min:0,max:100,grid:{color:'#eaeaea'},ticks:{color:'#666666',callback:v=>v+'%'}},
          y:{grid:{display:false},ticks:{color:'#333333',font:{size:11}}}
        }
      }
    });
  }
}

/* ═══════ INDICADORES (unchanged logic) ═══════ */
function buildIndicadores(){
  const years=[...new Set(DATA.indicadores.map(r=>r['Año']))].sort();
  const container=document.getElementById('yf-ind');
  years.forEach(y=>{
    const b=document.createElement('button');
    b.className='year-btn'+(y===2025?' active':'');b.textContent=y;
    b.onclick=()=>{
      document.querySelectorAll('#yf-ind .year-btn').forEach(x=>x.classList.remove('active'));
      b.classList.add('active');
      renderIndicadores(y);
    };
    container.appendChild(b);
  });
  renderIndicadores(2025);
}

function renderIndicadores(year){
  const filtered=DATA.indicadores.filter(r=>r['Año']===year);
  if(charts.ind)charts.ind.destroy();
  const canvas=document.getElementById('chart-ind');
  canvas.style.maxHeight=Math.max(filtered.length*50,200)+'px';
  charts.ind=new Chart(canvas,{
    type:'bar',
    data:{
      labels:filtered.map(r=>r['Indicador']),
      datasets:[{
        data:filtered.map(r=>r['Resultado (%)']*100),
        backgroundColor:filtered.map((_,i)=>COLORS[i%COLORS.length]+'cc'),
        borderRadius:6,borderSkipped:false
      }]
    },
    options:{
      indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>c.raw.toFixed(1)+'%'}}},
      scales:{
        x:{min:0,max:100,grid:{color:'#eaeaea'},ticks:{color:'#666666',callback:v=>v+'%'}},
        y:{grid:{display:false},ticks:{color:'#333333',font:{size:12}}}
      }
    }
  });
}

/* ═══════ VALORES SEBASTIANOS (with toggles) ═══════ */
function buildValoresSection(){
  const years=[...new Set(DATA.valores.map(r=>r['Año']))].sort();
  sectionState['val']={selectedYear:2025,activeItems:new Set(),sortBy:'value'};
  const container=document.getElementById('yf-val');
  years.forEach(y=>{
    const b=document.createElement('button');
    b.className='year-btn'+(y===2025?' active':'');b.textContent=y;
    b.onclick=()=>{
      document.querySelectorAll('#yf-val .year-btn').forEach(x=>x.classList.remove('active'));
      b.classList.add('active');
      sectionState['val'].selectedYear=y;
      refreshValores();
    };
    container.appendChild(b);
  });

  const ctrl=document.getElementById('ctrl-val');
  ctrl.innerHTML='<button onclick="toggleAllVal(true)">✓ Todos</button>'
    +'<button onclick="toggleAllVal(false)">✕ Ninguno</button>'
    +'<span class="item-count" id="count-val"></span>';

  refreshValores();
}

function refreshValores(){
  const st=sectionState['val'];
  const year=st.selectedYear;
  const items=DATA.valores.filter(r=>r['Año']===year).map(r=>r['Valor Sebastiano']);
  st.activeItems=new Set(items);
  buildValChips();
  redrawValores();
}

function buildValChips(){
  const st=sectionState['val'];
  const year=st.selectedYear;
  const items=DATA.valores.filter(r=>r['Año']===year).sort((a,b)=>b['% de Estudiantes']-a['% de Estudiantes']).map(r=>r['Valor Sebastiano']);
  const container=document.getElementById('chips-val');
  container.innerHTML='';
  items.forEach(item=>{
    const chip=document.createElement('span');
    chip.className='item-chip'+(st.activeItems.has(item)?'':' off');
    chip.textContent=item;
    chip.onclick=()=>{
      if(st.activeItems.has(item)) st.activeItems.delete(item);
      else st.activeItems.add(item);
      chip.classList.toggle('off');
      updateValCount();
      redrawValores();
    };
    container.appendChild(chip);
  });
  updateValCount();
}

function updateValCount(){
  const st=sectionState['val'];
  const total=DATA.valores.filter(r=>r['Año']===st.selectedYear).length;
  document.getElementById('count-val').textContent=st.activeItems.size+' de '+total+' seleccionados';
}

function toggleAllVal(on){
  const st=sectionState['val'];
  const items=DATA.valores.filter(r=>r['Año']===st.selectedYear).map(r=>r['Valor Sebastiano']);
  if(on) items.forEach(i=>st.activeItems.add(i)); else st.activeItems.clear();
  document.querySelectorAll('#chips-val .item-chip').forEach(c=>{
    if(on) c.classList.remove('off'); else c.classList.add('off');
  });
  updateValCount();
  redrawValores();
}

function redrawValores(){
  const st=sectionState['val'];
  const year=st.selectedYear;
  const filtered=DATA.valores.filter(r=>r['Año']===year && st.activeItems.has(r['Valor Sebastiano']))
    .sort((a,b)=>b['% de Estudiantes']-a['% de Estudiantes']);
  if(charts.val)charts.val.destroy();
  const canvas=document.getElementById('chart-val');
  canvas.style.maxHeight=Math.max(filtered.length*45,150)+'px';
  charts.val=new Chart(canvas,{
    type:'bar',
    data:{
      labels:filtered.map(r=>r['Valor Sebastiano']),
      datasets:[{
        data:filtered.map(r=>r['% de Estudiantes']*100),
        backgroundColor:filtered.map((_,i)=>COLORS[i%COLORS.length]+'cc'),
        borderRadius:6,borderSkipped:false,barThickness:24
      }]
    },
    options:{
      indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>c.raw.toFixed(1)+'%'}}},
      scales:{
        x:{min:0,grid:{color:'#eaeaea'},ticks:{color:'#666666',callback:v=>v.toFixed(0)+'%'}},
        y:{grid:{display:false},ticks:{color:'#333333',font:{size:11}}}
      }
    }
  });
}

/* ═══════ TRENDS (unchanged) ═══════ */
function buildTrends(){
  const years=[2021,2022,2023,2024,2025];
  const topHab=['Empatía','Comunicación efectiva','Trabajo en equipo / Colaboración','Adaptación y flexibilidad'];
  const ds1=topHab.map((h,i)=>({
    label:h,borderColor:COLORS[i],backgroundColor:COLORS[i]+'33',
    data:years.map(y=>{const m=DATA.habilidades.find(r=>r.Indicador===h&&r['Año']===y);return m?(m['Top_2_Box (%)']*100):null}),
    tension:.3,spanGaps:true,pointRadius:5
  }));
  charts.trend1=new Chart(document.getElementById('chart-trend1'),{
    type:'line',data:{labels:years,datasets:ds1},
    options:{responsive:true,plugins:{title:{display:true,text:'Evolución Top 4 Habilidades (T2B %)',color:'#333333',font:{size:14}},legend:{labels:{color:'#666666',font:{size:10}}}},scales:{x:{grid:{color:'#eaeaea'},ticks:{color:'#666666'}},y:{min:70,max:100,grid:{color:'#eaeaea'},ticks:{color:'#666666',callback:v=>v+'%'}}}}
  });
  const topImp=['Conocer la realidad (problemas/desafíos)','Aplicar lo aprendido en clases','Fortalecer vocación profesional','Fortalecer valores sebastianos'];
  const ds2=topImp.map((h,i)=>({
    label:h,borderColor:COLORS[i+4],backgroundColor:COLORS[i+4]+'33',
    data:years.map(y=>{const m=DATA.importancia.find(r=>r.Indicador===h&&r['Año']===y);return m?(m['Top_2_Box (%)']*100):null}),
    tension:.3,spanGaps:true,pointRadius:5
  }));
  charts.trend2=new Chart(document.getElementById('chart-trend2'),{
    type:'line',data:{labels:years,datasets:ds2},
    options:{responsive:true,plugins:{title:{display:true,text:'Evolución Top 4 Aspectos Formativos (T2B %)',color:'#333333',font:{size:14}},legend:{labels:{color:'#666666',font:{size:10}}}},scales:{x:{grid:{color:'#eaeaea'},ticks:{color:'#666666'}},y:{min:60,max:100,grid:{color:'#eaeaea'},ticks:{color:'#666666',callback:v=>v+'%'}}}}
  });
  const indNames=['Significancia en Formación (T2B)','Expectativas Cumplidas (T2B)','Recomendaría a compañeros (% Sí)'];
  const ds3=indNames.map((h,i)=>({
    label:h,borderColor:COLORS[i+8],backgroundColor:COLORS[i+8]+'33',
    data:years.map(y=>{const m=DATA.indicadores.find(r=>r.Indicador===h&&r['Año']===y);return m?(m['Resultado (%)']*100):null}),
    tension:.3,spanGaps:true,pointRadius:5
  }));
  charts.trend3=new Chart(document.getElementById('chart-trend3'),{
    type:'line',data:{labels:years,datasets:ds3},
    options:{responsive:true,plugins:{title:{display:true,text:'Evolución Indicadores Principales',color:'#333333',font:{size:14}},legend:{labels:{color:'#666666',font:{size:10}}}},scales:{x:{grid:{color:'#eaeaea'},ticks:{color:'#666666'}},y:{min:60,max:100,grid:{color:'#eaeaea'},ticks:{color:'#666666',callback:v=>v+'%'}}}}
  });
  const partData=[{y:2021,n:911},{y:2022,n:2422},{y:2023,n:1953},{y:2024,n:3970},{y:2025,n:4629}];
  charts.trend4=new Chart(document.getElementById('chart-trend4'),{
    type:'bar',data:{labels:years,datasets:[{label:'Estudiantes encuestados',data:partData.map(d=>d.n),backgroundColor:years.map(y=>YEAR_COLORS[y]+'cc'),borderRadius:8}]},
    options:{responsive:true,plugins:{title:{display:true,text:'Participación por Año',color:'#333333',font:{size:14}},legend:{display:false}},scales:{x:{grid:{color:'#eaeaea'},ticks:{color:'#666666'}},y:{grid:{color:'#eaeaea'},ticks:{color:'#666666'}}}}
  });
}
</script>"""

# Replace the entire script block
html = re.sub(r'<script>.*?</script>', new_js, html, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html)

print('Dashboard upgraded successfully!')
