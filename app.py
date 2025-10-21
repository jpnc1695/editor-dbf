from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Olá, mundo! Bem-vindo ao seu **tutorial em Flask**."

if __name__ == "__main__":
    app.run(debug=True)