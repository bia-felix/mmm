import os, sqlite3, json, secrets
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE=os.path.dirname(os.path.abspath(__file__))
app=Flask(__name__)
app.secret_key=os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.environ.get('RENDER')=='true')
app.config['MAX_CONTENT_LENGTH']=5*1024*1024
DB=os.path.join('/tmp','gracas_aventais_demo.db') if os.environ.get('DEMO_MODE')=='1' else os.path.join(BASE,'pedidos.db')
UPLOAD=os.path.join('/tmp','gracas_aventais_uploads') if os.environ.get('DEMO_MODE')=='1' else os.path.join(BASE,'uploads')
os.makedirs(UPLOAD,exist_ok=True)

def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c

def init():
 with db() as c:
  c.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)')
  c.execute('CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT DEFAULT CURRENT_TIMESTAMP, client TEXT, phone TEXT, garment TEXT, cut TEXT, embroidery TEXT, image TEXT, cut_status TEXT DEFAULT "Pendente", embroidery_status TEXT DEFAULT "Pendente")')
  if not c.execute('SELECT 1 FROM users').fetchone():
   for u,p,r in [('admin',os.environ.get('ADMIN_PASSWORD'), 'admin'),('cortador',os.environ.get('CUTTER_PASSWORD'),'cortador'),('bordador',os.environ.get('EMBROIDERER_PASSWORD'),'bordador')]:
    if not p: raise RuntimeError('Configure ADMIN_PASSWORD, CUTTER_PASSWORD e EMBROIDERER_PASSWORD no Render antes de iniciar.')
    c.execute('INSERT INTO users(username,password,role) VALUES(?,?,?)',(u,generate_password_hash(p),r))
init()

@app.before_request
def csrf_protect():
 if request.method=='POST':
  token=session.get('_csrf')
  if not token or not secrets.compare_digest(token,request.form.get('_csrf','')):abort(400)

@app.context_processor
def csrf_context():
 if '_csrf' not in session:session['_csrf']=secrets.token_urlsafe(32)
 return {'csrf_token':session['_csrf']}

def access(*roles):
 def deco(fn):
  @wraps(fn)
  def inner(*a,**kw):
   if not session.get('uid'):return redirect(url_for('login'))
   if session.get('role') not in roles:abort(403)
   return fn(*a,**kw)
  return inner
 return deco

@app.context_processor
def context():return {'role':session.get('role'),'username':session.get('username')}

@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  with db() as c:u=c.execute('SELECT * FROM users WHERE username=?',(request.form.get('username'),)).fetchone()
  if u and check_password_hash(u['password'],request.form.get('password','')):
   session.clear();session.update(uid=u['id'],username=u['username'],role=u['role']);return redirect(url_for('home'))
  flash('Usuário ou senha incorretos.')
 return render_template('login.html')

@app.route('/logout')
def logout():session.clear();return redirect(url_for('login'))

@app.route('/')
@access('admin','cortador','bordador')
def home():
 with db() as c:orders=c.execute('SELECT * FROM orders ORDER BY id DESC').fetchall()
 return render_template('home.html',orders=orders)

@app.route('/novo',methods=['GET','POST'])
@access('admin')
def novo():
 if request.method=='POST':
  if os.environ.get('DEMO_MODE')=='1' and request.files.get('imagem') and request.files['imagem'].filename:
   flash('Na demonstração, não envie imagens de clientes.');return redirect(url_for('novo'))
  f=request.form
  cut_keys=['sexo','tamanho_tipo','tamanho','busto','cintura','quadril','ombro','manga_medida','comprimento','comprimento_calca','cintura_calca','gola','manga','punho','calca','bolso_blusa','bolso_calca','formato_bolso','tecido','cor','quantidade','obs_corte']
  emb_keys=['tem_bordado','tipo_bordado','texto_bordado','local_bordado','cor_bordado','fonte','simbolo','obs_bordado']
  cut={k:f.get(k,'') for k in cut_keys};emb={k:f.get(k,'') for k in emb_keys}
  filename=None;upload=request.files.get('imagem')
  if upload and upload.filename:
   ext=os.path.splitext(secure_filename(upload.filename))[1].lower()
   if ext not in ('.png','.jpg','.jpeg','.webp'):flash('Imagem inválida.');return redirect(url_for('novo'))
   filename=secrets.token_hex(16)+ext;upload.save(os.path.join(UPLOAD,filename))
  with db() as c:c.execute('INSERT INTO orders(client,phone,garment,cut,embroidery,image) VALUES(?,?,?,?,?,?)',(f.get('client','').strip(),f.get('phone','').strip(),f.get('garment','jaleco'),json.dumps(cut,ensure_ascii=False),json.dumps(emb,ensure_ascii=False),filename))
  flash('Pedido criado com sucesso.');return redirect(url_for('home'))
 return render_template('new.html')

@app.route('/pedido/<int:oid>')
@access('admin','cortador','bordador')
def pedido(oid):
 with db() as c:o=c.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone()
 if not o:abort(404)
 return render_template('order.html',o=o,cut=json.loads(o['cut']),emb=json.loads(o['embroidery']))

@app.route('/pedido/<int:oid>/status',methods=['POST'])
@access('admin','cortador','bordador')
def status(oid):
 field='cut_status' if session['role']=='cortador' else 'embroidery_status' if session['role']=='bordador' else request.form.get('field')
 if field not in ('cut_status','embroidery_status'):abort(400)
 value=request.form.get('status')
 if value not in ('Pendente','Em andamento','Concluído'):abort(400)
 with db() as c:c.execute(f'UPDATE orders SET {field}=? WHERE id=?',(value,oid))
 return redirect(url_for('pedido',oid=oid))

@app.route('/imagem/<int:oid>')
@access('admin','bordador')
def imagem(oid):
 with db() as c:o=c.execute('SELECT image FROM orders WHERE id=?',(oid,)).fetchone()
 if not o or not o['image']:abort(404)
 return send_from_directory(UPLOAD,o['image'])

@app.route('/senha',methods=['GET','POST'])
@access('admin','cortador','bordador')
def senha():
 if request.method=='POST':
  with db() as c:
   u=c.execute('SELECT password FROM users WHERE id=?',(session['uid'],)).fetchone()
   if not check_password_hash(u['password'],request.form.get('old','')):flash('Senha atual incorreta.')
   elif len(request.form.get('new',''))<10:flash('A nova senha precisa ter pelo menos 10 caracteres.')
   else:
    c.execute('UPDATE users SET password=? WHERE id=?',(generate_password_hash(request.form['new']),session['uid']))
    flash('Senha alterada.')
 return render_template('password.html')

if __name__=='__main__':app.run(debug=False,host='127.0.0.1',port=5000)
