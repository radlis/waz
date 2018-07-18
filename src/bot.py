#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .user import User
import atexit
import datetime
import itertools
import json
import logging
import random
import signal
import sys
import time
import requests
from fake_useragent import UserAgent
import re

class Bot:

    url = 'https://www.instagram.com/'
    url_tag = 'https://www.instagram.com/explore/tags/%s/?__a=1'
    url_location = 'https://www.instagram.com/explore/locations/%s/?__a=1'
    url_likes = 'https://www.instagram.com/web/likes/%s/like/'
    url_unlike = 'https://www.instagram.com/web/likes/%s/unlike/'
    url_comment = 'https://www.instagram.com/web/comments/%s/add/'
    url_follow = 'https://www.instagram.com/web/friendships/%s/follow/'
    url_unfollow = 'https://www.instagram.com/web/friendships/%s/unfollow/'
    url_login = 'https://www.instagram.com/accounts/login/ajax/'
    url_logout = 'https://www.instagram.com/accounts/logout/'
    url_media_detail = 'https://www.instagram.com/p/%s/?__a=1'
    url_user_detail = 'https://www.instagram.com/%s/'
    api_user_detail = 'https://i.instagram.com/api/v1/users/%s/info/'

    user_agent = "" ""
    accept_language = 'en-GB,en;q=0.5'

    # If instagram ban you - query return 400 error.
    error_400 = 0
    # If you have 3 400 error in row - looks like you banned.
    error_400_to_ban = 3
    # If InstaBot think you are banned - going to sleep.
    ban_sleep_time = 2 * 60 * 60

    # All counter.
    current_user = 'hajka'
    current_index = 0
    current_id = 'abcds'

    # Log setting.
    logging.basicConfig(filename='errors.log', level=logging.INFO)
    log_file_path = ''
    log_file = 0
    log_mod = 0 # - Log mod: log_mod = 0 log to console, log_mod = 1 log to file,
    # Other.
    user_id = 0
    login_status = False
    by_location = False

    def __init__(self,
                 login,
                 password):

        fake_ua = UserAgent()
        self.user_agent = str(fake_ua.random)
        self.s = requests.Session()

        # convert login to lower
        self.user_login = login.lower()
        self.user_password = password

        now_time = datetime.datetime.now()
        log_string = 'bot started at %s:\n' % \
                     (now_time.strftime("%d.%m.%Y %H:%M"))
        self.write_log(log_string)

    def login(self):
        log_string = 'Trying to login as %s...\n' % (self.user_login)
        self.write_log(log_string)
        self.login_post = {
            'username': self.user_login,
            'password': self.user_password
        }

        self.s.headers.update({
            'Accept': '*/*',
            'Accept-Language': self.accept_language,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Host': 'www.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'User-Agent': self.user_agent,
            'X-Instagram-AJAX': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        })

        r = self.s.get(self.url)
        self.s.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
        time.sleep(5 * random.random())
        login = self.s.post(
            self.url_login, data=self.login_post, allow_redirects=True)
        self.s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrftoken = login.cookies['csrftoken']
        #ig_vw=1536; ig_pr=1.25; ig_vh=772;  ig_or=landscape-primary;
        self.s.cookies['ig_vw'] = '1536'
        self.s.cookies['ig_pr'] = '1.25'
        self.s.cookies['ig_vh'] = '772'
        self.s.cookies['ig_or'] = 'landscape-primary'
        time.sleep(5 * random.random())

        if login.status_code == 200:
            r = self.s.get(self.url)
            finder = r.text.find(self.user_login)
            if finder != -1:
                u = User()
                self.user_id = u.get_user_id_by_login(self.user_login)
                self.login_status = True
                log_string = '%s login success!' % (self.user_login)
                self.write_log(log_string)
            else:
                self.login_status = False
                self.write_log('Login error! Check your login data!')
        else:
            self.write_log('Login error! Connection error!')

    def logout(self):
        now_time = datetime.datetime.now()
        log_string = 'Logout'
        self.write_log(log_string)

        try:
            logout_post = {'csrfmiddlewaretoken': self.csrftoken}
            logout = self.s.post(self.url_logout, data=logout_post)
            self.write_log("Logout success!")
            self.login_status = False
        except:
            logging.exception("Logout error!")

    def write_log(self, log_text):
            """ Write log by print() or logger """

            if self.log_mod == 0:
                try:
                    now_time = datetime.datetime.now()
                    print(now_time.strftime("%d.%m.%Y_%H:%M")  + " " + log_text)
                except UnicodeEncodeError:
                    print("Your text has unicode problem!")
            elif self.log_mod == 1:
                # Create log_file if not exist.
                if self.log_file == 0:
                    self.log_file = 1
                    now_time = datetime.datetime.now()
                    self.log_full_path = '%s%s_%s.log' % (
                        self.log_file_path, self.user_login,
                        now_time.strftime("%d.%m.%Y_%H:%M"))
                    formatter = logging.Formatter('%(asctime)s - %(name)s '
                                                  '- %(message)s')
                    self.logger = logging.getLogger(self.user_login)
                    self.hdrl = logging.FileHandler(self.log_full_path, mode='w')
                    self.hdrl.setFormatter(formatter)
                    self.logger.setLevel(level=logging.INFO)
                    self.logger.addHandler(self.hdrl)
                # Log to log file.
                try:
                    self.logger.info(log_text)
                except UnicodeEncodeError:
                    print("Your text has unicode problem!")
