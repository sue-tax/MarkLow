# -*- encoding: utf-8 -*-
'''
Created on 2021/09/19
マークロウ(MarkLow)のブラウザソフト
@author: sue-t
'''

'''
複数のマークロウをタブ切替で表示する
　タブ名はファイル名を流用

読込は
　ml,
　mlp,
　整形テキストファイル（一部カラー表示できず）
表示エリア（スクロールバーあり）はウィンドウ全体

ウィンドゥサイズ、フォント、色は設定ファイルで指定

IDの活用?
'''
from tkinter import Tk, Menu, Frame, Label, Text, Scrollbar, Button, \
        NONE, HORIZONTAL, VERTICAL, END, NORMAL, DISABLED, \
        filedialog, messagebox
from tkinter import BOTH, X, Y, BOTTOM, RIGHT
import tkinter.ttk as ttk
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


# __version__ = 0.02
# __version__ = 0.03  # 桁合わせ(#)を採用
__version__ = 0.04  # ハイパーリンク機能


# TODO Textを形だけ入力可能し、コピーができるようにする？
# 括弧の移動も、検討


class MlBrowser(object):
    '''
    マークロウ（整形テキスト）の表示用のウィンドゥ
    '''

    def __init__(self):
#         global text_tate, text_yoko
#         self.text_height = text_tate
#         self.text_width = text_yoko

        self.color_form = True
