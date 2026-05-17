// Part 1: Core utilities, filters, KPIs, FULL_NAMES, dynamic titles, interpretation
Chart.register(ChartDataLabels);
let cur='imp',charts={},selInd={imp:null,hab:null},vm={imp:'t2b',hab:'t2b',ind:'t2b'};
const CL={t2b:'#003366',bar:['#dc2626','#f97316','#eab308','#22c55e','#0077cc'],ln:['#003366','#0077cc','#00a6fb','#22c55e','#f59e0b','#ef4444']};
const YEAR_COLORS={2021:'#8e44ad',2022:'#f39c12',2023:'#e84393',2024:'#2980b9',2025:'#16a085'};

// Nombres completos de cada indicador/pregunta
const FULL_NAMES={
  'Aplicar lo aprendido en clases':'Aplicar los contenidos de una asignatura de mi carrera',
  'Conocer la realidad (problemas/desafíos)':'Conocer la realidad, conectando con problemáticas de personas, instituciones o comunidades',
  'Fortalecer vocación profesional':'Fortalecer mi vocación profesional',
  'Fortalecer valores sebastianos':'Fortalecer los valores sebastianos en mi persona',
  'Potenciar desempeño futuro':'Potenciar y fortalecer mi desempeño para mi futuro como profesional',
  'Desarrollar habilidades transversales':'Desarrollar habilidades transversales (Ejemplo: trabajo en equipo, comunicación, liderazgo, etc.)',
  'Enfrentar desafíos con seguridad':'Enfrentar con mayor seguridad o confianza los desafíos profesionales',
  'Compromiso con la sociedad':'Compromiso con la sociedad',
  'Ser ciudadano responsable':'Ser ciudadano responsable',
  'Incrementar redes de contactos':'Incrementar mis redes de contactos profesionales',
  'Trabajar con otras carreras':'Trabajar en conjunto con estudiantes de otras carreras',
  'Conocer campo laboral':'Conocer más de mi campo laboral',
  'Interactuar en contexto real':'Interactuar con las personas en un contexto real desde un rol profesional',
  'Aportar desde el rol profesional':'Entender cómo aportar desde un rol profesional al abordaje de los desafíos o problemas del entorno',
  'Empatía':'Empatía',
  'Comunicación efectiva':'Comunicación efectiva',
  'Trabajo en equipo / Colaboración':'Trabajo en equipo / Colaboración',
  'Resolución de problemas':'Resolución de problemas',
  'Adaptación y flexibilidad':'Adaptación y flexibilidad',
  'Competencia disciplinar':'Competencia disciplinar',
  'Manejo de información (toma de decisiones)':'Manejo de información y toma de decisiones',
  'Prolijidad / Atención al detalle':'Prolijidad / Atención al detalle',
  'Pensamiento crítico y reflexivo':'Pensamiento crítico y reflexivo',
  'Ciudadanía responsable':'Ciudadanía responsable',
  'Creatividad / Pensamiento innovador':'Creatividad / Pensamiento innovador',
  'Autoconsciencia':'Autoconsciencia',
  'Significancia en Formación':'% de estudiantes que declaran que la participación en iniciativas VcM fue significativa o muy significativa para su formación profesional',
  'Cumplimiento de Expectativas':'% de estudiantes cuyas expectativas fueron cumplidas en alto grado',
  'Importancia para Comunidades Beneficiadas':'% de estudiantes que consideran importante o muy importante el impacto para los beneficiados',
  'Recomendaría a compañeros':'% de estudiantes que recomendarían a sus compañeros participar en un Proyecto Colaborativo VcM',
  'Permitió conocer campo laboral':'% de estudiantes que consideran que el proyecto les permitió conocer su campo laboral',
  'Sabía que era iniciativa VcM':'% de estudiantes que sabían que su proyecto era de Vinculación con el Medio'
};

// Prefijos y sufijos para títulos dinámicos
const TITLE_PREFIX={
  'imp':'Porcentaje de estudiantes que evalúa como importante su participación en el proyecto para: ',
  'hab':'Porcentaje de estudiantes que declaran que se fortaleció: ',
  'ind':'','val':'Porcentaje de estudiantes que identifican el valor: '
};
const TITLE_SUFFIX={
  'imp':' (Top-2-Box: Importante + Muy importante)',
  'hab':' (Top-2-Box: Fortalecida + Muy fortalecida)',
  'ind':'','val':''
};

