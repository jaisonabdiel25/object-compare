import json

from flask import Flask, jsonify, request

from comparer import LIMITE_POR_DEFECTO, comparar_json
from normalizer import ordenar_json

MAX_BYTES = 50 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_BYTES
# Flask reordena las claves de la respuesta por su cuenta; se desactiva para
# devolver exactamente el orden que produce ordenar_json.
app.json.sort_keys = False
app.json.ensure_ascii = False


class EntradaInvalida(Exception):
    """Entrada mal formada o incompleta: se traduce a un 400."""


def _leer_archivo(nombre_campo):
    """Parsea un archivo subido en multipart/form-data."""
    archivo = request.files[nombre_campo]
    try:
        return json.load(archivo.stream)
    except json.JSONDecodeError as e:
        raise EntradaInvalida(
            f"El archivo '{nombre_campo}' no es JSON valido: {e}"
        ) from e


def _leer_body():
    """Parsea el body de la peticion como JSON."""
    try:
        datos = request.get_json(force=True)
    except Exception as e:
        raise EntradaInvalida(f"El body no es JSON valido: {e}") from e

    if datos is None:
        raise EntradaInvalida("El body no es JSON valido o esta vacio.")

    return datos


def _obtener_uno(campo_archivo):
    """Entrada de /normalizar: un archivo subido o el body completo."""
    if campo_archivo in request.files:
        return _leer_archivo(campo_archivo)

    if request.files:
        raise EntradaInvalida(
            f"Falta el archivo '{campo_archivo}' en el formulario."
        )

    return _leer_body()


def _obtener_dos(campo_a, campo_b):
    """Entrada de /comparar: dos archivos subidos o dos claves del body."""
    if request.files:
        faltantes = [c for c in (campo_a, campo_b) if c not in request.files]
        if faltantes:
            raise EntradaInvalida(
                "Faltan archivos en el formulario: " + ", ".join(faltantes)
            )
        return _leer_archivo(campo_a), _leer_archivo(campo_b)

    datos = _leer_body()
    if not isinstance(datos, dict):
        raise EntradaInvalida(
            f"El body debe ser un objeto con las claves '{campo_a}' y '{campo_b}'."
        )

    faltantes = [c for c in (campo_a, campo_b) if c not in datos]
    if faltantes:
        raise EntradaInvalida(
            "Faltan claves en el body: " + ", ".join(faltantes)
        )

    return datos[campo_a], datos[campo_b]


def _limite_solicitado():
    valor = request.args.get("limite")
    if valor is None:
        return LIMITE_POR_DEFECTO

    try:
        limite = int(valor)
    except ValueError:
        raise EntradaInvalida("El parametro 'limite' debe ser un entero.")

    if limite < 1:
        raise EntradaInvalida("El parametro 'limite' debe ser mayor que cero.")

    return limite


@app.get("/health")
def health():
    return jsonify({"estado": "ok"})


@app.post("/normalizar")
def normalizar():
    obj = _obtener_uno("archivo")
    return jsonify(ordenar_json(obj))


@app.post("/comparar")
def comparar():
    limite = _limite_solicitado()
    original, nuevo = _obtener_dos("original", "nuevo")

    diferencias, truncado = comparar_json(
        ordenar_json(original), ordenar_json(nuevo), limite
    )

    return jsonify({
        "iguales": not diferencias,
        "total_diferencias": len(diferencias),
        "truncado": truncado,
        "diferencias": diferencias,
    })


@app.errorhandler(EntradaInvalida)
def _entrada_invalida(e):
    return jsonify({"error": str(e)}), 400


@app.errorhandler(413)
def _demasiado_grande(e):
    limite_mb = MAX_BYTES // (1024 * 1024)
    return jsonify({
        "error": f"La peticion supera el limite de {limite_mb} MB."
    }), 413


@app.errorhandler(404)
def _no_encontrado(e):
    return jsonify({"error": "Ruta no encontrada."}), 404


@app.errorhandler(405)
def _metodo_no_permitido(e):
    return jsonify({"error": "Metodo no permitido para esta ruta."}), 405


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
