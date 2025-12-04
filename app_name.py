from flask import Flask, request, session, redirect, url_for, jsonify
from cas import CASClient
from config import cas_server_url, cas_client_url, server_name

app = Flask(__name__)
app.secret_key = 'DFGtzenDRFz'
app.config['CAS_SERVER'] = server_name

cas_client = CASClient(
    version=3,
    service_url='http://localhost:8080/login?next=%2Fprofile',
    server_url=cas_server_url,

)

@app.route('/')
def index():
    return redirect('/static/')

@app.route('/static/')
#Redirection utile juste en local, sur le serveur NGinx sert lui-même les fichiers static et l'index par default
def static_index():
    return redirect('/static/index.html')

@app.route('/data')
def data(methods=['GET']):
    data = {}
    if 'username' in session:
        data['username'] = session['username']
    if 'ticket' in session:
        data['ticket'] = session['ticket']
    return jsonify(data)

@app.route('/login')
def login():
    if 'username' in session:
        # Already logged in
        return redirect(request.args.get('next'))

    ticket = request.args.get('ticket')
    if not ticket:
        # No ticket, the request come from end user, send to CAS login
        cas_client.service_url = cas_client_url + 'login?next=' + request.args.get('next')
        cas_login_url = cas_client.get_login_url()
        app.logger.debug('CAS login URL: %s', cas_login_url)
        return redirect(cas_login_url)

    # There is a ticket, the request come from CAS as callback.
    # need call `verify_ticket()` to validate ticket and get user profile.
    app.logger.debug('ticket: %s', ticket)
    app.logger.debug('next: %s', next)

    user, attributes, pgtiou = cas_client.verify_ticket(ticket)

    app.logger.debug(
        'CAS verify ticket response: user: %s, attributes: %s, pgtiou: %s', user, attributes, pgtiou)

    if not user:
        return 'Failed to verify ticket. <a href="/login">Login</a>'
    else:  # Login successfully, redirect according `next` query parameter.
        session['username'] = user
        session['ticket'] = ticket
        return redirect(request.args.get('next'))


@app.route('/logout')
def logout():
    redirect_url = url_for('logout_callback', _external=True)
    cas_logout_url = cas_client.get_logout_url(redirect_url)
    app.logger.debug('CAS logout URL: %s', cas_logout_url)

    return redirect(cas_logout_url)

@app.route('/logout_callback')
def logout_callback():
    # redirect from CAS logout request after CAS logout successfully
    session.pop('username', None)
    return 'Logged out from CAS. <a href="/login">Login</a>'

def start():
    app.run()


if __name__ == '__main__':
    app.run()
