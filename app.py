from flask import Flask, jsonify, request

from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import bcrypt

from database import db
from models.snack import Snack
from models.user import User

import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin123@127.0.0.1:3306/daily_diet"

login_manager = LoginManager()
db.init_app(app)

login_manager.init_app(app)
# view Login
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Rota padrão
@app.route("/", methods=["GET"])
def index():
    return "<h1>Daily Diet API</h1>"

### Login / Logout
# Cadastrar Admin
def startAdmin():
    hasUsers = User.query.filter_by(role="admin")
    print(f"hasUsers {hasUsers.first()}")
    if hasUsers.first() == None:
        print("entrou no if")
        master_admin = User(username="admin",password=bcrypt.hashpw(b"admin", bcrypt.gensalt()),role="admin")
        db.session.add(master_admin)
        db.session.commit()

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()

        if not user:
            startAdmin()
            user = User.query.filter_by(username=username).first()
            #time.sleep(2)

        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Usuário autenticado."})

    return jsonify({"message": "Credenciais incorretas."}), 400

# Logout
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Usuário desconectado."})

### USERS
# Obter lista de usuários
@app.route("/user", methods=["GET"])
@login_required
def get_user_all():
    users = User.query.all()
    response = []
    if users:
        if users[0]:
            for user in users:
                response.append(User.to_dict(user))

            return response
    
    return error_response(status_code=404, message="Nenhum usuário cadastrado.")

# Obter um usuário pelo id
@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def get_user(id_user):
    user = User.query.get(id_user)

    if user:
        return jsonify({"username": user.username})
    
    return error_response(status_code=404)

# Cadastrar um novo usuário
@app.route("/user", methods=["POST"])
@login_required
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if current_user.role == 'admin':
        if username and password:
            hashed = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
            user = User(username=username, password=hashed, role='user')
            db.session.add(user)
            db.session.commit()

            return jsonify({"message": "Usuário cadastrado com sucesso."})
        
        return jsonify({"message": "As informações do usuário estão incompletas."}), 400
    
    return error_response(status_code=403)

# Atualizar a senha de um usuário
@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    user = User.query.get(id_user)
    data = request.json
    new_password = data.get("password")

    if id_user != current_user.id and current_user.role == 'user':
        return error_response(status_code=403)
    
    if user and new_password:
        user.password = bcrypt.hashpw(str.encode(new_password), bcrypt.gensalt())
        db.session.commit()
        return jsonify({"message": f"Usuário {id_user} atualizado com sucesso."})
    
    return error_response(status_code=404, message=f"Usuário id {id_user} inexistente.")

# Apagar um usuário
@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)

    if current_user.role != 'admin':
        return error_response(status_code=403)

    if id_user == current_user.id:
        return error_response(status_code=403, message="O usuário não pode excluir a si mesmo.")

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Usuário {id_user} excluído com sucesso."})
    
    return error_response(status_code=404, message=f"Usuário id {id_user} inexistente.")

### SNACKS
# Cadastrar refeição
@app.route("/snack", methods=["POST"])
@login_required
def register_snack():
    data = request.json
    snackname = data.get("snackname")
    description = data.get("description")
    enjoyed_on = data.get("enjoyed_on")
    diet_menu = data.get("diet_menu")

    if snackname and description and enjoyed_on:
        if not diet_menu:
            diet_menu = False

        snack = Snack(snackname=snackname, description=description, enjoyed_on=enjoyed_on, diet_menu=diet_menu, user_id=current_user.id)
        db.session.add(snack)
        db.session.commit()

        return jsonify({"message": "Refeição registrada com sucesso."})
    
    return jsonify({"message": "Dados inválidos. Refeição não registrada."})

# Atualizar refeição
@app.route("/snack/<int:id_snack>", methods=["PUT"])
@login_required
def update_snack(id_snack):
    
    snack = Snack.query.get(id_snack)
    
    data = request.json
    new_snackname = data.get("snackname")
    new_description = data.get("description")
    new_enjoyed_on = data.get("enjoyed_on")
    new_diet_menu = data.get("diet_menu")

    if snack:
        if snack.user_id == current_user.id:
            if new_snackname and new_description and new_enjoyed_on and new_diet_menu:
                snack.snackname = new_snackname
                snack.description = new_description
                snack.enjoyed_on = new_enjoyed_on
                snack.diet_menu = new_diet_menu
                db.session.commit()
                return jsonify({"message": f"Refeição {id_snack} atualizada com sucesso."})
            
        return error_response(status_code=403, message=f"Não é possível alterar a refeição de outra pessoa.")
    
    return error_response(status_code=404, message=f"Refeição com id {id_snack} inexistente.")

# Apagar refeição
@app.route("/snack/<int:id_snack>", methods=["DELETE"])
@login_required
def delete_snack(id_snack):
    snack = Snack.query.get(id_snack)

    if snack:
        if current_user.id == snack.user_id:
            db.session.delete(snack)
            db.session.commit()
            return jsonify({"message": f"Refeição com id {id_snack} excluída com sucesso."})
        
        return error_response(status_code=403, message=f"Não é possível excluir a refeição de outra pessoa.")
    
    return error_response(status_code=404, message=f"Refeição com id {id_snack} inexistente.")

# Obter todas as refeições
@app.route("/snack", methods=["GET"])
@login_required
def get_snack_all():
    snacks = Snack.query.filter_by(user_id=current_user.id).order_by(Snack.enjoyed_on)
    response = []
    if not snacks.first() == None:
        if snacks[0]:
            for snack in snacks:
                response.append(Snack.to_dict(snack))

            return response
    
    return error_response(status_code=404, message="Nenhuma refeição cadastrada.")

# Obter uma refeição pelo id
@app.route("/snack/<int:id_snack>", methods=["GET"])
@login_required
def get_snack(id_snack):
    snack = Snack.query.filter_by(id=id_snack, user_id=current_user.id).first()

    if not snack == None:
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