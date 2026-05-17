// Part 2: Tab renderers with all rules applied
function render(tab){
  if(tab==='imp')rLik('imp','Importancia Aspectos Formativos','importancia');
  else if(tab==='hab')rLik('hab','Desarrollo de Habilidades','habilidades');
  else if(tab==='ind')rInd();
  else if(tab==='val')rVal();
  else if(tab==='evo')rEvo();
  else if(tab==='dim')rDim();
}

function rLik(tk,catName,catKey){
  const el=document.getElementById('T'+tk);
  const lik=filt(D.likert).filter(r=>r.Categoria===catName);
  const allLik=D.likert.filter(r=>r.Categoria===catName);
  const pregs=[...new Set(lik.map(r=>r.Pregunta))];
  const allPregs=[...new Set(allLik.map(r=>r.Pregunta))];
  const mode=vm[tk]||'t2b';
  const sel=selInd[tk];
  const ci=D.categorias[catKey];
  const selY=gY();
  const active=sel?[sel]:pregs;
  const single=active.length===1;
  const singleY=selY.length===1;

  // Availability note: indicators missing in selected year
  let availNote='';
  if(singleY){
    const yPregs=new Set(lik.map(r=>r.Pregunta));
    const missing=allPregs.filter(p=>!yPregs.has(p));
    if(missing.length>0) availNote='<div style="font-size:12px;color:#64748b;background:#f8fafc;padding:10px 14px;border-left:3px solid #003366;border-radius:0 8px 8px 0;margin-bottom:14px"><strong>No disponible en '+selY[0]+':</strong> '+missing.join(', ')+'</div>';
  }

  // Dynamic title
  const title=getDynTitle(tk,active,mode);

  // N display
  let nH='';
  if(single&&singleY){const a=aggLik(lik,active[0]);nH='<span class="cn">N = '+a.n.toLocaleString('es-CL')+'</span>';}

  let h='<div class="sd"><h3>'+ci.titulo+'</h3><p>'+ci.descripcion+'</p>';
  if(ci.escala)h+='<p style="font-size:12px;color:#64748b;margin-top:6px"><strong>Escala:</strong> '+ci.escala.join(', ')+'</p>';
  h+='<p class="tip">💡 '+ci.tip+'</p></div>';

  // Pills
  h+='<div class="pills">';
  h+='<span class="pill '+(sel===null?'on':'')+'" onclick="selInd.'+tk+'=null;render(\''+tk+'\')">Todos</span>';
  pregs.forEach(p=>{h+='<span class="pill '+(sel===p?'on':'')+'" onclick="selInd.'+tk+'=\''+p.replace(/'/g,"\\'")+'\';render(\''+tk+'\')">'+p+'</span>';});
  h+='</div>';
  h+=availNote;

  // Chart card
  h+='<div class="cc" id="cc'+tk+'"><div class="ch"><div><span class="ct" id="ctitle'+tk+'"></span>'+nH+'</div><div class="ca">';
  h+='<button class="tg '+(mode==='t2b'?'on':'')+'" onclick="vm.'+tk+'=\'t2b\';render(\''+tk+'\')">Top-2-Box</button>';
  h+='<button class="tg '+(mode==='likert'?'on':'')+'" onclick="vm.'+tk+'=\'likert\';render(\''+tk+'\')">Distribución Likert</button>';
  h+='<button class="dl" onclick="dlPng(\'cc'+tk+'\',\''+tk+'\')">⤓ PNG</button></div></div>';
  h+='<canvas id="ch'+tk+'" height="'+(active.length*32+80)+'"></canvas></div>';

  // Interpretation block
  h+='<div id="interp'+tk+'" style="font-size:13px;color:#475569;margin-top:0;padding:12px 16px;background:#f8fafc;border-left:3px solid #003366;border-radius:0 8px 8px 0"></div>';
  el.innerHTML=h;

  // Set dynamic title via DOM (avoids HTML escaping issues)
  const titleEl=document.getElementById('ctitle'+tk);
  if(titleEl)titleEl.textContent=Array.isArray(title)?title.join(' '):title;

  // Interpretation
  const interpEl=document.getElementById('interp'+tk);
  if(interpEl)interpEl.innerHTML=getInterp(tk,active,filt(D.likert).filter(r=>r.Categoria===catName),filt(D.dicotomicas),selY);

  // Draw chart
  const ctx=document.getElementById('ch'+tk).getContext('2d');dc('ch'+tk);
  if(mode==='t2b'){
    const lb=active,vals=active.map(p=>aggLik(lik,p).t2b*100);
    charts['ch'+tk]=new Chart(ctx,{type:'bar',data:{labels:lb,datasets:[{label:'Top-2-Box (%)',data:vals,backgroundColor:CL.t2b,borderRadius:6,barThickness:26}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},datalabels:{color:'#fff',font:{weight:'bold',size:12},anchor:'center',align:'center',formatter:v=>v.toFixed(1).replace('.',',')+' %'},tooltip:{callbacks:{label:i=>i.raw.toFixed(1).replace('.',',')+' %'}}},scales:{x:{max:100,ticks:{callback:v=>v+'%'},grid:{color:'#f0f0f0'}},y:{ticks:{font:{size:11,family:'Inter'}}}}}});
  }else{
    const lb=active;
    const esc=ci.escala||['1','2','3','4','5'];
    const ds=esc.map((e,i)=>({label:e,data:active.map(p=>{const a=aggLik(lik,p);return a.dist[i]*100;}),backgroundColor:CL.bar[i],borderRadius:2}));
    charts['ch'+tk]=new Chart(ctx,{type:'bar',data:{labels:lb,datasets:ds},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{font:{size:10,family:'Inter'}}},datalabels:{color:'#fff',font:{weight:'bold',size:9},formatter:v=>v>=5?v.toFixed(0)+'%':''},tooltip:{callbacks:{label:i=>i.dataset.label+': '+i.raw.toFixed(1).replace('.',',')+' %'}}},scales:{x:{stacked:true,max:100,ticks:{callback:v=>v+'%'}},y:{stacked:true,ticks:{font:{size:11,family:'Inter'}}}}}});
  }
}

