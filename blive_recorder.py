#!/usr/bin/env python3
# -*- encoding: utf-8

import sys
import time
import datetime
import requests


class BLive():
    def __init__(self, room_id):
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/59.0.3071.115 Safari/537.36 '
        }
        self.room_id = room_id
        self.session = requests.session()

    def get_room_info(self):
        data = {}
        room_info_url = 'https://api.live.bilibili.com/room/v1/Room/get_info'
        user_info_url = 'https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room'
        response = self.session.get(room_info_url, headers=self.headers, params={'room_id': self.room_id}, verify=False).json()
        if response['msg'] == 'ok':
            data['roomname'] = response['data']['title']
            data['status'] = response['data']['live_status'] == 1
        self.room_id = str(response['data']['room_id'])  # 解析完整 room_id
        return data

    def get_live_urls(self):
        live_urls = []
        url = 'https://api.live.bilibili.com/api/playurl'
        data = {
            'cid': self.room_id,
            'otype': 'json',
            'quality': 0,
            'platform': 'web'
        }
        durls = self.session.get(url, headers=self.headers, params=data, verify=False).json()
        for durl in durls['durl']:
            live_urls.append(durl['url'])
        return live_urls


def record(room_id, length, interval):
    b = BLive(room_id)
    while True:
        room_info = b.get_room_info()
        if room_info['status']:
            break
        else:
            print(room_id, 'PENDING')
        time.sleep(interval)

    live_url = b.get_live_urls()[0]
    print("RECORDING...")
    start = time.time()
    end = start + int(length)
    resp = requests.get(live_url, stream=True)
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + '.flv'
    with open(filename, "wb") as f:
        for chunk in resp.iter_content(chunk_size=512):
            f.write(chunk) if chunk else None
            if time.time() > end:
                print("DONE!")
                break

if __name__ == '__main__':
    record(sys.argv[1], sys.argv[2], sys.argv[3])




