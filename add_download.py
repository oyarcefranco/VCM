import os
import re

css_addition = """
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
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      z-index: 10;
      transition: all 0.2s;
    }
    .download-btn:hover {
      background: #f0f0f0;
      color: #1b365d;
      border-color: #1b365d;
    }
"""

js_addition_raw = """
  <script>
    // Función global para añadir botones de descarga PNG
    (function() {
      const initDownloadButtons = () => {
        document.querySelectorAll('.chart-wrap').forEach(wrap => {
          const canvas = wrap.querySelector('canvas');
          if (!canvas || wrap.querySelector('.download-btn')) return;
          
          const btn = document.createElement('button');
          btn.className = 'download-btn';
          btn.innerHTML = '⬇ PNG';
          btn.title = 'Descargar gráfico como PNG';
          btn.onclick = () => {
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
          };
          wrap.appendChild(btn);
        });
      };

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDownloadButtons);
      } else {
        initDownloadButtons();
      }
      
      // También intentar después de un pequeño retraso por si los gráficos se cargan dinámicamente
      setTimeout(initDownloadButtons, 1500);
    })();
  </script>
"""

files = ['dashboard_vcm.html', 'dashboard_vcm_detalle.html', 'make_dim5.py']

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove previous script block if exists
    content = re.sub(r'<script>\s*// Función global para añadir botones de descarga PNG.*?</script>', '', content, flags=re.DOTALL)
    # Also remove the one without script tags if it's still there
    content = content.replace("// Función global para añadir botones de descarga PNG", "")

    # Add CSS if not present
    if ".download-btn {" not in content:
        if "</style>" in content:
            content = content.replace("</style>", css_addition + "</style>")

    # Add JS
    js_to_add = js_addition_raw
    if file == 'make_dim5.py':
        js_to_add = js_to_add.replace("{", "{{").replace("}", "}}")

    if "</body>" in content:
        content = content.replace("</body>", js_to_add + "\n</body>")

    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Applied robust download button fix")
