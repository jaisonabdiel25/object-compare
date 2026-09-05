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
            # ordenar_json ya devuelve cada item con las claves ordenadas, asi
            # que sort_keys volveria a ordenarlas: se omite por velocidad.
            return sorted(
                (ordenar_json(item) for item in obj),
                key=json.dumps
            )
        else:
            return obj  # listas simples se respetan

    else:
        return obj
