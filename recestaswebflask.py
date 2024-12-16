from flask import Flask, request, jsonify, render_template
import redis
import json

# Configuración de la base de datos KeyDB
keydb = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Crear una instancia de Flask
app = Flask(__name__)

# Ruta para la página principal
@app.route('/')
def home():
    return render_template('index.html')

# Ruta para agregar una receta
@app.route('/recetas', methods=['POST'])
def agregar_receta():
    data = request.json
    nombre = data.get('nombre')
    ingredientes = data.get('ingredientes')
    pasos = data.get('pasos')

    if not (nombre and ingredientes and pasos):
        return jsonify({"error": "Faltan datos de la receta"}), 400

    receta = {
        "nombre": nombre,
        "ingredientes": ingredientes,
        "pasos": pasos
    }
    keydb.set(nombre, json.dumps(receta))
    return jsonify({"message": "Receta agregada con éxito."}), 201

# Ruta para actualizar una receta existente
@app.route('/recetas/<nombre>', methods=['PUT'])
def actualizar_receta(nombre):
    if not keydb.exists(nombre):
        return jsonify({"error": "Receta no encontrada."}), 404

    receta = json.loads(keydb.get(nombre))
    data = request.json

    receta["nombre"] = data.get("nombre", receta["nombre"])
    receta["ingredientes"] = data.get("ingredientes", receta["ingredientes"])
    receta["pasos"] = data.get("pasos", receta["pasos"])

    keydb.delete(nombre)
    keydb.set(receta["nombre"], json.dumps(receta))
    return jsonify({"message": "Receta actualizada con éxito."})

# Ruta para eliminar una receta existente
@app.route('/recetas/<nombre>', methods=['DELETE'])
def eliminar_receta(nombre):
    if not keydb.exists(nombre):
        return jsonify({"error": "Receta no encontrada."}), 404

    keydb.delete(nombre)
    return jsonify({"message": "Receta eliminada con éxito."})

# Ruta para ver el listado de recetas
@app.route('/recetas', methods=['GET'])
def ver_recetas():
    claves = keydb.keys()
    recetas = []
    for clave in claves:
        receta = json.loads(keydb.get(clave))
        recetas.append(receta)
    return jsonify(recetas)

# Ruta para buscar una receta por nombre
@app.route('/recetas/<nombre>', methods=['GET'])
def buscar_receta(nombre):
    if not keydb.exists(nombre):
        return jsonify({"error": "Receta no encontrada."}), 404

    receta = json.loads(keydb.get(nombre))
    return jsonify(receta)

# Archivo principal de ejecución
if __name__ == '__main__':
    app.run(debug=True)
