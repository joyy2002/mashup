from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import os
import subprocess

app = Flask(__name__)

# Flask-Mail setup
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'albusdumbledore2521@gmail.com'  # replace with your Gmail email
app.config['MAIL_PASSWORD'] = 'Joyy@1410'  # replace with your Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'albusdumbledore2521@gmail.com' 

mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mashup', methods=['POST'])
def perform_mashup():
    try:
        # Extract data from the form
        artist = request.form['artist']
        num_videos = int(request.form['num_videos'])
        audio_duration = int(request.form['audio_duration'])
        output_file = request.form['output_file']
        email = request.form['email']

        # Call the mashup script
        script_path = os.path.join(os.path.dirname(__file__), '102117024.py')
        command = f'python {script_path} {artist} {num_videos} {audio_duration} {output_file}'
        subprocess.check_output(command, shell=True, text=True)

        # Send email
        with open(output_file, 'rb') as audio_file:
            msg = Message('Mashup Results', recipients=[email])
            msg.body = 'Your mashup is ready! Here is the output audio file.'
            msg.attach(output_file, 'audio/mpeg', audio_file.read())
            mail.send(msg)

        return jsonify(message='Mashup operation completed. Results sent to your email.')
    except Exception as e:
        error_message = f'Error: {str(e)}'
        print(error_message)
        return jsonify(message=error_message)

if __name__ == '__main__':
    app.run(debug=True)