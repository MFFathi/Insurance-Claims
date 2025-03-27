from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None

    if request.method == "POST":
        injury = request.form.get("injury")
        earnings = request.form.get("earnings")
        expenses = request.form.get("expenses")
        prediction = "$6,700 (estimated settlement)"

        print("Form submitted:")
        print("Injury:", injury)
        print("Earnings:", earnings)
        print("Expenses:", expenses)

    return render_template("index.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
