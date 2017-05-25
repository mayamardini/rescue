import os
from flask import Flask, request, redirect, url_for
from twilio.twiml.voice_response import VoiceResponse
import psycopg2
from urllib.parse import urlparse
import json
from psycopg2.extras import RealDictCursor

url = urlparse(os.environ['DATABASE_URL'])

conn = psycopg2.connect(database=url.path[1:],
  user=url.username,
  password=url.password,
  host=url.hostname,
  port=url.port
)

cur = conn.cursor(cursor_factory=RealDictCursor)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/recordings/"

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming requests."""
    resp = VoiceResponse()
    resp.play("http://f66ace1e.ngrok.io/static/recordings/lucas_song.mp3", 5)
    return str(resp)

@app.route("/api/users/<id>", methods=['GET'])
def get_user(id):
    """Gets a user from the database using the id parameter"""
    cur.execute("SELECT * FROM recordings WHERE id = " + id)
    users = cur.fetchone()
    return json.dumps(users)

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    """Serve upload form and um and upload files or somthing"""
    if request.method == 'POST':
        # check if the post request has the file part
        if 'audio' not in request.files:
            return redirect(request.url)
        file = request.files['audio']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return redirect("/")
    return '''
    <!doctype html>
    <title>Upload new recording</title>
    <h1>Upload new File</h1>
    <button id="stop">Stop
<script>
  let shouldStop = false;
  let stopped = false;
  const downloadLink = document.getElementById('download');
  const stopButton = document.getElementById('stop');

  stopButton.addEventListener('click', function() {
    shouldStop = true;
  })

  var handleSuccess = function(stream) {
    const options = {mimeType: 'video/webm;codecs=vp9'};
    const recordedChunks = [];
    const mediaRecorder = new MediaRecorder(stream, options);

    mediaRecorder.addEventListener('dataavailable', function(e) {
      if (e.data.size > 0) {
        recordedChunks.push(e.data);
      }

      if(shouldStop === true && stopped === false) {
        mediaRecorder.stop();
        stopped = true;
      }
    });

    mediaRecorder.addEventListener('stop', function() {
      downloadLink.href = URL.createObjectURL(new Blob(recordedChunks));
      downloadLink.download = 'acetest.wav';
    });

    mediaRecorder.start();
  };

  navigator.mediaDevices.getUserMedia({ audio: true, video: false })
      .then(handleSuccess);

</script>
    <form method=post enctype=multipart/form-data>
      <p>
         <input type="file" accept="audio/*;capture=microphone" name="audio">
         <input type="submit" value="Upload">
      </p>
    </form>
    '''
if __name__ == "__main__":
    app.run(debug=True)
