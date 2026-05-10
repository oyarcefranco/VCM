import re, json

with open("dashboard_vcm_dim5.html", "r", encoding="utf-8") as f:
    content = f.read()

data_match = re.search(r'DATA=\{.*?\};', content)
if not data_match:
    print("Could not find DATA")
    exit(1)

data_json = data_match.group(0)

# Inject Likert distribution for Significancia en Formación into indicadores
try:
    import pandas as pd
    raw_data_str = data_json[5:-1]  # Remove 'DATA=' and ';'
    dim5_data = json.loads(raw_data_str)
    
    df_sig = pd.read_excel('base_homologada_final.xlsx', sheet_name='Significancia_Formacion')
    year_col = [c for c in df_sig.columns if c.startswith('A')][0]
    
    for ind_record in dim5_data.get('indicadores', []):
        if ind_record.get('Indicador') == 'Significancia en Formación (T2B)':
            year = ind_record['Año']
            subset = df_sig[df_sig[year_col] == year]['Q01_Significancia'].dropna()
            n = len(subset)
            if n > 0:
                for level in [1, 2, 3, 4, 5]:
                    ind_record[f'% {level}'] = round(float((subset == level).sum() / n), 6)
    
    data_json = 'DATA=' + json.dumps(dim5_data, ensure_ascii=False) + ';'
    print("Injected Likert data for Significancia en Formación")
except Exception as e:
    print(f"Warning: Could not inject Likert data: {e}")

header_css = content.split('</head>')[0]
if ".download-btn" not in header_css:
    header_css = header_css.replace("</style>", """
    .download-btn {
      position: absolute;
      top: 10px;
      right: 10px;
      background: #fff;
      border: 1px solid #ccc;
      padding: 6px 10px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 700;
      color: #555;
      cursor: pointer;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      z-index: 10;
      transition: all 0.2s;
    }
    .download-btn:hover {
      background: #f0f0f0;
      color: #1b365d;
      border-color: #1b365d;
    }
</style>""")

