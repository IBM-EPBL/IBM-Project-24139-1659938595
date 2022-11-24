import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# from_address we pass to our Mail object, edit with your name
FROM_EMAIL = 'from@email.com'


def SendEmail(to_email):
    """ Send an email to the provided email addresses
    :param to_email = email to be sent to
    :returns API response code
    :raises Exception e: raises an exception """
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject='A Test from SendGrid!',
        html_content='<strong>Hello.This is test mail from SendGrid.')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        code, body, headers = response.status_code, response.body, response.headers
        print(f"Response Code: {code} ")
        print(f"Response Body: {body} ")
        print(f"Response Headers: {headers} ")
        print("Message Sent!")
    except Exception as e:
        print("Error: {0}".format(e))
    return str(response.status_code)


if _name_ == "_main_":
    SendEmail(to_email=input("to@email.com"))
