# import requirements needed
#from flask import Flask, render_template
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
#from utils import get_base_url
from werkzeug.utils import secure_filename
from utils_file import get_base_url

import cv2
import torch 
import os

app = Flask(__name__)

os.environ['KMP_DUPLICATE_LIB_OK']='True'

# setup the webserver
# port may need to be changed if there are multiple flask servers running on same server
port = 12345
base_url = get_base_url(port)

# if the base url is not empty, then the server is running in development, and we need to specify the static folder so that the static files are served
if base_url == '/':
    app = Flask(__name__)
else:
    app = Flask(__name__, static_url_path=base_url+'static')


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

model = torch.hub.load(os.path.join(os.getcwd(),'yolov5'), 'custom', path= os.path.join(os.getcwd(),'yolov5/best.pt'), source='local')  # local repo

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# set up the routes and logic for the webserver
@app.route(f'{base_url}')
def home():
    return render_template('index.html')

# define additional routes here
# for example:
# @app.route(f'{base_url}/team_members')
# def team_members():
#     return render_template('team_members.html') # would need to actually make this page

@app.route('/', methods=['POST'])
#@app.route(base_url, methods=['POST'])
def home_post():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('results', filename=filename))


@app.route('/uploads/<filename>')
#@app.route(base_url + '/uploads/<filename>')
def results(filename): 
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    results = model(image_path, size=640)
    results.save( save_dir= os.path.join(os.getcwd(),'uploads/detected') )

    return render_template('results.html', filename=filename) 


@app.route('/uploads/detected/<path:filename>')
#@app.route(base_url + '/files/<path:filename>')
def detected_files(filename):
    return send_from_directory(os.path.join(os.getcwd(),'uploads/detected') , filename, as_attachment=True)


if __name__ == '__main__':
    # IMPORTANT: change url to the site where you are editing this file.
    website_url = 'url'
    
    print(f'Try to open\n\n    https://{website_url}' + base_url + '\n\n')
    app.run(host = '0.0.0.0', port=port, debug=True)
    import sys; sys.exit(0)
