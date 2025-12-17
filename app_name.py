from flask import Flask, request, session, redirect, jsonify
from cas import CASClient
from config import cas_server_url, cas_client_url, secret_key

app = Flask(__name__)
app.secret_key = secret_key
app.config.update(
    SESSION_COOKIE_DOMAIN='.bouillabaisse.ec-m.fr',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
    PERMANENT_SESSION_LIFETIME=60*60*24*30,
)

cas_client = CASClient(
    version=3,
    server_url=cas_server_url,
)


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
        if request.args.get('redirect'):
            link = request.args.get('redirect')
            if link[:4] != "http":
                link = "https://" + link
            return redirect(link)
        elif request.args.get('next'):
            return redirect('/static/' + request.args.get('next'))
        else:
            return redirect('/static/index.html')

    ticket = request.args.get('ticket')
    if not ticket:
        if request.args.get('redirect'):
            link = request.args.get('redirect')
            if link[:4] != "http":
                link = "https://" + link
            cas_client.service_url = cas_client_url + 'login?redirect=' + link
        elif request.args.get('next'):
            cas_client.service_url = cas_client_url + 'login?next=' + request.args.get('next')
        cas_login_url = cas_client.get_login_url()
        return redirect(cas_login_url)


    user, attributes, pgtiou = cas_client.verify_ticket(ticket)

    if not user:
        return 'La vérification de votre ticket a échoué. <a href="/login">Se connecter</a>'
    else:
        session.permanent = True
        session['username'] = user
        session['ticket'] = ticket

        if request.args.get('redirect'):
            link = request.args.get('redirect')
            if link[:4] != "http":
                link = "https://" + link
            return redirect(link)
        elif request.args.get('next'):
            return redirect('/static/' + request.args.get('next'))
        else:
            return redirect('/static/index.html')

@app.route('/logout')
def logout():
    redirect_url = cas_client_url + 'logout_callback'
    cas_logout_url = cas_client.get_logout_url(redirect_url)

    return redirect(cas_logout_url)

@app.route('/logout_callback')
def logout_callback():
    session.pop('username', None)
    return 'Vous êtes deconnecté du CAS. <a href="/login">Se connecter</a>'

@app.route('/validate_session')
def validate_session():
    if 'username' in session:
        response = jsonify({"valid": True})
        response.headers['X-Auth-User'] = session['username']
        return response
    else:
        return jsonify({"valid": False}), 403

if __name__ == '__main__':
    app.run()
