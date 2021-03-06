import config
import db_operations
from models import *
from flask import Flask, request, redirect, render_template, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

app.config.from_object(config.DevelopmentConfig)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#app.route diz que função deve ser chamada
#quando entramos nessa url no servidor
@app.route("/")
def index():
	#session é um hash global
	email = session.get('user_id')
	if email is None:
		#url_for(algo) da um url para a ação algo
		return redirect(url_for('login'))

	name = db_operations.get_name_from_email(email)

	if name is None:
		error = "User not associated with any Person. Ask the Admin to fix this."
		session.clear()
		return error + "<br> <a href=\"/\"> Voltar </a>"

	results = db_operations.get_servs_from_email(email)

	#Render_Template pega um html da pasta templates
	#os outros args servem para preencher as coisas dentro do html 
	return render_template('index.html', name=name, servs=results)

@app.route("/login", methods=('GET', 'POST'))
def login():
	error = None

	#POST é chamado quando mandamos o form de login
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']

		data = db_operations.check_login(email, password)

		if data is None:
			error = 'Incorrect username/password.'

		if error is None:
			#clear limpa a session (garantia)
			session.clear()
			#É um hash, lembra?
			session['user_id'] = email
			return redirect(url_for('index'))

	return render_template('login.html', error=error)

@app.route("/logout")
def logout():
	if session.get('user_id') is not None:
		session.clear()

	return redirect(url_for('index'))

#Verifica se a pessoa tem permissão para acessar a pagina em questão
def check_permission(serv_num):
	#verifica se está logada
	email = session.get('user_id')
	if email is None:
		return redirect(url_for('login'))

	servs = db_operations.get_servs_from_email(email)

	if type(servs) == str:
			return servs + "<br> <a href=\"/\"> Voltar </a>"

	#se tem o serviço associado
	if not serv_num in servs:
		return redirect(url_for('index'))

	return None

@app.route("/add_p")
def add_p():
	block = check_permission(1)

	if block is not None:
		return block

	#request.args pega args do url: /algo?name=coisa
	name=request.args.get('name')
	cpf=request.args.get('cpf')

	if name == '' or cpf == '':
		return "Parametros de inserção invalidos. <br> <a href=\"/\"> Voltar </a>"

	return db_operations.add_p(name, cpf)

@app.route("/getall_p")
def getall_p():
	block = check_permission(1)

	if block is not None:
		return block

	results = db_operations.get_all_p()

	#No caso, se a função retornar uma string,
	#é uma mensagem de erro
	if type(results) == str:
		return results + "<br> <a href=\"/\"> Voltar </a>"

	return render_template('Pessoa/getall_p.html', results=results)

@app.route("/update_p", methods=('GET', 'POST'))
def update_p():
	block = check_permission(1)

	if block is not None:
		return block

	pes_id = request.args.get('id')
	if pes_id is None:
		return "No ID Specified <br> <a href=\"/\"> Voltar </a>"

	#Se a pessoa preencheu o formulario, atualize
	if request.method == 'POST':
		name = request.form['name']
		cpf= request.form['cpf']

		result = db_operations.update_p(pes_id, name, cpf)

		if type(result) == str:
			return result + "<br> <a href=\"/\"> Voltar </a>"

		return redirect(url_for('getall_p'))

	#Se não, só preencha e espere modificações
	else:
		pes_info = db_operations.get_p(pes_id)

		if type(pes_info) == str:
			return pes_info + "<br> <a href=\"/\"> Voltar </a>"

		return render_template('Pessoa/update_p.html', info=pes_info)

@app.route("/delete_p")
def delete_p():
	block = check_permission(1)

	if block is not None:
		return block

	pes_cpf = request.args.get('cpf')
	if pes_cpf is None:
		return "No ID Specified <br> <a href=\"/\"> Voltar </a>"

	result = db_operations.delete_p(pes_cpf)

	return result

@app.route("/work_profs")
def work_profs():
	semestre=request.args.get('semestre')
	ano=request.args.get('ano')

	if semestre == '' or ano == '':
		return "Parametros de pesquisa invalidos. <br> <a href=\"/\"> Voltar </a>"

	results = db_operations.work_profs(semestre, ano)

	if type(results) == str:
		return results + "<br> <a href=\"/\"> Voltar </a>"

	return render_template('work_profs.html', results=results)

@app.route("/add_curso")
def add_curso():
	block = check_permission(3)

	if block is not None:
		return block

	#request.args pega args do url: /algo?name=coisa
	code=request.args.get('code')
	name=request.args.get('name')
	cpf=request.args.get('cpf')
	timein=request.args.get('timein')
	timeout=request.args.get('timeout')

	if code == '' or cpf == '':
		return "Parametros de inserção invalidos. <br> <a href=\"/\"> Voltar </a>"

	return db_operations.add_curso(code, name, cpf, timein, timeout)

