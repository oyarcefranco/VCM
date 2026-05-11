import re

with open(r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_vcm.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace predefined colors
content = content.replace(
    "const COLORS=['#3b82f6','#6366f1','#8b5cf6','#a855f7','#ec4899','#f43f5e','#f97316','#eab308','#22c55e','#14b8a6','#06b6d4','#0ea5e9','#64748b','#78716c'];",
    "const COLORS=['#1e4c9a','#7d4199','#009a74','#f37021','#f3a81a','#4c3c5c','#2a82c9','#e64d3d','#8c7a6b','#5c9d38'];"
)

content = content.replace(
    "const YEAR_COLORS={2021:'#3b82f6',2022:'#8b5cf6',2023:'#22c55e',2024:'#f97316',2025:'#ec4899'};",
    "const YEAR_COLORS={2021:'#1e4c9a',2022:'#7d4199',2023:'#009a74',2024:'#f37021',2025:'#f3a81a'};"
)

content = content.replace(
    "backgroundColor:values.map(v=>v>=90?'#22c55e':v>=80?'#3b82f6':v>=70?'#f97316':'#ef4444')",
    "backgroundColor:values.map(v=>v>=90?'#009a74':v>=80?'#1e4c9a':v>=70?'#f3a81a':'#e64d3d')"
)

# Dark mode to light mode colors in charts
content = content.replace("'#1e293b'", "'#eaeaea'")  # Grids
content = content.replace("'#94a3b8'", "'#666666'")  # Ticks / Subtitles
content = content.replace("'#e2e8f0'", "'#333333'")  # Main text / Titles
content = content.replace("'#334155'", "'#eaeaea'")  # Trend grids

with open(r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_vcm.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Colors updated!')
