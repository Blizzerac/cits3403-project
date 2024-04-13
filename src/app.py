# Imports
from flash import *

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def home():
    return render_template("index.html")


# Runs flask if not script not imported
if __name__ == "__main__":
    app.run(debug=True)