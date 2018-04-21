from flask import Flask, request, redirect, make_response, url_for, stream_with_context, Response, session, render_template
from flask import send_from_directory
from werkzeug import secure_filename
import os
import time
from flask import Response
import markdown
from flask import Markup
#import volunteerscore

UPLOAD_FOLDER = 'upload/'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.debug = True
app.secret_key = "q9283jrisadjfklasdfoqiweurlkajsdf"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/getfile/<thisfile>')
def uploaded_file(thisfile):
    #return outfile
    return send_from_directory(app.config['UPLOAD_FOLDER'], thisfile)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            session['filename'] = secure_filename(file.filename)
            file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], session['filename']))
            #return redirect('/convert/')
            return redirect(url_for('getscores',
                                    filename=session['filename']))
    session.pop('filename', None)
    return render_template('index.html')


@app.route('/about')
def about():
    with open('readme.md', 'r') as f:
        content = Markup(markdown.markdown(f.read()))
    return render_template('markdown.html', content=content)


@app.route('/uploads/<filename>')
def getscores(filename):
    def generate():
        yield '''<!doctype html>
        <title>Processing File...</title>
        <center>
        <h1>Processing File</h1>
        <img src="http://sierrafire.cr.usgs.gov/images/loading.gif" width=250 height=250>'''
        yield '<br>Loading ABS Data Set. May take a few minutes...<br>'
        import volunteerscore
        yield '<br>Dataset loaded. Processing your file...<br>'
        path = 'upload/' + str(filename)
        yield str(path)
        scores = volunteerscore.makescores(path)
        #yield str(scores)
        yield "<br>Scores calculated, generating CSV<br>"
        outfile = volunteerscore.makecsv(scores)
        yield outfile
        urlstring = '<a href="/getfile/{}"> Get Scores </a>'.format(outfile)
        yield urlstring
    return Response(generate())

if __name__ == '__main__':
    app.run()