@app.route("/getall_curso")
def getall_curso():
	block = check_permission(3)

	if block is not None:
		return block

	results = db_operations.get_all_curso()

	#No caso, se a função retornar uma string,
	#é uma mensagem de erro
	if type(results) == str:
		return results + "<br> <a href=\"/\"> Voltar </a>"

	return render_template('Curso/getall_curso.html', results=results)

@app.route("/update_curso", methods=('GET', 'POST'))
def update_curso():
	block = check_permission(3)

	if block is not None:
		return block

	cur_id = request.args.get('id')
	if cur_id is None:
		return "No ID Specified <br> <a href=\"/\"> Voltar </a>"

	#Se a pessoa preencheu o formulario, atualize
	if request.method == 'POST':
		code = request.form['code']
		name = request.form['name']
		cpf = request.form['cpf']
		date_in = request.form['datein']
		date_out = request.form['dateout']

		result = db_operations.update_curso(cur_id, code, name, cpf, date_in, date_out)

		if type(result) == str:
			return result + "<br> <a href=\"/\"> Voltar </a>"

		return redirect(url_for('getall_curso'))

	#Se não, só preencha e espere modificações
	else:
		cur_info = db_operations.get_curso(cur_id)

		if type(cur_info) == str:
			return cur_info + "<br> <a href=\"/\"> Voltar </a>"

		cur_info = list(cur_info)
		#Datatime em html é YYYY-MM-DDTHH:MM:SS
		cur_info[4] = str(cur_info[4]).replace(" ","T")
		cur_info[5] = str(cur_info[5]).replace(" ","T")

		return render_template('Curso/update_curso.html', info=cur_info)

@app.route("/delete_curso")
def delete_curso():
	block = check_permission(3)

	if block is not None:
		return block

	cur_code = request.args.get('code')
	if cur_code is None:
		return "No ID Specified <br> <a href=\"/\"> Voltar </a>"

	result = db_operations.delete_curso(cur_code)

	return result

@app.route("/add_per")
def add_perfil():
	block = check_permission(4)

	if block is not None:
		return block

	#request.args pega args do url: /algo?name=coisa

	name=request.args.get('name')
	desc=request.args.get('desc')

	if name == '':
		return "Parametros de inserção invalidos. <br> <a href=\"/\"> Voltar </a>"

	return db_operations.add_per(name, desc)

@app.route("/getall_per")
def getall_perfil():
	block = check_permission(4)

	if block is not None:
		return block


	results = db_operations.get_all_per()

	#No caso, se a função retornar uma string,
	#é uma mensagem de erro
	if type(results) == str:
		return results + "<br> <a href=\"/\"> Voltar </a>"

	return render_template('Perfil/getall_per.html', results=results)

@app.route("/update_per", methods=('GET', 'POST'))
def update_perfil():
	block = check_permission(4)

	if block is not None:
		return block

	per_id = request.args.get('id')
	if per_id is None:
		return "No ID Specified <br> <a href=\"/\"> Voltar </a>"

	#Se a pessoa preencheu o formulario, atualize
	if request.method == 'POST':
		name = request.form['name']
		desc = request.form['desc']

		result = db_operations.update_per(per_id, name, desc)

		if type(result) == str:
			return result + "<br> <a href=\"/\"> Voltar </a>"

		return redirect(url_for('getall_perfil'))

	#Se não, só preencha e espere modificações
	else:
		per_info = db_operations.get_per(per_id)

		if type(per_info) == str:
			return per_info + "<br> <a href=\"/\"> Voltar </a>"

		return render_template('Perfil/update_per.html', info=per_info)

@app.route("/delete_per")
def delete_perfil():
	block = check_permission(4)

	if block is not None:
		return block

	per_name = request.args.get('name')
	if per_name is None:
		return "No ID Specified <br> <a href=\"/\"> Voltar </a>"

	result = db_operations.delete_per(per_name)

	return result

@app.route("/add_rel_pes_us")
def add_rel_pes_us():
	block = check_permission(5)

	if block is not None:
		return block

	#request.args pega args do url: /algo?name=coisa
	cpf=request.args.get('cpf')
	email=request.args.get('email')
	date_in=request.args.get('datein')
	date_out=request.args.get('dateout')

	if cpf == '' or email == '' or date_in == '':
		return "Parametros de inserção invalidos. <br> <a href=\"/\"> Voltar </a>"

	return db_operations.add_rel_pes_us(cpf, email, date_in, date_out)

@app.route("/getall_rel_pes_us")
def getall_rel_pes_us():
	block = check_permission(5)

	if block is not None:
		return block

	results = db_operations.get_all_rel_pes_us()

	#No caso, se a função retornar uma string,
	#é uma mensagem de erro
	if type(results) == str:
		return results + "<br> <a href=\"/\"> Voltar </a>"

	return render_template('Rel/getall_rel_pes_us.html', results=results)

