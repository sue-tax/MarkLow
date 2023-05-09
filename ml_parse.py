# -*- encoding: utf-8 -*-
'''
マークロウの初期処理用の字句解析
　　lexが複数使えないため、自作
Created on 2021/08/27
@author: sue-t
'''


import re

import c
import d
import e


def parse_return_full(in_text):
    '''
    入力テキストをマークロウに合うように加工する。
    （の前,）,。,、の後に改行を追加する。

    Parameters
    ----------
    in_text : str
        入力データ。

    Returns
    -------
    out_text : str
        加工テキスト。
    '''
    d.dprint_method_start()
    out_text = _parse_return_sub(in_text, \
            flag_maru=True, flag_ten=True, flag_kakko= True)
    return out_text

def parse_return_maru(in_text):
    '''
    入力テキストをマークロウに合うように加工する。
    。の後に改行を追加する。

    Parameters
    ----------
    in_text : str
        入力データ。

    Returns
    -------
    out_text : str
        加工テキスト。
    '''
    d.dprint_method_start()
    out_text = _parse_return_sub(in_text,
            flag_maru=True, flag_ten=False, flag_kakko=False)
    return out_text

def parse_return_ten(in_text):
    '''
    入力テキストをマークロウに合うように加工する。
    、の後に改行を追加する。

    Parameters
    ----------
    in_text : str
        入力データ。

    Returns
    -------
    out_text : str
        加工テキスト。
    '''
    d.dprint_method_start()
    out_text = _parse_return_sub(in_text,
            flag_maru=False, flag_ten=True, flag_kakko=False)
    return out_text

def parse_return_kakko(in_text):
    '''
    入力テキストをマークロウに合うように加工する。
    （）の前後に改行を追加する。

    Parameters
    ----------
    in_text : str
        入力データ。

    Returns
    -------
    out_text : str
        加工テキスト。
    '''
    d.dprint_method_start()
    out_text = _parse_return_sub(in_text,
            flag_maru=False, flag_ten=False, flag_kakko=True)
    return out_text

def _parse_return_sub(in_text,
            flag_maru, flag_ten, flag_kakko):
    out_text = ""
    for index, c in enumerate(in_text):
        if c == '（':
            if flag_kakko:
                out_text += "'n\n"
            out_text += c
        elif c == '）':
            # 括弧の対応はチェックしない
            out_text += c
            if flag_kakko:
                if (index < len(in_text) -1) \
                        and in_text[index + 1] != '\n':
                    out_text += "'n\n"
        elif c == "。":
            out_text += c
            if flag_maru:
                if (index < len(in_text) -1) \
                        and in_text[index + 1] != '\n':
                    out_text += "'n\n"
        elif c == "、":
            out_text += c
            if flag_ten:
                if (index < len(in_text) -1) \
                        and in_text[index + 1] != '\n':
                    out_text += "'n\n"
        elif c == r'\n':
            out_text += c
        else:
            out_text += c
    return out_text


def parse_init_full(in_text):
    '''
    入力テキストをマークロウに合うように加工する。
    半角英数字をアンダースコアで囲う。
    括弧内を非表示設定にする。
    半角括弧を全角括弧にする。
    半角空白を削除する。

    Parameters
    ----------
    in_text : str
        入力データ。

    Returns
    -------
    out_text : str
        加工テキスト。
    '''
    d.dprint_method_start()
    global re_alnum
    re_alnum = re.compile(r'^[a-zA-Z0-9]*$')
    (out_text, _o_index, _kakko_level, _line_no, _pos) \
            = _parse_init_sub(in_text, index=0, \
            kakko_level=0, line_no=1, pos=1,
            flag_alnum=True, flag_hihyouji=True, \
            flag_kakko=True, flag_kuhaku=True)
    return out_text

def parse_init_alnum(in_text):
    '''
    入力テキストをマークロウに合うように加工する。
    半角英数字をアンダースコアで囲う。

    Parameters
    ----------
    in_text : str
        入力データ。

    Returns
    -------
    out_text : str
        加工テキスト。
    '''
    d.dprint_method_start()
    global re_alnum
    re_alnum = re.compile(r'^[a-zA-Z0-9 ]*$')
    (out_text, _o_index, _kakko_level, _line_no, _pos) \
            = _parse_init_sub(in_text, index=0, \
            kakko_level=0, line_no=1, pos=1,
            flag_alnum=True, flag_hihyouji=False, \
            flag_kakko=False, flag_kuhaku=False)
    return out_text

