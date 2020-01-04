# -*- coding: utf-8 -*-
import curses
import csv
from math import ceil

ROWS_PER_PAGE = 20

ENTER = ord( "\n" )
ESC = 27
DOWN = curses.KEY_DOWN
UP = curses.KEY_UP

class UI():

    def __init__(self, header, rows):
        super().__init__()
        self.header = header 
        self.rows = rows
        # 初期化
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        self.screen.keypad(1)
        # 色の設定
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        self.highlight_text = curses.color_pair(1) # 上の行のpair idを使う
        self.normal_text = curses.A_NORMAL
        self.screen.border(0)
        curses.curs_set(0)
        self.rows_per_page = ROWS_PER_PAGE
        self.total_rows = len(self.rows)
        # 各カラムの幅を記録
        self.widths = []
        # ボーダーの描画
        self.tavnit = '|'
        self.separator = '+'

        for index, title in enumerate(self.header):
            # カラムのタイトルと各行の最長値をカラムの幅にする
            max_col_length = max([len(row[index]) for row in self.rows])
            max_col_length = max(max_col_length, len(title))
            self.widths.append(max_col_length)

        # ボーダーの設定
        for w in self.widths:
            # こんな感じになる：
            # | %-2s | %-10s | %-10s | %-11s | %-9s | %-7s |
            self.tavnit += " %-"+"%ss |" % (w,)
            # こんな感じになる：
            # +----+------------+------------+-------------+-----------+---------+
            self.separator += '-'*w + '--+'

        self.total_pages = int(ceil(self.total_rows / self.rows_per_page))
        self.position = 1
        self.page = 1
        # 表示させるメッセージ
        self.msg = 'Page: {}/{}'.format(self.page, self.total_pages)

    def end(self):
        curses.endwin()

    def draw(self):
        self.screen.erase()
        # 一番上にメッセージを表示        
        self.screen.addstr(1, 2, self.msg, self.normal_text)
        # テーブルの上ボーダー
        self.screen.addstr(2, 2, self.separator, self.normal_text)
        # ヘッダーを表示        
        self.screen.addstr(3, 2, self.tavnit % tuple(self.header), self.normal_text)
        # ヘッダーと内容の間のボーダー
        self.screen.addstr(4, 2, self.separator, self.normal_text)
        # 毎行を描画
        row_start = 1 + (self.rows_per_page * (self.page - 1))
        row_end = self.rows_per_page + 1 + (self.rows_per_page * (self.page - 1))
        for i in range(row_start, row_end):
            if i >= self.total_rows + 1:
                break
            row_number = i + (self.rows_per_page * (self.page - 1))
            # ハイライトの行
            if (row_number == self.position + (self.rows_per_page * (self.page - 1))):
                color = self.highlight_text
            else:
                color = self.normal_text
            # 上にメッセージやボーダーなど4行あるので+4
            draw_number = i - (self.rows_per_page * (self.page - 1)) + 4 # 上にメッセージやボーダーなど4行あるので
            self.screen.addstr(draw_number , 2, self.tavnit % tuple(self.rows[i - 1]), color)
        # テーブルの下ボーダー, 上にメッセージやボーダーなど4行あるので+4
        bottom = min(row_end, self.total_rows + 1) - (self.rows_per_page * (self.page - 1)) + 4
        self.screen.addstr(bottom, 2, self.separator, self.normal_text)
        self.screen.refresh()

    def down(self):
        if self.page == self.total_pages:
            if self.position < self.total_rows:
                self.position += 1
        else:
            if self.position < self.rows_per_page + (self.rows_per_page * (self.page - 1)):
                self.position += 1
            else:
                self.page += 1
                self.position = 1 + (self.rows_per_page * (self.page - 1))
                self.msg = 'Page: {}/{}'.format(self.page, self.total_pages)
        self.draw()

    def up(self):
        if self.page == 1:
            if self.position > 1:
                self.position -= 1
        else:
            if self.position > (1 + (self.rows_per_page * (self.page - 1))):
                self.position -= 1
            else:
                self.page -= 1
                self.position = self.rows_per_page + (self.rows_per_page * (self.page - 1))
                self.msg = 'Page: {}/{}'.format(self.page, self.total_pages)
        self.draw()

    def esc(self):
        self.end()

    def enter(self):
        # ここにやりたい処理
        prefecture_id = self.rows[self.position - 1][0]
        prefecture = self.rows[self.position - 1][1]
        self.msg = 'Page: {}/{} ({} {} was selected.)' \
                .format(self.page, self.total_pages, prefecture_id, prefecture)
        self.draw()

    def loop(self):
        # 入力したキーを検知
        key = self.screen.getch()
        while 1:
            if key == ENTER:
                self.enter()
            elif key == ESC:
                self.esc()
                break
            elif key == DOWN:
                self.down()
            elif key == UP:
                self.up()
            key = self.screen.getch()

if __name__ == '__main__':
    with open('prefectures.csv') as f:
        reader = csv.reader(f)
        data = list(reader)
    header = data[0]
    rows = data[1:]
    
    ui = UI(header, rows)
    ui.draw()
    ui.loop()