@app.route("/update_rel_pes_us", methods=('GET', 'POST'))
def update_rel_pes_us():
	block = check_permission(5)

	if block is not None:
		return block

	original_cpf = request.args.get('cpf')
	original_email = request.args.get('email')
	if original_cpf is None or original_email is None:
		return "No ID Specified <br> <a href=\"/\"> Voltar </a>"

	#Se a pessoa preencheu o formulario, atualize
	if request.method == 'POST':
		cpf= request.form['cpf']
		email = request.form['email']
		date_in = request.form['datein']
		date_out = request.form['dateout']

		result = db_operations.update_rel_pes_us(original_cpf, original_email, cpf, email, date_in, date_out)

		if type(result) == str:
			return result + "<br> <a href=\"/\"> Voltar </a>"

		return redirect(url_for('getall_rel_pes_us'))

	#Se não, só preencha e espere modificações
	else:
		rel_info = db_operations.get_rel_pes_us(original_cpf, original_email)

		if type(rel_info) == str:
			return rel_info + "<br> <a href=\"/\"> Voltar </a>"

		rel_info = list(rel_info)
		#Datatime em html é YYYY-MM-DDTHH:MM:SS
		rel_info[2] = str(rel_info[2]).replace(" ","T")
		rel_info[3] = str(rel_info[3]).replace(" ","T")

		return render_template('Rel/update_rel_pes_us.html', info=rel_info)

@app.route("/delete_rel_pes_us")
def delete_rel_pes_us():
	block = check_permission(5)

	if block is not None:
		return block

	cpf=request.args.get('cpf')
	email=request.args.get('email')

	if cpf is None:
		return "No ID Specified <br> <a href=\"/\"> Voltar </a>"

	result = db_operations.delete_rel_pes_us(cpf, email)

	return result

@app.route("/add_rel_prof_dis")
def add_rel_prof_dis():
	block = check_permission(6)

	if block is not None:
		return block

	prof_nusp = request.args.get('prof_nusp')
	dis_code = request.args.get('dis_code')
	semester = request.args.get('semester')
	year = request.args.get('year')

	if prof_nusp == '' or dis_code == '':
		return "Parametros de inserção invalidos. <br> <a href=\"/\"> Voltar </a>"

	return db_operations.add_rel_prof_dis(prof_nusp, dis_code, semester, year)

@app.route("/getall_rel_prof_dis")
def getall_rel_prof_dis():
	block = check_permission(6)

	if block is not None:
		return block

	results = db_operations.getall_rel_prof_dis()

	#No caso, se a função retornar uma string,
	#é uma mensagem de erro
	if type(results) == str:
		return results + "<br> <a href=\"/\"> Voltar </a>"

	return render_template('Rel/getall_rel_prof_dis.html', results=results)

@app.route("/update_rel_prof_dis", methods=('GET', 'POST'))
def update_rel_prof_dis():
	block = check_permission(6)

	if block is not None:
		return block

	original_prof_nusp = request.args.get('prof_nusp')
	original_dis_code = request.args.get('dis_code')
	if original_prof_nusp is None or original_dis_code is None:
		return "No ID Specified <br> <a href=\"/\"> Voltar </a>"

	#Se a pessoa preencheu o formulario, atualize
	if request.method == 'POST':
		prof_nusp = request.form['prof_nusp']
		dis_code = request.form['dis_code']
		semester = request.form['semester']
		year = request.form['year']

		result = db_operations.update_rel_prof_dis(original_prof_nusp, original_dis_code, prof_nusp, dis_code, semester, year)

		if type(result) == str:
			return result + "<br> <a href=\"/\"> Voltar </a>"

		return redirect(url_for('getall_rel_prof_dis'))

	#Se não, só preencha e espere modificações
	else:
		rel_info = db_operations.get_rel_prof_dis(original_prof_nusp, original_dis_code)

		if type(rel_info) == str:
			return rel_info + "<br> <a href=\"/\"> Voltar </a>"

		return render_template('Rel/update_rel_prof_dis.html', info=rel_info)

@app.route("/delete_rel_prof_dis")
def delete_rel_prof_dis():
	block = check_permission(6)

	if block is not None:
		return block

	prof_nusp = request.args.get('prof_nusp')
	dis_code = request.args.get('dis_code')
	semester = request.args.get('semester')
	year = request.args.get('year')
	if prof_nusp is None or dis_code is None:
		return "No ID Specified <br> <a href=\"/\"> Voltar </a>"

	result = db_operations.delete_rel_prof_dis(prof_nusp, dis_code, semester, year)

	return result


if __name__ == '__main__':
	app.run()