function rInd(){
  const el=document.getElementById('Tind');
  const ci=D.categorias.indicadores;
  const lik=filt(D.likert),dic=filt(D.dicotomicas);
  const selY=gY();
  const singleY=selY.length===1;
  const mode=vm.ind||'t2b';
  const subs=ci.sub;
  const items=[
    {k:'Significancia en Formación',src:'lik'},
    {k:'Cumplimiento de Expectativas',src:'lik'},
    {k:'Importancia para Comunidades Beneficiadas',src:'lik'},
    {k:'Recomendaría a compañeros',src:'dic'},
    {k:'Permitió conocer campo laboral',src:'dic'},
    {k:'Sabía que era iniciativa VcM',src:'dic'}
  ];

  let h='<div class="sd"><h3>'+ci.titulo+'</h3><p>'+ci.descripcion+'</p>';
  Object.entries(subs).forEach(([k,v])=>{h+='<p style="font-size:12px;margin-top:6px"><strong>'+k+':</strong> '+v.p+'</p>';});
  h+='<p class="tip">💡 '+ci.tip+'</p></div>';

  // KPI cards
  h+='<div class="ig">';
  items.forEach(it=>{
    const info=subs[it.k]||{};
    let val,n;
    if(it.src==='lik'){const a=aggLik(lik,it.k);val=pct(a.t2b);n=a.n;}
    else{const a=aggDic(dic,it.k);val=pct(a.pct);n=a.n;}
    h+='<div class="kc"><div class="kv" style="font-size:24px">'+val+'</div><div class="kl">'+it.k+'</div>';
    if(singleY)h+='<div style="font-size:10px;color:#94a3b8;margin-top:4px">N = '+n.toLocaleString('es-CL')+'</div>';
    h+='</div>';
  });
  h+='</div>';

  // Toggle
  h+='<div class="cc" id="ccind"><div class="ch"><span class="ct">Indicadores Clave — '+(mode==='t2b'?'Resumen T2B':'Detalle distribución')+'</span>';
  h+='<div class="ca"><button class="tg '+(mode==='t2b'?'on':'')+'" onclick="vm.ind=\'t2b\';render(\'ind\')">Resumen T2B</button>';
  h+='<button class="tg '+(mode==='detail'?'on':'')+'" onclick="vm.ind=\'detail\';render(\'ind\')">Detalle</button>';
  h+='<button class="dl" onclick="dlPng(\'ccind\',\'indicadores\')">⤓ PNG</button></div></div>';
  h+='<canvas id="chind" height="'+(mode==='detail'?450:300)+'"></canvas></div>';
  el.innerHTML=h;

  const ctx=document.getElementById('chind').getContext('2d');dc('chind');

  if(mode==='t2b'){
    const lb=[],vals=[],colors=[];
    items.forEach(it=>{
      lb.push(it.k);
      if(it.src==='lik'){vals.push(aggLik(lik,it.k).t2b*100);colors.push(CL.t2b);}
      else{vals.push(aggDic(dic,it.k).pct*100);colors.push('#0077cc');}
    });
    charts.chind=new Chart(ctx,{type:'bar',data:{labels:lb,datasets:[{data:vals,backgroundColor:colors,borderRadius:6,barThickness:28}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},datalabels:{color:'#fff',font:{weight:'bold',size:12},anchor:'center',align:'center',formatter:v=>v.toFixed(1).replace('.',',')+' %'},tooltip:{callbacks:{label:i=>i.raw.toFixed(1).replace('.',',')+' %'}}},scales:{x:{max:100,ticks:{callback:v=>v+'%'}},y:{ticks:{font:{size:11,family:'Inter'}}}}}});
  }else{
    // Stacked detail view
    const likItems=items.filter(it=>it.src==='lik');
    const dicItems=items.filter(it=>it.src==='dic');
    const allLb=[...likItems.map(it=>it.k),...dicItems.map(it=>it.k)];

    // For Likert: 5-scale stacked; for Dicotomic: Sí/No stacked
    const ds=[];
    const likEsc=['Escala 1','Escala 2','Escala 3','Escala 4','Escala 5'];
    for(let i=0;i<5;i++){
      ds.push({label:likEsc[i],data:allLb.map(lb=>{
        const likIt=likItems.find(it=>it.k===lb);
        if(likIt){const a=aggLik(lik,lb);return a.dist[i]*100;}
        return null;
      }),backgroundColor:CL.bar[i],borderRadius:2,stack:'s1'});
    }
    // Dicotomic layers
    ds.push({label:'Sí',data:allLb.map(lb=>{
      const dicIt=dicItems.find(it=>it.k===lb);
      if(dicIt){const a=aggDic(dic,lb);return a.pct*100;}
      return null;
    }),backgroundColor:'#22c55e',borderRadius:2,stack:'s1'});
    ds.push({label:'No',data:allLb.map(lb=>{
      const dicIt=dicItems.find(it=>it.k===lb);
      if(dicIt){const a=aggDic(dic,lb);return(1-a.pct)*100;}
      return null;
    }),backgroundColor:'#dc2626',borderRadius:2,stack:'s1'});

    charts.chind=new Chart(ctx,{type:'bar',data:{labels:allLb,datasets:ds},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{font:{size:10,family:'Inter'}}},datalabels:{color:'#fff',font:{weight:'bold',size:9},formatter:v=>(v&&v>=5)?v.toFixed(0)+'%':''},tooltip:{callbacks:{label:i=>i.dataset.label+': '+(i.raw?i.raw.toFixed(1).replace('.',',')+' %':'N/A')}}},scales:{x:{stacked:true,max:100,ticks:{callback:v=>v+'%'}},y:{stacked:true,ticks:{font:{size:11,family:'Inter'}}}}}});
  }
}