#         self.color_html = False
#         self.color_md = False

    def create_window(self):
        '''
        マークロウの表示用のウィンドゥを作成する。

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

        self.nb = ttk.Notebook(self.root)
#         frame_form = self.create_frame_form()
#         nb.add(frame_form, text="test1", padding=2)
        self.nb.pack(expand=1, fill="both")

        set_title()
        return self.root

    def create_menu(self):
        menu_bar = Menu(self.root)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="parseを読込", command=load_parse)
        file_menu.add_command(label="マークロウを読込", command=load_marklow)
#         file_menu.add_command(label="整形テキストを読込", command=load_form)
        file_menu.add_separator()
        # 現在のタブを閉じる
        file_menu.add_command(label="終了", command=shuryou)
        menu_bar.add_cascade(label="ファイル", menu=file_menu)

        self.root.config(menu=menu_bar)


    def create_frame_form(self):
        frame = Frame(self.root)

        entry_form = Text(frame,
                width=250, height=150,
                wrap=NONE)
        global font_name, font_size
        entry_form.configure(font=(font_name, font_size))
        scrollbar_form_x = Scrollbar(frame, orient=HORIZONTAL,
                command=entry_form.xview)
        entry_form.configure(
                xscrollcommand=scrollbar_form_x.set)
        scrollbar_form_y = Scrollbar(frame, orient=VERTICAL,
                command=entry_form.yview)
        entry_form.configure(
                yscrollcommand=scrollbar_form_y.set)
        scrollbar_form_x.pack(side=BOTTOM, fill=X)
        scrollbar_form_y.pack(side=RIGHT, fill=Y)
        entry_form.pack(expand = True)

#         entry_form.configure(state=DISABLED)
        # v0.02 20210921
        entry_form.configure(state=NORMAL)
        entry_form.bind("<Key>", lambda e: ctrlEvent(e))
        # ver0.04 2021/10/11
        entry_form.bind('<Button-3>', right_click_form)
        entry_form.focus_set()

        entry_form.tag_config('NORMAL', foreground="black")
        global color_list
        for color_item in color_list:
            if color_item[0] == "強調":
                self.set_color(entry_form, 'EMPHASIS', color_item)
            elif color_item[0] == "挿入":
                self.set_color(entry_form, 'INSERT', color_item)
            elif color_item[0] == "取消線":
                self.set_color(entry_form, 'HIDE', color_item)
            elif color_item[0] == "読替":
                self.set_color(entry_form, 'REPLACE', color_item)
            elif color_item[0] == "読替２":
                self.set_color(entry_form, 'REPLACE2', color_item)
            elif color_item[0] == "定義":
                self.set_color(entry_form, 'DEFINE', color_item)
            elif color_item[0] == "定義２":
                self.set_color(entry_form, 'DEFINE2', color_item)
            elif color_item[0] == "参照":
                self.set_color(entry_form, 'REFFER', color_item)
            elif color_item[0] == "参照２":
                self.set_color(entry_form, 'REFFER2', color_item)
            elif color_item[0] == "当てはめ":
                self.set_color(entry_form, 'APPLY', color_item)
            elif color_item[0] == "当てはめ２":
                self.set_color(entry_form, 'APPLY2', color_item)
        return (frame, entry_form)

    def set_color(self, form, tag, color_item):
#         d.dprint(color_item)
        if (color_item[1] != "#FFFFFF") \
                and (color_item[2] != "#FFFFFF"):
            form.tag_config(tag,
                    foreground= color_item[1],
                    background=color_item[2])
        elif color_item[1] != "#FFFFFF":
            form.tag_config(tag,
                    foreground= color_item[1])
        elif color_item[2] != "#FFFFFF":
            form.tag_config(tag,
                    background= color_item[2])

    def create_form(self, title, low_parse):
        (frame, entry_form) = self.create_frame_form()
        entry_form.configure(state=NORMAL)
        self.create_form_sub(entry_form, low_parse, 'NORMAL')
        entry_form.configure(state=DISABLED)
        self.nb.add(frame, text=title, padding=2)
        self.nb.select(self.nb.tabs()[self.nb.index('end')-1])
        return frame

    def create_form_sub(self, frame, low_parse, tag):
        d.dprint_method_start()
        d.dprint(frame)
        d.dprint(low_parse)
        d.dprint(tag)
        for item in low_parse:
            if type(item) is str:
                frame.insert('end', item, tag)
            elif type(item) is int:
                if item == ml_yacc.TAB:
                    frame.insert('end', '\t', tag)
                # 20211002 v0.03 #を追加
                elif item == ml_yacc.SHARP:
                    pass
                else:
                    assert False, "create_form_sub int {}".format(item)
            elif type(item) is tuple:
                if item[0] == ml_yacc.SPACE:
                    if item[1] == 0:    # 's 半角空白
                        frame.insert('end', ' ' * item[2], tag)
                    elif item[1] == 1:  # 'S 全角空白
                        frame.insert('end', '　' * item[2], tag)
                    else:
                        assert False, "create_form_sub SPACE {}".format(item[2])
                elif item[0] == ml_yacc.RETURN: # 20210823
                    if item[1] == 0:    # 'n_
                        frame.insert('end', '\n', tag)
                    elif item[1] == 1:
                        frame.insert('end', '\n', tag)
                    else:
                        pass
                elif item[0] == ml_yacc.EMPHASIS:
                    frame.insert('end', '[', 'EMPHASIS')
                    self.create_form_sub(frame, item[2], 'EMPHASIS')
                    frame.insert('end', ']', 'EMPHASIS')
                elif item[0] == ml_yacc.INSERT:
                    self.create_form_sub(frame, item[2], 'INSERT')
                elif item[0] == ml_yacc.ELLIPSIS:
                    pass
                elif item[0] == ml_yacc.HIDE:
                    frame.insert('end', '~~~', 'HIDE')
                elif item[0] == ml_yacc.REPLACE:
                    self.create_form_sub(frame, item[3][1], 'REPLACE')
                elif item[0] == ml_yacc.DEFINE:
                    frame.insert('end', '(|', 'DEFINE')
                    self.create_form_sub(frame, item[2], 'DEFINE')
                    frame.insert('end', '|)', 'DEFINE')
                    frame.insert('end', '(', 'DEFINE2')
                    self.create_form_sub(frame, item[3][1], 'DEFINE2')
                    frame.insert('end', ')', 'DEFINE2')
                elif item[0] == ml_yacc.REFFER:
                    frame.insert('end', '(&', 'REFFER')
                    self.create_form_sub(frame, item[2], 'REFFER')
                    frame.insert('end', '&)', 'REFFER')
#                     frame.insert('end', '(', 'REFFER2')
                    # v0.04 20211011
                    frame.insert('end', '( ', 'REFFER2')
                    self.create_form_sub(frame, item[3][1], 'REFFER2')
#                     frame.insert('end', ')', 'REFFER2')
                    # v0.04 20211011
                    frame.insert('end', ' )', 'REFFER2')
                elif item[0] == ml_yacc.APPLY:
                    frame.insert('end', '("', 'APPLY')
                    self.create_form_sub(frame, item[2], 'APPLY')
                    frame.insert('end', '")', 'APPLY')
                    frame.insert('end', '(', 'APPLY2')
                    self.create_form_sub(frame, item[3][1], 'APPLY2')
                    frame.insert('end', ')', 'APPLY2')
                else:
                    assert False, "create_form_sub {}".format(item[1])
            elif type(item) is list:
                    self.create_form_sub(frame, item, tag)
            else:
                assert False, "create_form_sub {}".format(item)



def set_window_size():
    from dialog_widget import DialogWidget
    global editor
    DialogWidget(editor, editor.text_height, editor.text_width)

# ver0.04 2021/10/11
def right_click_form(e):
    '''整形テキストで右ボタンをクリック。リンクを開く'''
    d.dprint_method_start()
    global editor
    d.dprint(e.widget)
     # TODO アクティブを取得
    entry_form = e.widget
    try:
        start = entry_form.index('sel.first')
    except Exception as e:
        return
    end = entry_form.index('sel.last')
    if start == end:
        return
    link_text = entry_form.get(start, end)
    d.dprint(link_text)

    # ver.0.04 2021/10/11
    file_name = link_text
    dirname = os.path.dirname(file_name)
    basename = os.path.splitext(os.path.basename(file_name))[0]
    parse_file_name = os.path.join(dirname, basename + '.mlp')
    d.dprint(parse_file_name)
    if os.path.isfile(parse_file_name):
        load_parse_main(parse_file_name)
    elif os.path.isfile(file_name):
        load_marklow_main(file_name)
    else:
        d.dprint("ファイル名をどうする？")

#     global low_file_name
#     if low_file_name == None:
#         if os.path.isfile(link_text):
#             d.dprint("isfile true")
#             subprocess.run( \
#                     r' start ml_editor.exe "' + link_text + '"',
#                     shell=True)
#             return
#     if low_file_name != None:
#         dir_name = os.path.dirname(low_file_name)
#         file_name = os.path.join(dir_name, link_text)
#         d.dprint(file_name)
#         if os.path.isfile(file_name):
#             subprocess.run( \
#                     r' start ml_editor.exe "' + file_name + '"',
#                     shell=True)
#             return
#     import webbrowser
#     rv = webbrowser.open(link_text, new=0, autoraise=True)
#     # ファイル名でも起動しようとしてTrueが変える。
#     d.dprint(rv)
'''
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
'''
def ctrlEvent(event):
    d.dprint(event)
    if(12==event.state and event.keysym=='c' ):
        return
    else:
        return "break"

def load_marklow():
    file_type = [('マークロウファイル', '*.ml;*.ML'),
            ('テキストファイル', '*.txt'),
            ('', '*')]
#     dir = 'C:\\pg'
#     global low_file_name
    file_name = filedialog.askopenfilename(filetypes = file_type,
            title='マークロウファイルのファイル名')   # , initialdir = dir)
    if file_name == '':
        return
    load_marklow_main(file_name)

def load_marklow_main(file_name):
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
    parsing(read_text)
    global browser, low_parse
    basename = os.path.splitext(os.path.basename(file_name))[0]
    browser.create_form(basename, low_parse)


def load_parse():
    file_type = [('parseファイル', '*.mlp'),
            ('', '*')]
    file_name = filedialog.askopenfilename(filetypes = file_type,
            title='parseファイルのファイル名')
    if file_name == '':
        return
    load_parse_main(file_name)

def load_parse_main(file_name):
    try:
        f = open(file_name,
                "r",
                encoding="UTF-8")
        read_list = f.readlines()
        f.close()
    except OSError as e:
        messagebox.showwarning(
                'ファイル読込失敗', e)
        return
    global low_parse
    (low_parse, _) = load_low_parse_sub(0, read_list)
    global browser
    basename = os.path.splitext(os.path.basename(file_name))[0]
    d.dprint_name("file_name", file_name)
    browser.create_form(basename, low_parse)

# def load_low_parse_sub(index, read_list):
#     parse_list = []
#     line_no = index
#     line_len = len(read_list)
#     while line_no < line_len:
#         line = read_list[line_no]
#         if line[0] == "'":
#             if line[1] == "t":
#                 parse_list.append(ml_yacc.TAB)
#             elif line[1] == "s":
#                 num = int(line[2:])
#                 parse_list.append((ml_yacc.SPACE, 0, num))
#             elif line[1] == "S":
#                 num = int(line[2:])
#                 parse_list.append((ml_yacc.SPACE, 1, num))
#             elif line[1] == "n":
#                 num = int(line[2:])
#                 parse_list.append((ml_yacc.RETURN, num))
#             else:
#                 assert False, "load_low_parse_sub '{}".format(line[1:])
#             line_no += 1
#         elif line[0] == 'S':
#             assert line[1]=="(",  "load_low_parse_sub S not("
#             id_str = line[2:][:-1]
#             (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
#             assert read_list[line_no]==")S\n", "load_low_parse_sub not )S"
#             line_no += 1
#             parse_list.append((ml_yacc.EMPHASIS, id_str, parse))
#         elif line[0] == 'I':
#             assert line[1]=="(",  "load_low_parse_sub I not("
#             id_str = line[2:][:-1]
#             (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
#             assert read_list[line_no]==")I\n", "load_low_parse_sub not )I"
#             line_no += 1
#             parse_list.append((ml_yacc.INSERT, id_str, parse))
#         elif line[0] == 'E':
#             assert line[1]=="(",  "load_low_parse_sub E not("
#             id_str = line[2:][:-1]
#             (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
#             assert read_list[line_no]==")E\n", "load_low_parse_sub not )E"
#             line_no += 1
#             parse_list.append((ml_yacc.ELLIPSIS, id_str, parse))
#         elif line[0] == 'H':
#             assert line[1]=="(",  "load_low_parse_sub H not("
#             id_str = line[2:][:-1]
#             (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
#             assert read_list[line_no]==")H\n", "load_low_parse_sub not )E"
#             line_no += 1
#             parse_list.append((ml_yacc.HIDE, id_str, parse))
#         elif line[0] == 'R':
#             assert line[1]=="(",  "load_low_parse_sub R not("
#             id_str = line[2:][:-1]
#             (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
#             assert read_list[line_no][:2]==")(", "load_low_parse_sub not )("
#             id2_str = line[2:][:-1]
#             line_no += 1
#             (parse2, line_no) = load_low_parse_sub(line_no, read_list)
#             assert read_list[line_no]==")R\n", "load_low_parse_sub not )R"
#             line_no += 1
#             parse_list.append((ml_yacc.REPLACE, id_str, parse, (id2_str, parse2)))
#         elif line[0] == 'D':
#             assert line[1]=="(",  "load_low_parse_sub D not("
#             id_str = line[2:][:-1]
#             (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
#             assert read_list[line_no][:2]==")(", "load_low_parse_sub not )("
#             id2_str = line[2:][:-1]
#             line_no += 1
#             (parse2, line_no) = load_low_parse_sub(line_no, read_list)
#             assert read_list[line_no]==")D\n", "load_low_parse_sub not )D"
#             line_no += 1
#             parse_list.append((ml_yacc.DEFINE, id_str, parse, (id2_str, parse2)))
#         elif line[0] == 'C':
#             assert line[1]=="(",  "load_low_parse_sub C not("
#             id_str = line[2:][:-1]
#             (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
#             assert read_list[line_no][:2]==")(", "load_low_parse_sub not )("
#             id2_str = line[2:][:-1]
#             line_no += 1
#             (parse2, line_no) = load_low_parse_sub(line_no, read_list)
#             assert read_list[line_no]==")C\n", "load_low_parse_sub not )C"
#             line_no += 1
#             parse_list.append((ml_yacc.REFFER, id_str, parse, (id2_str, parse2)))
#         elif line[0] == 'A':
#             assert line[1]=="(",  "load_low_parse_sub A not("
#             id_str = line[2:][:-1]
#             (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
#             assert read_list[line_no][:2]==")(", "load_low_parse_sub not )("
#             id2_str = line[2:][:-1]
#             line_no += 1
#             (parse2, line_no) = load_low_parse_sub(line_no, read_list)
#             assert read_list[line_no]==")A\n", "load_low_parse_sub not )A"
#             line_no += 1
#             parse_list.append((ml_yacc.APPLY, id_str, parse, (id2_str, parse2)))
#         elif line[0] == 'l':
#             assert line[1]=="[",  "load_low_parse_sub l not["
#             parse_l_list = []
#             while True:
#                 (parse, line_no) = load_low_parse_sub(line_no + 1, read_list)
#                 parse_l_list.append(parse)
#                 line_no += 1
#                 if read_list[line_no] == "]l\n":
#                     break
#             line_no += 1
#             parse_list.append(parse_l_list)
#         elif line[0] == ')':
#             break
#         else:
#             line_no += 1
#             parse_list.append(line[:-1])
#     return (parse_list, line_no)
# v0.21 20210921
def load_low_parse_sub(index, read_list):
    parse_list = []
    line_no = index
    line_len = len(read_list)
    while line_no < line_len:
        line = read_list[line_no]
        if line[0:2] == "'t":
            parse_list.append(ml_yacc.TAB)
            line_no += 1
        # 20211002 v0.03 #を追加
        if line[0:1] == "#":
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

def load_form():
    pass


def shuryou():
    editor.root.destroy()
    sys.exit()


def set_title(browser_parm=None, flag_parm=None, file_parm=None):
    global browser
    if browser_parm is None:
        browser_parm = browser

    browser_parm.root.title(
            "マークロウ（ＭａｒｋＬｏｗ）ブラウザ (version {:})" \
            .format(__version__))

def on_closing():
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
        messagebox.showerror(
            'ファイル読込エラー', e)
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
    inputList = readFile("ml_browser_cfg.csv")
    if len(inputList) == 0:
        return False

    global color_list
    color_list = []
    for inputLine in inputList:
        if inputLine[0] == "ウィンドゥ縦":
            global window_tate
            window_tate = int(inputLine[1])
        elif inputLine[0] == "ウィンドゥ横":
            global window_yoko
            window_yoko = int(inputLine[1])
        elif inputLine[0] == "フォント":
            global font_name, font_size
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
            color_list.append((inputLine[0],
                    inputLine[1],
                    inputLine[2]))
    del inputList
    return True

if __name__ == '__main__':
    if not readSettei():
        exit()
    global lexer
    lexer = None

    global parser
    parser = create_parser()
    global browser
    browser = MlBrowser()
    root = browser.create_window()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


'''
import tkinter as tk

