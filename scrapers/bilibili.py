import requests
import json
import os

class BilibiliScraper:
    def __init__(self):
        self.session = requests.Session()
        self.cookie_file = 'bilibili_cookies.json'
        self.load_cookies()

    def load_cookies(self):
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'r') as f:
                cookies = json.load(f)
                self.session.cookies.update(cookies)
                if self.check_login():
                    return True
        return False

    def save_cookies(self):
        with open(self.cookie_file, 'w') as f:
            json.dump(self.session.cookies.get_dict(), f)

    def login(self, username, password):
        login_url = 'https://passport.bilibili.com/x/passport-login/web/login'
        login_data = {
            'username': username,
            'password': password,
            'keep': 'true'
        }
        response = self.session.post(login_url, data=login_data)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                success = True
                self.save_cookies()
                return success
        return False

    def check_login(self):
        check_url = 'https://api.bilibili.com/x/web-interface/nav'
        response = self.session.get(check_url)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                return True
        return False

    def get_personal_recommendations(self):
        rec_url = 'https://api.bilibili.com/x/web-interface/index/top/rcmd'
        response = self.session.get(rec_url)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                return data['data']['item']
        return []

    def get_popular_videos(self):
        pop_url = 'https://api.bilibili.com/x/web-interface/popular'
        response = self.session.get(pop_url)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                return data['data']['list']
        return []
