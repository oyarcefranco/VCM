with open('make_dim5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The JS addition starts with "// Función global"
parts = content.split("// Función global para añadir botones de descarga PNG")
if len(parts) == 2:
    js_part = parts[1]
    # Escape braces since it's inside an f-string
    js_part = js_part.replace("{", "{{").replace("}", "}}")
    content = parts[0] + "// Función global para añadir botones de descarga PNG" + js_part
    with open('make_dim5.py', 'w', encoding='utf-8') as f:
        f.write(content)