class Application(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)

        self.master.geometry("250x250")
        self.entry_form = Text(self.master, wrap=NONE)
        scrollbar_form_x = Scrollbar(self.master, orient=HORIZONTAL,
                command=self.entry_form.xview)
        self.entry_form.configure(
                xscrollcommand=scrollbar_form_x.set)
        scrollbar_form_y = Scrollbar(self.master, orient=VERTICAL,
                command=self.entry_form.yview)
        self.entry_form.configure(
                yscrollcommand=scrollbar_form_y.set)
        scrollbar_form_x.pack(side=tk.BOTTOM, fill=X)
        scrollbar_form_y.pack(side=tk.RIGHT, fill=Y)
        self.entry_form.pack(expand = True)

        self.entry_form.insert('end', "あああああああああああああああああああああ\n")
        self.entry_form.insert('end', "あああああああああああああああああああああ\n")
        self.entry_form.insert('end', "あああああああああああああああああああああ\n")
        self.entry_form.insert('end', "あああああああああああああああああああああ\n")
        self.entry_form.insert('end', "あああああああああああああああああああああ\n")
        self.entry_form.insert('end', "あああああああああああああああああああああ\n")
        self.entry_form.insert('end', "あああああああああああああああああああああ\n")
        self.entry_form.insert('end', "あああああああああああああああああああああ\n")
        self.entry_form.insert('end', "あああああああああああああああああああああ\n")
        self.entry_form.insert('end', "あああああああああああああああああああああ\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master = root)
    app.mainloop()
'''