function gY(){return[...document.getElementById('fY').selectedOptions].map(o=>o.value);}
function gS(){return[...document.getElementById('fS').selectedOptions].map(o=>o.value);}
function gC(){return[...document.getElementById('fC').selectedOptions].map(o=>o.value);}
function filt(rows){const y=gY(),s=gS(),c=gC();return rows.filter(r=>(y.length===0||y.includes(String(r['Año'])))&&(s.length===0||s.includes(r.SEDE))&&(c.length===0||c.includes(r.CARRERA)));}
function pct(v){return(v*100).toFixed(1).replace('.',',')+'%';}
function pctDot(v){return(v*100).toFixed(1)+'%';}
function dc(id){if(charts[id]){charts[id].destroy();delete charts[id];}}
function dlPng(id,nm){html2canvas(document.getElementById(id),{backgroundColor:'#fff',scale:2}).then(c=>{const a=document.createElement('a');a.download=nm+'.png';a.href=c.toDataURL();a.click();});}

// Aggregation functions
function aggLik(rows,pregunta){
  const f=rows.filter(r=>r.Pregunta===pregunta);
  let n=0,f1=0,f2=0,f3=0,f4=0,f5=0,ft=0;
  f.forEach(r=>{n+=r.N_Respuestas;f1+=r.Frec_1;f2+=r.Frec_2;f3+=r.Frec_3;f4+=r.Frec_4;f5+=r.Frec_5;ft+=r.Frec_T2B;});
  return{n,f1,f2,f3,f4,f5,ft,t2b:n?ft/n:0,dist:n?[f1/n,f2/n,f3/n,f4/n,f5/n]:[0,0,0,0,0]};
}
function aggDic(rows,pregunta){
  const f=rows.filter(r=>r.Pregunta===pregunta);
  let n=0,si=0,no=0;
  f.forEach(r=>{n+=r.N_Respuestas;si+=r.Frec_Si;no+=r.Frec_No;});
  return{n,si,no,pct:n?si/n:0};
}
function aggVS(rows,valor){
  const f=rows.filter(r=>r.Valor_Sebastiano===valor);
  let n=0,m=0;
  f.forEach(r=>{n+=r.N_Respuestas;m+=r.Menciones;});
  return{n,m,pct:n?m/n:0};
}

// Dynamic title generator
function getDynTitle(sec,items,mode){
  if(items.length===1){
    const name=items[0];
    const fullName=FULL_NAMES[name]||name;
    const prefix=TITLE_PREFIX[sec]||'';
    const suffix=mode==='likert'?' — Distribución Likert':(TITLE_SUFFIX[sec]||' — Top-2-Box');
    const text=prefix+fullName+suffix;
    // Wrap long titles
    if(text.length>80){
      const words=text.split(' ');const lines=[];let cur='';
      words.forEach(w=>{if((cur+' '+w).trim().length>80&&cur){lines.push(cur.trim());cur=w;}else{cur=cur?cur+' '+w:w;}});
      if(cur)lines.push(cur.trim());
      return lines;
    }
    return text;
  }
  const names={'imp':'Importancia Aspectos Formativos','hab':'Desarrollo de Habilidades','ind':'Indicadores Clave','val':'Valores Sebastianos'};
  return(names[sec]||'Resultados')+' — '+(mode==='likert'?'Distribución Likert':'Top-2-Box');
}

