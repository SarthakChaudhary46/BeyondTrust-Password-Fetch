# This library is maintained by @Sarthak.chaudhary1@cloud.com
# To retrieve a password using the username, use: "BT.secretname"
# To retrieve a password using the secret ID, use: "BT.secretid" 
# Include the appropriate call in your script after importing the library.

import os
import http.client
import json
import requests
import urllib3
import base64

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Constants
BASE_URL = os.environ.get('BT_URL') or os.environ.get('BT_BASE_URL')
AUTH_KEY =  os.environ.get('BT_CREDS_AUTHKEY') or os.environ.get('BT_AUTH_KEY')
RUNAS = os.environ.get('BT_CREDS_Username') or os.environ.get('Username')
SYSTEM_NAME = 'bt-local'

# API URLs
SIGNIN_URL = "/BeyondTrust/api/public/v3/Auth/SignAppIn"
SIGNOUT_URL = "/BeyondTrust/api/public/v3/Auth/Signout"
SECRETS_ID_URL = '/BeyondTrust/api/public/v3/Secrets-Safe/Secrets/{secret_id}'
FILE_DETAILS_URL = '/BeyondTrust/api/public/v3/Secrets-Safe/Secrets/{secret_id}/file'
ATTACHMENT_URL = '/BeyondTrust/api/public/v3/Secrets-Safe/Secrets/{secret_id}/file/download'

def secretid(secret_id):
    auth_key = get_auth_key()
    session_cookie = sign_in(BASE_URL, SIGNIN_URL, auth_key, RUNAS)
    try:
        result = retrieval(BASE_URL, SECRETS_ID_URL, FILE_DETAILS_URL, ATTACHMENT_URL, secret_id, session_cookie)
        return result
    finally:
        sign_out(BASE_URL, SIGNOUT_URL, session_cookie)

def secretname(secret_name):
    auth_key = get_auth_key()
    base_url = f"https://{BASE_URL}/BeyondTrust/api/public/v3/"
    headers = { 'Authorization': f"PS-Auth key={auth_key}; runas={RUNAS}" }

    session = pws_sign_in(base_url, headers)
    try:
        managed_account = get_managed_account(base_url, headers, session, secret_name)
        request_id = request_credentials(base_url, headers, session, managed_account['SystemId'], managed_account['AccountId'], 1)
        credentials = get_credentials(base_url, headers, session, request_id)
        return credentials
    finally:
        checkin_credentials(base_url, headers, session, request_id, "No longer needed")
        sign_out_sn(base_url, headers, session)

def get_auth_key():
    if AUTH_KEY:
        return AUTH_KEY
    path = os.path.join(os.path.expanduser("~"), ".beyondtrust")
    if not os.path.exists(path):
        raise FileNotFoundError("Auth key file does not exist")
    with open(path, 'r') as f:
        return f.read().strip()

def sign_in(base_url, signin_url, auth_key, runas):
    conn = http.client.HTTPSConnection(base_url)
    headers = { 'Authorization': f"PS-Auth key={auth_key}; runas={runas}" }
    conn.request("POST", signin_url, "", headers)
    res = conn.getresponse()
    if res.status != 200:
        raise RuntimeError(f"Sign-in failed with status {res.status}")
    return res.getheader('Set-Cookie')

def sign_out(base_url, signout_url, session_cookie):
    conn = http.client.HTTPSConnection(base_url)
    headers = { 'Cookie': session_cookie, 'Content-Type': 'application/json' }
    conn.request("POST", signout_url, "", headers)
    res = conn.getresponse()
    if res.status != 200:
        raise RuntimeError(f"Sign-out failed with status {res.status}")

def normalize(value):
    if isinstance(value, str) and value.lower() == "null":
        return None
    return value or None


def retrieval(base_url, secrets_id_url, file_details_url, attachment_url, secret_id, session_cookie):
    secret = get_secrets(base_url, session_cookie, secrets_id_url, secret_id)

    # Case 1: File attachment secret
    if secret.get('FileName'):
        data = get_attachment(base_url, attachment_url, secret_id, session_cookie)
        decoded = data.decode('utf-8').strip()
        if decoded.startswith('{'):
            try:
                parsed = json.loads(decoded)
                return parsed.get("password") or parsed  # return only password if available
            except json.JSONDecodeError:
                return decoded  
        return decoded  

    # Case 2: Non-file-based secret (base64 or plain string)
    raw_password = secret.get('Password', '')

    try:
        decoded_password = base64.b64decode(raw_password).decode('utf-8')
    except Exception:
        decoded_password = raw_password  

    return decoded_password


def get_attachment(base_url, attachment_url, secret_id, session_cookie):
    conn = http.client.HTTPSConnection(base_url)
    headers = { 'Cookie': session_cookie, 'Content-Type': 'application/json' }
    conn.request("GET", attachment_url.format(secret_id=secret_id), headers)
    res = conn.getresponse()
    if res.status != 200:
        raise RuntimeError(f"Failed to get attachment with status {res.status}")
    return res.read()

def get_secrets(base_url, session_cookie, secrets_id_url, secret_id):
    conn = http.client.HTTPSConnection(base_url)
    headers = { 'Cookie': session_cookie, 'Content-Type': 'application/json' }
    conn.request("GET", secrets_id_url.format(secret_id=secret_id), headers=headers)
    res = conn.getresponse()
    if res.status != 200:
        raise RuntimeError(f"Failed to get secrets with status {res.status}")
    return json.loads(res.read().decode("utf-8"))

def pws_sign_in(base_url, headers):
    response = requests.post(f"{base_url}Auth/SignAppIn", headers=headers, verify=False)
    response.raise_for_status()
    return response.cookies

def get_managed_account(base_url, headers, session, account_name):
    response = requests.get(
        f"{base_url}ManagedAccounts?systemName={SYSTEM_NAME}&accountName={account_name}",
        headers=headers, cookies=session, verify=False
    )
    response.raise_for_status()
    return response.json()

def request_credentials(base_url, headers, session, system_id, account_id, duration_minutes):
    data = { "SystemId": system_id, "AccountId": account_id, "DurationMinutes": duration_minutes }
    response = requests.post(f"{base_url}Requests", headers=headers, json=data, cookies=session, verify=False)
    response.raise_for_status()
    return response.json()

def get_credentials(base_url, headers, session, request_id):
    response = requests.get(f"{base_url}Credentials/{request_id}", headers=headers, cookies=session, verify=False)
    response.raise_for_status()
    return response.json()

def checkin_credentials(base_url, headers, session, request_id, reason):
    data = { "Reason": reason }
    response = requests.put(f"{base_url}Requests/{request_id}/Checkin", headers=headers, json=data, cookies=session, verify=False)
    response.raise_for_status()

def sign_out_sn(base_url, headers, session):
    response = requests.post(f"{base_url}Auth/Signout", headers=headers, cookies=session, verify=False)
    response.raise_for_status()
