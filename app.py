from flask import Flask, jsonify, request
from database import db
from models.snack import Snack

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin123@127.0.0.1:3306/daily_diet"

db.init_app(app)

# Rota padrão
@app.route("/", methods=["GET"])
def index():
    return "<h1>Daily Diet API</h1>"

# Cadastrar refeição
@app.route("/snack", methods=["POST"])
def register_snack():
    data = request.json
    snackname = data.get("snackname")
    description = data.get("description")
    enjoyed_on = data.get("enjoyed_on")
    diet_menu = data.get("diet_menu")

    if snackname and description and enjoyed_on:
        if not diet_menu:
            diet_menu = False

        snack = Snack(snackname=snackname, description=description, enjoyed_on=enjoyed_on, diet_menu=diet_menu)
        db.session.add(snack)
        db.session.commit()

        return jsonify({"message": "Refeição registrada com sucesso."})
    
    return jsonify({"message": "Dados inválidos. Refeição não registrada."})

# Atualizar refeição
@app.route("/snack/<int:id_snack>", methods=["PUT"])
def update_snack(id_snack):
    
    snack = Snack.query.get(id_snack)
    
    data = request.json
    new_snackname = data.get("snackname")
    new_description = data.get("description")
    new_enjoyed_on = data.get("enjoyed_on")
    new_diet_menu = data.get("diet_menu")

    if snack and new_snackname and new_description and new_enjoyed_on and new_diet_menu:
        snack.snackname = new_snackname
        snack.description = new_description
        snack.enjoyed_on = new_enjoyed_on
        snack.diet_menu = new_diet_menu
        db.session.commit()
        return jsonify({"message": f"Refeição {id_snack} atualizada com sucesso."})
    
    return error_response(status_code=404, message=f"Refeição com id {id_snack} inexistente.")

# Apagar refeição
@app.route("/snack/<int:id_snack>", methods=["DELETE"])
def delete_user(id_snack):
    snack = Snack.query.get(id_snack)

    if snack:
        db.session.delete(snack)
        db.session.commit()
        return jsonify({"message": f"Refeição com id {id_snack} excluída com sucesso."})
    
    return error_response(status_code=404, message=f"Refeição com id {id_snack} inexistente.")

# Obter todas as refeições
@app.route("/snack", methods=["GET"])
def get_snack_all():
    snacks = Snack.query.all()
    response = []
    if snacks[0]:
        for snack in snacks:
            response.append(Snack.to_dict(snack))

        return response
    
    return error_response(status_code=404, message="Nenhuma refeição cadastrada.")

# Obter uma refeição pelo id
@app.route("/snack/<int:id_snack>", methods=["GET"])
def get_user(id_snack):
    snack = Snack.query.get(id_snack)

    if snack:
        return jsonify(Snack.to_dict(snack))
    
    return error_response(status_code=404)

# Retorno de erro padronizado
def error_response(status_code, message="", id=0):
    response = f"Erro genérico."
    if status_code == 400:
        response = f"Informações incorretas."
    if status_code == 401:
        response = f"Usuário sem permissão."
    if status_code == 403:
        response = f"Ação não permitida."
    if status_code == 404:
        response =  f"Não encontrado."
    
    return jsonify({"message": f"{response} {message}"}), status_code


if __name__ == '__main__':
    app.run(debug=True)