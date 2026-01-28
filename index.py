import json

def ordenar_json(obj):
    if isinstance(obj, dict):
        return {
            k: ordenar_json(v)
            for k, v in sorted(obj.items())
        }

    elif isinstance(obj, list):
        # Ordenar listas de dicts de forma estable
        if all(isinstance(item, dict) for item in obj):
            return sorted(
                (ordenar_json(item) for item in obj),
                key=lambda x: json.dumps(x, sort_keys=True)
            )
        else:
            return obj  # listas simples se respetan

    else:
        return obj


with open("original/input_original.json", "r", encoding="utf-8") as f:
    obj1 = json.load(f)

with open("original/input_new.json", "r", encoding="utf-8") as f:
    obj2 = json.load(f)

resultado1 = ordenar_json(obj1)
resultado2 = ordenar_json(obj2)

with open("new/output_original.json", "w", encoding="utf-8") as f:
    json.dump(resultado1, f, indent=4, ensure_ascii=False)

with open("new/output_new.json", "w", encoding="utf-8") as f:
    json.dump(resultado2, f, indent=4, ensure_ascii=False)

print("✅ JSON normalizados para comparación en VS Code")
