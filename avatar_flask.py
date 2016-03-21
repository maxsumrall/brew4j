from avatar_generator import Avatar
from flask import Flask, make_response

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

@app.route("/avatar/<username>")
def avatar_for(username):
    avatar = Avatar.generate(128, username)
    headers = { 'Content-Type': 'image/png' }
    return make_response(avatar, 200, headers)

if __name__ == "__main__":
    app.run()

