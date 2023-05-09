# -*- encoding: utf-8 -*-
'''
Created on 2021/08/19
マークロウ(MarkLow)の編集ウィンドゥ
@author: sue-t
'''


from tkinter import Tk, Menu, Frame, Label, Text, Scrollbar, Button, \
        NONE, HORIZONTAL, VERTICAL, END, NORMAL, DISABLED, \
        filedialog, messagebox
import sys
import os
import re
import ply.lex as lex

import c
import d
import e
import ml_lex
from ml_yacc import create_parser
from ml_parse import *
import ml_yacc


# __version__ = 0.20  # マークロウ フォーマット変更
# __version__ = 0.21  # parseフォーマット変更
__version__ = 0.22  # 桁合わせ(#)を採用,parse読込失敗時,初期ファイルがない場合
                    # ﾌｧｲﾙ指定してオープン
# 挿入等のダイアログで半角入力などは、_の加工を行なう
# 整形テキスト等のリンク先をダブルクリックで開くようにする


# TODO Undo機能　ctrlEventに簡易なアンドゥを付けることは可能？

# TODO 色変更ダイアログ、HTML・MDでの色付け
# TODO キー操作でダイアログ表示したら、元ウィンドウが操作可能のままのようだ
# TODO 整形テキストのカラー印刷

# TODO IDの活用


class MlEditor(object):
    '''
    マークロウファイルの編集用のウィンドゥ
    '''

    def __init__(self):
        global text_tate, text_yoko
        self.text_height = text_tate
        self.text_width = text_yoko

        self.color_form = True
        self.color_html = False
        self.color_md = False

        self.undo_str = None

    def create_window(self):
        '''
        マークロウファイルの編集用のウィンドゥを作成する。

        Parameters
        ----------

        Returns
        -------
        root :
            Tkのルート。
        '''
        self.root = Tk()

        global window_tate, window_yoko
        window_size = "{}x{}".format(window_yoko, window_tate)
        self.root.geometry(window_size)

        self.create_menu()
        frame_form = self.create_frame_form()
        frame_low = self.create_frame_low()
        frame_form.grid(row=1, column=0)
        frame_low.grid(row=0, column=0)
        frame_button = self.create_frame_button()
        frame_button.grid(row=0, column=1, rowspan=2)
        set_title()
        return self.root

    def create_menu(self):
        menu_bar = Menu(self.root)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="新規", command=new)
        file_menu.add_separator()
        file_menu.add_command(label="読込", command=load_file)
        file_menu.add_command(label="保存", command=save_file)
#         file_menu.entryconfigure('保存', state = 'disabled')
        file_menu.add_command(label="名前を付けて保存", command=save_new)
        file_menu.add_separator()
        file_menu.add_command(label="全部を保存", command=save_full)
        file_menu.add_separator()
        file_menu.add_command(label="オリジナルテキストを保存", command=save_original)
        file_menu.add_command(label="プレーンテキストを保存", command=save_plain)
        file_menu.add_command(label="整形テキストを保存", command=save_form)
        file_menu.add_command(label="マークダウンを保存", command=save_markdown)
        file_menu.add_command(label="HTMLを保存", command=save_html)
        file_menu.add_separator()
        file_menu.add_command(label="parseと共に読込", command=load_low_parse)
        file_menu.add_command(label="parseと共に保存", command=save_low_parse)
#         file_menu.add_command(label="HTML経由のPDFを保存", command=save_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=shuryou)
        menu_bar.add_cascade(label="ファイル", menu=file_menu)

        copy_menu = Menu(menu_bar, tearoff=0)
        copy_menu.add_command(label="オリジナルテキスト", command=copy_original)
        copy_menu.add_command(label="プレーンテキスト", command=copy_plain)
        copy_menu.add_command(label="整形テキスト", command=copy_form)
        copy_menu.add_command(label="マークダウンテキスト", command=copy_markdown)
        copy_menu.add_command(label="HTMLテキスト", command=copy_html)
        copy_menu.add_command(label="マークロウテキスト", command=copy_marklow)
        menu_bar.add_cascade(label="コピー", menu=copy_menu)

        return_menu = Menu(menu_bar, tearoff=0)
        return_menu.add_command(label="改行全部", command=return_full)
        return_menu.add_separator()
        return_menu.add_command(label="。（句点）", command=return_kuten)
        return_menu.add_command(label="、（読点）", command=return_touten)
        return_menu.add_command(label="括弧前後", command=return_kakko)
        menu_bar.add_cascade(label="改行", menu=return_menu)

        init_menu = Menu(menu_bar, tearoff=0)
        init_menu.add_command(label="初期化全部", command=init_full)
        init_menu.add_separator()
        init_menu.add_command(label="半角英数字を囲う", command=init_alnum)
        init_menu.add_command(label="括弧内を非表示", command=init_hihyouji)
        init_menu.add_separator()
        init_menu.add_command(label="半角括弧を全角に", command=init_kakko)
        init_menu.add_command(label="半角空白を削除", command=init_kuhaku)
        menu_bar.add_cascade(label="初期化", menu=init_menu)

        # 変換（漢数字→全角数字、漢数字→半角数字、全角数字→半角数字、半角数字→全角数字）
        trans_menu = Menu(menu_bar, tearoff=0)
        trans_menu.add_command(label="半角数字を全角に", command=change_suuji)
        trans_menu.add_command(label="HTMLの空白を変換", command=init_html_kuhaku)
        menu_bar.add_cascade(label="変換", menu=trans_menu)

        # 設定（挿入などのID 〇以上、IDリストアップ）

        config_menu = Menu(menu_bar, tearoff=0)
        config_menu.add_command(label="テキストウィンドゥ", command=set_window_size)
        menu_bar.add_cascade(label="設定", menu=config_menu)

        self.root.config(menu=menu_bar)


    def create_frame_form(self):
        frame = Frame(self.root)
        Label(frame, text="整形テキスト").grid(row=0, column=0)
        self.entry_form = Text(frame,
                width=self.text_width, height=self.text_height, wrap=NONE)
#         self.entry_form.configure(font=("MS ゴシック", 12))
        global font_name, font_size
        self.entry_form.configure(font=(font_name, font_size))
        scrollbar_form_x = Scrollbar(frame, orient=HORIZONTAL,
                command=self.entry_form.xview)
        self.entry_form.configure(
                xscrollcommand=scrollbar_form_x.set)
        scrollbar_form_y = Scrollbar(frame, orient=VERTICAL,
                command=self.entry_form.yview)
        self.entry_form.configure(
                yscrollcommand=scrollbar_form_y.set)
        self.entry_form.grid(row=1, column=0)
        scrollbar_form_x.grid(row=2, column=0, sticky='ew')
        scrollbar_form_y.grid(row=1, column=1, sticky='ns')
        self.entry_form.configure(state=DISABLED)
        self.entry_form.tag_config('NORMAL', foreground="black")
#         global color_list
#         for color_item in color_list:
#             if color_item[0] == "強調":
#                 self.set_color('EMPHASIS', color_item)
#             elif color_item[0] == "挿入":
#                 self.set_color('INSERT', color_item)
#             elif color_item[0] == "取消線":
#                 self.set_color('HIDE', color_item)
#             elif color_item[0] == "読替":
#                 self.set_color('REPLACE', color_item)
#             elif color_item[0] == "読替２":
#                 self.set_color('REPLACE2', color_item)
#             elif color_item[0] == "定義":
#                 self.set_color('DEFINE', color_item)
#             elif color_item[0] == "定義２":
#                 self.set_color('DEFINE2', color_item)
#             elif color_item[0] == "参照":
#                 self.set_color('REFFER', color_item)
#             elif color_item[0] == "参照２":
#                 self.set_color('REFFER2', color_item)
#             elif color_item[0] == "当てはめ":
#                 self.set_color('APPLY', color_item)
#             elif color_item[0] == "当てはめ２":
#                 self.set_color('APPLY2', color_item)
        # ver.0.22 2021/10/07
        global color_dict
        for key, color_item in color_dict.items():
            if key == "強調":
                self.set_color('EMPHASIS', color_item)
            elif key == "挿入":
                self.set_color('INSERT', color_item)
            elif key == "取消線":
                self.set_color('HIDE', color_item)
            elif key == "読替":
                self.set_color('REPLACE', color_item)
            elif key == "読替２":
                self.set_color('REPLACE2', color_item)
            elif key == "定義":
                self.set_color('DEFINE', color_item)
            elif key == "定義２":
                self.set_color('DEFINE2', color_item)
            elif key == "参照":
                self.set_color('REFFER', color_item)
            elif key == "参照２":
                self.set_color('REFFER2', color_item)
            elif key == "当てはめ":
                self.set_color('APPLY', color_item)
            elif key == "当てはめ２":
                self.set_color('APPLY2', color_item)
        # ver0.22 2021/10/05
        self.entry_form.bind('<Button-3>', right_click_form)
        return frame

