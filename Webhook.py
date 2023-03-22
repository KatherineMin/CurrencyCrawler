from flask import Flask, request
from CRUD import InputProcessing

app = Flask(__name__)


@app.route("/webhook", methods=['POST'])
def handle_webhook():
    if request.method == 'POST':
        data = request.json
        InputProcessing.process_webhook_data(data)
        print(data)

        return "Hello World"


if __name__ == "__main__":
    app.run(port=4041, debug=True)
