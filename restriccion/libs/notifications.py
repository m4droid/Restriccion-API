from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib

from gcm import GCM
import jinja2

from restriccion import CONFIG


def send_to_email_addresses(emails_list, data):
    if not CONFIG['notifications'].get('email', {}).get('enabled', False):
        return []

    if len(emails_list or []) == 0 or (data or {}) == {}:
        return []

    templates_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../../templates'
    )

    templates_loader = jinja2.FileSystemLoader(searchpath=templates_path)
    templates_env = jinja2.Environment(loader=templates_loader)

    template = templates_env.get_template(CONFIG['notifications']['email']['template'])

    login_info = CONFIG['notifications']['email']['server'].get('login')

    sent_emails = []

    service = smtplib.SMTP(*CONFIG['notifications']['email']['server']['host'])
    service.starttls()
    service.ehlo()

    if login_info is not None:
        service.login(*login_info)

    for email_to in emails_list:
        new_data = dict(data)
        new_data['email_to'] = email_to
        html = template.render(**data)

        email_from = CONFIG['notifications']['email']['from']

        msg = MIMEMultipart('alternative')
        msg['Subject'] = CONFIG['notifications']['email']['subject']
        msg['From'] = email_from
        msg['To'] = email_to

        part = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
        msg.attach(part)

        try:
            service.sendmail(email_from, email_to, msg.as_string())
            sent_emails.append(email_to)
        except:
            pass
    service.quit()

    return sent_emails


def send_to_gcm(device_list, data, collapse_key=None, ttl=43200):
    if len(device_list or []) == 0 or (data or {}) == {}:
        return ([], [])

    gcm = GCM(CONFIG['notifications']['gcm']['api_key'])

    kargs = {
        'registration_ids': device_list,
        'data': data,
        'time_to_live': ttl
    }

    if collapse_key is not None:
        kargs['collapse_key'] = collapse_key

    response = gcm.json_request(**kargs)

    devices_ok = []
    devices_to_remove = []

    # Delete not registered or invalid devices
    if 'errors' in response:
        devices_to_remove = response['errors'].get('NotRegistered', [])
        devices_to_remove += response['errors'].get('InvalidRegistration', [])

    if 'canonical' in response:
        for old_id, canonical_id in response['canonical'].items():
            devices_ok.append(canonical_id)
            devices_to_remove.append(old_id)

    return (devices_ok, devices_to_remove)
