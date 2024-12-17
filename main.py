from flask import Flask, render_template, request, redirect, url_for, flash
import redis

app = Flask(__name__)
app.secret_key = "llaveultrasecreta"

# Conexión con Redis
client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# Ruta principal
@app.route("/")
def home():
    keys = client.keys("receta:*")
    recetas = []
    for key in keys:
        receta_id = key.split(":")[1]
        receta = client.hgetall(key)
        receta["id"] = receta_id
        recetas.append(receta)
    return render_template("index.html", recetas=recetas)


# Ruta para ver una receta
@app.route("/receta/<int:receta_id>")
def ver_receta(receta_id):
    key = f"receta:{receta_id}"
    if client.exists(key):
        receta = client.hgetall(key)
        receta["id"] = receta_id
        return render_template("detalle.html", receta=receta)
    else:
        flash("Receta no encontrada.", "error")
        return redirect(url_for('home'))


# Ruta para crear una nueva receta
@app.route("/nueva", methods=["GET", "POST"])
def nueva_receta():
    if request.method == "POST":
        nombre = request.form["nombre"]
        ingredientes = request.form["ingredientes"]
        pasos = request.form["pasos"]

        if not nombre or not ingredientes or not pasos:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('nueva_receta'))

        receta_id = client.incr("receta:id")
        key = f"receta:{receta_id}"
        receta = {"nombre": nombre, "ingredientes": ingredientes, "pasos": pasos}
        client.hset(key, mapping=receta)
        flash("Receta agregada exitosamente!", "success")
        return redirect(url_for('home'))
    return render_template("nueva.html")


# Servidor con Waitress
if __name__ == "__main__":
    from waitress import serve
    print("Servidor corriendo en http://127.0.0.1:8080")
    serve(app, host="127.0.0.1", port=8080)
