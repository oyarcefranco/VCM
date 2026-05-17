import re

files = [
    r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_vcm.html',
    r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_vcm_detalle.html'
]

for filename in files:
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()
    
    if 'DOMContentLoaded' not in html:
        html = re.sub(r'</body>', '<script>\ndocument.addEventListener("DOMContentLoaded", init);\n</script>\n</body>', html, flags=re.IGNORECASE)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

print("Done")