#     def set_color(self, tag, color_item):
# #         d.dprint(color_item)
#         if (color_item[1] != "#FFFFFF") \
#                 and (color_item[2] != "#FFFFFF"):
#             self.entry_form.tag_config(tag,
#                     foreground= color_item[1],
#                     background=color_item[2])
#         elif color_item[1] != "#FFFFFF":
#             self.entry_form.tag_config(tag,
#                     foreground= color_item[1])
#         elif color_item[2] != "#FFFFFF":
#             self.entry_form.tag_config(tag,
#                     background= color_item[2])
    # ver.0.22 2021/10/07
    def set_color(self, tag, color_item):
        if (color_item[0] != "#FFFFFF") \
                and (color_item[1] != "#FFFFFF"):
            self.entry_form.tag_config(tag,
                    foreground= color_item[0],
                    background=color_item[1])
        elif color_item[0] != "#FFFFFF":
            self.entry_form.tag_config(tag,
                    foreground= color_item[0])
        elif color_item[1] != "#FFFFFF":
            self.entry_form.tag_config(tag,
                    background= color_item[1])

    def create_frame_low(self):
        frame = Frame(self.root)
        self.title_low = Label(frame, text="マークロウテキスト【入力　可】")
        self.title_low.grid(row=0, column=0)
#         self.entry_low = Text(frame,
#                 width=60, height=26, wrap=NONE)
        self.entry_low = Text(frame,
                width=self.text_width, height=self.text_height, wrap=NONE)
#         self.entry_low.configure(font=("MS ゴシック", 12))
        global font_name, font_size
        self.entry_low.configure(font=(font_name, font_size))
        scrollbar_low_x = Scrollbar(frame, orient=HORIZONTAL,
                command=self.entry_low.xview)
        self.entry_low.configure(
                xscrollcommand=scrollbar_low_x.set)
        scrollbar_low_y = Scrollbar(frame, orient=VERTICAL,
                command=self.entry_low.yview)
        self.entry_low.configure(
                yscrollcommand=scrollbar_low_y.set)
        self.entry_low.grid(row=1, column=0)
        scrollbar_low_x.grid(row=2, column=0, sticky='ew')
        scrollbar_low_y.grid(row=1, column=1, sticky='ns')
#         self.entry_low.configure(state=DISABLED)
#        これで行なうとカーソルも受け付けない
#        挿入、改行などの際に困る
        self.entry_low.bind("<Key>", lambda e: ctrlEvent(e))
        self.input_flag = True
        # 20210830 version 0.11
        self.entry_low.bind('<Alt-s>', press_key_s)
        self.entry_low.bind('<Alt-i>', press_key_i)
#         self.entry_low.bind('<Alt-b>', press_key_b)
        self.entry_low.bind('<Alt-e>', press_key_e)
        self.entry_low.bind('<Alt-h>', press_key_h)
        self.entry_low.bind('<Alt-r>', press_key_r)
        self.entry_low.bind('<Alt-d>', press_key_d)
        self.entry_low.bind('<Alt-c>', press_key_c)
        self.entry_low.bind('<Alt-a>', press_key_a)
        self.entry_low.bind('<Alt-n>', press_key_n)
        self.entry_low.bind('<Alt-l>', press_key_l)
        self.entry_low.bind('<Alt-t>', press_key_t)
        self.entry_low.bind('<Alt-m>', press_key_m)
        self.entry_low.bind('<Alt-Return>', press_key_return)
        self.entry_low.bind('<Alt-k>', press_key_return)

        self.entry_low.bind('<Control-s>', press_key_save)
        self.entry_low.bind('<Control-z>', press_key_undo)

        self.entry_low.bind('<Control-8>', press_key_8)
        self.entry_low.bind('<Control-9>', press_key_9)
        self.entry_low.bind('<Control-Alt-Key-a>', press_ca_a)
        self.entry_low.bind('<Control-Alt-Key-e>', press_ca_e)
        self.entry_low.bind('<Control-Alt-Key-s>', press_ca_s)
        self.entry_low.bind('<Control-Alt-Key-h>', press_ca_h)
        self.entry_low.bind('<Control-Alt-Key-n>', press_ca_n)

        self.entry_low.bind('<Control-Alt-Key-l>', error_log)

        self.entry_low.focus_set()

        return frame

    def create_frame_button(self):
        frame = Frame(self.root)

        Button(frame, text="強調(S)", padx=4, pady=2,
                command=self.click_button_emphasis) \
                .grid(row=0, column=0, columnspan=1)
        Button(frame, text="挿入(I)", padx=4, pady=2,
                command=self.click_button_insert) \
                .grid(row=0, column=1, columnspan=1)
