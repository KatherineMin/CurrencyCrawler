from apscheduler.schedulers.background import BackgroundScheduler

from CRUD.UpdateWorkSheets import email_recipients

from Webhook import app as webhook_app
from SendAlert import app as send_email_app


scheduler = BackgroundScheduler()
scheduler.add_job(
    func=email_recipients,
    trigger='cron',
    day_of_week='mon-fri',
    minute='0',
    id='get_email_recipients'
)

scheduler.start()


if __name__ == '__main__':
    webhook_app.run(port=4041, debug=True, threaded=True)
    send_email_app.run(port=4999, debug=True, threaded=True)



