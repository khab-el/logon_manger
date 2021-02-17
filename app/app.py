
import ldap as l
from flask import Flask, g, request, session, redirect, url_for, render_template, Response
from flask_simpleldap import LDAP
import os
import requests

app = Flask(__name__)
app.secret_key = 'dev key'

app.config['LDAP_HOST'] = os.getenv('LDAP_HOST', 'localhost')
app.config['LDAP_PORT'] = os.getenv('LDAP_PORT', '389')
app.config['LDAP_BASE_DN'] = os.getenv('LDAP_BASE_DN', 'ou=Users,dc=elastic,dc=co')
app.config['LDAP_USERNAME'] = os.getenv('LDAP_USERNAME', 'cn=admin,dc=elastic,dc=co')
app.config['LDAP_PASSWORD'] = os.getenv('LDAP_PASSWORD', 'password')

app.config['LDAP_OPENLDAP'] = os.getenv('LDAP_OPENLDAP', "True")
app.config['LDAP_OBJECTS_DN'] = os.getenv('LDAP_OBJECTS_DN', 'dn')
app.config['LDAP_USER_OBJECT_FILTER'] = os.getenv('LDAP_USER_OBJECT_FILTER', '(&(objectclass=inetOrgPerson)(cn=%s))')

app.config['LDAP_GROUP_MEMBERS_FIELD'] = os.getenv('LDAP_GROUP_MEMBERS_FIELD', "uniquemember")
app.config['LDAP_GROUP_OBJECT_FILTER'] = os.getenv('LDAP_GROUP_OBJECT_FILTER', "(&(objectclass=groupOfUniqueNames)(cn=%s))")
app.config['LDAP_GROUP_MEMBER_FILTER'] = os.getenv('LDAP_GROUP_MEMBER_FILTER', "(&(cn=*)(objectclass=groupOfUniqueNames)(uniquemember=%s))")
app.config['LDAP_GROUP_MEMBER_FILTER_FIELD'] = os.getenv('LDAP_GROUP_MEMBER_FILTER_FIELD', "cn")

base_url = os.getenv('BASE_URL', "/kibana")

redirect_url = os.getenv('REDIRECT_URL', 'http://localhost:5601/')
SITE_NAME = redirect_url

ldap = LDAP(app)

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        # This is where you'd query your database to get the user info.
        g.user = {}
        # Create a global with the LDAP groups the user is a member of.
        g.ldap_groups = ldap.get_user_groups(user=session['user_id'])

@app.route('/<path:path>',methods=['GET','POST','DELETE', 'PUT'])
@ldap.login_required
def index(path):
    global SITE_NAME
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    if request.method=='GET':
        if request.get_json(silent=True) is None:
            resp = requests.get(f'{SITE_NAME}{path}', params=request.args, headers=request.get_data())
        else:
            resp = requests.get(f'{SITE_NAME}{path}', params=request.args, json=request.get_json(), headers=request.get_data())
        headers = [(name, value) for (name, value) in  resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method=='POST':
        if request.get_json(silent=True) is None:
            if (request.get_data() is None) == False:
                resp = requests.post(f'{SITE_NAME}{path}', params=request.args, data=request.get_data(), headers=request.headers)
            else:
                resp = requests.post(f'{SITE_NAME}{path}', params=request.args, headers=request.headers)
        else:
            resp = requests.post(f'{SITE_NAME}{path}', params=request.args, json=request.get_json(), headers=request.headers)
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method=='PUT':
        if request.get_json(silent=True) is None:
            if (request.get_data() is None) == False:
                resp = requests.put(f'{SITE_NAME}{path}', params=request.args, data=request.get_data(), headers=request.headers)
            else:
                resp = requests.put(f'{SITE_NAME}{path}', params=request.args, headers=request.headers)
        else:
            resp = requests.put(f'{SITE_NAME}{path}', params=request.args, json=request.get_json(), headers=request.headers)
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method=='DELETE':
        if request.get_json(silent=True) is None:
            resp = requests.delete(f'{SITE_NAME}{path}', params=request.args, headers=request.headers)
        else:
            resp = requests.delete(f'{SITE_NAME}{path}', params=request.args, json=request.get_json(), headers=request.headers)
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response

# @app.route('/', methods=['GET','POST'])
# def base():
#     return redirect(f'{base_url}')

@app.route(f'{base_url}', methods=['GET','POST'])
@ldap.login_required
def button():
    return render_template('button.html')

@app.route(f'{base_url}/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(f'{base_url}')
    if request.method == 'POST':
        user = request.form['user']
        passwd = request.form['passwd']
        print(user, passwd)
        test = ldap.bind_user(user, passwd)
        if test is None or passwd == '':
            return redirect(f'{base_url}/login')
        else:
            session['user_id'] = request.form['user']
            return redirect(f'{base_url}')
    return render_template('login.html')

@app.route(f'{base_url}/logout')
def logout():
    session.pop('user_id', None)
    return redirect(f'{base_url}/login')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)