#         Button(frame, text="ブロック(B)", padx=4, pady=2,
#                 command=self.click_button_simple_block) \
#                 .grid(row=1, column=1, columnspan=1)
        Button(frame, text="非表示(E)", padx=4, pady=2,
                command=self.click_button_ellipsis) \
                .grid(row=2, column=0, columnspan=1)
        Button(frame, text="取消線(H)", padx=4, pady=2,
                command=self.click_button_hide) \
                .grid(row=2, column=1, columnspan=1)
        Button(frame, text="読替(R)", padx=4, pady=2,
                command=self.click_button_replace) \
                .grid(row=3, column=0, columnspan=1)
        Button(frame, text="定義(D)", padx=4, pady=2,
                command=self.click_button_define) \
                .grid(row=3, column=1, columnspan=1)
        Button(frame, text="参照(C)", padx=4, pady=2,
                command=self.click_button_reffer) \
                .grid(row=4, column=0, columnspan=1)
        Button(frame, text="当てはめ(A)", padx=4, pady=2,
                command=self.click_button_apply) \
                .grid(row=4, column=1, columnspan=1)

        Label(frame, text="").grid(row=5, column=0)

        Button(frame, text="改行(N)", padx=4, pady=2,
                command=self.click_button_return) \
                .grid(row=6, column=0, columnspan=1)
        Button(frame, text="改行せず(L)", padx=4, pady=2,
                command=self.click_button_no_return) \
                .grid(row=6, column=1, columnspan=1)

        Button(frame, text="タブ(T)", padx=4, pady=2,
                command=self.click_button_tab) \
                .grid(row=7, column=0, columnspan=1)
        Button(frame, text="半角空白", padx=4, pady=2,
                command=self.click_button_space) \
                .grid(row=8, column=0, columnspan=1)
        Button(frame, text="全角空白", padx=4, pady=2,
                command=self.click_button_space_zenkaku) \
                .grid(row=8, column=1, columnspan=1)

        Label(frame, text="").grid(row=9, column=0)

        Button(frame, text="入力　可", padx=4, pady=2,
                command=self.click_button_input_able) \
                .grid(row=10, column=0, columnspan=1)
        Button(frame, text="入力不可", padx=4, pady=2,
                command=self.click_button_input_disable) \
                .grid(row=10, column=1, columnspan=1)

        Label(frame, text="").grid(row=11, column=0)

        Button(frame, text="適用(M)", padx=4, pady=2,
                command=self.click_button_tekiyou) \
                .grid(row=12, column=1, columnspan=1)
        return frame

    def click_button_emphasis(self):
        '''
        '''
        try:
            start = self.entry_low.index('sel.first')
        except Exception as e:
            return
        end = self.entry_low.index('sel.last')
        if start == end:
            return
        self.undo_str = self.entry_low.get('1.0', 'end -1c')
        self.entry_low.insert(end, ']')
        self.entry_low.insert(start, '[')
        global edit_flag, low_parse
        edit_flag = True
        low_parse = None
        set_title()

    def click_button_insert(self):
        '''
        文字列を挿入する。
        (^挿入文字列^)
        original
        '''
        self.undo_str = self.entry_low.get('1.0', 'end -1c')
        from dialog_insert import DialogInsert
        global low_file_name
        DialogInsert(self, low_file_name)

    def click_button_ellipsis(self):
        # ID設定は省略
        try:
            start = self.entry_low.index('sel.first')
        except Exception as e:
            return
        end = self.entry_low.index('sel.last')
        if start == end:
            return
        self.undo_str = self.entry_low.get('1.0', 'end -1c')
        self.entry_low.insert(end, '%)')
        self.entry_low.insert(start, '(%')
        global edit_flag, low_parse
        edit_flag = True
        low_parse = None
        set_title()

    def click_button_hide(self):
        # ID設定は省略
        try:
            start = self.entry_low.index('sel.first')
        except Exception as e:
            return
        end = self.entry_low.index('sel.last')
        if start == end:
            return
        self.undo_str = self.entry_low.get('1.0', 'end -1c')
        self.entry_low.insert(end, '~)')
        self.entry_low.insert(start, '(~')
        global edit_flag, low_parse
        edit_flag = True
        low_parse = None
        set_title()

    def click_button_replace(self):
        try:
            start = self.entry_low.index('sel.first')
        except Exception as e:
            return
        end = self.entry_low.index('sel.last')
        if start == end:
            return
        str_org = self.entry_low.get(start, end)
        from dialog_replace_etc import DialogReplaceEtc
        global low_file_name
        DialogReplaceEtc(self, low_file_name, 'replace', '読替', str_org)

    def click_button_define(self):
        try:
            start = self.entry_low.index('sel.first')
        except Exception as e:
            return
        end = self.entry_low.index('sel.last')
        if start == end:
            return
        str_org = self.entry_low.get(start, end)
        from dialog_replace_etc import DialogReplaceEtc
        global low_file_name
        DialogReplaceEtc(self, low_file_name, 'define', '定義', str_org)

    def click_button_reffer(self):
        try:
            start = self.entry_low.index('sel.first')
        except Exception as e:
            return
        end = self.entry_low.index('sel.last')
        if start == end:
            return
        str_org = self.entry_low.get(start, end)
        from dialog_replace_etc import DialogReplaceEtc
        global low_file_name
        DialogReplaceEtc(self, low_file_name, 'reffer', '参照', str_org)

    def click_button_apply(self):
        try:
            start = self.entry_low.index('sel.first')
        except Exception as e:
            return
        end = self.entry_low.index('sel.last')
        if start == end:
            return
        str_org = self.entry_low.get(start, end)
        from dialog_replace_etc import DialogReplaceEtc
        global low_file_name
        DialogReplaceEtc(self, low_file_name, 'apply', '当てはめ', str_org)


    def click_button_return(self):
        self.undo_str = self.entry_low.get('1.0', 'end -1c')
        self.entry_low.insert('insert', "'n\n")
        global edit_flag, low_parse
        edit_flag = True
        low_parse = None
        set_title()

    def click_button_no_return(self):
        self.undo_str = self.entry_low.get('1.0', 'end -1c')
        str_text = self.entry_low.get('insert', 'insert +1c')
        d.dprint(str_text)
        if str_text[0] == "\n":
            self.entry_low.delete('insert', 'insert +1c')
            self.entry_low.insert('insert', "'N")
            global edit_flag, low_parse
            edit_flag = True
            low_parse = None
            set_title()

    def click_button_tab(self):
        self.undo_str = self.entry_low.get('1.0', 'end -1c')
        self.entry_low.insert('insert', "'t")
        global edit_flag, low_parse
        edit_flag = True
        low_parse = None
        set_title()

    def click_button_space(self):
        self.undo_str = self.entry_low.get('1.0', 'end -1c')
        self.entry_low.insert('insert', "'s")
        global edit_flag, low_parse
        edit_flag = True
        low_parse = None
        set_title()

    def click_button_space_zenkaku(self):
        self.undo_str = self.entry_low.get('1.0', 'end -1c')
        self.entry_low.insert('insert', "'S")
        global edit_flag, low_parse
        edit_flag = True
        low_parse = None
        set_title()

    def click_button_input_able(self):
        self.input_flag = True
        global edit_flag, low_parse
        edit_flag = True
        low_parse = None
        self.title_low['text'] = "マークロウテキスト【入力　可】"
        set_title()

    def click_button_input_disable(self):
        self.input_flag = False
        global edit_flag, low_parse
        edit_flag = True
        low_parse = None
        self.title_low['text'] = "マークロウテキスト【入力不可】"
        set_title()

    def click_button_tekiyou(self):
#         global low_text, form_text
        global low_parse
        low_text = self.entry_low.get('1.0', 'end -1c')
        parsing(low_text)
#         from MarkLow import low_to_form
#         form_text = low_to_form(low_parse)
        self.display_form(low_parse)

#         self.entry_form.configure(state=NORMAL)
#         self.entry_form.delete("0.0", END)
#         self.entry_form.insert("0.0", form_text)
#         self.entry_form.configure(state=DISABLED)

    def display_form(self, low_parse):
#         low_text = self.entry_low.get('1.0', 'end -1c')
#         global low_parse
#         parsing(low_text)
        self.entry_form.configure(state=NORMAL)
        self.entry_form.delete("0.0", END)
        self.display_form_sub(low_parse, 'NORMAL')
        self.entry_form.configure(state=DISABLED)


    def display_form_sub(self, low_parse, tag):
        for item in low_parse:
            if type(item) is str:
                self.entry_form.insert('end', item, tag)
            elif type(item) is int:
                if item == ml_yacc.TAB:
                    self.entry_form.insert('end', '\t', tag)
                # 20211002 v0.21 #を追加
                elif item == ml_yacc.SHARP:
                    pass
                else:
                    assert False, "display_form_sub int {}".format(item)
            elif type(item) is tuple:
                if item[0] == ml_yacc.SPACE:
                    if item[1] == 0:    # 's 半角空白
                        self.entry_form.insert('end', ' ' * item[2], tag)
                    elif item[1] == 1:  # 'S 全角空白
                        self.entry_form.insert('end', '　' * item[2], tag)
                    else:
                        assert False, "display_form_sub SPACE {}".format(item[2])
                elif item[0] == ml_yacc.RETURN: # 20210823
                    if item[1] == 0:    # 'n_
                        self.entry_form.insert('end', '\n', tag)
                    elif item[1] == 1:
                        self.entry_form.insert('end', '\n', tag)
                    else:
                        pass
                elif item[0] == ml_yacc.EMPHASIS:
                    self.entry_form.insert('end', '[', 'EMPHASIS')
                    self.display_form_sub(item[2], 'EMPHASIS')
                    self.entry_form.insert('end', ']', 'EMPHASIS')
                elif item[0] == ml_yacc.INSERT:
                    self.display_form_sub(item[2], 'INSERT')
                elif item[0] == ml_yacc.ELLIPSIS:
                    pass
                elif item[0] == ml_yacc.HIDE:
                    self.entry_form.insert('end', '~~~', 'HIDE')
                elif item[0] == ml_yacc.REPLACE:
                    self.display_form_sub(item[3][1], 'REPLACE')
                elif item[0] == ml_yacc.DEFINE:
                    self.entry_form.insert('end', '(|', 'DEFINE')
                    self.display_form_sub(item[2], 'DEFINE')
                    self.entry_form.insert('end', '|)', 'DEFINE')
                    self.entry_form.insert('end', '(', 'DEFINE2')
                    self.display_form_sub(item[3][1], 'DEFINE2')
                    self.entry_form.insert('end', ')', 'DEFINE2')
                elif item[0] == ml_yacc.REFFER:
                    self.entry_form.insert('end', '(&', 'REFFER')
                    self.display_form_sub(item[2], 'REFFER')
                    self.entry_form.insert('end', '&)', 'REFFER')
#                     self.entry_form.insert('end', '(', 'REFFER2')
#                     self.display_form_sub(item[3][1], 'REFFER2')
#                     self.entry_form.insert('end', ')', 'REFFER2')
                    # ver.0.22 2021/10/07
                    self.entry_form.insert('end', '( ', 'REFFER2')
                    self.display_form_sub(item[3][1], 'REFFER2')
                    self.entry_form.insert('end', ' )', 'REFFER2')
                elif item[0] == ml_yacc.APPLY:
                    self.entry_form.insert('end', '("', 'APPLY')
                    self.display_form_sub(item[2], 'APPLY')
                    self.entry_form.insert('end', '")', 'APPLY')
                    self.entry_form.insert('end', '(', 'APPLY2')
                    self.display_form_sub(item[3][1], 'APPLY2')
                    self.entry_form.insert('end', ')', 'APPLY2')
                else:
                    assert False, "display_form_sub {}".format(item[1])
            elif type(item) is list:
                    self.display_form_sub(item, tag)
            else:
                assert False, "display_form_sub {}".format(item)


def set_window_size():
    from dialog_widget import DialogWidget
    global editor
    DialogWidget(editor, editor.text_height, editor.text_width)

def press_key_s(_):
#     d.dprint_method_start()
    global editor
    editor.click_button_emphasis()

def press_key_i(_):
#     d.dprint_method_start()
    global editor
    editor.click_button_insert()

