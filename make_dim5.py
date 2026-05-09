import re

with open("dashboard_vcm_dim5.html", "r", encoding="utf-8") as f:
    content = f.read()

data_match = re.search(r'DATA=\{.*?\};', content)
if not data_match:
    print("Could not find DATA")
    exit(1)

data_json = data_match.group(0)

header_css = content.split('</head>')[0]

new_html = f"""{header_css}
</head>
<body>
  <div class="header-top">
    <div style="display: flex; align-items: center; gap: 20px;">
      <h1>Universidad San Sebastián</h1>
      <a href="dashboard_vcm.html" style="background: #1b365d; color: #fff; padding: 6px 12px; border-radius: 4px; font-size: 13px; font-weight: 600; text-decoration: none; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">⬅ Volver al Resumen</a>
    </div>
    <div class="logo">Dimensión 5: Resultados Formativos</div>
  </div>
  <div class="header-nav">
    <div class="subtitle">Evaluación de Resultados en Estudiantes</div>
    <div>2021 — 2025</div>
  </div>
  <div class="container">
    <div class="section">
      <div class="section-title" style="display:flex; justify-content:space-between; align-items:center;">
        <span>Indicadores de Dimensión 5</span>
        <button id="view-toggle" class="year-btn active" style="font-size: 14px;" onclick="toggleView()">Ver: Top-2-Box (%) / % Sí</button>
      </div>
      <div class="section-sub">Métricas vinculadas al desarrollo de competencias, habilidades y percepción de impacto profesional.</div>
      <div class="year-filter" id="yf-dim5"></div>
      <div class="item-controls" id="ctrl-dim5"></div>
      <div class="item-chips" id="chips-dim5"></div>
      <div class="chart-wrap"><canvas id="chart-dim5"></canvas></div>
    </div>
  </div>
  <script>
    const COLORS = ['#1e4c9a', '#7d4199', '#009a74', '#f37021', '#f3a81a', '#4c3c5c', '#2a82c9', '#e64d3d', '#8c7a6b', '#5c9d38'];
    const YEAR_COLORS = {{ 2021: '#8e44ad', 2022: '#f39c12', 2023: '#e84393', 2024: '#2980b9', 2025: '#16a085' }};
    let chartDim5 = null;
    Chart.register(ChartDataLabels);
    
    function hexToRgba(hex, alpha) {{
       let hexColor = hex.replace('#', '');
       if(hexColor.length === 3) hexColor = hexColor.split('').map(c => c+c).join('');
       const r = parseInt(hexColor.substring(0,2), 16);
       const g = parseInt(hexColor.substring(2,4), 16);
       const b = parseInt(hexColor.substring(4,6), 16);
       return `rgba(${{r}},${{g}},${{b}},${{alpha}})`;
    }}

    let DATA;
    {data_json}

    // Definición de Indicadores de Dimensión 5 y dónde se encuentran en DATA
    const DIM5_ITEMS = [
      {{ id: 23, label: 'Significancia en Formación (T2B)', source: 'indicadores' }},
      {{ id: 24, label: 'Permitió conocer campo laboral (% Sí)', source: 'indicadores' }},
      {{ id: 25, label: 'Trabajar con otras carreras', source: 'importancia' }},
      {{ id: 26, label: 'Trabajo en equipo / Colaboración', source: 'habilidades' }},
      {{ id: 27, label: 'Competencia disciplinar', source: 'habilidades' }},
      {{ id: 28, label: 'Manejo de información (toma de decisiones)', source: 'habilidades' }},
      {{ id: 29, label: 'Prolijidad / Atención al detalle', source: 'habilidades' }},
      {{ id: 30, label: 'Empatía', source: 'habilidades' }},
      {{ id: 31, label: 'Trabajo en equipo / Colaboración', source: 'habilidades' }},
      {{ id: 32, label: 'Comunicación efectiva', source: 'habilidades' }},
      {{ id: 33, label: 'Adaptación y flexibilidad', source: 'habilidades' }},
      {{ id: 34, label: 'Resolución de problemas', source: 'habilidades' }},
      {{ id: 35, label: 'Ciudadanía responsable', source: 'habilidades' }},
      {{ id: 36, label: 'Conocer la realidad (problemas/desafíos)', source: 'importancia' }},
      {{ id: 37, label: 'Aportar desde el rol profesional', source: 'importancia' }},
      {{ id: 38, label: 'Incrementar redes de contactos', source: 'importancia' }},
      {{ id: 39, label: 'Fortalecer vocación profesional', source: 'importancia' }}
    ];

    let currentYear = 'Todos los años';
    let viewMode = 't2b'; // 't2b' or 'likert'
    let activeItems = new Set();

    function getUniqueItems() {{
        const unique = [];
        const seen = new Set();
        DIM5_ITEMS.forEach(item => {{
            if(!seen.has(item.label)) {{
                seen.add(item.label);
                unique.push(item.label);
            }}
        }});
        return unique;
    }}

    function init() {{
      const years = [2021, 2022, 2023, 2024, 2025];
      const yf = document.getElementById('yf-dim5');
      
      const allBtn = document.createElement('button');
      allBtn.className = 'year-btn active'; 
      allBtn.textContent = 'Todos los años';
      allBtn.onclick = () => {{
        document.querySelectorAll('#yf-dim5 .year-btn').forEach(x => x.classList.remove('active'));
        allBtn.classList.add('active');
        currentYear = 'Todos los años';
        renderChart();
      }};
      yf.appendChild(allBtn);

      years.forEach(y => {{
        const b = document.createElement('button');
        b.className = 'year-btn'; 
        b.textContent = y;
        b.onclick = () => {{
          document.querySelectorAll('#yf-dim5 .year-btn').forEach(x => x.classList.remove('active'));
          b.classList.add('active');
          currentYear = y;
          renderChart();
        }};
        yf.appendChild(b);
      }});

      activeItems = new Set(getUniqueItems());
      
      const ctrl = document.getElementById('ctrl-dim5');
      ctrl.innerHTML = '<button onclick="toggleAll(true)">✓ Todos</button>'
        + '<button onclick="toggleAll(false)">✕ Ninguno</button>'
        + '<span class="item-count" id="count-dim5"></span>';

      buildChips();
      renderChart();
    }}

    function buildChips() {{
      const container = document.getElementById('chips-dim5');
      container.innerHTML = '';
      const items = getUniqueItems();
      items.forEach(item => {{
        const chip = document.createElement('span');
        chip.className = 'item-chip' + (activeItems.has(item) ? '' : ' off');
        chip.textContent = item;
        chip.onclick = () => {{
          if (activeItems.has(item)) activeItems.delete(item);
          else activeItems.add(item);
          chip.classList.toggle('off');
          updateCount();
          renderChart();
        }};
        container.appendChild(chip);
      }});
      updateCount();
    }}

    function updateCount() {{
      const total = getUniqueItems().length;
      document.getElementById('count-dim5').textContent = activeItems.size + ' de ' + total + ' seleccionados';
    }}

    function toggleAll(on) {{
      const items = getUniqueItems();
      if (on) items.forEach(i => activeItems.add(i));
      else activeItems.clear();
      document.querySelectorAll('#chips-dim5 .item-chip').forEach(c => {{
        if (on) c.classList.remove('off'); else c.classList.add('off');
      }});
      updateCount();
      renderChart();
    }}

    function toggleView() {{
      viewMode = viewMode === 't2b' ? 'likert' : 't2b';
      const btn = document.getElementById('view-toggle');
      if (viewMode === 't2b') {{
        btn.textContent = 'Ver: Top-2-Box (%) / % Sí';
        btn.classList.add('active');
      }} else {{
        btn.textContent = 'Ver: Distribución Likert (1-5)';
        btn.classList.remove('active');
      }}
      renderChart();
    }}

    function setChartHeight(canvas, h) {{
      canvas.parentElement.style.height = h + 'px';
    }}

    function renderChart() {{
      if (chartDim5) chartDim5.destroy();
      const canvas = document.getElementById('chart-dim5');
      
      const isAll = currentYear === 'Todos los años';
      const indexAxis = 'y';

      // Deduplicate labels and apply active filter
      const uniqueItems = [];
      const seen = new Set();
      DIM5_ITEMS.forEach(item => {{
          if(!seen.has(item.label) && activeItems.has(item.label)) {{
              seen.add(item.label);
              uniqueItems.push(item);
          }}
      }});

      let datasets = [];
      let labels = [];

      if (viewMode === 't2b') {{
          // TOP-2-BOX VIEW (Simple bars)
          labels = uniqueItems.map(item => item.label);
          
          if (isAll) {{
              setChartHeight(canvas, Math.max(labels.length * 150, 450));
              const years = [2021, 2022, 2023, 2024, 2025];
              datasets = years.map(y => {{
                  const data = uniqueItems.map(item => {{
                      let val = null;
                      if (item.source === 'indicadores') {{
                          const m = DATA.indicadores.find(r => r['Año'] === y && r['Indicador'] === item.label);
                          if (m) val = m['Resultado (%)'] * 100;
                      }} else {{
                          const m = DATA[item.source].find(r => r['Año'] === y && r['Indicador'] === item.label);
                          if (m) val = m['Top_2_Box (%)'] * 100;
                      }}
                      return val;
                  }});
                  return {{
                      label: y.toString(),
                      data: data,
                      backgroundColor: YEAR_COLORS[y],
                      borderRadius: 6,
                      barThickness: 16
                  }};
              }});
          }} else {{
              setChartHeight(canvas, Math.max(labels.length * 55, 250));
              const data = uniqueItems.map(item => {{
                  let val = null;
                  if (item.source === 'indicadores') {{
                      const m = DATA.indicadores.find(r => r['Año'] === currentYear && r['Indicador'] === item.label);
                      if (m) val = m['Resultado (%)'] * 100;
                  }} else {{
                      const m = DATA[item.source].find(r => r['Año'] === currentYear && r['Indicador'] === item.label);
                      if (m) val = m['Top_2_Box (%)'] * 100;
                  }}
                  return val;
              }});
              datasets = [{{
                  data: data,
                  backgroundColor: labels.map((_, i) => COLORS[i % COLORS.length]),
                  borderRadius: 6,
                  barThickness: 22
              }}];
          }}
          
          chartDim5 = new Chart(canvas, {{
              type: 'bar',
              data: {{ labels: labels, datasets: datasets }},
              options: {{
                  indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                  plugins: {{
                      legend: {{ display: isAll, position: 'top', labels: {{ color: '#333333', usePointStyle: true, pointStyle: 'circle', font: {{ size: 15 }} }} }},
                      title: {{ display: true, text: 'Indicadores Dimensión 5 (' + currentYear + ') - Top-2-Box / % Sí', font: {{ size: 18 }} }},
                      datalabels: {{
                          color: '#fff',
                          font: {{ weight: 'bold', size: 14 }},
                          formatter: (value) => value ? (value.toFixed(2) + '%').replace('.', ',') : ''
                      }},
                      tooltip: {{ 
                          titleFont: {{ size: 16 }},
                          bodyFont: {{ size: 16 }},
                          callbacks: {{ label: c => (isAll ? c.dataset.label + ': ' : '') + (c.raw ? (c.raw.toFixed(2) + '%').replace('.', ',') : 'Sin dato') }} 
                      }}
                  }},
                  scales: {{
                      x: {{ min: 0, max: 100, grid: {{ color: '#eaeaea' }}, ticks: {{ color: '#666666', font: {{ size: 15 }}, callback: v => v + '%' }} }},
                      y: {{ grid: {{ display: false }}, ticks: {{ color: '#333333', font: {{ size: 15 }} }} }}
                  }}
              }}
          }});

      }} else {{
          // LIKERT VIEW (Stacked bars)
          // Filter out items that are from "indicadores" because they do not have Likert distributions
          const likertItems = uniqueItems.filter(i => i.source === 'importancia' || i.source === 'habilidades');
          labels = likertItems.map(item => item.label);
          const likertLabels = ['Nota 1 / Nada', 'Nota 2 / Poco', 'Nota 3 / Medianamente', 'Nota 4 / Importante o Fortalecida', 'Nota 5 / Muy importante o fortalecida'];
          
          if (isAll) {{
              setChartHeight(canvas, Math.max(labels.length * 150, 450));
              const years = [2021, 2022, 2023, 2024, 2025];
              const opacities = [0.2, 0.4, 0.6, 0.8, 1.0];
              
              years.forEach(y => {{
                  [1,2,3,4,5].forEach(level => {{
                      datasets.push({{
                          label: likertLabels[level-1],
                          datasetYear: y,
                          stack: y.toString(),
                          data: likertItems.map(item => {{
                              const m = DATA[item.source].find(r => r['Año'] === y && r['Indicador'] === item.label);
                              return m ? (m[`% ${{level}}`] * 100) : 0;
                          }}),
                          backgroundColor: hexToRgba(YEAR_COLORS[y], opacities[level-1]),
                          barThickness: 16
                      }});
                  }});
              }});
              
              chartDim5 = new Chart(canvas, {{
                  type: 'bar',
                  data: {{ labels: labels, datasets }},
                  options: {{
                      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                      plugins: {{
                          legend: {{
                              position: 'top', 
                              onClick: function(e, legendItem, legend) {{
                                  const index = legendItem.datasetIndex; // 0 to 4
                                  const chart = legend.chart;
                                  const isHidden = chart.isDatasetVisible(index);
                                  chart.data.datasets.forEach((ds, i) => {{
                                      if (i % 5 === index) {{
                                          if (isHidden) chart.hide(i);
                                          else chart.show(i);
                                      }}
                                  }});
                              }},
                              labels: {{ 
                                  color: '#333333', usePointStyle: true, pointStyle: 'rectRounded', font: {{ size: 15 }},
                                  filter: function(item, chart) {{ return item.datasetIndex < 5; }}
                              }} 
                          }},
                          title: {{ display: true, text: 'Distribución Likert (' + currentYear + ') - Indicadores con Escala', font: {{ size: 18 }} }},
                          datalabels: {{
                              color: '#fff',
                              font: {{ weight: 'bold', size: 13 }},
                              formatter: (value, context) => {{
                                  const level = (context.datasetIndex % 5) + 1;
                                  if (level >= 4 && value >= 4.0) return (value.toFixed(2) + '%').replace('.', ',');
                                  return '';
                              }}
                          }},
                          tooltip: {{ 
                              titleFont: {{ size: 16 }},
                              bodyFont: {{ size: 16 }},
                              callbacks: {{ 
                                  title: (context) => context[0].label + ' (' + context[0].dataset.datasetYear + ')',
                                  label: c => likertLabels[(c.datasetIndex % 5)] + ': ' + (c.raw ? (c.raw.toFixed(2) + '%').replace('.', ',') : 'Sin dato') 
                              }} 
                          }}
                      }},
                      scales: {{
                          x: {{ stacked: true, min: 0, max: 100, grid: {{ color: '#eaeaea' }}, ticks: {{ color: '#666666', font: {{ size: 15 }}, callback: v => v + '%' }} }},
                          y: {{ stacked: true, grid: {{ display: false }}, ticks: {{ color: '#333333', font: {{ size: 15 }} }} }}
                      }}
                  }}
              }});

          }} else {{
              setChartHeight(canvas, Math.max(labels.length * 55, 250));
              const opacities = [0.2, 0.4, 0.6, 0.8, 1.0];
              datasets = [1, 2, 3, 4, 5].map(level => {{
                  return {{
                      label: likertLabels[level-1],
                      data: likertItems.map(item => {{
                          const m = DATA[item.source].find(r => r['Año'] === currentYear && r['Indicador'] === item.label);
                          return m ? (m[`% ${{level}}`] * 100) : 0;
                      }}),
                      backgroundColor: hexToRgba(YEAR_COLORS[currentYear], opacities[level-1]),
                      barThickness: 22
                  }}
              }});

              chartDim5 = new Chart(canvas, {{
                  type: 'bar',
                  data: {{ labels, datasets }},
                  options: {{
                      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                      plugins: {{
                          legend: {{ position: 'top', labels: {{ color: '#333333', usePointStyle: true, pointStyle: 'rectRounded', font: {{ size: 15 }} }} }},
                          title: {{ display: true, text: 'Distribución Likert (' + currentYear + ') - Indicadores con Escala', font: {{ size: 18 }} }},
                          datalabels: {{
                              color: '#fff',
                              font: {{ weight: 'bold', size: 14 }},
                              formatter: (value, context) => {{
                                  const datasetIndex = context.datasetIndex; // 0 to 4
                                  if (datasetIndex >= 3 && value >= 4.0) return (value.toFixed(2) + '%').replace('.', ',');
                                  return '';
                              }}
                          }},
                          tooltip: {{ 
                              titleFont: {{ size: 16 }},
                              bodyFont: {{ size: 16 }},
                              callbacks: {{ label: c => c.dataset.label + ': ' + (c.raw.toFixed(2) + '%').replace('.', ',') }} 
                          }}
                      }},
                      scales: {{
                          x: {{ stacked: true, min: 0, max: 100, grid: {{ color: '#eaeaea' }}, ticks: {{ color: '#666666', font: {{ size: 15 }}, callback: v => v + '%' }} }},
                          y: {{ stacked: true, grid: {{ display: false }}, ticks: {{ color: '#333333', font: {{ size: 15 }} }} }}
                      }}
                  }}
              }});
          }}
      }}
    }}

    document.addEventListener("DOMContentLoaded", init);
  </script>

    // Función global para añadir botones de descarga PNG
    document.addEventListener('DOMContentLoaded', () => {{
      document.querySelectorAll('.chart-wrap').forEach(wrap => {{
        const canvas = wrap.querySelector('canvas');
        if (!canvas) return;
        
        const btn = document.createElement('button');
        btn.className = 'download-btn';
        btn.innerHTML = '⬇ PNG';
        btn.title = 'Descargar gráfico como PNG';
        btn.onclick = () => {{
          const tempCanvas = document.createElement('canvas');
          tempCanvas.width = canvas.width;
          tempCanvas.height = canvas.height;
          const ctx = tempCanvas.getContext('2d');
          ctx.fillStyle = '#ffffff';
          ctx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
          ctx.drawImage(canvas, 0, 0);
          
          const link = document.createElement('a');
          link.download = canvas.id + '.png';
          link.href = tempCanvas.toDataURL('image/png', 1.0);
          link.click();
        }};
        wrap.appendChild(btn);
      }});
    }});

</body>
</html>
"""

with open("dashboard_vcm_dim5.html", "w", encoding="utf-8") as f:
    f.write(new_html)

print("Created dashboard_vcm_dim5.html successfully")