function rVal(){
  const el=document.getElementById('Tval');
  const ci=D.categorias.valores;
  const vs=filt(D.valores_sebastianos);
  const vals=[...new Set(vs.map(r=>r.Valor_Sebastiano))].filter(v=>v!=='Ninguno');

  let h='<div class="sd"><h3>'+ci.titulo+'</h3><p>'+ci.descripcion+'</p></div>';
  h+='<div class="cc" id="ccval"><div class="ch"><span class="ct">Valores Sebastianos identificados en el proyecto</span>';
  h+='<button class="dl" onclick="dlPng(\'ccval\',\'valores\')">⤓ PNG</button></div><canvas id="chval" height="400"></canvas></div>';

  // Conditioning indicator: IMP_04
  h+='<div class="cc" id="cc04"><div class="ch"><span class="ct">Indicador relacionado: Fortalecer los valores sebastianos en mi persona (T2B por año)</span>';
  h+='<button class="dl" onclick="dlPng(\'cc04\',\'imp04_evol\')">⤓ PNG</button></div>';
  h+='<p style="font-size:12px;color:#64748b;padding:0 0 12px 0">Este indicador condiciona la sección de Valores Sebastianos: solo respondieron la pregunta de valores los estudiantes que calificaron positivamente este aspecto.</p>';
  h+='<canvas id="ch04" height="220"></canvas></div>';
  el.innerHTML=h;

  // Valores chart
  dc('chval');
  const sorted=vals.map(v=>({v,p:aggVS(vs,v).pct*100})).sort((a,b)=>b.p-a.p);
  charts.chval=new Chart(document.getElementById('chval'),{type:'bar',data:{labels:sorted.map(s=>s.v),datasets:[{data:sorted.map(s=>s.p),backgroundColor:CL.t2b,borderRadius:6,barThickness:24}]},options:{indexAxis:'y',responsive:true,plugins:{legend:{display:false},datalabels:{color:'#fff',font:{weight:'bold',size:12},anchor:'center',align:'center',formatter:v=>v.toFixed(1).replace('.',',')+' %'},tooltip:{callbacks:{label:i=>i.raw.toFixed(1).replace('.',',')+' %'}}},scales:{x:{max:100,ticks:{callback:v=>v+'%'}},y:{ticks:{font:{size:11,family:'Inter'}}}}}});

  // IMP_04 evolution chart
  dc('ch04');
  const yrs=[2021,2022,2023,2024,2025];
  const imp04=yrs.map(y=>{const r=D.likert.filter(x=>x['Año']===y&&x.Pregunta==='Fortalecer valores sebastianos');let n=0,t=0;r.forEach(x=>{n+=x.N_Respuestas;t+=x.Frec_T2B;});return n?t/n*100:0;});
  charts.ch04=new Chart(document.getElementById('ch04'),{type:'bar',data:{labels:yrs,datasets:[{label:'T2B (%)',data:imp04,backgroundColor:yrs.map(y=>YEAR_COLORS[y]||CL.t2b),borderRadius:8,barThickness:44}]},options:{responsive:true,plugins:{legend:{display:false},datalabels:{color:'#fff',font:{weight:'bold',size:14},formatter:v=>v.toFixed(1).replace('.',',')+' %'}},scales:{y:{min:0,max:100,ticks:{callback:v=>v+'%'}}}}});
}

