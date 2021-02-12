from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import credentials

def send_email(name, dest, link):
    email_html = open('templates/email.html')
    email_body = email_html.read().format(name=name, link=link)
    
    message = Mail(
        from_email=credentials.Email,
        to_emails=dest,
        subject='HELP!!! HELP!!! HELP!!!',
        html_content=email_body)
    try:
        sg = SendGridAPIClient(credentials.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        pass
    
