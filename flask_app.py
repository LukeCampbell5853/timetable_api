from flask import Flask, request, jsonify
import edumate_lib

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def api():
    auth = request.headers.get("auth")
    edu_auth = request.headers.get("edumate_auth")
    num = request.headers.get("num")

    if auth == "rfvjkswer6789":
        timetable = edumate_lib.get_timetable(edu_auth,int(num))
        return(jsonify(timetable))
    else:
        return("invalid login")

if __name__ == "__main__":
    app.run(debug=True)