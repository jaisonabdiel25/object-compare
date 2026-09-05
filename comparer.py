LIMITE_POR_DEFECTO = 1000


def _ruta_clave(ruta, clave):
    return f"{ruta}.{clave}"


def _ruta_indice(ruta, indice):
    return f"{ruta}[{indice}]"


def _recorrer(original, nuevo, ruta, diferencias, limite):
    """Acumula diferencias en `diferencias`. Devuelve True si se llenó el cupo."""
    if len(diferencias) >= limite:
        return True

    if type(original) is not type(nuevo):
        diferencias.append({
            "ruta": ruta,
            "tipo": "tipo_distinto",
            "detalle": f"{type(original).__name__} vs {type(nuevo).__name__}",
            "original": original,
            "nuevo": nuevo,
        })
        return len(diferencias) >= limite

    if isinstance(original, dict):
        for clave in original:
            if clave not in nuevo:
                diferencias.append({
                    "ruta": _ruta_clave(ruta, clave),
                    "tipo": "solo_en_original",
                    "original": original[clave],
                    "nuevo": None,
                })
                if len(diferencias) >= limite:
                    return True
            elif _recorrer(original[clave], nuevo[clave],
                           _ruta_clave(ruta, clave), diferencias, limite):
                return True

        for clave in nuevo:
            if clave not in original:
                diferencias.append({
                    "ruta": _ruta_clave(ruta, clave),
                    "tipo": "solo_en_nuevo",
                    "original": None,
                    "nuevo": nuevo[clave],
                })
                if len(diferencias) >= limite:
                    return True

        return False

    if isinstance(original, list):
        for i in range(min(len(original), len(nuevo))):
            if _recorrer(original[i], nuevo[i],
                         _ruta_indice(ruta, i), diferencias, limite):
                return True

        for i in range(len(nuevo), len(original)):
            diferencias.append({
                "ruta": _ruta_indice(ruta, i),
                "tipo": "solo_en_original",
                "original": original[i],
                "nuevo": None,
            })
            if len(diferencias) >= limite:
                return True

        for i in range(len(original), len(nuevo)):
            diferencias.append({
                "ruta": _ruta_indice(ruta, i),
                "tipo": "solo_en_nuevo",
                "original": None,
                "nuevo": nuevo[i],
            })
            if len(diferencias) >= limite:
                return True

        return False

    if original != nuevo:
        diferencias.append({
            "ruta": ruta,
            "tipo": "valor_distinto",
            "original": original,
            "nuevo": nuevo,
        })

    return len(diferencias) >= limite


def comparar_json(original, nuevo, limite=LIMITE_POR_DEFECTO):
    """Compara dos estructuras ya normalizadas.

    Devuelve (diferencias, truncado). `truncado` indica que se alcanzó
    `limite` y el recorrido se detuvo antes de terminar.
    """
    diferencias = []
    # Se recorre con un margen de uno para distinguir "terminó justo en el
    # límite" de "quedaban más diferencias por recorrer".
    _recorrer(original, nuevo, "$", diferencias, limite + 1)
    truncado = len(diferencias) > limite
    return diferencias[:limite], truncado
