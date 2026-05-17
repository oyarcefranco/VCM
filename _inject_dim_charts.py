import os, re

HTML_PATH = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_vcm.html"

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the HTML section for Dim
new_sec_dim = '''
    <div id="sec-dim" class="section hidden">
      <div class="section-title">Modelo de Evaluaci&oacute;n VcM</div>
      <div class="section-sub">Dimensiones del Modelo de Evaluaci&oacute;n de Vinculaci&oacute;n con el Medio de la Universidad San Sebasti&aacute;n. Cada dimensi&oacute;n incluye indicadores cuantitativos y cualitativos para evaluar el impacto institucional.<br><span style="color:#2980b9; font-style:italic;">💡 Seleccione un indicador (píldora) y un año específico para visualizar los resultados.</span></div>
      <div class="year-filter" id="yf-dim">
        <button class="yr-btn active" onclick="setDimYear(null)">Todos los años</button>
        <button class="yr-btn" onclick="setDimYear('2021')">2021</button>
        <button class="yr-btn" onclick="setDimYear('2022')">2022</button>
        <button class="yr-btn" onclick="setDimYear('2023')">2023</button>
        <button class="yr-btn" onclick="setDimYear('2024')">2024</button>
        <button class="yr-btn" onclick="setDimYear('2025')">2025</button>
      </div>
      <div id="dim-content"></div>
    </div>
'''

html = re.sub(r'<div id="sec-dim".*?<div id="dim-content"></div>\s*</div>', new_sec_dim.strip(), html, flags=re.DOTALL)

