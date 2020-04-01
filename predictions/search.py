from django.db import models
from django.http import HttpResponse
from django.views import generic
from django.test import TestCase
from bs4 import BeautifulSoup
from operator import itemgetter
import requests
import re


# Create your models here.

# ターゲット
target = ['japan_post', 'sagawa', 'kuroneko', 'seino', 'nittsu', 'fukutsu']
"""
日本郵政
https://trackings.post.japanpost.jp/services/srv/search/direct?reqCodeNo1=39447460371
佐川
http://k2k.sagawa-exp.co.jp/cgi-bin/mall.mmcgi?oku01=355715379191
クロネコ
http://jizen.kuronekoyamato.co.jp/jizen/servlet/crjz.b.NQ0010?id=111111111111
西濃運輸
http://track.seino.co.jp/kamotsu/KamotsuPrintServlet?ACTION=LIST&GNPNO1=1111111111
日通ペリカン便　（日本通運）
https://lp-trace.nittsu.co.jp/web/webarpaa702.srv?LANG=JP&officeselect2=&denpyoNo1=
福山通運
https://corp.fukutsu.co.jp/situation/tracking_no_hunt/
china post
https://www.trackingmore.com/china-post-tracking/ja.html?number=LO830234377CN

"""


class Craw_page(models.Model):
    # 検索サイトのURL登録
    def __init__(self, track_num):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.track_num = track_num
        self.urls = {
            target[0]: f'https://trackings.post.japanpost.jp/services/srv/search/direct?reqCodeNo1={track_num}',
            # クロネコだけpost
            target[1]: f'http://k2k.sagawa-exp.co.jp/cgi-bin/mall.mmcgi?oku01={track_num}',
            target[2]: f'http://toi.kuronekoyamato.co.jp/cgi-bin/tneko',
            target[3]: f'http://track.seino.co.jp/kamotsu/KamotsuPrintServlet?ACTION=LIST&GNPNO1={track_num}',
            target[4]: f'https://lp-trace.nittsu.co.jp/web/webarpaa702.srv?LANG=JP&officeselect2=&denpyoNo1={track_num}',
            target[5]: f'https://corp.fukutsu.co.jp/situation/tracking_no_hunt/{track_num}',
        }

    def get_text(self):
        text_list = {}
        for url in self.urls:
            if url == 'kuroneko':
                settion_info = {
                    "number00": "1",  # 詳細ボタンをオン
                    "number01": f'{self.track_num}',  # 番号入力
                }
                html = requests.session().post(
                    self.urls[url], data=settion_info)
            else:
                html = requests.get(self.urls[url], headers=self.headers)
            text = BeautifulSoup(html.content, "html.parser")
            text_list.setdefault(url, text)
        return text_list


class Scrape_page(models.Model):
    def parse_tag(self, text_list):  # 取得タグ
        track_tag = {
            target[0]: ["tableType01 txt_c m_b5", "履歴情報"],
            target[1]: "ichiran-bg ichiran-bg-msrc2",
            target[2]: "meisai",
            target[3]: "base clear-both",
            target[4]: "listtabale",
            target[5]: "table01 formtable",
        }
        judge_word = {  # 見つからなかった時の単語
            target[0]: "見つかりません",
            target[1]: "お確かめ",
            target[2]: "誤り",
            # target[3]: "",  # 西濃はエラーメッセージなし
            target[4]: "存在しません",
            target[5]: ["ありません", "半角数字"],
        }

        res_scrape = {}
        scrape_text = []
        for carriers in target:
            try:
                if type(track_tag[carriers]) == list:  # サマリーつきかどうか
                    # サマリーで検索
                    parse = text_list[carriers].select(
                        f"[summary={track_tag[carriers][1]}]")
                    if parse == []:  # ダメならclassで検索
                        parse = text_list[carriers].find_all(
                            class_=track_tag[carriers][0])
                else:
                    parse = text_list[carriers].find(
                        class_=track_tag[carriers])

                if type(parse) == list:
                    for p in parse:
                        scrape_text.extend(p.get_text().split("\n"))  # 改行でリスト化
                else:
                    scrape_text = parse.get_text().split("\n")  # 改行でリスト化

                for _i in range(2):  # タブとか排除
                    scrape_text = [t.strip('\t\r ')
                                   for t in scrape_text if t != '']
                    # 取り除けないやつを個別に消す
                    scrape_text = [t.replace('\u3000', '').replace('\xa0', '')
                                   for t in scrape_text if t != '']

                if carriers == 'seino':  # 西濃の場合、項目3以下は結果無し
                    judge = [True if len(scrape_text) < 5 else False]
                elif carriers == 'seino':
                    judge = [bool(i) for i in scrape_text
                             if judge_word[carriers][0] in i]
                    judge = [bool(i) for i in scrape_text
                             if judge_word[carriers][1] in i]
                elif len(scrape_text) < 5:  # 項目4未満は結果なし
                    judge = True
                else:  # エラーメッセージを含んだらTrue
                    judge = [bool(i) for i in scrape_text
                             if judge_word[carriers] in i]
                if True in judge:
                    res_scrape.setdefault(carriers, ['該当なし'])
                else:
                    res_scrape.setdefault(carriers, scrape_text)
            except:  # エラーは全部無し
                res_scrape.setdefault(carriers, ['該当なし'])
        return res_scrape


def sort_dict(track_d, num):
    tmp_odd = []
    tmp_even = []
    for i in range(1, num, 2):
        tmp_odd.append(track_d[i])
        tmp_even.append(track_d[i+1])
    len_odd = len(tmp_odd)
    for i in range(1, num):
        if i < len_odd+1:
            track_d[i] = tmp_odd[i-1]
        else:
            track_d[i] = tmp_even[(i - 1) - len_odd]
    return track_d


def scraping(track_num):
    track_detail = {}
    # 追跡番号整形はviewで
    # track_num = jaconv.z2h(track_num, digit=True, ascii=True)  # 全角を半角に
    # track_num = re.sub("\\D", "", track_num)  # 数字以外を消す

    craw_page = Craw_page(track_num)
    text = craw_page.get_text()  # テキスト取得
    urls = craw_page.urls  # 各URL

    parse = Scrape_page()
    res_scrape = parse.parse_tag(text)
    # print(res_scrape)  #各社+詳細のdict

    for carriers in target:  # URLを先頭に追加
        res_scrape[carriers].insert(0, urls[carriers])
    track_detail.update(res_scrape)

    # 佐川と福山通運だけ縦並びなので並び順を修正
    num_sagawa = len(track_detail['sagawa']) - 1
    num_fukutsu = len(track_detail['fukutsu']) - 1

    if num_sagawa - 1:
        track_detail['sagawa'] = sort_dict(track_detail['sagawa'], num_sagawa)
    elif num_fukutsu-1:
        track_detail['fukutsu'] = sort_dict(
            track_detail['fukutsu'], num_sagawa)
    return track_detail
