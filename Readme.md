# Object Compare (JSON Sorter + API)

Normaliza objetos JSON ordenando sus propiedades de forma **recursiva** y los
compara para decir **exactamente qué cambió**.

Resuelve un problema concreto: dos respuestas de servicio que deberían ser
equivalentes generan miles de diferencias falsas en un diff porque las claves y
los elementos de las listas vienen en distinto orden. Al normalizar ambos lados
primero, solo quedan las diferencias reales.

Se usa de dos formas:

- **API HTTP** (`app.py`) — le mandas dos JSON y responde si son iguales y en
  qué rutas difieren.
- **Script CLI** (`index.py`) — normaliza dos archivos fijos a disco para
  compararlos a mano en VS Code. Es el flujo original del proyecto.

---

## Requisitos

- Python **3.8 o superior**
- Git (opcional, para clonar el repo)

Verificar Python:

```bash
python --version
```

---

## Instalación

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1     # Windows PowerShell
# source .venv/bin/activate      # Linux / macOS
pip install -r requirements.txt
```

El script CLI no necesita dependencias; solo la API requiere Flask.

---

## API

Arrancar:

```bash
python app.py
```

Queda escuchando en `http://127.0.0.1:5000`.

Los dos endpoints principales aceptan la entrada de **dos maneras**: con el JSON
en el body (`Content-Type: application/json`) o subiendo archivos
(`multipart/form-data`).

### `GET /health`

```bash
curl http://127.0.0.1:5000/health
```

```json
{ "estado": "ok" }
```

### `POST /normalizar`

Devuelve el JSON con claves y listas ordenadas. Body o archivo en el campo
`archivo`.

```bash
curl -X POST http://127.0.0.1:5000/normalizar \
  -H "Content-Type: application/json" \
  -d '{"b":1,"a":{"z":1,"y":2}}'
```

```json
{ "a": { "y": 2, "z": 1 }, "b": 1 }
```

Con archivo:

```bash
curl -X POST http://127.0.0.1:5000/normalizar \
  -F "archivo=@original/input_original.json"
```

### `POST /comparar`

Normaliza ambos lados y devuelve las diferencias. Body con las claves `original`
y `nuevo`, o archivos en los campos del mismo nombre.

```bash
curl -X POST http://127.0.0.1:5000/comparar \
  -F "original=@original/input_original.json" \
  -F "nuevo=@original/input_new.json"
```

```json
{
  "iguales": false,
  "total_diferencias": 92,
  "truncado": false,
  "diferencias": [
    {
      "ruta": "$.data.data[1].sumInsuredCertificate",
      "tipo": "valor_distinto",
      "original": 76550.49,
      "nuevo": 76550.48999999999
    }
  ]
}
```

Con body JSON:

```bash
curl -X POST http://127.0.0.1:5000/comparar \
  -H "Content-Type: application/json" \
  -d '{"original":{"a":1},"nuevo":{"a":2}}'
```

**Tipos de diferencia:**

| `tipo` | Significado |
|---|---|
| `valor_distinto` | Misma ruta, valores escalares diferentes |
| `tipo_distinto` | Distinto tipo de dato (p. ej. `str` vs `int`); incluye `detalle` |
| `solo_en_original` | La clave o índice existe solo en el primero |
| `solo_en_nuevo` | La clave o índice existe solo en el segundo |

**Rutas:** la raíz es `$`, las claves van con punto y los índices entre
corchetes — `$.data.customerInfo[0].idNumber`.

**Parámetro `limite`:** tope de diferencias devueltas, por defecto `1000`. Si se
alcanza, el recorrido se detiene y `truncado` viene en `true`.

```bash
curl -X POST "http://127.0.0.1:5000/comparar?limite=50" ...
```

**Límite de tamaño:** 50 MB por petición. Si se supera, responde `413`.

Todos los errores devuelven JSON con una clave `error`: `400` si el JSON está
mal formado o faltan campos, `413` si es demasiado grande, `404` y `405` para
rutas y métodos incorrectos.

---

## Script CLI

Flujo original, con rutas fijas:

```bash
python index.py
```

| Carpeta | Rol |
|---|---|
| `original/` | Entradas: `input_original.json` e `input_new.json` |
| `new/` | Salidas normalizadas: `output_original.json` y `output_new.json` |

Luego se abren los dos archivos de `new/` lado a lado en VS Code para el diff.

---

## Cómo se normaliza

Lógica en `normalizer.py`, función `ordenar_json`:

- **Diccionarios** → claves ordenadas alfabéticamente, de forma recursiva.
- **Listas donde todos los elementos son diccionarios** → ordenadas por su
  contenido serializado (`json.dumps(x, sort_keys=True)`), para que el mismo
  conjunto de objetos quede siempre en el mismo orden.
- **Cualquier otra lista** (números, strings, mixta) → se respeta el orden
  original, porque ahí la posición sí puede ser significativa.

### Advertencia sobre listas de objetos

Como las listas de diccionarios se ordenan por su contenido, si un objeto dentro
de una lista cambia, **su posición en el orden también cambia**. Un solo campo
modificado puede aparecer entonces como varias diferencias desplazadas dentro de
esa lista, y las rutas `[i]` no corresponden a la posición original del dato.

Es el mismo comportamiento que ya tenía el diff manual en VS Code. Para listas
con identificador estable conviene leer las diferencias por su contenido, no por
el índice.

---

## Estructura

```
object-compare/
├── app.py            # API Flask
├── comparer.py       # Diff recursivo
├── normalizer.py     # Ordenamiento recursivo (núcleo del proyecto)
├── index.py          # Script CLI original
├── requirements.txt
├── original/         # Entradas del flujo CLI
└── new/              # Salidas del flujo CLI
```