// Interpretation text generator
function getInterp(sec,items,lik,dic,selY){
  if(items.length!==1)return '<strong>Nota:</strong> Seleccione un solo indicador para ver la interpretación descriptiva detallada y el número de respuestas validadas.';
  const name=items[0];
  const fullName=FULL_NAMES[name]||name;
  const a=aggLik(lik,name);
  const sY=selY.length===1?selY[0]:null;
  if(sY){
    // Single year
    const yLik=lik.filter(r=>String(r['Año'])===sY);
    const ya=aggLik(yLik,name);
    const val=pct(ya.t2b);
    const nText=ya.n.toLocaleString('es-CL');
    // Historical avg
    const allYears=[...new Set(lik.map(r=>r['Año']))];
    let sum=0,cnt=0;
    allYears.forEach(y=>{const aa=aggLik(lik.filter(r=>r['Año']===y),name);if(aa.n>0){sum+=aa.t2b;cnt++;}});
    const avg=cnt?pct(sum/cnt):'N/D';
    return '<strong>Interpretación:</strong> En <strong>'+sY+'</strong>, el <strong>'+val+'</strong> de los estudiantes reporta un resultado positivo en "'+fullName+'". El promedio histórico es de <strong>'+avg+'</strong>. <em>(n = '+nText+' respuestas)</em>';
  }else{
    // All years - trend
    const allYears=[...new Set(lik.map(r=>r['Año']))].sort();
    const vals=allYears.map(y=>{const aa=aggLik(lik.filter(r=>r['Año']===y),name);return{y,t2b:aa.t2b,n:aa.n};}).filter(x=>x.n>0);
    if(vals.length<2)return '';
    const first=vals[0].t2b*100,last=vals[vals.length-1].t2b*100;
    const trend=last>first+2?'creciente':(last<first-2?'decreciente':'estable');
    return '<strong>Interpretación:</strong> El indicador "'+fullName+'" muestra una tendencia <strong>'+trend+'</strong> entre '+vals[0].y+' y '+vals[vals.length-1].y+', pasando de <strong>'+first.toFixed(1).replace('.',',')+' %</strong> a <strong>'+last.toFixed(1).replace('.',',')+' %</strong>.';
  }
}

// Filters initialization
function initF(){
  const lik=D.likert;
  const ys=[...new Set(lik.map(r=>r['Año']))].sort();
  const ss=[...new Set(lik.map(r=>r.SEDE))].sort();
  const fY=document.getElementById('fY'),fS=document.getElementById('fS');
  ys.forEach(y=>{const o=document.createElement('option');o.value=y;o.text=y;fY.add(o);});
  ss.forEach(s=>{const o=document.createElement('option');o.value=s;o.text=s;fS.add(o);});
  updC();
  fY.onchange=fS.onchange=()=>{updC();updAll();};
  document.getElementById('fC').onchange=()=>updAll();
}
function updC(){
  const ss=gS(),lik=D.likert;
  let r=lik;if(ss.length)r=r.filter(x=>ss.includes(x.SEDE));
  const cs=[...new Set(r.map(x=>x.CARRERA))].sort();
  const fC=document.getElementById('fC');fC.innerHTML='';
  cs.forEach(c=>{const o=document.createElement('option');o.value=c;o.text=c;fC.add(o);});
}
function resetF(){['fY','fS','fC'].forEach(id=>{[...document.getElementById(id).options].forEach(o=>o.selected=false);});updC();updAll();}

function updKPI(){
  const lik=filt(D.likert),dic=filt(D.dicotomicas);
  const pregs=[...new Set(lik.map(r=>r.Pregunta))];
  const first=pregs[0]||'';
  const nRows=lik.filter(r=>r.Pregunta===first);
  let nTotal=0;nRows.forEach(r=>nTotal+=r.N_Respuestas);
  document.getElementById('kN').textContent=nTotal.toLocaleString('es-CL');
  const rec=aggDic(dic,'Recomendaría a compañeros');
  document.getElementById('kR').textContent=pct(rec.pct);
  const sig=aggLik(lik,'Significancia en Formación');
  document.getElementById('kS').textContent=pct(sig.t2b);
  const exp=aggLik(lik,'Cumplimiento de Expectativas');
  document.getElementById('kE').textContent=pct(exp.t2b);
}

function go(tab){
  cur=tab;
  const tabs=['imp','hab','ind','val','evo','dim'];
  document.querySelectorAll('.tb').forEach((b,i)=>b.classList.toggle('on',tabs[i]===tab));
  document.querySelectorAll('.tc').forEach(t=>t.classList.remove('on'));
  document.getElementById('T'+tab).classList.add('on');
  render(tab);
}
function updAll(){updKPI();render(cur);}