new_html = f"""{header_css}
</head>
<body>
  <div class="header-top">
    <div style="display: flex; align-items: center; gap: 16px;">
      <img src="logo_uss.png" alt="Logo USS" style="height: 40px; object-fit: contain;" onerror="this.style.display='none'">
      <img src="logo_vcm.png" alt="Logo VcM" style="height: 40px; object-fit: contain;" onerror="this.style.display='none'">
      <h1>Universidad San Sebastián</h1>
      <a href="dashboard_vcm.html" style="background: #1b365d; color: #fff; padding: 6px 12px; border-radius: 4px; font-size: 13px; font-weight: 600; text-decoration: none; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">⬅ Volver al Resumen</a>
    </div>
  </div>
  <div class="header-nav">
    <div class="subtitle">Resultados formativos estudiantes — Modelo de Evaluación VcM: Dimensión 5</div>
    <div>2021 — 2025</div>
  </div>
  <div class="container">
    <div class="section">
      <div class="section-title" style="display:flex; justify-content:space-between; align-items:center;">
        <span>Indicadores de Dimensión 5</span>
        <button id="view-toggle" class="year-btn active" style="font-size: 14px;" onclick="toggleView()">Ver: Top-2-Box (%) / % Sí</button>
      </div>
      <div class="section-sub">Esta dimensión evalúa los resultados formativos percibidos por los estudiantes a partir de su participación en iniciativas y experiencias de Vinculación con el Medio, considerando el desarrollo de competencias disciplinares, habilidades transversales, capacidades socioemocionales y comprensión del rol profesional en relación con el entorno.<br><strong>Métricas:</strong> Top-2-Box (%) para indicadores Likert y % Sí para indicadores dicotómicos.<br><strong>Fórmula T2B</strong> = (n Nota 4 + n Nota 5) / N total × 100. <strong>% Sí</strong> = n respuestas "Sí" / N total × 100.<br><span style="color:#2980b9; font-style:italic;">💡 Seleccione un solo indicador y un año específico para ver la interpretación descriptiva detallada y el número de respuestas validadas (n).</span></div>
      <div class="year-filter" id="yf-dim5"></div>
      <div class="item-controls" id="ctrl-dim5"></div>
      <div class="item-chips" id="chips-dim5"></div>
      <div id="avail-dim5" class="avail-note" style="display: none; margin-bottom: 20px;"></div>
      <div class="chart-wrap"><canvas id="chart-dim5"></canvas></div>
      <div id="interp-dim5" style="font-size: 13px; color: #475569; margin-top: 12px; padding: 12px 16px; background: #F8FAFC; border-left: 3px solid #1b365d; border-radius: 0 8px 8px 0;"></div>
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

    const DIM5_OFFICIAL_TITLES = {{
      'Significancia en Formación (T2B)': '% de estudiantes que declaran que la participación en iniciativas VcM fue significativa o muy significativa para su formación profesional',
      'Permitió conocer campo laboral (% Sí)': '% de estudiantes que consideran que el proyecto les permitió conocer su campo laboral',
      'Trabajar con otras carreras': '% de estudiantes que participan en proyectos multidisciplinarios',
      'Trabajo en equipo / Colaboración': '% de estudiantes que fortalecen colaboración a partir de iniciativas VcM',
      'Competencia disciplinar': '% de estudiantes que fortalecen su competencia disciplinar a partir de iniciativas VcM',
      'Manejo de información (toma de decisiones)': '% de estudiantes que fortalecen manejo de información a partir de iniciativas VcM',
      'Prolijidad / Atención al detalle': '% de estudiantes que fortalecen prolijidad disciplinar a partir de iniciativas VcM',
      'Empatía': '% de estudiantes que fortalecen empatía a partir de iniciativas VcM',
      'Comunicación efectiva': '% de estudiantes que fortalecen comunicación a partir de iniciativas VcM',
      'Adaptación y flexibilidad': '% de estudiantes que fortalecen adaptación y flexibilidad a partir de iniciativas VcM',
      'Resolución de problemas': '% de estudiantes que fortalecen resolución de problemas',
      'Ciudadanía responsable': '% de estudiantes que fortalecen habilidades de ciudadanía',
      'Conocer la realidad (problemas/desafíos)': '% de estudiantes que valoran la experiencia para conocer la realidad social',
      'Aportar desde el rol profesional': '% de estudiantes que comprenden su aporte profesional',
      'Incrementar redes de contactos': '% de estudiantes que incrementan redes de contacto',
      'Fortalecer vocación profesional': '% de estudiantes que fortalecen su vocación profesional'
    }};

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
      const availEl = document.getElementById('avail-dim5');
      const interpEl = document.getElementById('interp-dim5');
      if (interpEl) interpEl.innerHTML = '';
      
      const isAll = currentYear === 'Todos los años';

      if (!isAll) {{
          // Availability check
          const allItemsLabels = [...new Set(DIM5_ITEMS.map(i => i.label))];
          const yearItems = DIM5_ITEMS.filter(item => {{
              const dataPool = DATA[item.source];
              return dataPool.some(r => r['Año'] === currentYear && r['Indicador'] === item.label);
          }});
          const yearItemLabels = new Set(yearItems.map(i => i.label));
          const missing = allItemsLabels.filter(l => !yearItemLabels.has(l));
          
          if (missing.length > 0) {{
              availEl.innerHTML = '<strong>No disponible en ' + currentYear + ':</strong> ' + missing.join(', ');
              availEl.style.display = 'inline-block';
          }} else {{
              availEl.style.display = 'none';
          }}
      }} else {{
          availEl.style.display = 'none';
      }}

      // Deduplicate labels and apply active filter
      const uniqueItems = [];
      const seen = new Set();
      DIM5_ITEMS.forEach(item => {{
          if(!seen.has(item.label) && activeItems.has(item.label)) {{
              seen.add(item.label);
              uniqueItems.push(item);
          }}
      }});

      // Filter out items with no data for selected year
      const filteredItems = isAll ? uniqueItems : uniqueItems.filter(item => {{
          const dataPool = DATA[item.source];
          return dataPool.some(r => r['Año'] === currentYear && r['Indicador'] === item.label);
      }});

      const isSingleItem = filteredItems.length === 1;
      let datasets = [];
      let labels = [];

      if (viewMode === 't2b') {{
          // TOP-2-BOX VIEW
          labels = filteredItems.map(item => item.label);
          const indexAxis = isSingleItem ? 'x' : 'y';
          
          if (isAll) {{
              setChartHeight(canvas, isSingleItem ? 400 : Math.max(labels.length * 150, 450));
              const years = [2021, 2022, 2023, 2024, 2025];
              datasets = years.map(y => {{
                  const data = filteredItems.map(item => {{
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
                      barThickness: isSingleItem ? undefined : 16,
                      maxBarThickness: isSingleItem ? 80 : undefined
                  }};
              }});
          }} else {{
            setChartHeight(canvas, isSingleItem ? 400 : Math.max(labels.length * 55, 250));
            const data = filteredItems.map(item => {{
                let val = null;
                let nResp = null;
                if (item.source === 'indicadores') {{
                    const m = DATA.indicadores.find(r => r['Año'] === currentYear && r['Indicador'] === item.label);
                    if (m) {{ val = m['Resultado (%)'] * 100; nResp = m['N_Respuestas']; }}
                }} else {{
                    const m = DATA[item.source].find(r => r['Año'] === currentYear && r['Indicador'] === item.label);
                    if (m) {{ val = m['Top_2_Box (%)'] * 100; nResp = m['N_Respuestas']; }}
                }}
                return val;
            }});
            datasets = [{{
                data: data,
                backgroundColor: YEAR_COLORS[currentYear],
                borderRadius: 6,
                barThickness: isSingleItem ? undefined : 22,
                maxBarThickness: isSingleItem ? 80 : undefined
            }}];

            // Show N + interpretation for single item
            if (isSingleItem && interpEl) {{
                const item = filteredItems[0];
                let nResp = null;
                let val = null;
                if (item.source === 'indicadores') {{
                    const m = DATA.indicadores.find(r => r['Año'] === currentYear && r['Indicador'] === item.label);
                    if (m) {{ val = m['Resultado (%)'] * 100; nResp = m['N_Respuestas']; }}
                }} else {{
                    const m = DATA[item.source].find(r => r['Año'] === currentYear && r['Indicador'] === item.label);
                    if (m) {{ val = m['Top_2_Box (%)'] * 100; nResp = m['N_Respuestas']; }}
                }}
                let html = '<strong>Respuestas validadas:</strong> n = ' + (nResp || '—').toLocaleString('es-CL') + ' (' + currentYear + ')';
                if (val !== null) {{
                    const pct = val.toFixed(2).replace('.', ',');
                    let trend = val >= 85 ? 'alto' : val >= 70 ? 'moderado' : 'bajo';
                    html += '<br><strong>Interpretación:</strong> El ' + pct + '% de los estudiantes encuestados en ' + currentYear + ' presenta un nivel <strong>' + trend + '</strong> en este indicador.';
                }}
                interpEl.innerHTML = html;
            }}
        }}

          // Use official title for single item
          const chartTitle = isSingleItem
              ? (DIM5_OFFICIAL_TITLES[labels[0]] || labels[0]) + ' — ' + currentYear
              : (labels.length === 1 ? labels[0] + ' — ' : 'Indicadores Dimensión 5 — ') + currentYear + (labels.length > 1 ? ' (Top-2-Box / % Sí)' : '');
          
          chartDim5 = new Chart(canvas, {{
              type: 'bar',
              data: {{ labels: labels, datasets: datasets }},
              options: {{
                  indexAxis: isSingleItem ? 'x' : 'y', responsive: true, maintainAspectRatio: false,
                  plugins: {{
                      legend: {{ display: isAll, position: 'top', labels: {{ color: '#333333', usePointStyle: true, pointStyle: 'circle', font: {{ size: 15 }} }} }},
                      title: {{ display: true, text: chartTitle, font: {{ size: isSingleItem ? 14 : 18 }} }},
                      datalabels: {{
                          color: '#fff',
                          font: {{ weight: 'bold', size: 14 }},
                          formatter: (value, context) => {{
                              if (!value) return '';
                              const yr = isAll ? context.dataset.label : currentYear;
                              return yr + ': ' + (value.toFixed(2) + '%').replace('.', ',');
                          }}
                      }},
                      tooltip: {{ 
                          titleFont: {{ size: 16 }},
                          bodyFont: {{ size: 16 }},
                          callbacks: {{ label: c => (isAll ? c.dataset.label + ': ' : '') + (c.raw ? (c.raw.toFixed(2) + '%').replace('.', ',') : 'Sin dato') }} 
                      }}
                  }},
                  scales: isSingleItem ? {{
                      x: {{ grid: {{ color: '#eaeaea' }}, ticks: {{ color: '#666666', font: {{ size: 15 }} }} }},
                      y: {{ min: 0, max: 100, grid: {{ display: true }}, ticks: {{ color: '#333333', font: {{ size: 15 }}, callback: v => v + '%' }} }}
                  }} : {{
                      x: {{ min: 0, max: 100, grid: {{ color: '#eaeaea' }}, ticks: {{ color: '#666666', font: {{ size: 15 }}, callback: v => v + '%' }} }},
                      y: {{ type: 'category', grid: {{ display: false }}, ticks: {{ color: '#333333', font: {{ size: 15 }} }} }}
                  }}
              }}
          }});

      }} else {{
          // LIKERT VIEW (Stacked bars)
          // Include indicadores source items too if they have Likert data
          const likertItems = filteredItems.filter(i => i.source === 'importancia' || i.source === 'habilidades' || (i.source === 'indicadores' && DATA.indicadores.some(r => r['Indicador'] === i.label && r['% 1'] !== undefined)));
          labels = likertItems.map(item => item.label);
          const likertLabels = ['Nada', 'Poco', 'Medianamente', 'Importante / Fortalecida', 'Muy importante / Muy fortalecida'];
          
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
                          barThickness: labels.length === 1 ? undefined : 16,
                          maxBarThickness: labels.length === 1 ? 80 : undefined
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
                          title: {{ display: true, text: 'Distribución Likert — ' + (labels.length === 1 ? labels[0] + ' — ' : '') + currentYear, font: {{ size: labels.length === 1 ? 15 : 18 }} }},
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
                      barThickness: labels.length === 1 ? undefined : 22,
                      maxBarThickness: labels.length === 1 ? 80 : undefined
                  }}
              }});

              // Show N for single item in Likert view (no interpretation)
              if (likertItems.length === 1 && interpEl) {{
                  const item = likertItems[0];
                  const m = DATA[item.source].find(r => r['Año'] === currentYear && r['Indicador'] === item.label);
                  if (m) {{
                      interpEl.innerHTML = '<strong>Respuestas validadas:</strong> n = ' + (m['N_Respuestas'] || '—').toLocaleString('es-CL') + ' (' + currentYear + ')';
                  }}
              }}

              const likertTitle = labels.length === 1 
                  ? 'Distribución Likert: ' + (DIM5_OFFICIAL_TITLES[labels[0]] || labels[0]) + ' — ' + currentYear
                  : 'Distribución Likert — ' + currentYear;

              chartDim5 = new Chart(canvas, {{
                  type: 'bar',
                  data: {{ labels, datasets }},
                  options: {{
                      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                      plugins: {{
                          legend: {{ position: 'top', labels: {{ color: '#333333', usePointStyle: true, pointStyle: 'rectRounded', font: {{ size: 15 }} }} }},
                          title: {{ display: true, text: likertTitle, font: {{ size: labels.length === 1 ? 14 : 18 }} }},
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

    
  


  


  <script>
    // Función global para añadir botones de descarga PNG
    (function() {{
      const initDownloadButtons = () => {{
        document.querySelectorAll('.chart-wrap').forEach(wrap => {{
          const canvas = wrap.querySelector('canvas');
          if (!canvas || wrap.querySelector('.download-btn')) return;
          
          const btn = document.createElement('button');
          btn.className = 'download-btn';
          btn.innerHTML = '⬇ PNG';
          btn.title = 'Descargar gráfico como PNG';
          btn.onclick = (e) => {{
            e.preventDefault();
            e.stopPropagation();
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = canvas.width;
            tempCanvas.height = canvas.height;
            const ctx = tempCanvas.getContext('2d');
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
            ctx.drawImage(canvas, 0, 0);
            
            const link = document.createElement('a');
            link.download = (canvas.id || 'grafico') + '.png';
            link.href = tempCanvas.toDataURL('image/png', 1.0);
            link.click();
          }};
          wrap.appendChild(btn);
        }});
      }};

      if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initDownloadButtons);
      }} else {{
        initDownloadButtons();
      }}
      
      // Intentos periódicos para asegurar que aparezca en gráficos cargados dinámicamente
      setInterval(initDownloadButtons, 2000);
    }})();
  </script>

</body>
</html>
"""

with open("dashboard_vcm_dim5.html", "w", encoding="utf-8") as f:
    f.write(new_html)

print("Created dashboard_vcm_dim5.html successfully")