def press_key_e(_):
    global editor
    editor.click_button_ellipsis()

def press_key_h(_):
    global editor
    editor.click_button_hide()

def press_key_r(_):
    global editor
    editor.click_button_replace()

def press_key_d(_):
    global editor
    editor.click_button_define()

def press_key_c(_):
    global editor
    editor.click_button_reffer()

def press_key_a(_):
    global editor
    editor.click_button_apply()

def press_key_n(_):
    '''
    'nだけを挿入し、改行は入れない　（旧バージョンより変更）
    '''
    global editor
    global editor
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    editor.entry_low.insert('insert', "'n")
    global edit_flag, low_parse
    edit_flag = True
    low_parse = None
    set_title()

def press_key_l(_):
    global editor
    editor.click_button_no_return()

def press_key_return(_):
    '''
    'nだけを挿入し、改行を入れる（キー入力の関係で自然に入る）
    '''
    global editor
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    editor.entry_low.insert('insert', "'n")
    global edit_flag, low_parse
    edit_flag = True
    low_parse = None
    set_title()

def press_key_save(_):
    save_file()

def press_key_undo(_):
    global editor
    if editor.undo_str is not None:
        d.dprint(editor.undo_str)
        editor.entry_low.delete("0.0", "end")
        editor.entry_low.insert("0.0", editor.undo_str)
        global low_parse
        low_parse = None    # マークロウ構造体
        edit_flag = True
        set_title()
        editor.undo_str = None

def press_key_t(_):
    global editor
    editor.click_button_tab()

def press_key_m(_):
    global editor
    editor.click_button_tekiyou()

def press_key_8(_):
    # カーソルの後が（ならば、対応する）の後までジャンプ
    d.dprint_method_start()
    global editor
    str_text = editor.entry_low.get('insert', 'end -1c')
    d.dprint(str_text)
    if str_text[0] == "（":
        pos = editor.entry_low.index('insert')
        d.dprint(pos)
        row, column = pos.split('.')
        d.dprint(row)
        d.dprint(column)
        row = int(row)
        column = int(column)
        level = 0
        for c in str_text[1:]:
            if c == '）':
                if level == 0:
                    column += 1 + 1
                    break
                else:
                    level -= 1
            if c == '（':
                level += 1
            if c == '\n':
                row += 1
                column = 0
            else:
                column += 1
        else:
            # 対応する）なし
            e.eprint("エラー", "対応する）が見つかりません")
            return
        new_pos = "{}.{}".format(row, column)
        d.dprint(new_pos)
        editor.entry_low.mark_set('insert', new_pos)
        editor.entry_low.see('insert')
    d.dprint_method_end()

def press_key_9(_):
    # カーソルの前が）ならば、対応する（の前までジャンプ
    d.dprint_method_start()
    global editor
    str_text = editor.entry_low.get('1.0', 'insert')
    d.dprint(str_text)
    if str_text[-1] == "）":
        pos = editor.entry_low.index('insert')
        d.dprint(pos)
        row, column = pos.split('.')
        d.dprint(row)
        d.dprint(column)
        row = int(row)
        row_o = row
        column = int(column) - 1
        level = 0
        for c in reversed(str_text[:-2]):
            if c == '（':
                if level == 0:
                    column -= 1
                    break
                else:
                    level -= 1
            if c == '）':
                level += 1
            if c == '\n':
                row -= 1
                column = 0  # マイナス調整が必要？
            else:
                column -= 1
        else:
            # 対応する）なし
            e.eprint("エラー", "対応する（が見つかりません")
            return
        if row == row_o:
            new_pos = "{}.{}".format(row, column - 1)
            d.dprint(new_pos)
            editor.entry_low.mark_set('insert', new_pos)
        else:
            new_pos = "{}.end".format(row)
            d.dprint(new_pos)
            editor.entry_low.mark_set('insert', new_pos)
            end_pos = editor.entry_low.index('insert')
            d.dprint(end_pos)
            _, end_column = end_pos.split('.')
            end_column = int(end_column)
            column += end_column
            new_pos = "{}.{}".format(row, column)
            d.dprint(new_pos)
            editor.entry_low.mark_set('insert', new_pos)
        editor.entry_low.see('insert')
    d.dprint_method_end()

def press_ca_a(_):
    global editor
    try:
        start = editor.entry_low.index('sel.first')
    except Exception as e:
        return
    end = editor.entry_low.index('sel.last')
    if start == end:
        return
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    low_text = editor.entry_low.get(start, end)
    d.dprint(low_text)
    new_text = parse_init_alnum(low_text)
    d.dprint(new_text)
    editor.entry_low.delete(start, end)
    editor.entry_low.insert(start, new_text)

    global edit_flag
    edit_flag = True
    set_title()

def press_ca_e(_):
    global editor
    try:
        start = editor.entry_low.index('sel.first')
    except Exception as e:
        return
    end = editor.entry_low.index('sel.last')
    if start == end:
        return
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    low_text = editor.entry_low.get(start, end)
    d.dprint(low_text)
    new_text = parse_init_hihyouji(low_text)
    d.dprint(new_text)
    editor.entry_low.delete(start, end)
    editor.entry_low.insert(start, new_text)

#     low_text = editor.entry_low.get('1.0', 'end -1c')
#     parsing(new_text)
#     from MarkLow import low_to_form
#     form_text = low_to_form(low_parse)
#     editor.entry_form.configure(state=NORMAL)
#     editor.entry_form.delete("0.0", "end")
#     editor.entry_form.insert("0.0", form_text)
#     editor.entry_form.configure(state=DISABLED)
    global edit_flag
    edit_flag = True
    set_title()

def press_ca_s(_):
    global editor
    try:
        start = editor.entry_low.index('sel.first')
    except Exception as e:
        return
    end = editor.entry_low.index('sel.last')
    if start == end:
        return
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    low_text = editor.entry_low.get(start, end)
    d.dprint(low_text)
    new_text = parse_init_kuhaku(low_text)
    d.dprint(new_text)
    editor.entry_low.delete(start, end)
    editor.entry_low.insert(start, new_text)

    global edit_flag
    edit_flag = True
    set_title()

def press_ca_h(_):
    global editor
    try:
        start = editor.entry_low.index('sel.first')
    except Exception as e:
        return
    end = editor.entry_low.index('sel.last')
    if start == end:
        return
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    low_text = editor.entry_low.get(start, end)
    d.dprint(low_text)
    new_text = parse_init_kakko(low_text)
    d.dprint(new_text)
    editor.entry_low.delete(start, end)
    editor.entry_low.insert(start, new_text)

    global edit_flag
    edit_flag = True
    set_title()


def press_ca_t(_):
    global editor
    try:
        start = editor.entry_low.index('sel.first')
    except Exception as e:
        return
    end = editor.entry_low.index('sel.last')
    if start == end:
        return
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    low_text = editor.entry_low.get(start, end)
    d.dprint(low_text)
    new_text = parse_return_ten(low_text)
    d.dprint(new_text)
    editor.entry_low.delete(start, end)
    editor.entry_low.insert(start, new_text)

    global edit_flag
    edit_flag = True
    set_title()

def press_ca_m(_):
    global editor
    try:
        start = editor.entry_low.index('sel.first')
    except Exception as e:
        return
    end = editor.entry_low.index('sel.last')
    if start == end:
        return
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    low_text = editor.entry_low.get(start, end)
    d.dprint(low_text)
    new_text = parse_return_maru(low_text)
    d.dprint(new_text)
    editor.entry_low.delete(start, end)
    editor.entry_low.insert(start, new_text)

    global edit_flag
    edit_flag = True
    set_title()

def press_ca_k(_):
    global editor
    try:
        start = editor.entry_low.index('sel.first')
    except Exception as e:
        return
    end = editor.entry_low.index('sel.last')
    if start == end:
        return
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    low_text = editor.entry_low.get(start, end)
    d.dprint(low_text)
    new_text = parse_return_kakko(low_text)
    d.dprint(new_text)
    editor.entry_low.delete(start, end)
    editor.entry_low.insert(start, new_text)

    global edit_flag
    edit_flag = True
    set_title()


def press_ca_n(_):
    global editor
    try:
        start = editor.entry_low.index('sel.first')
    except Exception as e:
        return
    end = editor.entry_low.index('sel.last')
    if start == end:
        return
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    low_text = editor.entry_low.get(start, end)
    new_text = trans(low_text)
    editor.entry_low.delete(start, end)
    editor.entry_low.insert(start, new_text)

    global edit_flag
    edit_flag = True
    set_title()

