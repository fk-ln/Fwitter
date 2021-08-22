import tkinter as tk
from tkinter import Label, filedialog
import tweepy
import config
import traceback
import tkinter.font as f
import re
import time
import os
import webbrowser
import pyperclip
import requests
from selenium import webdriver

consumer_token = config.API_KEY
consumer_secret = config.API_KEY_SECRET
access_token = config.ACCESS_TOKEN
access_token_secret = config.ACCESS_TOKEN_SECRET
callback_url = 'https://twitter.com'

auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

iconfile = 'icon.ico'


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.title('Fwitter')  # ウィンドウタイトル
        master.geometry('600x520')  # ウィンドウサイズ
        self.file_name = ''
        master.iconbitmap(default=iconfile)
        self.font1 = f.Font(root=self.master, size=10)
        self.create_menubar()
        self.create_widgets()

    def create_menubar(self):
        self.menubar = tk.Menu(self.master)

        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='設定')
        self.filemenu.add_command(label='終了', command=self.master.quit)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label='ヘルプ')

        self.accountmenu = tk.Menu(self.menubar, tearoff=0)
        self.accountmenu.add_command(
            label='アカウントを切り換える', command=self.switch_account)

        self.menubar.add_cascade(label='ファイル', menu=self.filemenu)
        self.menubar.add_cascade(label='ヘルプ', menu=self.helpmenu)
        self.menubar.add_cascade(label='アカウント', menu=self.accountmenu)

        self.master.config(menu=self.menubar)

    def create_widgets(self):
        self.current_account_val = tk.StringVar()
        self.current_account_val.set(
            api.me().name+'(@'+api.me().screen_name+')でログイン中')
        self.current_account = Label(
            self.master, textvariable=self.current_account_val)
        self.current_account.grid(
            row=0, column=0, padx=10, pady=5, sticky=tk.W)

        # 送信用キーバインド
        self.master.bind('<Control-Return>', self.post_tweet)

        # 新規ツイートフレーム
        self.frame_post = tk.LabelFrame(
            self.master, text='新規ツイート', width=580, height=200)

        # ツイート本文入力ボックス
        self.post_text = tk.Text(
            self.frame_post, width=50, height=6, wrap=tk.CHAR, relief=tk.RIDGE)
        self.post_text.grid(row=0, rowspan=2, column=0, columnspan=5, padx=10, pady=20,
                            sticky=(tk.N, tk.S, tk.E, tk.W))

        # 画像添付ボタン
        self.img_button = tk.Button(
            self.frame_post, text='画像を添付', command=self.att_img)
        self.img_status_val = tk.StringVar()
        self.img_status_val.set('画像が選択されていません')
        self.img_status = tk.Label(
            self.frame_post, textvariable=self.img_status_val, width=60)
        self.img_status.grid(row=2, column=1, columnspan=5,
                             padx=10, pady=10, sticky=tk.W)
        self.img_button.grid(row=2, column=0, padx=10, pady=10)

        # 実況タグ1
        self.frame1 = tk.LabelFrame(self.frame_post, text="タグ1")
        self.tag1_val = tk.StringVar()
        self.tag1_val.set("")
        self.tag1 = tk.Entry(self.frame1, relief=tk.RIDGE,
                             textvariable=self.tag1_val)
        self.tag1.pack(padx=3, pady=3, side=tk.TOP)
        self.frame1.grid(row=3, column=0, columnspan=2,
                         padx=10, pady=10, sticky=(tk.W, tk.E))

        # 実況タグ2
        self.frame2 = tk.LabelFrame(self.frame_post, text="タグ2")
        self.tag2_val = tk.StringVar()
        self.tag2_val.set("")
        self.tag2 = tk.Entry(self.frame2, relief=tk.RIDGE,
                             textvariable=self.tag2_val)
        self.tag2.pack(padx=3, pady=3, side=tk.TOP)
        self.frame2.grid(row=3, column=2, columnspan=2, padx=10,
                         pady=10, sticky=(tk.W, tk.E))

        # 実況タグ3
        self.frame3 = tk.LabelFrame(self.frame_post, text="タグ3")
        self.tag3_val = tk.StringVar()
        self.tag3_val.set("")
        self.tag3 = tk.Entry(self.frame3, relief=tk.RIDGE,
                             textvariable=self.tag3_val)
        self.tag3.pack(padx=3, pady=3, side=tk.TOP)
        self.frame3.grid(row=3, column=4, padx=10,
                         columnspan=2, pady=10, sticky=(tk.W, tk.E))

        # ツイートボタン
        self.tweet_button_img = tk.PhotoImage(
            file='tweet_button.png').subsample(6, 6)
        self.post_button = tk.Button(
            self.frame_post, image=self.tweet_button_img, compound=tk.TOP, command=self.post_tweet, relief=tk.FLAT, borderwidth=0)
        self.post_button.grid(row=0, column=5, padx=20,
                              pady=5, sticky=(tk.W, tk.E))

        # ツイートステータス
        self.status_text = tk.StringVar()
        self.status_text.set("")
        self.status_label = tk.Label(
            self.frame_post, textvariable=self.status_text)
        self.status_label.grid(row=1, column=5, padx=10, pady=5)

        self.frame_post.grid(row=1, column=0, padx=10,
                             pady=10, sticky=(tk.E, tk.W))

        # テンプレートフレーム
        self.frame_template = tk.LabelFrame(
            self.master, text='テンプレート投稿', width=580)

        # テンプレ1
        self.temp1_label = tk.StringVar()
        self.temp1_label.set('1')
        self.temp1_body = tk.StringVar()
        self.temp1_body.set('テンプレート1')
        self.temp1_button = tk.Button(
            self.frame_template, textvariable=self.temp1_label, width=23, relief=tk.RIDGE, command=lambda: self.post_temp(self.temp1_body.get()))
        self.temp1_button.grid(
            row=0, column=0,  columnspan=4, padx=10, pady=10)

        # テンプレ2
        self.temp2_label = tk.StringVar()
        self.temp2_label.set('2')
        self.temp2_body = tk.StringVar()
        self.temp2_body.set('テンプレート2')
        self.temp2_button = tk.Button(
            self.frame_template, textvariable=self.temp2_label, width=23, relief=tk.RIDGE, command=lambda: self.post_temp(self.temp2_body.get()))
        self.temp2_button.grid(row=0, column=4, columnspan=4, padx=10, pady=10)

        # テンプレ3
        self.temp3_label = tk.StringVar()
        self.temp3_label.set("3")
        self.temp3_body = tk.StringVar()
        self.temp3_body.set("テンプレート3")
        self.temp3_button = tk.Button(
            self.frame_template, textvariable=self.temp3_label, width=23, relief=tk.RIDGE, command=lambda: self.post_temp(self.temp3_body.get()))
        self.temp3_button.grid(row=0, column=8, columnspan=4, padx=10, pady=10)

        # テンプレ編集
        self.option_list = ['テンプレートを選択', 'テンプレート1', 'テンプレート2', 'テンプレート3']

        self.selected_option = tk.StringVar()
        self.selected_option.set(self.option_list[0])
        self.options = tk.OptionMenu(
            self.frame_template, self.selected_option, *self.option_list, command=self.option_selected)
        self.options.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.label_name = tk.Label(self.frame_template, text='ラベル名')
        self.label_name.grid(row=1, column=3, columnspan=3, padx=10, pady=10)
        self.label_val = tk.StringVar()
        self.label_val.set('')
        self.label_entry = tk.Entry(
            self.frame_template, textvariable=self.label_val, width=40)
        self.label_entry.grid(row=1, column=6, columnspan=6, padx=10, pady=10)

        self.body_name = tk.Label(self.frame_template, text='テンプレート内容')
        self.body_name.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        self.body_val = tk.StringVar()
        self.body_val.set('')
        self.body_entry = tk.Entry(
            self.frame_template, textvariable=self.body_val, width=40)
        self.body_entry.grid(row=2, column=3, columnspan=7, padx=10, pady=10)
        self.save_button = tk.Button(
            self.frame_template, text='テンプレート上書き', command=self.save_temp)
        self.save_button.grid(row=2, column=10, columnspan=2, padx=10, pady=10)

        self.frame_template.grid(
            row=2, column=0, padx=10, pady=10)

    def option_selected(self, event=None):
        self.label_val.set('')
        self.body_val.set('')
        if self.selected_option.get() == 'テンプレート1':
            self.label_val.set(self.temp1_label.get())
            self.body_val.set(self.temp1_body.get())
        if self.selected_option.get() == 'テンプレート2':
            self.label_val.set(self.temp2_label.get())
            self.body_val.set(self.temp2_body.get())
        if self.selected_option.get() == 'テンプレート3':
            self.label_val.set(self.temp3_label.get())
            self.body_val.set(self.temp3_body.get())
        if self.selected_option.get() == 'テンプレートを選択':
            self.label_val.set('')
            self.body_val.set('')

    def save_temp(self, event=None):
        if self.selected_option.get() == 'テンプレート1':
            self.temp1_label.set(self.label_val.get())
            self.temp1_body.set(self.body_val.get())
            self.option_list[1] = self.label_val.get()
        if self.selected_option.get() == 'テンプレート2':
            self.temp2_label.set(self.label_val.get())
            self.temp2_body.set(self.body_val.get())
            self.option_list[2] = self.label_val.get()
        if self.selected_option.get() == 'テンプレート3':
            self.temp3_label.set(self.label_val.get())
            self.temp3_body.set(self.body_val.get())
            self.option_list[3] = self.label_val.get()
        if self.selected_option.get() == 'テンプレートを選択':
            pass

    def att_img(self, event=None):
        self.file_type = [('画像ファイル', '*.png;*.gif;*.jpg')]
        self.initial_dir = os.path.abspath(os.path.dirname(__file__))
        self.file_name = filedialog.askopenfilename(
            filetypes=self.file_type, initialdir=self.initial_dir)

        if len(self.file_name) == 0:
            self.img_status_val.set("画像が選択されていません。")
        else:
            self.img_status_val.set(self.file_name+'が選択されています')

    def post_temp(self, text):
        if 'テンプレート' not in text:
            try:
                api.update_status(text)
            except tweepy.TweepError as e:
                if e.reason == "[{'message': 'Rate limit exceeded', 'code': 88}]":
                    self.status_text.set("エラー；リクエスト上限に達しました。15分間待ってください")
                if e.reason == "[{'code': 187, 'message': 'Status is a duplicate.'}]":
                    self.status_text.set("エラー：ツイートが重複しています")
                else:
                    print(e.reason)
            else:
                self.status_text.set("ツイート成功")
        else:
            self.status_text.set('テンプレート内容を入力してください')

    def post_tweet(self, event=None):  # ツイート送信ボタン
        # タグが入力されてるとき本文に追加
        self.tweet = self.post_text.get('1.0', tk.END)+'\n'
        if self.tag1_val.get() != '':
            self.tweet = self.tweet+'#'+self.tag1_val.get()+' '
        if self.tag2_val.get() != '':
            self.tweet = self.tweet+'#'+self.tag2_val.get()+' '
        if self.tag3_val.get() != '':
            self.tweet = self.tweet+'#'+self.tag3_val.get()+' '

        if len(self.file_name) == 0:

            if not re.match('\s+', self.tweet):
                # ツイート送信
                try:
                    api.update_status(self.tweet)
                except tweepy.TweepError as e:
                    if e.reason == "[{'code': 88', message': 'Rate limit exceeded'}]":
                        self.status_text.set("エラー；リクエスト上限に達しました。15分間待ってください")
                    if e.reason == "[{'code': 187, 'message': 'Status is a duplicate.'}]":
                        self.status_text.set("エラー：ツイートが重複しています")
                    else:
                        self.status_text.set(e.reason)
                else:
                    self.post_text.delete("1.0", tk.END)
                    self.status_text.set("ツイート成功")

            else:
                self.status_text.set('本文が入力されていません')

        else:
            self.tweet = self.post_text.get('1.0', tk.END)+'\n'

            try:
                api.update_with_media(
                    status=self.tweet, filename=self.file_name)
            except tweepy.TweepError as e:
                if e.reason == "[{'message': 'Rate limit exceeded', 'code': 88}]":
                    self.status_text.set("エラー；リクエスト上限に達しました。15分間待ってください")
                if e.reason == "[{'code': 187, 'message': 'Status is a duplicate.'}]":
                    self.status_text.set("エラー：ツイートが重複しています")
            except Exception as e:
                print(e)
            else:
                self.post_text.delete("1.0", tk.END)
                self.status_text.set("画像付きツイート成功")

    def switch_account(self, event=None):
        self.base_url = 'https://api.twitter.com/'
        self.access_token_url = self.base_url + 'oauth/access_token'

        try:
            self.redirect_url = auth.get_authorization_url()
        except:
            print('エラー:リクエストトークンの取得に失敗しました')

        webbrowser.open(self.redirect_url)

        self.oauth_window = tk.Tk()
        self.oauth_window.geometry('300x150')
        self.oauth_window.title('アカウント切り替え')
        self.label_paste = tk.Label(
            self.oauth_window, text='ブラウザに遷移します。\n連携アプリ認証後のURLをコピーしたあと\n以下のボタンを押してください\n(クリップボードからtokenとvarifierを取得します)')
        self.label_paste.pack(padx=10, pady=10)
        self.callback_button = tk.Button(
            self.oauth_window, text='アカウントを切り換える', command=self.switch_button)
        self.callback_button.pack(padx=10, pady=10)
        self.current_account.grid(
            row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.oauth_window.mainloop()

    def switch_button(self, event=None):
        self.url = pyperclip.paste()
        list = self.url.split("=")

        oauth_token = (list[1].split("&"))[0]
        oauth_verifier = list[2]

        auth.request_token = {
            'oauth_token': oauth_token, 'oauth_token_secret': oauth_verifier}

        try:
            self.token = auth.get_access_token(oauth_verifier)
        except tweepy.TweepError:
            print('エラー:アクセストークンの取得に失敗しました')

        auth.set_access_token(self.token[0], self.token[1])
        api = tweepy.API(auth)

        self.oauth_window.destroy()

        self.current_account_val.set(
            api.me().name+'(@'+api.me().screen_name+')でログイン中')


def main():
    root = tk.Tk()
    app = App(master=root)
    app.mainloop()


if __name__ == '__main__':
    main()
