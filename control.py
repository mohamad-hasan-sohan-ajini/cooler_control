import json

from flask import Flask, redirect, url_for, render_template, request

from cooler import Cooler

# globals
app = Flask(__name__)
config_file = "config.json"
inverse_logic = True
cooler = Cooler(
    pump_pin=21,
    slow_pin=20,
    speed_pin=16,
    inverse_logic=inverse_logic,
    config_file=config_file,
)


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "GET":
        return render_template("index.html", **cooler.__dict__)

    if request.method == "POST":
        cooler.control_mode = request.form["mode"]

        if request.form["mode"] == "automatic":
            # TODO: check rationality if thresholds
            try:
                cooler.min_threshold = float(request.form["min_threshold"])
                with open(config_file) as f:
                    config = json.load(f)
                config["min_threshold"] = cooler.min_threshold
                with open(config_file, "w") as f:
                    json.dump(config, f)
            except Exception as E:
                pass
            try:
                cooler.max_threshold = float(request.form["max_threshold"])
                with open(config_file) as f:
                    config = json.load(f)
                config["max_threshold"] = cooler.max_threshold
                with open(config_file, "w") as f:
                    json.dump(config, f)
            except Exception as E:
                pass
            cooler.set_speed(False)
            return redirect("/update")

        if request.form["mode"] == "manual":
            if "Pump" in request.form:
                cooler.set_pump(True)
            else:
                cooler.set_pump(False)
            if "Slow" in request.form:
                cooler.set_slow(True)
            else:
                cooler.set_slow(False)
            if "Speed" in request.form:
                cooler.set_speed(True)
            else:
                cooler.set_speed(False)
            return redirect("/update")

        return "not implemented!"


@app.route("/automatic.html")
def automatic():
    return render_template("automatic.html", **cooler.__dict__)


@app.route("/manual.html")
def manual():
    return render_template("manual.html", **cooler.__dict__)


@app.route("/update")
def update():
    cooler.update()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=8000)