# ver0.22 2021/10/05
def right_click_form(_):
    '''整形テキストで右ボタンをクリック。リンクを開く'''
    global editor
    try:
        start = editor.entry_form.index('sel.first')
    except Exception as e:
        return
    end = editor.entry_form.index('sel.last')
    if start == end:
        return
    link_text = editor.entry_form.get(start, end)
    d.dprint(link_text)
    import subprocess
    global low_file_name
    if low_file_name == None:
        if os.path.isfile(link_text):
            d.dprint("isfile true")
            subprocess.run( \
                    r' start ml_editor.exe "' + link_text + '"',
                    shell=True)
            return
    if low_file_name != None:
        dir_name = os.path.dirname(low_file_name)
        file_name = os.path.join(dir_name, link_text)
        d.dprint(file_name)
        if os.path.isfile(file_name):
            subprocess.run( \
                    r' start ml_editor.exe "' + file_name + '"',
                    shell=True)
            return
    import webbrowser
    rv = webbrowser.open(link_text, new=0, autoraise=True)
    # ファイル名でも起動しようとしてTrueが変える。
    d.dprint(rv)

def ctrlEvent(event):
    if(12==event.state and event.keysym=='c' ):
        return
    else:
        global editor
        if editor.input_flag:
#             d.dprint("ctrlEvent ifelse if")
#             editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
            global edit_flag, low_parse
            edit_flag = True
            low_parse = None
            # 20210831 ver0.11
            set_title()
            return
        return "break"


def trans(str_text):
    '''
    半角数字を全角数字に変換する
    '''
    return str_text.translate( \
            str.maketrans('0123456789', '０１２３４５６７８９'))


def change_suuji():
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    editor.undo_str = low_text
    new_text = trans(low_text)

    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", new_text)
    global edit_flag
    edit_flag = True
    set_title()


def return_full():
    '''
    （の前,）,。,、の後に改行を追加する。
    '''
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    editor.undo_str = low_text
    new_text = parse_return_full(low_text)
    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", new_text)
    global edit_flag
    edit_flag = True
    set_title()

def return_kuten():
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    editor.undo_str = low_text
    new_text = parse_return_ten(low_text)
    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", new_text)
    global edit_flag
    edit_flag = True
    set_title()

def return_touten():
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    editor.undo_str = low_text
    new_text = parse_return_maru(low_text)
    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", new_text)
    global edit_flag
    edit_flag = True
    set_title()

def return_kakko():
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    editor.undo_str = low_text
    new_text = parse_return_kakko(low_text)
    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", new_text)
    global edit_flag
    edit_flag = True
    set_title()


def init_full():
    '''
    半角英数字をアンダースコアで囲う。
    括弧内を非表示設定にする。
    半角括弧を全角括弧にする。
    半角空白を削除する。
    '''
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    editor.undo_str = low_text
    new_text = parse_init_full(low_text)

    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", new_text)
    global edit_flag
    edit_flag = True
    set_title()

def init_alnum():
    '''
    半角英数字をアンダースコアで囲う。
    '''
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    editor.undo_str = low_text
    new_text = parse_init_alnum(low_text)

    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", new_text)
    global edit_flag
    edit_flag = True
    set_title()

def init_hihyouji():
    '''
    括弧内を非表示設定にする。
    '''
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    editor.undo_str = low_text
    new_text = parse_init_hihyouji(low_text)

    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", new_text)
    global edit_flag
    edit_flag = True
    set_title()

def init_kakko():
    '''
    半角括弧を全角括弧にする。
    '''
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    editor.undo_str = low_text
    new_text = parse_init_kakko(low_text)

    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", new_text)
    global edit_flag
    edit_flag = True
    set_title()

def init_kuhaku():
    '''
    半角空白を削除する。
    '''
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    editor.undo_str = low_text
    new_text = parse_init_kuhaku(low_text)

    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", new_text)
    global edit_flag
    edit_flag = True
    set_title()

def init_html_kuhaku():
    '''
    HTML上の空白を削除する。
    '''
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    editor.undo_str = low_text
    new_text = parse_init_html_kuhaku(low_text)

    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", new_text)
    global edit_flag
    edit_flag = True
    set_title()

import pyperclip

def copy_original():
    global low_parse, parser
    global editor
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
        low_parse = parser.parse(low_text)
    from MarkLow import low_to_original
    org_text = low_to_original(low_parse)
    pyperclip.copy(org_text)

def copy_plain():
    global low_parse, parser
    global editor
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
        low_parse = parser.parse(low_text)
    from MarkLow import low_to_plain
    plane_text = low_to_plain(low_parse)
    pyperclip.copy(plane_text)

def copy_form():
    global low_parse, parser
    global editor
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
#         low_parse = parser.parse(low_text)
        parsing(low_text)
    from MarkLow import low_to_form
    form_text = low_to_form(low_parse)
    pyperclip.copy(form_text)
    editor.display_form(low_parse)

def copy_markdown():
    global low_parse, parser
    global editor
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
        low_parse = parser.parse(low_text)
    from MarkLow import low_to_markdown
    markdown_text = low_to_markdown(low_parse)
    pyperclip.copy(markdown_text)

def copy_html():
    global low_parse, parser
    global editor
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
        low_parse = parser.parse(low_text)
    from MarkLow import low_to_html
    html_text = low_to_html(low_parse)
    pyperclip.copy(html_text)

def copy_marklow():
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    pyperclip.copy(low_text)


def new():
    global edit_flag
    if edit_flag:
        answer = messagebox.askyesnocancel("ファイル変更あり", "ファイルを保存しますか？")
        if answer is None:
            return
        elif answer:
            global low_file_name
            if low_file_name == None:
                save_new()
            else:
                save_file()
#     global low_file_name
    low_file_name = ""
    global low_parse
    edit_flag = False   # マークロウ構造体を再作成するか否か
    low_parse = None    # マークロウ構造体
    set_title()
    global editor
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    editor.entry_low.delete("0.0", "end")
    editor.entry_form.configure(state=NORMAL)
    editor.entry_form.delete("0.0", "end")
    editor.entry_form.configure(state=DISABLED)

def load_file():
    global edit_flag
    if edit_flag:
        answer = messagebox.askyesnocancel("ファイル変更あり", "ファイルを保存しますか？")
        if answer is None:
            return
        elif answer:
            global low_file_name
            if low_file_name == None:
                save_new()
            else:
                save_file()
    file_type = [('マークロウファイル', '*.ml;*.ML'),
            ('テキストファイル', '*.txt'),
            ('', '*')]
#     dir = 'C:\\pg'
#     global low_file_name
    file_name = filedialog.askopenfilename(filetypes = file_type,
            title='マークロウファイルのファイル名')   # , initialdir = dir)
    if file_name == '':
        return
    # v0.22 2021/10/05
    load_file_main(file_name)

def load_file_main(file_name):
    try:
        f = open(file_name,
                "r",
                encoding="UTF-8")
#                 encoding="ms932")
        read_list = f.readlines()
        f.close()
    except OSError as e:
        messagebox.showwarning(
                'ファイル読込失敗', e)
        return
#     d.dprint(read_list)
    read_text = ""
    for line in read_list:
        read_text += line
    global low_file_name
    low_file_name = file_name
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", read_text)
    global low_parse
    low_parse = None    # マークロウ構造体
    edit_flag = False
    set_title()
    editor.entry_form.configure(state=NORMAL)
    editor.entry_form.delete("0.0", "end")
    editor.entry_form.configure(state=DISABLED)

def save_file():
    global low_file_name
    if low_file_name == None:
        e.eprint("ファイル保存", "名前を付けて保存を選択してください。")
        return
    pos = editor.entry_low.index('insert')
    low_text = editor.entry_low.get('1.0', 'end -1c')
    try:
        with open(low_file_name, mode="w", encoding="UTF-8") as f:
            f.write(low_text)
        global edit_flag
        edit_flag = False
        set_title()
        editor.entry_low.mark_set('insert', pos)
        editor.entry_low.see('insert')
    except Exception as err:
        e.eprint("ファイル保存エラー", err)

def save_new():
    file_type = [('マークロウファイル', '*.ml')]
    file_name = filedialog.asksaveasfilename(
            defaultextension="ml",
            filetypes=file_type,
#              [initialdir],
            title="名前を付けて保存")
    if file_name == '':
        return
    d.dprint(file_name)
    global editor, low_file_name
    pos = editor.entry_low.index('insert')
    low_text = editor.entry_low.get('1.0', 'end -1c')
    try:
        with open(file_name, mode="w", encoding="UTF-8") as f:
            f.write(low_text)
        low_file_name = file_name
        global edit_flag
        edit_flag = False
        set_title()
        editor.entry_low.mark_set('insert', pos)
        editor.entry_low.see('insert')
    except Exception as err:
        e.eprint("ファイル保存エラー", err)

