# http://stackoverflow.com/questions/35459719/no-webcam-stream-when-embedding-webrtc-in-flask-app
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

app.debug = True

@app.route('/')
def home():
  return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app)