function rEvo(){
  const el=document.getElementById('Tevo');
  const yrs=[2021,2022,2023,2024,2025];
  const ss=gS(),cs=gC();
  const ff=r=>(ss.length===0||ss.includes(r.SEDE))&&(cs.length===0||cs.includes(r.CARRERA));

  let h='<div class="sd"><h3>Evolución</h3><p>Tendencia de los principales indicadores a lo largo de los 5 años de aplicación de la encuesta de estudiantes. Cada gráfico muestra la evolución de un grupo de preguntas vinculadas a la percepción formativa, habilidades y satisfacción de los estudiantes participantes en Proyectos Colaborativos de Vinculación con el Medio.</p></div>';

  // N students
  h+='<div class="cc" id="ccen"><div class="ch"><span class="ct">Estudiantes encuestados por año</span><button class="dl" onclick="dlPng(\'ccen\',\'evol_n\')">⤓ PNG</button></div>';
  h+='<p style="font-size:12px;color:#64748b;padding:0 0 8px 0">Total de estudiantes que respondieron la encuesta en cada período</p>';
  h+='<canvas id="chen" height="200"></canvas></div>';

  // Main indicators
  h+='<div class="cc" id="ccem"><div class="ch"><span class="ct">Evolución de indicadores principales</span><button class="dl" onclick="dlPng(\'ccem\',\'evol_main\')">⤓ PNG</button></div>';
  h+='<p style="font-size:12px;color:#64748b;padding:0 0 8px 0">Indicadores: Significancia en formación (T2B), Expectativas cumplidas (T2B), Recomendaría a compañeros (% Sí)</p>';
  h+='<canvas id="chem" height="280"></canvas></div>';

  // Top 4 IMP
  h+='<div class="cc" id="ccei"><div class="ch"><span class="ct">Top 4 Aspectos Formativos (T2B)</span><button class="dl" onclick="dlPng(\'ccei\',\'evol_imp\')">⤓ PNG</button></div>';
  h+='<p style="font-size:12px;color:#64748b;padding:0 0 8px 0">Pregunta: "Evalúa el grado de importancia que tuvo participar en el Proyecto Colaborativo para el logro de los siguientes aspectos" (T2B: Importante + Muy importante)</p>';
  h+='<canvas id="chei" height="280"></canvas></div>';

  // Top 4 HAB
  h+='<div class="cc" id="cceh"><div class="ch"><span class="ct">Top 4 Habilidades (T2B)</span><button class="dl" onclick="dlPng(\'cceh\',\'evol_hab\')">⤓ PNG</button></div>';
  h+='<p style="font-size:12px;color:#64748b;padding:0 0 8px 0">Pregunta: "En base a tu experiencia en el Proyecto Colaborativo, evalúa el grado de fortalecimiento de las siguientes habilidades" (T2B: Fortalecida + Muy fortalecida)</p>';
  h+='<canvas id="cheh" height="280"></canvas></div>';
  el.innerHTML=h;

  // N students chart
  dc('chen');
  const firstP=[...new Set(D.likert.map(r=>r.Pregunta))][0];
  const nY=yrs.map(y=>{let n=0;D.likert.filter(r=>r['Año']===y&&r.Pregunta===firstP&&ff(r)).forEach(r=>n+=r.N_Respuestas);return n;});
  charts.chen=new Chart(document.getElementById('chen'),{type:'bar',data:{labels:yrs,datasets:[{data:nY,backgroundColor:yrs.map(y=>YEAR_COLORS[y]),borderRadius:8,barThickness:44}]},options:{responsive:true,plugins:{legend:{display:false},datalabels:{color:'#333',font:{weight:'bold',size:14},anchor:'end',align:'end',formatter:v=>v.toLocaleString('es-CL')}},scales:{y:{beginAtZero:true}}}});

  // Main indicators
  dc('chem');
  const mSets=[
    {l:'Recomendación (% Sí)',fn:y=>{let n=0,s=0;D.dicotomicas.filter(r=>r['Año']===y&&r.Pregunta==='Recomendaría a compañeros'&&ff(r)).forEach(r=>{n+=r.N_Respuestas;s+=r.Frec_Si;});return n?s/n*100:0;}},
    {l:'Significancia (T2B)',fn:y=>{let n=0,t=0;D.likert.filter(r=>r['Año']===y&&r.Pregunta==='Significancia en Formación'&&ff(r)).forEach(r=>{n+=r.N_Respuestas;t+=r.Frec_T2B;});return n?t/n*100:0;}},
    {l:'Expectativas (T2B)',fn:y=>{let n=0,t=0;D.likert.filter(r=>r['Año']===y&&r.Pregunta==='Cumplimiento de Expectativas'&&ff(r)).forEach(r=>{n+=r.N_Respuestas;t+=r.Frec_T2B;});return n?t/n*100:0;}}
  ];
  charts.chem=new Chart(document.getElementById('chem'),{type:'line',data:{labels:yrs,datasets:mSets.map((s,i)=>({label:s.l,data:yrs.map(y=>s.fn(y)),borderColor:CL.ln[i],backgroundColor:CL.ln[i]+'20',tension:.3,pointRadius:5,pointBackgroundColor:CL.ln[i]}))},options:{responsive:true,plugins:{legend:{position:'bottom',labels:{font:{size:11,family:'Inter'}}},datalabels:{display:false}},scales:{y:{min:50,max:100,ticks:{callback:v=>v+'%'}}}}});

  // Top 4 IMP
  dc('chei');
  const impP=[...new Set(D.likert.filter(r=>r.Categoria==='Importancia Aspectos Formativos').map(r=>r.Pregunta))];
  const impRank=impP.map(p=>{const r=D.likert.filter(x=>x.Pregunta===p&&ff(x));let n=0,t=0;r.forEach(x=>{n+=x.N_Respuestas;t+=x.Frec_T2B;});return{p,v:n?t/n:0};}).sort((a,b)=>b.v-a.v).slice(0,4);
  charts.chei=new Chart(document.getElementById('chei'),{type:'line',data:{labels:yrs,datasets:impRank.map((item,i)=>({label:item.p,data:yrs.map(y=>{let n=0,t=0;D.likert.filter(r=>r['Año']===y&&r.Pregunta===item.p&&ff(r)).forEach(r=>{n+=r.N_Respuestas;t+=r.Frec_T2B;});return n?t/n*100:null;}),borderColor:CL.ln[i],tension:.3,pointRadius:4,pointBackgroundColor:CL.ln[i],spanGaps:true}))},options:{responsive:true,plugins:{legend:{position:'bottom',labels:{font:{size:10,family:'Inter'}}},datalabels:{display:false}},scales:{y:{min:50,max:100,ticks:{callback:v=>v+'%'}}}}});

  // Top 4 HAB
  dc('cheh');
  const habP=[...new Set(D.likert.filter(r=>r.Categoria==='Desarrollo de Habilidades').map(r=>r.Pregunta))];
  const habRank=habP.map(p=>{const r=D.likert.filter(x=>x.Pregunta===p&&ff(x));let n=0,t=0;r.forEach(x=>{n+=x.N_Respuestas;t+=x.Frec_T2B;});return{p,v:n?t/n:0};}).sort((a,b)=>b.v-a.v).slice(0,4);
  charts.cheh=new Chart(document.getElementById('cheh'),{type:'line',data:{labels:yrs,datasets:habRank.map((item,i)=>({label:item.p,data:yrs.map(y=>{let n=0,t=0;D.likert.filter(r=>r['Año']===y&&r.Pregunta===item.p&&ff(r)).forEach(r=>{n+=r.N_Respuestas;t+=r.Frec_T2B;});return n?t/n*100:null;}),borderColor:CL.ln[i],tension:.3,pointRadius:4,pointBackgroundColor:CL.ln[i],spanGaps:true}))},options:{responsive:true,plugins:{legend:{position:'bottom',labels:{font:{size:10,family:'Inter'}}},datalabels:{display:false}},scales:{y:{min:50,max:100,ticks:{callback:v=>v+'%'}}}}});
}