def save_full():
    file_type = [('マークロウファイル', '*.ml')]
    global low_file_name
    if low_file_name != None:
        basename = os.path.splitext(os.path.basename(low_file_name))[0]
    else:
        basename = ""
    file_name = filedialog.asksaveasfilename(
            defaultextension="ml",
            filetypes=file_type,
            initialfile=basename,
#              [initialdir],
            title="全ファイルを保存（マークロウファイル名を指定）")
    if file_name == '':
        return
    dirname = os.path.dirname(file_name)
    basename = os.path.splitext(os.path.basename(file_name))[0]
    org_file_name = os.path.join(dirname, basename + '_o.txt')
    plain_file_name = os.path.join(dirname, basename + '_p.txt')
    form_file_name = os.path.join(dirname, basename + '_f.txt')
    markdown_file_name = os.path.join(dirname, basename + '.md')
    html_file_name = os.path.join(dirname, basename + '.html')
    if os.path.exists(org_file_name) \
            or os.path.exists(plain_file_name) \
            or os.path.exists(form_file_name) \
            or os.path.exists(markdown_file_name) \
            or os.path.exists(html_file_name):
        ret = messagebox.askyesno('確認', '既に存在しているファイルがあります。上書きして良いですか？')
        if not ret:
            return

    global low_parse
    global editor
    pos = editor.entry_low.index('insert')
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
#         low_parse = parser.parse(low_text)
        parsing(low_text)
    low_text = editor.entry_low.get('1.0', 'end -1c')
    try:
        with open(file_name, mode="w", encoding="UTF-8") as f:
            f.write(low_text)
        low_file_name = file_name
        global edit_flag
        edit_flag = False
        set_title()
        editor.entry_low.mark_set('insert', pos)
        editor.entry_low.see('insert')
    except Exception as err:
        e.eprint("ファイル保存エラー", err)

    from MarkLow import low_to_original
    org_text = low_to_original(low_parse)
    try:
        with open(org_file_name, mode="w", encoding="UTF-8") as f:
            f.write(org_text)
    except Exception as err:
        e.eprint("ファイル保存エラー", err)
    from MarkLow import low_to_plain
    plain_text = low_to_plain(low_parse)
    try:
        with open(plain_file_name, mode="w", encoding="UTF-8") as f:
            f.write(plain_text)
    except Exception as err:
        e.eprint("ファイル保存エラー", err)
    from MarkLow import low_to_form
    form_text = low_to_form(low_parse)
    try:
        with open(form_file_name, mode="w", encoding="UTF-8") as f:
            f.write(form_text)
    except Exception as err:
        e.eprint("ファイル保存エラー", err)

    editor.display_form(low_parse)

    from MarkLow import low_to_markdown
    markdown_text = low_to_markdown(low_parse)
    try:
        with open(markdown_file_name, mode="w", encoding="UTF-8") as f:
            f.write(markdown_text)
    except Exception as err:
        e.eprint("ファイル保存エラー", err)
    from MarkLow import low_to_html
    html_text = low_to_html(low_parse)
    try:
        with open(html_file_name, mode="w", encoding="UTF-8") as f:
            f.write(html_text)
    except Exception as err:
        e.eprint("ファイル保存エラー", err)

def save_original():
    file_type = [('オリジナルテキストファイル', '*.txt')]
    global low_file_name
    if low_file_name != None:
        basename = os.path.splitext(os.path.basename(low_file_name))[0] + '_o'
    else:
        basename = ""
    file_name = filedialog.asksaveasfilename(
            defaultextension="txt",
            filetypes=file_type,
            initialfile=basename,
#              [initialdir],
            title="オリジナルテキストファイルを保存")
    global low_parse
    global editor
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
#         low_parse = parser.parse(low_text)
        parsing(low_text)
    from MarkLow import low_to_original
    org_text = low_to_original(low_parse)
    try:
        with open(file_name, mode="w", encoding="UTF-8") as f:
            f.write(org_text)
    except Exception as err:
        e.eprint("ファイル保存エラー", err)

def save_plain():
    file_type = [('プレーンテキストファイル', '*.txt')]
    global low_file_name
    if low_file_name != None:
        basename = os.path.splitext(os.path.basename(low_file_name))[0] + '_p'
    else:
        basename = ""
    file_name = filedialog.asksaveasfilename(
            defaultextension="txt",
            filetypes=file_type,
            initialfile=basename,
#              [initialdir],
            title="プレーンテキストファイルを保存")
    global low_parse, parser
    global editor
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
#         low_parse = parser.parse(low_text)
        parsing(low_text)
    from MarkLow import low_to_plain
    plain_text = low_to_plain(low_parse)
    try:
        with open(file_name, mode="w", encoding="UTF-8") as f:
            f.write(plain_text)
    except Exception as err:
        e.eprint("ファイル保存エラー", err)

def save_form():
    file_type = [('整形テキストファイル', '*.txt')]
    global low_file_name
    if low_file_name != None:
        basename = os.path.splitext(os.path.basename(low_file_name))[0] + '_f'
    else:
        basename = ""
    file_name = filedialog.asksaveasfilename(
            defaultextension="txt",
            filetypes=file_type,
            initialfile=basename,
#              [initialdir],
            title="整形テキストファイルを保存")
    global low_parse
    global editor
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
#         low_parse = parser.parse(low_text)
        parsing(low_text)
    from MarkLow import low_to_form
    form_text = low_to_form(low_parse)
    try:
        with open(file_name, mode="w", encoding="UTF-8") as f:
            f.write(form_text)
    except Exception as err:
        e.eprint("ファイル保存エラー", err)
        editor.entry_form.configure(state=NORMAL)

    editor.display_form(low_parse)

def save_markdown():
    file_type = [('マークダウンファイル', '*.md')]
    global low_file_name
    if low_file_name != None:
        basename = os.path.splitext(os.path.basename(low_file_name))[0]
    else:
        basename = ""
    file_name = filedialog.asksaveasfilename(
            defaultextension="md",
            filetypes=file_type,
            initialfile=basename,
#              [initialdir],
            title="マークダウンファイルを保存")
    global low_parse, parser
    global editor
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
#         low_parse = parser.parse(low_text)
        parsing(low_text)
    from MarkLow import low_to_markdown
    markdown_text = low_to_markdown(low_parse)
    try:
        with open(file_name, mode="w", encoding="UTF-8") as f:
            f.write(markdown_text)
    except Exception as err:
        e.eprint("ファイル保存エラー", err)

def save_html():
    file_type = [('ｈｔｍｌファイル', '*.html')]
    global low_file_name
    if low_file_name != None:
        basename = os.path.splitext(os.path.basename(low_file_name))[0]
    else:
        basename = ""
    file_name = filedialog.asksaveasfilename(
            defaultextension="html",
            filetypes=file_type,
            initialfile=basename,
#              [initialdir],
            title="ｈｔｍｌファイルを保存")
    global low_parse
    global editor
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
#         low_parse = parser.parse(low_text)
        parsing(low_text)
    from MarkLow import low_to_html
    html_text = low_to_html(low_parse)
    try:
        with open(file_name, mode="w", encoding="UTF-8") as f:
            f.write(html_text)
    except Exception as err:
        e.eprint("ファイル保存エラー", err)

def load_low_parse():
    # marklowとparseを読込
    global edit_flag
    if edit_flag:
        answer = messagebox.askyesnocancel("ファイル変更あり", "ファイルを保存しますか？")
        if answer is None:
            return
        elif answer:
            global low_file_name
            if low_file_name == None:
                save_new()
            else:
                save_file()
    file_type = [('マークロウファイル', '*.ml;*.ML'),
            ('テキストファイル', '*.txt'),
            ('', '*')]
    file_name = filedialog.askopenfilename(filetypes = file_type,
            title='マークロウファイルのファイル名')   # , initialdir = dir)
    if file_name == '':
        return
    load_low_parse_main(file_name)

def load_low_parse_main(file_name):
    try:
        f = open(file_name,
                "r",
                encoding="UTF-8")
#                 encoding="ms932")
        read_list = f.readlines()
        f.close()
    except OSError as e:
        messagebox.showwarning(
                'ファイル読込失敗', e)
        return
    read_text = ""
    for line in read_list:
        read_text += line
    global low_file_name
    low_file_name = file_name
    editor.undo_str = editor.entry_low.get('1.0', 'end -1c')
    editor.entry_low.delete("0.0", "end")
    editor.entry_low.insert("0.0", read_text)
    edit_flag = False
    set_title()

    dirname = os.path.dirname(file_name)
    basename = os.path.splitext(os.path.basename(file_name))[0]
    parse_file_name = os.path.join(dirname, basename + '.mlp')
    global low_parse
    try:
        f = open(parse_file_name,
                "r",
                encoding="UTF-8")
