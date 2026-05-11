"""
CORRECT approach for Chart.js dynamic heights:
- responsive:true + maintainAspectRatio:false
- Set the HEIGHT on the parent container (.chart-wrap) via CSS
- Chart.js will auto-fill that container
"""
filepath = r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_vcm.html'

with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Revert responsive:false back to responsive:true
html = html.replace('responsive:false,maintainAspectRatio:false,', 'responsive:true,maintainAspectRatio:false,')

# 2. Fix setChartHeight to ONLY set the parent container height (the correct approach)
old_helper = """
function setChartHeight(canvas, h){
  var w = canvas.parentElement.offsetWidth || 1200;
  canvas.parentElement.style.height = h + 'px';
  canvas.width = w;
  canvas.height = h;
  canvas.style.width = '100%';
  canvas.style.height = h + 'px';
}
"""

new_helper = """
function setChartHeight(canvas, h){
  canvas.parentElement.style.height = h + 'px';
}
"""
html = html.replace(old_helper, new_helper)

# 3. Remove the canvas max-height:none!important override, let CSS handle it
html = html.replace(
    'canvas{max-height:none!important;width:100%!important}',
    ''
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html)

print('Correct Chart.js height approach applied!')
