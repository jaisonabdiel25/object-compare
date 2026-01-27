import json

def ordenar_json(obj):
    if isinstance(obj, dict):
        return {
            k: ordenar_json(v)
            for k, v in sorted(obj.items())
        }
    elif isinstance(obj, list):
        return [ordenar_json(item) for item in obj]
    else:
        return obj

# Leer archivos de entrada
with open("original/input_original.json", "r", encoding="utf-8") as f:
    obj1 = json.load(f)

with open("original/input_new.json", "r", encoding="utf-8") as f:
    obj12 = json.load(f)

# Ordenar JSON
resultado1 = ordenar_json(obj1)
resultado2 = ordenar_json(obj12)

# Escribir archivo de salida
with open("new/output_original.json", "w", encoding="utf-8") as f:
    json.dump(resultado1, f, indent=4, ensure_ascii=False)

with open("new/output_new.json", "w", encoding="utf-8") as f:
    json.dump(resultado2, f, indent=4, ensure_ascii=False)

print("✅ Archivos ordenados creados: output_original.json  output_new.json")
