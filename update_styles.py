import re
import glob

# The new style block
NEW_STYLE = """    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box
    }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    body {
      font-family: 'Inter', sans-serif;
      background: #F8FAFC;
      color: #334155;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
    }

    .header-top {
      background: #FFFFFF;
      border-bottom: 1px solid #E2E8F0;
      padding: 16px 48px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    .header-top h1 {
      font-size: 20px;
      font-weight: 700;
      color: #0F172A;
      letter-spacing: -0.02em;
    }

    .header-top .logo {
      font-weight: 600;
      color: #1b365d;
      background: #f1f5f9;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 14px;
    }

    .header-nav {
      background: linear-gradient(90deg, #1b365d 0%, #2a528a 100%);
      color: #fff;
      padding: 12px 48px;
      font-size: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
    }

    .header-nav .subtitle {
      font-weight: 500;
      opacity: 0.9;
      letter-spacing: 0.01em;
    }

    .container {
      max-width: 1360px;
      margin: 0 auto;
      padding: 40px 24px;
    }

    .kpi-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 24px;
      margin-bottom: 40px;
    }

    .kpi-card {
      border-radius: 16px;
      padding: 32px 24px;
      text-align: center;
      color: #F8FAFC;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      position: relative;
      overflow: hidden;
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      border: 1px solid #334155;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .kpi-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
    }

    .kpi-card::after {
      content: '';
      position: absolute;
      top: 0;
      right: 0;
      width: 150px;
      height: 150px;
      background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 70%);
      border-radius: 50%;
      transform: translate(30%, -30%);
    }

    .kpi-card .value {
      font-size: 42px;
      font-weight: 800;
      margin-bottom: 12px;
      line-height: 1;
      letter-spacing: -0.02em;
    }

    .kpi-card .label {
      font-size: 14px;
      font-weight: 500;
      line-height: 1.4;
      color: #94A3B8;
      letter-spacing: 0.01em;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
    }

    .info-icon {
      width: 16px;
      height: 16px;
      color: #64748B;
      display: inline-block;
      vertical-align: middle;
      cursor: help;
      transition: color 0.2s;
    }
    .info-icon:hover { color: #CBD5E1; }

    .section {
      background: #FFFFFF;
      border-radius: 16px;
      padding: 32px;
      margin-bottom: 32px;
      border: 1px solid #E2E8F0;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
    }

    .section-title {
      font-size: 22px;
      font-weight: 700;
      margin-bottom: 8px;
      color: #0F172A;
      letter-spacing: -0.01em;
    }

    .section-sub {
      font-size: 14px;
      color: #64748B;
      margin-bottom: 24px;
      line-height: 1.5;
    }

    .year-filter {
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }

    .year-btn {
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid #E2E8F0;
      background: #FFFFFF;
      color: #475569;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      transition: all .2s ease;
    }

    .year-btn.active {
      background: #1b365d;
      color: #fff;
      border-color: #1b365d;
      box-shadow: 0 1px 2px rgba(27, 54, 93, 0.2);
    }

    .year-btn:hover:not(.active) {
      background: #F1F5F9;
      border-color: #CBD5E1;
    }

    .chart-wrap {
      position: relative;
      width: 100%;
      max-width: 100%;
      margin: 0 auto 15px auto;
      overflow: visible;
    }

    .avail-note {
      font-size: 13px;
      color: #475569;
      margin-top: 8px;
      padding: 12px 16px;
      background: #F8FAFC;
      border-left: 3px solid #1b365d;
      border-radius: 0 8px 8px 0;
      display: inline-block;
    }

    .nav {
      display: flex;
      gap: 4px;
      margin-bottom: 32px;
      flex-wrap: wrap;
      background: #F1F5F9;
      padding: 6px;
      border-radius: 12px;
      width: fit-content;
    }

    .nav-btn {
      padding: 10px 20px;
      border-radius: 8px;
      border: none;
      background: transparent;
      color: #64748B;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      transition: all .2s ease;
    }

    .nav-btn.active {
      background: #FFFFFF;
      color: #0F172A;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .nav-btn:hover:not(.active) {
      color: #334155;
      background: rgba(255,255,255,0.5);
    }

    .hidden {
      display: none !important;
    }

    .trend-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 32px;
    }

    @media(max-width:900px) {
      .trend-grid { grid-template-columns: 1fr; }
      .header-top { flex-direction: column; gap: 16px; text-align: center; }
      .nav { width: 100%; justify-content: center; }
    }

    .item-controls {
      display: flex;
      gap: 8px;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }

    .item-controls button {
      padding: 6px 14px;
      border-radius: 6px;
      border: 1px solid #E2E8F0;
      background: #FFFFFF;
      color: #475569;
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
      transition: all .15s ease;
    }

    .item-controls button:hover {
      background: #F1F5F9;
      border-color: #CBD5E1;
      color: #0F172A;
    }

    .item-controls .sort-btn.active {
      background: #1b365d;
      color: #fff;
      border-color: #1b365d;
    }

    .item-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 24px;
      max-height: 140px;
      overflow-y: auto;
      padding: 4px 0;
    }

    .item-chip {
      padding: 6px 14px;
      border-radius: 9999px;
      border: 1px solid #CBD5E1;
      background: #FFFFFF;
      color: #334155;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
      transition: all .15s ease;
      user-select: none;
      white-space: nowrap;
      box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }

    .item-chip.off {
      background: #F8FAFC;
      color: #94A3B8;
      border-color: #E2E8F0;
      border-style: dashed;
      box-shadow: none;
    }

    .item-chip:hover:not(.off) {
      background: #F1F5F9;
      border-color: #94A3B8;
    }
    
    .item-chip.off:hover {
      background: #F1F5F9;
    }

    .item-count {
      font-size: 13px;
      color: #64748B;
      font-weight: 500;
      margin-left: 8px;
    }

    .download-btn {
      position: absolute;
      top: 12px;
      right: 12px;
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      color: #475569;
      cursor: pointer;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
      z-index: 10;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .download-btn:hover {
      background: #F8FAFC;
      color: #0F172A;
      border-color: #CBD5E1;
    }
    .download-btn svg {
      width: 14px;
      height: 14px;
    }"""

svg_icon = """<svg class="info-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>"""

files = glob.glob('*_alt.html')

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace style block
    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    if style_match:
        content = content.replace(style_match.group(1), f"\n{NEW_STYLE}\n")
    
    # Replace emojis with SVGs
    content = content.replace('ℹ️', svg_icon)
    
    # Add SVG arrow to download button
    dl_svg = """<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>"""
    content = content.replace("btn.innerHTML = '⬇ PNG';", f"btn.innerHTML = '{dl_svg} PNG';")
    
    # Fix top links styles (if any)
    content = content.replace('box-shadow: 0 2px 4px rgba(0,0,0,0.1);', 'box-shadow: 0 1px 2px rgba(0,0,0,0.05); transition: all 0.2s;')
    content = content.replace('text-decoration: none;', 'text-decoration: none; border: 1px solid transparent;')

    # Fix generic Chart.js font config globally if possible
    content = content.replace("Chart.register(ChartDataLabels);", "Chart.register(ChartDataLabels); Chart.defaults.font.family = \\\"'Inter', sans-serif\\\"; Chart.defaults.color = '#475569';")

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Updated 3 alternative files.")