def parse_init_hihyouji(in_text):
    '''
    入力テキストをマークロウに合うように加工する。
    括弧内を非表示設定にする。

    Parameters
    ----------
    in_text : str
        入力データ。

    Returns
    -------
    out_text : str
        加工テキスト。
    '''
    d.dprint_method_start()
    global re_alnum
    re_alnum = re.compile(r'^[a-zA-Z0-9 ]*$')
    (out_text, _o_index, _kakko_level, _line_no, _pos) \
            = _parse_init_sub(in_text, index=0, \
            kakko_level=0, line_no=1, pos=1,
            flag_alnum=False, flag_hihyouji=True, \
            flag_kakko=False, flag_kuhaku=False)
    return out_text

def parse_init_kakko(in_text):
    '''
    入力テキストをマークロウに合うように加工する。
    半角括弧を全角括弧にする。

    Parameters
    ----------
    in_text : str
        入力データ。

    Returns
    -------
    out_text : str
        加工テキスト。
    '''
    d.dprint_method_start()
    global re_alnum
    re_alnum = re.compile(r'^[a-zA-Z0-9 ]*$')
    (out_text, _o_index, _kakko_level, _line_no, _pos) \
            = _parse_init_sub(in_text, index=0, \
            kakko_level=0, line_no=1, pos=1,
            flag_alnum=False, flag_hihyouji=False, \
            flag_kakko=True, flag_kuhaku=False)
    return out_text

def parse_init_kuhaku(in_text):
    '''
    入力テキストをマークロウに合うように加工する。
    半角空白を削除する。

    Parameters
    ----------
    in_text : str
        入力データ。

    Returns
    -------
    out_text : str
        加工テキスト。
    '''
    d.dprint_method_start()
    global re_alnum
    re_alnum = re.compile(r'^[a-zA-Z0-9]+\D')   # $だと、\nにマッチする
    (out_text, _o_index, _kakko_level, _line_no, _pos) \
            = _parse_init_sub(in_text, index=0, \
            kakko_level=0, line_no=1, pos=1,
            flag_alnum=False, flag_hihyouji=False, \
            flag_kakko=False, flag_kuhaku=True)
    return out_text

def parse_init_html_kuhaku(in_text):
    '''
    入力テキストをマークロウに合うように加工する。
    を削除する。

    Parameters
    ----------
    in_text : str
        入力データ。

    Returns
    -------
    out_text : str
        加工テキスト。
    '''
    d.dprint_method_start()
    global re_alnum
    re_alnum = re.compile(r'^[a-zA-Z0-9]+\D')   # $だと、\nにマッチする
    (out_text, _o_index, _kakko_level, _line_no, _pos) \
            = _parse_init_sub(in_text, index=0, \
            kakko_level=0, line_no=1, pos=1,
            flag_alnum=False, flag_hihyouji=False, \
            flag_kakko=False, flag_kuhaku=False, flag_html_kuhaku=True)
    return out_text


def _parse_init_sub(in_text, index, kakko_level, line_no, pos,
            flag_alnum, flag_hihyouji, flag_kakko, flag_kuhaku,
            flag_html_kuhaku=False):
    d.dprint_method_start()
    out_text = ""
    mode_alnum = False
    global re_alnum
    while index < len(in_text):
        c = in_text[index]
        if c == '（':    # 全角括弧
#             d.dprint("全角（")
            if mode_alnum:
                if flag_alnum:
                    out_text += '_'
                    mode_alnum = False
            if flag_hihyouji:
                (o_text, index, _kakko, line_no, pos) \
                        = _parse_init_sub(in_text, index + 1, \
                        kakko_level + 1, line_no, pos + 1,
                        flag_alnum, flag_hihyouji, flag_kakko, flag_kuhaku)
                out_text += '（(%' + str(kakko_level + 1) + ' ' + o_text
                if _kakko != kakko_level:
                    return (out_text, index, _kakko, line_no, pos)
            else:
                out_text += c
                index += 1
                pos += 1
        elif c == '）':  # 全角括弧
#             d.dprint("全角）")
#             if kakko_level == 0:
#                 e.eprint(r"括弧の数が合いません",
#                         r"右括弧）が多い。")
#                 return (out_text, index, kakko_level, line_no, pos)
            if mode_alnum:
                if flag_alnum:
                    out_text += '_'
                    mode_alnum = False
            # kakko_level 検討
            if kakko_level == 0:
                pass
            elif flag_hihyouji:
                out_text += '%)）'
                return (out_text, index + 1, kakko_level - 1, line_no, pos + 1)
#             else:
            out_text += c
            index += 1
            pos += 1
        elif c == '(':  # 半角括弧