function rDim(){
  const el=document.getElementById('Tdim');
  const dims=D.dimensiones;
  let h='<div class="sd"><h3>Modelo de Evaluación VcM</h3><p>Dimensiones del Modelo de Evaluación de Vinculación con el Medio de la Universidad San Sebastián.</p></div>';
  Object.keys(dims).forEach(dk=>{
    const d=dims[dk];
    h+='<div class="dc"><div class="dh" onclick="this.nextElementSibling.classList.toggle(\'op\');this.querySelector(\'.ar\').classList.toggle(\'op\')"><h4>Dimensión '+dk.replace('Dim_','')+': '+d.titulo+'</h4><span class="ar">▼</span></div>';
    h+='<div class="db"><p>'+d.descripcion+'</p><table class="dt"><thead><tr><th>Indicador</th>';
    d.anios.forEach(a=>{h+='<th>'+a+'</th>';});
    h+='</tr></thead><tbody>';
    d.indicadores.forEach(ind=>{
      h+='<tr><td>'+ind.nombre+'</td>';
      d.anios.forEach(a=>{
        let v=ind[a];
        if(v==='Sin información')h+='<td style="color:#94a3b8;font-style:italic">Sin información</td>';
        else if(typeof v==='number'&&v>0&&v<1)h+='<td>'+(v*100).toFixed(1).replace('.',',')+' %</td>';
        else h+='<td>'+(v!=null?v.toLocaleString('es-CL'):'-')+'</td>';
      });
      h+='</tr>';
    });
    h+='</tbody></table></div></div>';
  });
  el.innerHTML=h;
}

document.addEventListener('DOMContentLoaded',()=>{initF();updAll();});