# 2. Update the JS block
new_js = '''
    var dimState = {};
    var dimYear = null;
    var dimCharts = {};
    var DIM_YEAR_COLORS = {'2021':'#8e44ad','2022':'#f39c12','2023':'#e84393','2024':'#2980b9','2025':'#16a085'};

    function setDimYear(y) {
      dimYear = y;
      var btns = document.getElementById('yf-dim').querySelectorAll('.yr-btn');
      btns.forEach(b => b.classList.remove('active'));
      if(y === null) btns[0].classList.add('active');
      else {
        btns.forEach(b => { if(b.textContent === y) b.classList.add('active'); });
      }
      var dimOrder = ['Dim_1','Dim_2','Dim_5','Dim_6','Dim_7','Dim_8','Dim_9','Dim_10','Dim_11','Dim_12'];
      dimOrder.forEach(dk => {
        if(document.getElementById('body-'+dk) && document.getElementById('body-'+dk).style.display === 'block') {
           updateDimChart(dk);
        }
      });
    }

    function buildDimensions() {
      var container = document.getElementById('dim-content');
      if (!container) return;
      var h = '';
      var dimOrder = ['Dim_1','Dim_2','Dim_5','Dim_6','Dim_7','Dim_8','Dim_9','Dim_10','Dim_11','Dim_12'];
      
      dimOrder.forEach(function(dk) {
        var d = DIM_DATA[dk];
        if (!d) return;
        dimState[dk] = 0; // Default first indicator
        var num = dk.replace('Dim_','');
        h += '<div style="margin-bottom:24px;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;background:#fff">';
        h += '<div onclick="toggleDimAccordion(\\''+dk+'\\')" style="background:#1b365d;color:#fff;padding:16px 20px;cursor:pointer;display:flex;justify-content:space-between;align-items:center">';
        h += '<div><strong>Dimensi\u00f3n ' + num + ':</strong> ' + d.titulo + '</div>';
        h += '<span id="arrow-'+dk+'" style="font-size:14px">\u25B6</span></div>'; // default closed
        
        h += '<div id="body-'+dk+'" style="display:none;padding:20px">';
        h += '<p style="font-size:13px;color:#666;margin-bottom:16px;font-style:italic">' + d.descripcion + '</p>';
        h += '<div class="item-chips" id="pills-'+dk+'" style="margin-bottom:20px"></div>';
        h += '<div class="chart-wrap" style="height:350px"><canvas id="chart-'+dk+'"></canvas></div>';
        h += '<div id="interp-'+dk+'" style="font-size: 13px; color: #475569; margin-top: 12px; padding: 12px 16px; background: #F8FAFC; border-left: 3px solid #1b365d; border-radius: 0 8px 8px 0;"></div>';
        h += '</div></div>';
      });
      container.innerHTML = h;
      
      // Open the first one
      toggleDimAccordion('Dim_1');
    }

    function toggleDimAccordion(dk) {
       var body = document.getElementById('body-'+dk);
       var arrow = document.getElementById('arrow-'+dk);
       if(body.style.display === 'none') {
          body.style.display = 'block';
          arrow.textContent = '\u25BC';
          renderDimPills(dk);
          updateDimChart(dk);
       } else {
          body.style.display = 'none';
          arrow.textContent = '\u25B6';
       }
    }

    function renderDimPills(dk) {
       var d = DIM_DATA[dk];
       var html = '';
       d.indicadores.forEach((ind, idx) => {
          var cls = idx === dimState[dk] ? 'item-chip active' : 'item-chip';
          html += '<div class="'+cls+'" onclick="setDimInd(\\''+dk+'\\','+idx+')" style="display:inline-block;padding:6px 12px;margin:4px;border-radius:16px;font-size:12px;cursor:pointer;background:'+(idx===dimState[dk]?'#1b365d':'#f1f5f9')+';color:'+(idx===dimState[dk]?'#fff':'#333')+'">' + ind.nombre + '</div>';
       });
       document.getElementById('pills-'+dk).innerHTML = html;
    }

    function setDimInd(dk, idx) {
       dimState[dk] = idx;
       renderDimPills(dk);
       updateDimChart(dk);
    }

    function updateDimChart(dk) {
       var d = DIM_DATA[dk];
       var idx = dimState[dk];
       var ind = d.indicadores[idx];
       
       var labels = [];
       var data = [];
       var colors = [];
       var anios = d.anios;
       
       if(dimYear !== null) {
          anios = [dimYear];
       }
       
       var isPercent = false;
       // First pass to determine if it's percent based on name or values
       if(ind.nombre.includes('%')) isPercent = true;
       
       anios.forEach(a => {
          var v = ind[a];
          if(v !== null && v !== undefined && v !== 'S/I' && v !== '-') {
             labels.push(a);
             if(typeof v === 'number' && isPercent) {
                data.push(v * 100);
             } else {
                data.push(v);
                if(typeof v === 'number' && v > 0 && v <= 1 && !Number.isInteger(v)) isPercent = true; 
             }
             colors.push(dimYear === null ? (DIM_YEAR_COLORS[a] || '#1b365d') : '#1b365d');
          }
       });
       
       var ctx = document.getElementById('chart-'+dk).getContext('2d');
       if(dimCharts[dk]) dimCharts[dk].destroy();
       
       var chartTitle = ind.nombre;
       if(chartTitle.length > 90) {
          var words = chartTitle.split(' ');
          var lines = []; var cur = '';
          words.forEach(w => { if((cur+' '+w).length > 90) { lines.push(cur); cur=w; } else cur += (cur?' ':'')+w; });
          if(cur) lines.push(cur);
          chartTitle = lines;
       }

       dimCharts[dk] = new Chart(ctx, {
          type: 'bar',
          data: {
             labels: labels,
             datasets: [{
                data: data,
                backgroundColor: colors,
                borderRadius: 4,
                maxBarThickness: 60
             }]
          },
          options: {
             responsive: true,
             maintainAspectRatio: false,
             plugins: {
                legend: { display: false },
                title: { display: true, text: chartTitle, font: { size: 14 } },
                datalabels: {
                   color: '#fff',
                   font: { weight: 'bold', size: 12 },
                   anchor: 'center',
                   align: 'center',
                   formatter: function(value) {
                      if(isPercent) return value.toFixed(1).replace('.',',') + '%';
                      if(value >= 1000) return value.toLocaleString('es-CL');
                      return value;
                   }
                },
                tooltip: {
                   callbacks: {
                      label: function(c) {
                         if(isPercent) return c.raw.toFixed(1).replace('.',',') + '%';
                         return c.raw.toLocaleString('es-CL');
                      }
                   }
                }
             },
             scales: {
                y: {
                   beginAtZero: true,
                   max: isPercent ? 100 : undefined,
                   ticks: {
                      callback: function(value) {
                         if(isPercent) return value + '%';
                         if(value >= 1000) return value.toLocaleString('es-CL');
                         return value;
                      }
                   }
                }
             }
          }
       });

       // Interpretation
       var interpEl = document.getElementById('interp-'+dk);
       if(labels.length === 0) {
          interpEl.innerHTML = '<strong>Nota:</strong> No hay datos disponibles para el indicador seleccionado en el año '+ (dimYear||'seleccionado') +'.';
       } else if (labels.length === 1) {
          var valStr = isPercent ? data[0].toFixed(1).replace('.',',') + '%' : data[0].toLocaleString('es-CL');
          interpEl.innerHTML = '<strong>Interpretación:</strong> En <strong>'+labels[0]+'</strong>, el indicador registra un valor de <strong>'+valStr+'</strong>.';
       } else {
          var first = data[0]; var last = data[data.length-1];
          var trend = last > first ? 'un incremento' : (last < first ? 'una disminución' : 'estabilidad');
          var v1 = isPercent ? first.toFixed(1).replace('.',',') + '%' : first.toLocaleString('es-CL');
          var v2 = isPercent ? last.toFixed(1).replace('.',',') + '%' : last.toLocaleString('es-CL');
          interpEl.innerHTML = '<strong>Interpretación:</strong> Entre '+labels[0]+' y '+labels[labels.length-1]+', el indicador muestra <strong>'+trend+'</strong>, pasando de <strong>'+v1+'</strong> a <strong>'+v2+'</strong>.';
       }
    }
'''

html = re.sub(r'function buildDimensions\(\) \{.*?(?=function buildTrends)', new_js, html, flags=re.DOTALL)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("Done replacing dimensions logic.")
