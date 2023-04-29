#!/usr/bin/python3
# -*- coding: utf8 -*-
"""
说明: 环境变量`KOY_EB`账号密码`-`分割，多账户用&隔开[例如：aaa-bbb&ccc-ddd]
cron: 20 9 */7 * *
new Env('koyeb-自动登陆');
"""
import json
import requests
import os, random
import time, datetime
try:
    from sendNotify import send
except:
    def send(*args):
        print("未找到通知文件sendNotify.py不启用通知！")

List = []
session = requests.Session()


# 内置Python环境变量[纯Python环境可启用]
#os.environ['KOY_EB'] = "aaa-bbb"

def get_time_stamp(result):
    utct_date = datetime.datetime.strptime(result, "%Y-%m-%dT%H:%M:%S.%f%z")
    local_date = utct_date + datetime.timedelta(hours=8)
    local_date_srt = datetime.datetime.strftime(local_date, "%Y-%m-%d %H:%M:%S")
    return local_date_srt

def auto_living(token):
    # 获取账户应用信息
    list_url = 'https://app.koyeb.com/v1/apps?limit=100'
    list_head = {
        'authorization': f'Bearer {token}',
        'cookie': f'accessToken={token}',
        'content-type': 'application/json',
        'referer': 'https://app.koyeb.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; PBEM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.52 Mobile Safari/537.36'
    }
    res_list = session.get(list_url, headers=list_head)
    if res_list.status_code == 200:
        list_date = res_list.json()
        if len(list_date.get("apps")) > 0:
            for i in range(len(list_date.get("apps"))):
                stop_url = f"https://app.koyeb.com/v1/apps/{list_date.get('apps')[i]['id']}/pause"  # 暂停api
                run_url = f"https://app.koyeb.com/v1/apps/{list_date.get('apps')[i]['id']}/resume"  # 启动api
                ac_head = {
                    'authorization': f'Bearer {token}',
                    'content-type': 'application/json',
                    'origin': 'https://app.koyeb.com',
                    'referer': f"https://app.koyeb.com/apps/{list_date.get('apps')[i]['id']}/settings/danger-zone",
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; PBEM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.52 Mobile Safari/537.36'
                }
                if list_date.get('apps')[i]['status'].lower() == "healthy":
                    List.append(f"{list_date.get('apps')[i]['name']} 应用运行正常！！！")
                elif list_date.get('apps')[i]['status'].lower() == "paused":
                    List.append(f"{list_date.get('apps')[i]['name']} 应用已暂停运行！！！")
                    res_run = session.post(run_url, headers=ac_head)
                    if res_run.status_code == 200:
                        List.append(f"启动命令已发送，应用将在3分钟后恢复正常！！！")
                    else:
                        List.append(f"启动命令发送出错，请检查url！！！")
                elif list_date.get('apps')[i]['status'].lower() == "resuming":
                    List.append(f"{list_date.get('apps')[i]['name']} 应用正在启动中！！！")
                else:
                    List.append(f"{list_date.get('apps')[i]['name']} 应用运行出错！！！")
                    res_stop = session.post(stop_url, headers=ac_head)
                    if res_stop.status_code == 200:
                        List.append(f"暂停命令已发送，等待1分钟后发送启动命令")
                    else:
                        List.append(f"暂停命令发送出错，请检查url！！！")
                    time.sleep(60)
                    res_run = session.post(run_url, headers=ac_head)
                    if res_run.status_code == 200:
                        List.append(f"启动命令已发送，应用将在3分钟后恢复正常！！！")
                    else:
                        List.append(f"启动命令发送出错，请检查url！！！")
        else:
            List.append(f"当前账户未创建实例应用！！！")
    else:
        List.append(f"获取账户应用信息出错，请检查url！！！")
        print(res_list.text)

def login(usr, pwd):
    login_url = 'https://app.koyeb.com/v1/account/login'
    headers = {
        'origin': 'https://app.koyeb.com',
        'referer': 'https://app.koyeb.com/auth/signin',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; PBEM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.52 Mobile Safari/537.36'
    }
    data = {
        'email': usr,
        'password': pwd
    }
    res = session.post(login_url, headers=headers, data=json.dumps(data))
    if res.status_code == 200:
        status = res.json()
        token = status.get('token').get('id')
        check_url = 'https://app.koyeb.com/v1/account/profile'
        check_head = {
            'authorization': f'Bearer {token}',
            'referer': 'https://app.koyeb.com/auth/signin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; PBEM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.52 Mobile Safari/537.36'

        }
        resp = session.get(check_url, headers=check_head)
        if resp.status_code == 200:
            info = resp.json()
            List.append(f"账号`{info.get('user').get('name')}`登陆成功")
            List.append(f"ID：{info.get('user').get('id')}")
            List.append(f"注册日期：{get_time_stamp(info.get('user').get('created_at'))}")
            lastlogin_url = 'https://app.koyeb.com/v1/activities?offset=0&limit=20'
            lastlogin_head = {
                'authorization': f'Bearer {token}',
                'referer': 'https://app.koyeb.com/activity',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; PBEM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.52 Mobile Safari/537.36'

            }
            time.sleep(7)
            resg = session.get(lastlogin_url, headers=lastlogin_head)
            if resg.status_code == 200:
                lastlogin = resg.json()
                j = 0
                for i in range(len(lastlogin.get('activities'))):
                    if lastlogin.get('activities')[i].get('object').get('name') == "console" and j < 2:
                        if lastlogin.get('count') > 1 and j == 1:
                            List.append(f"上次登录日期：{get_time_stamp(lastlogin.get('activities')[i].get('created_at'))}")
                        else:
                            List.append(f"当前登录日期：{get_time_stamp(lastlogin.get('activities')[i].get('created_at'))}")
                        j += 1
            else:
                print(resg.text)
        else:
            print(resp.text)
        # 自动保活应用
        auto_living(token)
    else:
        List.append('账号登陆失败: 账号或密码错误')
        List.append(res.text)


if __name__ == '__main__':
    delay_sec = random.randint(1,50)
    List.append(f'随机延时{delay_sec}s')
    time.sleep(delay_sec)
    i = 0
    if 'KOY_EB' in os.environ:
        users = os.environ['KOY_EB'].split('&')
        for x in users:
            i += 1
            name, pwd = x.split('-')
            List.append(f'===> [账号{str(i)}]Start <===')
            login(name, pwd)
            List.append(f'===> [账号{str(i)}]End <===\n')
            time.sleep(1)
        tt = '\n'.join(List)
        print(tt)
        send('koyeb', tt)
    else:
        print('未配置环境变量')
        send('koyeb', '未配置环境变量')
