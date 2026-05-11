import json

with open(r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_data.json','r',encoding='utf-8') as f:
    data = json.load(f)
json_str = json.dumps(data, ensure_ascii=False, default=str)

with open(r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_vcm.html','r',encoding='utf-8') as f:
    html = f.read()

old = "fetch('dashboard_data.json').then(r=>r.json()).then(d=>{DATA=d;init()});"
new = 'DATA=' + json_str + ';init();'
html = html.replace(old, new)

with open(r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_vcm.html','w',encoding='utf-8') as f:
    f.write(html)
print('OK - datos incrustados en HTML')