#                 encoding="ms932")
        read_list = f.readlines()
        f.close()
    except OSError as e:
        messagebox.showwarning(
                'ファイル読込失敗', e)
        # v0.22 2021/10/04
#         d.dprint("load_low_parse0 low_parse")
#         global low_parse
        low_parse = None
#         edit_flag = False
#         set_title()
        editor.entry_form.configure(state=NORMAL)
        editor.entry_form.delete("0.0", "end")
        editor.entry_form.configure(state=DISABLED)
        return
#     d.dprint("load_low_parse1 low_parse")
#     global low_parse
    (low_parse, _) = load_low_parse_sub(0, read_list)
    editor.display_form(low_parse)

def load_low_parse_sub(index, read_list):
    parse_list = []
    line_no = index
    line_len = len(read_list)
    while line_no < line_len:
        line = read_list[line_no]
        if line[0:2] == "'t":
            parse_list.append(ml_yacc.TAB)
            line_no += 1
        # 20211002 v0.21 #を追加
        elif line[0:1] == "#":
            parse_list.append(ml_yacc.SHARP)
            line_no += 1
        elif line[0:2] == "'s":
            num = int(line[2:])
            parse_list.append((ml_yacc.SPACE, 0, num))
            line_no += 1
        elif line[0:2] == "'S":
            num = int(line[2:])
            parse_list.append((ml_yacc.SPACE, 1, num))
            line_no += 1
        elif line[0:2] == "'n":
            num = int(line[2:])
            parse_list.append((ml_yacc.RETURN, num))
            line_no += 1
        elif line[0:2] == 'S(':
            id_str = line[2:][:-1]
            (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
            assert read_list[line_no]==")S\n", "load_low_parse_sub not )S"
            line_no += 1
            parse_list.append((ml_yacc.EMPHASIS, id_str, parse))
        elif line[0:2] == 'I(':
            id_str = line[2:][:-1]
            (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
            assert read_list[line_no]==")I\n", "load_low_parse_sub not )I"
            line_no += 1
            parse_list.append((ml_yacc.INSERT, id_str, parse))
        elif line[0:2] == 'E(':
            id_str = line[2:][:-1]
            (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
            assert read_list[line_no]==")E\n", "load_low_parse_sub not )E"
            line_no += 1
            parse_list.append((ml_yacc.ELLIPSIS, id_str, parse))
        elif line[0:2] == 'H(':
            id_str = line[2:][:-1]
            (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
            assert read_list[line_no]==")H\n", "load_low_parse_sub not )E"
            line_no += 1
            parse_list.append((ml_yacc.HIDE, id_str, parse))
        elif line[0:2] == 'R(':
            id_str = line[2:][:-1]
            (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
            assert read_list[line_no][:2]==")(", "load_low_parse_sub not )("
            id2_str = line[2:][:-1]
            line_no += 1
            (parse2, line_no) = load_low_parse_sub(line_no, read_list)
            assert read_list[line_no]==")R\n", "load_low_parse_sub not )R"
            line_no += 1
            parse_list.append((ml_yacc.REPLACE, id_str, parse, (id2_str, parse2)))
        elif line[0:2] == 'D(':
            id_str = line[2:][:-1]
            (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
            assert read_list[line_no][:2]==")(", "load_low_parse_sub not )("
            id2_str = line[2:][:-1]
            line_no += 1
            (parse2, line_no) = load_low_parse_sub(line_no, read_list)
            assert read_list[line_no]==")D\n", "load_low_parse_sub not )D"
            line_no += 1
            parse_list.append((ml_yacc.DEFINE, id_str, parse, (id2_str, parse2)))
        elif line[0:2] == 'C(':
            id_str = line[2:][:-1]
            (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
            assert read_list[line_no][:2]==")(", "load_low_parse_sub not )("
            id2_str = line[2:][:-1]
            line_no += 1
            (parse2, line_no) = load_low_parse_sub(line_no, read_list)
            assert read_list[line_no]==")C\n", "load_low_parse_sub not )C"
            line_no += 1
            parse_list.append((ml_yacc.REFFER, id_str, parse, (id2_str, parse2)))
        elif line[0:2] == 'A(':
            id_str = line[2:][:-1]
            (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
            assert read_list[line_no][:2]==")(", "load_low_parse_sub not )("
            id2_str = line[2:][:-1]
            line_no += 1
            (parse2, line_no) = load_low_parse_sub(line_no, read_list)
            assert read_list[line_no]==")A\n", "load_low_parse_sub not )A"
            line_no += 1
            parse_list.append((ml_yacc.APPLY, id_str, parse, (id2_str, parse2)))
        elif line[0:2] == 'l[':
            parse_l_list = []
            while True:
                (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
                parse_l_list.append(parse)
                line_no += 1
                if read_list[line_no] == "]l\n":
                    break
            line_no += 1
            parse_list.append(parse_l_list)
        elif line[0] == ')':
            break
        else:
            line_no += 1
            if line[0] == '_':
                parse_list.append(line[1:-1])
            else:
                parse_list.append(line[:-1])
    return (parse_list, line_no)

def save_low_parse():
    save_file()
    global low_file_name
    dirname = os.path.dirname(low_file_name)
    basename = os.path.splitext(os.path.basename(low_file_name))[0]
    parse_file_name = os.path.join(dirname, basename + '.mlp')

#     file_type = [('parseファイル', '*.mlp')]
#     global low_file_name
#     if low_file_name != None:
#         basename = os.path.splitext(os.path.basename(low_file_name))[0]
#     else:
#         basename = ""
#     file_name = filedialog.asksaveasfilename(
#             defaultextension="mlp",
#             filetypes=file_type,
#             initialfile=basename,
# #              [initialdir],
#             title="parseファイルを保存")
    global low_parse, parser
    global editor
    if low_parse == None:
        low_text = editor.entry_low.get('1.0', 'end -1c')
        parsing(low_text)
    try:
        with open(parse_file_name, mode="w", encoding="UTF-8") as f:
            save_low_parse_sub(f, low_parse)
    except Exception as err:
        e.eprint("ファイル保存エラー", err)
        editor.entry_form.configure(state=NORMAL)
    editor.display_form(low_parse)

def save_low_parse_sub(f, low_parse):
    d.dprint(low_parse)
    for item in low_parse:
        if type(item) is str:
#             f.write(item + "\n")
            # v0.21 20210921
            f.write("_" + item + "\n")
        elif type(item) is int:
            if item == ml_yacc.TAB:
                f.write("'t\n")
            # 20211002 v0.21 #を追加
            elif item == ml_yacc.SHARP:
                f.write("#\n")
            else:
                assert False, "save_low_parse_sub int {}".format(item)
        elif type(item) is tuple:
            if item[0] == ml_yacc.SPACE:
                if item[1] == 0:    # 's 半角空白
                    f.write("'s{}\n".format(item[2]))
                elif item[1] == 1:  # 'S 全角空白
                    f.write("'S{}\n".format(item[2]))
                else:
                    assert False, "save_low_parse_sub SPACE {}".format(item[1])
            elif item[0] == ml_yacc.RETURN:
                f.write("'n{}\n".format(item[1]))
            elif item[0] == ml_yacc.EMPHASIS:
                f.write("S(" + item[1] + "\n")
                save_low_parse_sub(f, item[2])
                f.write(")S\n")
            elif item[0] == ml_yacc.INSERT:
                f.write("I(" + item[1] + "\n")
                save_low_parse_sub(f, item[2])
                f.write(")I\n")
            elif item[0] == ml_yacc.ELLIPSIS:
                f.write("E(" + item[1] + "\n")
                save_low_parse_sub(f, item[2])
                f.write(")E\n")
            elif item[0] == ml_yacc.HIDE:
                f.write("H(" + item[1] + "\n")
                save_low_parse_sub(f, item[2])
                f.write(")H\n")
            elif item[0] == ml_yacc.REPLACE:
                f.write("R(" + item[1] + "\n")
                save_low_parse_sub(f, item[2])
                f.write(")(" + item[3][0] + "\n")
                save_low_parse_sub(f, item[3][1])
                f.write(")R\n")
            elif item[0] == ml_yacc.DEFINE:
                f.write("D(" + item[1] + "\n")
                save_low_parse_sub(f, item[2])
                f.write(")(" + item[3][0] + "\n")
                save_low_parse_sub(f, item[3][1])
                f.write(")D\n")
            elif item[0] == ml_yacc.REFFER:
                f.write("C(" + item[1] + "\n")
                save_low_parse_sub(f, item[2])
                f.write(")(" + item[3][0] + "\n")
                save_low_parse_sub(f, item[3][1])
                f.write(")C\n")
            elif item[0] == ml_yacc.APPLY:
                f.write("A(" + item[1] + "\n")
                save_low_parse_sub(f, item[2])
                f.write(")(" + item[3][0] + "\n")
                save_low_parse_sub(f, item[3][1])
                f.write(")A\n")
            else:
                assert False, "save_low_parse_sub {}".format(item[1])
        elif type(item) is list:
                f.write("l[\n")
                save_low_parse_sub(f, item)
                f.write("]l\n")
        else:
            assert False, "save_low_parse_sub {}".format(item)

# def save_pdf():
#     file_type = [('ＰＤＦファイル', '*.pdf')]
#     global low_file_name
#     if low_file_name != None:
#         basename = os.path.splitext(os.path.basename(low_file_name))[0]
#     else:
#         basename = ""
#     file_name = filedialog.asksaveasfilename(
#             defaultextension="pdf",
#             filetypes=file_type,
#             initialfile=basename,
# #              [initialdir],
#             title="ＰＤＦファイルを保存")
#     dirname = os.path.dirname(file_name)
#     basename = os.path.splitext(os.path.basename(file_name))[0]
#     html_file_name = os.path.join(dirname, basename + '.html')
#
#     print(html_file_name)
#     print(file_name)
#     import pdfkit
#     options = {
#         'page-size': 'A4',
#         'margin-top': '0.1in',
#         'margin-right': '0.1in',
#         'margin-bottom': '0.1in',
#         'margin-left': '0.1in',
#         'encoding': "UTF-8",
#         'no-outline': None
#     }
#     pdfkit.from_file("testhtml.html", "testhtml.pdf")
# #     pdfkit.from_file(html_file_name, file_name, options=options)


def shuryou():
    global edit_flag
    if edit_flag:
        answer = messagebox.askyesnocancel("ファイル変更あり", "ファイルを保存しますか？")
        if answer is None:
            return
        elif answer:
            global low_file_name
            if low_file_name == None:
                save_new()
            else:
                save_file()
    global editor
    editor.root.destroy()
    sys.exit()


def set_title(editor_parm=None, flag_parm=None, file_parm=None):
    global editor, edit_flag, low_file_name
    if editor_parm is None:
        editor_parm = editor
    if flag_parm is None:
        flag_parm = edit_flag
    if file_parm is None:
        file_parm = low_file_name
    if file_parm is None:
        file_parm = ""

    editor_parm.root.title(
            "マークロウ（ＭａｒｋＬｏｗ）エディタ (version {:}) {}{}" \
            .format(__version__, "*" if flag_parm else " ", file_parm))

def on_closing():
    global edit_flag
    if edit_flag:
        answer = messagebox.askyesnocancel("ファイル変更あり", "ファイルを保存しますか？")
        if answer is None:
            return
        elif answer:
            global low_file_name
            if low_file_name == None:
                save_new()
            else:
                save_file()
    root.destroy()


def parsing(low_text):
    import ply.lex as lex
    lexer = lex.lexer
    if lexer != None:
        lexer.lexpos = 0
        lexer.lineno = 1
        state = 'INITIAL'
        lexer.lexre = lexer.lexstatere[state]             # Master regular expression. This is a list of
        lexer.lexretext = lexer.lexstateretext[state]         # Current regular expression strings
        lexer.lexstate = state     # Current lexer state
        lexer.lexstatestack = []       # Stack of lexer states
        lexer.lexerrorf = lexer.lexstateerrorf.get(state, None)         # Error rule (if any)
        lexer.lexeoff = lexer.lexstateeoff.get(state, None)           # EOF rule (if any)
        lexer.lexignore = lexer.lexstateignore.get(state, '')          # Ignored characters

    c.logfile = None
    global parser, low_parse
    low_parse = parser.parse(low_text)


def error_log(_):
    import ply.lex as lex
    lexer = lex.lexer
    if lexer != None:
        lexer.lexpos = 0
        lexer.lineno = 1
    c.logfile = open("error_log.txt", "w", encoding="utf_8")
    global parser
    global editor
    low_text = editor.entry_low.get('1.0', 'end -1c')
    parser.parse(low_text)
    c.logfile.close()

import csv

def readFile(fileName):
    '''
    CSVファイル（文字コードはutf-8でなく、ms932）を読み込む。

    Parameters
    ----------
    fileName : str
        読み込むCSVファイル名。

    Returns
    -------
    inputList : list of tuple of str
        読み込んだ各行の内容のリスト。
    '''
    inputList = []
    try:
        with open(fileName, "r", encoding="ms932", newline='') \
                as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                inputList.append(row)
        return inputList
    except OSError as e:
        # ver.0.22 2021/10/07
#         messagebox.showerror(
#             'ファイル読込エラー', e)
        return []
    else:
        pass

def readSettei():
    '''
    設定ファイルを読み込む。

     Parameters
    ----------
    fileName : str
        読み込む設定ファイル名。
    '''
    # v0.22 20211007
    global window_tate, window_yoko, text_tate, text_yoko
    global font_name, font_size, color_dict
    window_tate = int(650)
    window_yoko = int(1150)
    text_tate = int(16)
    text_yoko = int(120)
    font_name = "MS ゴシック"
    font_size = int(12)
    color_dict = {}
    color_dict["強調"] = ("#FFFFFF", "#FF0000")
    color_dict["挿入"] = ("#FFFFFF", "#ADFF2F")
    color_dict["取消線"] = ("#808080", "#FFFFFF")
    color_dict["読替"] = ("#A52A2A", "#FFFFFF")
    color_dict["読替２"] = ("#FFFFFF", "#A52A2A")
    color_dict["定義"] = ("#00FFFF", "#FFFFFF")
    color_dict["定義２"] = ("#FFFFFF", "#00FFFF")
    color_dict["参照"] = ("#1E90FF", "#FFFFFF")
    color_dict["参照２"] = ("#FFFFFF", "#1E90FF")
    color_dict["当てはめ"] = ("#BCBD22", "#FFFFFF")
    color_dict["当てはめ２"] = ("#FFFFFF", "#FFFF00")

    inputList = readFile("ml_editor_cfg.csv")
    if len(inputList) == 0:
#         return False
        return True
#     global color_list
#     color_list = []
    for inputLine in inputList:
        if inputLine[0] == "ウィンドゥ縦":
#             global window_tate
            window_tate = int(inputLine[1])
        elif inputLine[0] == "ウィンドゥ横":
#             global window_yoko
            window_yoko = int(inputLine[1])
        elif inputLine[0] == "テキストウィンドゥ縦":
#             global text_tate
            text_tate = int(inputLine[1])
        elif inputLine[0] == "テキストウィンドゥ横":
#             global text_yoko
            text_yoko = int(inputLine[1])
        elif inputLine[0] == "フォント":
#             global font_name, font_size
            font_name = inputLine[1]
            font_size = int(inputLine[2])
        elif (inputLine[0] == "強調") \
                or (inputLine[0] == "挿入") \
                or (inputLine[0] == "取消線") \
                or (inputLine[0] == "読替") \
                or (inputLine[0] == "読替２") \
                or (inputLine[0] == "定義") \
                or (inputLine[0] == "定義２") \
                or (inputLine[0] == "参照") \
                or (inputLine[0] == "参照２") \
                or (inputLine[0] == "当てはめ") \
                or (inputLine[0] == "当てはめ２"):
#             color_list.append((inputLine[0],
#                     inputLine[1],
#                     inputLine[2]))
            # ver.0.22 20211007
            color_dict[inputLine[0]] = \
                    (inputLine[1],
                    inputLine[2])
    del inputList
    return True


if __name__ == '__main__':
    if not readSettei():
        exit()
    global lexer
    lexer = None

    global parser
    parser = create_parser()
    global low_file_name
    low_file_name = None    # ファイル保存とタイトル表示で使う
    global edit_flag, low_parse
    edit_flag = False   # マークロウ構造体を再作成するか否か
    low_parse = None    # マークロウ構造体
    global editor
    editor = MlEditor()
    root = editor.create_window()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # v0.22 2021/10/05
    if len(sys.argv) == 2:
        filename = str(sys.argv[1])
#         load_file_main(filename)
        # ver.0.22 2021/10/07
        d.dprint(filename)
        load_low_parse_main(filename)
    root.mainloop()
