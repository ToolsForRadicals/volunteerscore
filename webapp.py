from flask import Flask, session, request, redirect, make_response, jsonify, url_for, stream_with_context, Response, session, render_template
from flask import Response
import flask
import markdown
from flask import Markup
from flask_session import Session
import httplib2
import nationbuilder as nb
import numpy as np
import volunteerscore
import json


production = False

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

app.debug = True
app.secret_key = "q9283jrisadjfklasdfoqiweurlkajsdf"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if production:
    app.config['CELERY_BROKER_URL'] = 'amqp://guest@localhost'
    app.config['CELERY_RESULT_BACKEND'] = 'amqp://guest@localhost'
    nation_clientid = 'b91a22315a6b7b0d91700a8cdc8885962a9af7f83e7ff0ea241613ccb365ac58'
    nation_clientsecret = "0b70cf8bcea80c059c61549ea1c2be9754d1fe85b08a70b4652e9cd60884f980"

else:
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    nation_clientid = 'b91a22315a6b7b0d91700a8cdc8885962a9af7f83e7ff0ea241613ccb365ac58'
    nation_clientsecret = '0b70cf8bcea80c059c61549ea1c2be9754d1fe85b08a70b4652e9cd60884f980'




@app.route('/about')
def about():
    with open('readme.md', 'r') as f:
        content = Markup(markdown.markdown(f.read()))
    return render_template('markdown.html', content=content)


@app.route('/processing', methods=['POST','GET'])
def makepeople():
    nation = session['nation']
    if request.method == 'POST':
        if int(request.form['listid'] ) >= 0:
            people = nb.getList(nation,request.form['listid'])
        else:
            people = nb.getPeople(nation)
        for supporter in people:  
            try:
                output_supporter = dict()
                output_supporter['sex'] = supporter['sex']
                output_supporter['first_name'] = supporter['first_name']
                output_supporter['born_at'] = supporter['birthdate']
                output_supporter['region'] = volunteerscore.geocode_address(int(supporter['primary_address']['zip']))
                supporter['turnout_probability_score'] = int(volunteerscore.getvolunteerscore(output_supporter))
            except:
                supporter['turnout_probability_score'] = 0
        
        people.sort(key=lambda supporter: supporter['turnout_probability_score'])
        
        prioritised_lists = np.array_split(people,3)
        
        listdetails = nb.getLists(nation)
        listdetails = [listdetail for listdetail in listdetails if listdetail['id'] == int(request.form['listid'])]
        listdetails = listdetails[0]
        
        labels = ['Low','Medium','High']
        
        for i,prioritised_list in enumerate(prioritised_lists):
            listname = "{}_{}".format(listdetails['name'],labels[i])
            thislist = nb.makeList(nation,listname)
            listdetails = thislist.json()
            #if the list has a 200 response
            peoplelist = [person['id'] for person in prioritised_list]
            addlist = nb.addPeopletoList(nation,peoplelist,int(listdetails['list_resource']['id']))
    return render_template("")


# @app.route('/subscribe', methods=['POST','GET'])
# def stripesubscribe():
#     return render_template('payment.html')
#
# @app.route('/paid', methods=['POST','GET'])
# def stripepaid():
#     amount = 900
#     customer = stripe.Customer.create(email=form['email'],source=request.form['stripeToken'])
#     charge = stripe.Charge.create(customer=customer.id,amount=amount,currency='usd',description='Volunteer Score')
#     return "Yay!"


@app.route('/', methods=['POST','GET'])
def authorizenationbuilder():
    if request.method == 'GET':
        return render_template('nbslug.html')

    if request.method == 'POST':
        nation_slug = request.form.get('nation_slug')
        session['nation_slug'] = nation_slug
        from rauth import OAuth2Service
        access_token_url = "https://" + nation_slug + ".nationbuilder.com/oauth/token"
        authorize_url = "https://" + nation_slug + ".nationbuilder.com/oauth/authorize"
        session['nbauth'] = OAuth2Service(
            client_id=nation_clientid,
            client_secret=nation_clientsecret,
            name="Volunteer Score",
            authorize_url=authorize_url,
            access_token_url=access_token_url,
            base_url=nation_slug + ".nationbuilder.com")
        return flask.redirect(
            session['nbauth'].get_authorize_url(
                redirect_uri=flask.url_for('authorized', _external=True),response_type='code'))
    return



def json_decoder(payload):
    return json.loads(payload.decode('utf-8'))

@app.route('/authorized', methods=['POST','GET'])
def authorized():
    if 'error' in flask.request.args:
        return str(flask.request.args.get('error'))
    elif 'code' not in flask.request.args:
        return flask.redirect(flask.url_for('authorizenationbuilder'))
    session['code'] = request.args.get('code')
    redirector = url_for("authorized",_external=True)
    token = session['nbauth'].get_access_token(decoder=json_decoder, data={"code": session['code'],
                                                               "redirect_uri": redirector,
                                                               "grant_type": "authorization_code"})
    session['nation'] = nb.getNation(token,session['nation_slug'])
    return redirect(url_for('chooselist'))

@app.route('/filter', methods=['POST','GET'])
def chooselist():
    nation = session['nation']
    session['lists'] = nb.getLists(nation)
    return render_template('tags.html', lists=session['lists'])




if __name__ == '__main__':
    app.run()
