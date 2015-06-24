from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib

from gcm import GCM
import jinja2
import moment
import pymongo

from restriccion_scl import CONFIG


def send_to_email_addresses(emails_list, data):
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

def send_to_android_devices(device_list, data):
    if len(device_list or []) == 0 or (data or {}) == {}:
        return False

    mongo_client = pymongo.MongoClient(**CONFIG['pymongo']['client'])
    mongo_db = mongo_client[CONFIG['pymongo']['database']]

    gcm = GCM(CONFIG['notifications']['gcm']['api_key'])
    response = gcm.json_request(registration_ids=device_list, data=data)

    # Delete not registered or invalid devices
    if 'errors' in response:
        device_ids = response['errors'].get('NotRegistered', [])
        device_ids += response['errors'].get('InvalidRegistration', [])
        mongo_db.devices.delete_many({'tipo': 'android', 'id': {'$in': device_ids}})

    current_datetime = moment.now().isoformat()

    # Delete old device IDs
    if 'canonical' in response:
        old_ids = []
        canonical_ids = []

        for old_id, canonical_id in response['canonical'].items():
            old_ids.append(old_id)
            canonical_ids.append(canonical_id)

        mongo_db.devices.delete_many({'tipo': 'android', 'id': {'$in': old_ids}})

        for id_ in canonical_ids:
            row = mongo_db.devices.find_one({'tipo': 'android', 'id': id_})

            if row is None:
                mongo_db.devices.insert_one({'tipo': 'android', 'id': id_, 'fecha_registro': current_datetime})

    return True
