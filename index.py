import json

from normalizer import ordenar_json

with open("original/input_original.json", "r", encoding="utf-8") as f:
    obj1 = json.load(f)

with open("original/input_new.json", "r", encoding="utf-8") as f:
    obj2 = json.load(f)

resultado1 = ordenar_json(obj1)
resultado2 = ordenar_json(obj2)

with open("new/output_original.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(resultado1, indent=4, ensure_ascii=False))

with open("new/output_new.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(resultado2, indent=4, ensure_ascii=False))

print("JSON normalizados para comparacion en VS Code")
