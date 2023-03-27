import SecretKeys
from CRUD import UpdateWorkSheets

from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = SecretKeys.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = SecretKeys.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['TESTING'] = False
# app.config['MAIL_DEBUG'] = True

mail = Mail(app)

recipient_df = UpdateWorkSheets.email_recipients()

@app.route("/send_email")
def index():
    if len(recipient_df) > 0:
        for i, row in recipient_df.iterrows():
            msg = Message(
                subject=f"Good News! {row['currency_from']} to {row['currency_to']} exchange rate has reached {row['fx_rate']}.",
                recipients=[f"{row['user_email']}"],
                body=f"""
                    Hello,
                    
                    
                    Thanks for using Exchange Rate Alert app.
                    
                    We have a good news for you today that the {row['currency_from']} to {row['currency_to']} exchange rate has reached {row['fx_rate']}.
                    
                    The rate {row['fx_rate']} may be not exactly the same as the rate of your interest, {row['threshold']}, that you provided on {row['last_edited_time'][:10]}.
                    
                    But we consider {row['fx_rate']} is close enough to notify you as the error range of two rates is equal to or less than 0.001. 
                    
                    We hope you find this email useful.
                    
                    Cheers,
                    
                    Katherine Min
                    
                    * Your feedbacks are essential to improve our app. Please contact at {SecretKeys.MAIL_USERNAME} or reply to this email is you'd like to give any feedbacks.
                """,
                sender=SecretKeys.MAIL_USERNAME
            )

            mail.send(msg)

        return 'Email Sent'

    else:
        return 'No recipient was captured.'


if __name__ == '__main__':
    app.run(port=4999, debug=True)