#             d.dprint("半角(")
            if mode_alnum:
                if flag_alnum:
                    out_text += '_'
                    mode_alnum = False
            if flag_kakko:
                out_text += '（'
                if flag_hihyouji:
                    (o_text, index, _kakko, line_no, pos) \
                            = _parse_init_sub(in_text, index + 1, \
                            kakko_level + 1, line_no, pos + 1,
                            flag_alnum, flag_hihyouji, flag_kakko, flag_kuhaku)
                    out_text += '(%' + str(kakko_level + 1) + ' ' + o_text
                    if _kakko != kakko_level:
                        return (out_text, index, _kakko, line_no, pos)
            else:
                out_text += c
            index += 1
            pos += 1
        elif c == ')':  # 半角括弧
#             d.dprint("半角)")
            if mode_alnum:
                if flag_alnum:
                    out_text += '_'
                    mode_alnum = False
            if flag_kakko:
                if kakko_level == 0:
                    out_text += '）'
#                     e.eprint(r"括弧の数が合いません",
#                             r"右括弧）が多い。")
#                     return (out_text, index, kakko_level, line_no, pos)
                else:
                    if flag_hihyouji:
                        out_text += '%)）'
                        return (out_text, index + 1, kakko_level - 1, line_no, pos + 1)
                    else:
                        out_text += '）'
            else:
                out_text += c
            index += 1
            pos += 1
        elif c == ' ':
#             d.dprint("空白")
            if mode_alnum:
                out_text += c
            else:
                if flag_kuhaku:
                    pass
                else:
                    out_text += c
            index += 1
            pos += 1
        elif c == '\n':
#             d.dprint("改行")
            if mode_alnum:
                if flag_alnum:
                    out_text += '_'
                    mode_alnum = False
            out_text += c
            index += 1
            line_no += 1
            pos = 1
        elif c == '_':
            d.dprint("アンダースコア")
            if flag_alnum:
                if mode_alnum:
                    out_text += '\\' + c
                    d.dprint(out_text)
                else:
                    out_text += '_\\' + c
                    d.dprint(out_text)
                    mode_alnum = True
            else:
                out_text += c
            index += 1
            pos += 1
        elif re_alnum.match(c) is not None:
            # _abc_ に２重に付くのは仕方ない
#             d.dprint_name("半角英数","*"+c+"*")
            if flag_alnum:
                if mode_alnum:
                    out_text += c
                else:
                    out_text += '_' + c
                    mode_alnum = True
            else:
                out_text += c
            index += 1
            pos += 1
        elif c == '\u2003':
            # HTML上での全角空白
            if mode_alnum:
                if flag_alnum:
                    out_text += '_'
                    mode_alnum = False
            if flag_html_kuhaku:
                out_text += '　'
            else:
                out_text += c
            index += 1
            pos += 1
        else:
#             d.dprint_name("その他", c)
            if mode_alnum:
                out_text += '_'
                mode_alnum = False
            out_text += c
            index += 1
            pos += 1
    # EOF
    if kakko_level != 0:
        e.eprint(r"括弧の数が合いません",
                r"右括弧）が少ない。")
        return (out_text, index, kakko_level, line_no, pos)
    if mode_alnum:
        out_text += '_'
    d.dprint_method_end()
    return (out_text, index, kakko_level, line_no, pos)


if __name__ == '__main__':

    data = 'これは、テストです。（の処理が）うまく（いく（のだろう）か）？'
    data = '５　法第四十条第一項後段に規定する政令で定める要件は、次に掲げる要件（同項後段の贈与又は遺贈が法人税法別表第一に掲げる独立行政法人、国立大学法人、大学共同利用機関法人、地方独立行政法人（地方独立行政法人法第二十一条第一号に掲げる業務、同条第三号チに掲げる事業に係る同号に掲げる業務、同条第四号に掲げる業務、同条第五号に掲げる業務若しくは地方独立行政法人法施行令第六条第一号に掲げる介護老人保健施設若しくは介護医療院若しくは同条第三号に掲げる博物館、美術館、植物園、動物園若しくは水族館に係る同法第二十一条第六号に掲げる業務を主たる目的とするもの又は同法第六十八条第一項に規定する公立大学法人に限る。）及び日本司法支援センターに対するものである場合には、第二号に掲げる要件）とする。'
    data = '''
これは、テストです。
（の処理が）うまく（いく（のだろう）か）？
ＯＫ？
'''
#     data = '''
# これは、テストです。
# （の処理が）うまく（いく（のだろうか）？
# エラーのはず
# '''
    print(data)
#     o_text = initialize(data)
#     print(o_text)
