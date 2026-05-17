"""Inyecta JS en el HTML del dashboard."""
import os
B=r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"
H=os.path.join(B,"dashboard_vcm_final.html")
with open(os.path.join(B,"dashboard_part1.js"),'r',encoding='utf-8') as f: j1=f.read()
with open(os.path.join(B,"dashboard_part2.js"),'r',encoding='utf-8') as f: j2=f.read()
with open(H,'r',encoding='utf-8') as f: html=f.read()
html=html.replace("</script></body>","\n"+j1+"\n"+j2+"\n</script></body>")
with open(H,'w',encoding='utf-8') as f: f.write(html)
print(f"OK: {os.path.getsize(H)/(1024*1024):.2f} MB")
