# -*- encoding: utf-8 -*-
'''
Created on 2021/08/16
マークロウ(MarkLow)
@author: sue-t
'''

'''
条文のテキストに記号等を直接記入してマークロウファイルを作る
マークロウファイルから本来の条文のテキストや加工後のテキストを作り出す
マークダウンファイル、HTMLファイルも作り出す

編集ソフト作成済み
テキスト出力の条件入力画面は検討中
'''

import c
import d
import ml_yacc


def low_to_original(low_parse):
    '''
    マークロウ構文データから、オリジナルテキストを作成する。
    'n, 't, 's, 'S, # を無視
    強調    …
    挿入    表示なし
    非表示    …
    取消線    …
    読替    …
    定義    …
    参照    …
    当てはめ    …

    Parameters
    ----------
    low_parse :
        マークロウ構文データ。

    Returns
    -------
    str_text : str
        プレーンテキスト。
    '''
    str_org = low_to_original_sub(low_parse)
    return str_org

def low_to_original_sub(low_parse):
    d.dprint_method_start()
    d.dprint(low_parse)
    str_text = ""
    for item in low_parse:
        if type(item) is str:
            str_text += item
        elif type(item) is int:
            if item == ml_yacc.TAB:
                pass
            # 20211002 v0.21 #を追加
            elif item == ml_yacc.SHARP:
                pass
            else:
                assert False, "low_to_original_sub int {}".format(item)
        elif type(item) is tuple:
            if item[0] == ml_yacc.SPACE:
                if item[1] == 0:    # 's 半角空白
                    pass
                elif item[1] == 1:  # 'S 全角空白
                    pass
                else:
                    assert False, "low_to_original_sub SPACE {}".format(item[2])
            elif item[0] == ml_yacc.RETURN: # 20210823
                if item[1] == 0:    # 'n_
                    pass
                elif item[1] == 1:
                    str_text += '\n'
                else:
                    str_text += '\n'
            elif item[0] == ml_yacc.EMPHASIS:
                str_text += low_to_original_sub(item[2])
            elif item[0] == ml_yacc.INSERT:
                pass
            elif item[0] == ml_yacc.ELLIPSIS:
                str_text += low_to_original_sub(item[2])
            elif item[0] == ml_yacc.HIDE:
                str_text += low_to_original_sub(item[2])
            elif item[0] == ml_yacc.REPLACE:
                str_text += low_to_original_sub(item[2])
            elif item[0] == ml_yacc.DEFINE:
                str_text += low_to_original_sub(item[2])
            elif item[0] == ml_yacc.REFFER:
                str_text += low_to_original_sub(item[2])
            elif item[0] == ml_yacc.APPLY:
                str_text += low_to_original_sub(item[2])
            else:
                assert False, "low_to_original_sub {}".format(item[1])
        elif type(item) is list:
            str_text += low_to_original_sub(item)
        else:
            assert False, "low_to_original_sub {}".format(item)
#         d.dprint(str_text)
    d.dprint_method_end()
    return str_text


def low_to_plain(low_parse):
    '''
    マークロウ構文データから、プレーンテキストを作成する。
    プレーンテキストは、オリジナルテキストに
    改行、タブ、空白だけを反映したテキスト。
    'n, 't, 's, 'S は反映
    強調    …
    挿入    表示なし
    非表示    …
    取消線    …
    読替    …
    定義    …
    参照    …
    当てはめ    …

    Parameters
    ----------
    low_parse :
        マークロウ構文データ。

    Returns
    -------
    str_text : str
        プレーンテキスト。
    '''
    str_text = low_to_plain_sub(low_parse)
    return str_text

def low_to_plain_sub(low_parse):
    d.dprint_method_start()
    d.dprint(low_parse)
    str_text = ""
    for item in low_parse:
        if type(item) is str:
            str_text += item
        elif type(item) is int:
            if item == ml_yacc.TAB:
                str_text += '\t'
            # 20211002 v0.21 #を追加
            elif item == ml_yacc.SHARP:
                pass
            else:
                assert False, "low_to_plain_sub int {}".format(item)
        elif type(item) is tuple:
            if item[0] == ml_yacc.SPACE:
                if item[1] == 0:    # 's 半角空白
                    str_text += ' ' * item[2]
                elif item[1] == 1:  # 'S 全角空白
                    str_text += '　' * item[2]
                else:
                    assert False, "low_to_plain_sub SPACE {}".format(item[2])
            elif item[0] == ml_yacc.RETURN: # 20210823
                if item[1] == 0:    # 'n
                    str_text += '\n'
                elif item[1] == 1:
                    str_text += '\n'
                else:
                    pass
            elif item[0] == ml_yacc.EMPHASIS:
                str_text += low_to_plain_sub(item[2])
            elif item[0] == ml_yacc.INSERT:
                pass
#             elif item[0] == ml_yacc.SIMPLE:
#                 str_text += low_to_plain_sub(item[2])
            elif item[0] == ml_yacc.ELLIPSIS:
                str_text += low_to_plain_sub(item[2])
            elif item[0] == ml_yacc.HIDE:
                str_text += low_to_plain_sub(item[2])
            elif item[0] == ml_yacc.REPLACE:
                str_text += low_to_plain_sub(item[2])
            elif item[0] == ml_yacc.DEFINE:
                str_text += low_to_plain_sub(item[2])
            elif item[0] == ml_yacc.REFFER:
                str_text += low_to_plain_sub(item[2])
            elif item[0] == ml_yacc.APPLY:
                str_text += low_to_plain_sub(item[2])
            else:
                assert False, "low_to_plain_sub {}".format(item[1])
        elif type(item) is list:
            str_text += low_to_plain_sub(item)
        else:
            assert False, "low_to_plain_sub {}".format(item)
#         d.dprint(str_text)
    d.dprint_method_end()
    return str_text


def low_to_form(low_parse):
    '''
    マークロウ構文データから、整形テキストを作成する。
    強調    […]
    挿入    …
    非表示    表示なし
    取消線    ~~~
    読替    ～
    定義    |…|～
    参照    &…&( ～ )
    当てはめ    "…"( ～ )

    Parameters
    ----------
    low_parse :
        マークロウ構文データ。

    Returns
    -------
    str_text : str
        整形テキスト。
    '''
    str_text = low_to_form_sub(low_parse)
    return str_text

def low_to_form_sub(low_parse):
    d.dprint_method_start()
    d.dprint(low_parse)
    str_text = ""
    for item in low_parse:
        if type(item) is str:
            str_text += item
        elif type(item) is int:
            if item == ml_yacc.TAB:
                str_text += '\t'
            else:
                assert False, "low_to_form_sub int {}".format(item)
        elif type(item) is tuple:
            if item[0] == ml_yacc.SPACE:
                if item[1] == 0:    # 's 半角空白
                    str_text += ' ' * item[2]
                elif item[1] == 1:  # 'S 全角空白
                    str_text += '　' * item[2]
                else:
                    assert False, "low_to_form_sub SPACE {}".format(item[2])
            elif item[0] == ml_yacc.RETURN: # 20210823
                if item[1] == 0:    # 'n_
                    str_text += '\n'
                elif item[1] == 1:
                    str_text += '\n'
                else:
                    pass
            elif item[0] == ml_yacc.EMPHASIS:
                str_text += '[' + low_to_form_sub(item[2]) + ']'
            elif item[0] == ml_yacc.INSERT:
                str_text += low_to_form_sub(item[2])
#             elif item[0] == ml_yacc.SIMPLE:
#                 str_text += low_to_form_sub(item[2])
            elif item[0] == ml_yacc.ELLIPSIS:
                pass
            elif item[0] == ml_yacc.HIDE:
                str_text += "~~~"
            elif item[0] == ml_yacc.REPLACE:
                str_text += low_to_form_sub(item[3][1])
            elif item[0] == ml_yacc.DEFINE:
                str_text += '(|' + low_to_form_sub(item[2]) + '|)' \
                        + '(' + low_to_form_sub(item[3][1]) + ')'
            elif item[0] == ml_yacc.REFFER:
#                 str_text += '(&' + low_to_form_sub(item[2]) + '&)' \
#                         + '(' + low_to_form_sub(item[3][1]) + ')'
                # ver.0.22 2021/10/07
                str_text += '(&' + low_to_form_sub(item[2]) + '&)' \
                        + '( ' + low_to_form_sub(item[3][1]) + ' )'
            elif item[0] == ml_yacc.APPLY:
                str_text += '("' + low_to_form_sub(item[2]) + '")' \
                        + '(' + low_to_form_sub(item[3][1]) + ')'
            else:
                assert False, "low_to_form_sub {}".format(item[1])
        elif type(item) is list:
            str_text += low_to_form_sub(item)
        else:
            assert False, "low_to_form_sub {}".format(item)
#         d.dprint(str_text)
    d.dprint_method_end()
    return str_text


def low_to_markdown(low_parse):
    '''
    マークロウ構文データから、マークダウンテキストを作成する。
    強調    太字(**…**)
    挿入    下線(<u>…</u>)
    非表示    注釈(...[^] [^]:…)
    取消線    取消線(~~…~~)
    読替    注釈(～[^] [^]:…)
    定義    注釈(…[^] [~]:～)
    参照    リンク([…](～))
    当てはめ    ハイライト("…"==～==)

    Parameters
    ----------
    low_parse :
        マークロウ構文データ。

    Returns
    -------
    str_text : str
        マークダウンテキスト。
    '''
    global num_remark
    num_remark = 1
    str_text, str_remark = low_to_markdown_sub(low_parse)
    return str_text + '\n' + str_remark

def low_to_markdown_sub(low_parse):
    d.dprint_method_start()
    d.dprint(low_parse)
    str_text = ""
    global num_remark
    str_remark = ""
    for item in low_parse:
        if type(item) is str:
            str_text += item
        elif type(item) is int:
            if item == ml_yacc.TAB:
                str_text += '\t'
            # 20211002 v0.21 #を追加
            elif item == ml_yacc.SHARP:
                pass
            else:
                assert False, "low_to_markdown_sub int {}".format(item)
        elif type(item) is tuple:
            if item[0] == ml_yacc.SPACE:
                if item[1] == 0:    # 's 半角空白
                    str_text += ' ' * item[2]
                elif item[1] == 1:  # 'S 全角空白
                    str_text += '　' * item[2]
                else:
                    assert False, "low_to_markdown_sub SPACE {}".format(item[2])
            elif item[0] == ml_yacc.RETURN: # 20210823
                if item[1] == 0:    # 'n_
                    str_text += '\n'
                elif item[1] == 1:
                    str_text += '\n'
                else:
                    pass
            elif item[0] == ml_yacc.EMPHASIS:
                str_t, str_r = low_to_markdown_sub(item[2])
                str_text += "**" + str_t + "**"
                str_remark += str_r
            elif item[0] == ml_yacc.INSERT:
                str_t, str_r = low_to_markdown_sub(item[2])
                str_text += "<u>" + str_t + "</u>"
                str_remark += str_r
#             elif item[0] == ml_yacc.SIMPLE:
#                 str_t, str_r = low_to_markdown_sub(item[2])
#                 str_text += str_t
#                 str_remark += str_r
            elif item[0] == ml_yacc.ELLIPSIS:
                str_t, str_r = low_to_markdown_sub(item[2])
                str_text += "...[^{}]".format(num_remark)
                str_remark += str_r + "[^{}]:{}\n" \
                        .format(num_remark, str_t)
                num_remark += 1
            elif item[0] == ml_yacc.HIDE:
                str_t, str_r = low_to_markdown_sub(item[2])
                str_text += "~~" + str_t + '~~'
                # 20210831 ver0.11
                str_remark += str_r
            elif item[0] == ml_yacc.REPLACE:
                str_t, str_r = low_to_markdown_sub(item[3][1])
                str_tt, str_rr = low_to_markdown_sub(item[2])
                str_text += str_t + '[^' + str(num_remark) + ']'
                str_remark += str_r + str_rr \
                        + '[^' + str(num_remark) + ']:' \
                        + str_tt + '\n'
                num_remark += 1
            elif item[0] == ml_yacc.DEFINE:
                str_t, str_r = low_to_markdown_sub(item[2])
                str_tt, str_rr = low_to_markdown_sub(item[3][1])
                str_text += str_t \
                        + '[^' + str(num_remark) + ']'
                str_remark += str_r + str_rr \
                        + '[^' + str(num_remark) + ']:' \
                        + str_tt + '\n'
                num_remark += 1
            elif item[0] == ml_yacc.REFFER:
                str_t, str_r = low_to_markdown_sub(item[2])
                str_tt, str_rr = low_to_markdown_sub(item[3][1])
                if str_tt[-3:] == ".ml":
                    str_tt = str_tt[:-1] + "d"
                str_text += "[" + str_t + ']' \
                        + '(' + str_tt + ')'
                str_remark += str_r + str_rr
            elif item[0] == ml_yacc.APPLY:
                str_t, str_r = low_to_markdown_sub(item[2])
                str_tt, str_rr = low_to_markdown_sub(item[3][1])
                str_text += '("' + str_t + '")' \
                        + "==" + str_tt + "=="
                str_remark += str_r + str_rr
            else:
                assert False, "low_to_markdown_sub {}".format(item[1])
        elif type(item) is list:
            str_t, str_r = low_to_markdown_sub(item)
            str_text += str_t
            str_remark += str_r
        else:
            assert False, "low_to_markdown_sub {}".format(item)
#         d.dprint(str_text)
    d.dprint_method_end()
    return str_text, str_remark


def low_to_html(low_parse):
    '''
    マークロウ構文データから、HTMLテキストを作成する。
    強調    大きめフォント(<big>…</big>)
    挿入    下線(<u>…</u>)
    非表示    ツールチップ表示(... title=…)
    取消線    取消線(<strike>…</strike>)
    読替    引用(<cite>～</cite> title=…)
    定義    ボールド(<bold>…</bold> title=～)
    参照    リンク([…](～))
    当てはめ    小さめ、強い強調(<small>…</small><strong>～</strong>)

    Parameters
    ----------
    low_parse :
        マークロウ構文データ。

    Returns
    -------
    str_text : str
        HTMLテキスト。
    '''
    global num_remark
    num_remark = 1
    str_text, str_remark = low_to_html_sub(low_parse)
    str_text = "<html><body>\n" \
            + str_text + '<br>\n' \
            + '<hr>' + str_remark \
            + "</body></html>"
    return str_text

def low_to_html_sub(low_parse):
    d.dprint_method_start()
    d.dprint(low_parse)
    str_text = ""
    global num_remark
    str_remark = ""
    for item in low_parse:
        if type(item) is str:
            str_text += item
        elif type(item) is int:
            if item == ml_yacc.TAB:
                str_text += '&#009;'
                # このままではダメ
                # <pre>が必要
            # 20211002 v0.21 #を追加
            elif item == ml_yacc.SHARP:
                pass
            else:
                assert False, "low_to_html_sub int {}".format(item)
        elif type(item) is tuple:
            if item[0] == ml_yacc.SPACE:
                if item[1] == 0:    # 's 半角空白
                    str_text += '&#160;' * item[2]
                elif item[1] == 1:  # 'S 全角空白
                    str_text += '　' * item[2]
                else:
                    assert False, "low_to_html_sub SPACE {}".format(item[2])
            elif item[0] == ml_yacc.RETURN: # 20210823
                if item[1] == 0:    # 'n_
                    str_text += '<br>\n'
                elif item[1] == 1:
                    str_text += '<br>\n'
                else:
                    pass
            elif item[0] == ml_yacc.EMPHASIS:
                str_t, str_r = low_to_html_sub(item[2])
                str_text += "<big>" + str_t + "</big>"
                str_remark += str_r
            elif item[0] == ml_yacc.INSERT:
                str_t, str_r = low_to_html_sub(item[2])
                str_text += "<u>" + str_t + "</u>"
                str_remark += str_r
#             elif item[0] == ml_yacc.SIMPLE:
#                 str_t, str_r = low_to_html_sub(item[2])
#                 str_text += str_t
#                 str_remark += str_r
            elif item[0] == ml_yacc.ELLIPSIS:
                str_t, str_r = low_to_html_sub(item[2])
                str_text += '<a href="#{}" title="{}">...<sup> [{}]</sup></a>' \
                        .format(num_remark, str_t, num_remark)
                str_remark += str_r + '<a name="{}">[{}] {}</a><br>' \
                        .format(num_remark, num_remark, str_t)
                num_remark += 1
            elif item[0] == ml_yacc.HIDE:
                str_t, str_r = low_to_html_sub(item[2])
                str_text += '<strike>' + str_t + '</strike>'
                str_remark += str_r
            elif item[0] == ml_yacc.REPLACE:
                str_t, str_r = low_to_html_sub(item[3][1])
                str_tt, str_rr = low_to_html_sub(item[2])
                str_text += \
                        '<a href="#{}" title="{}"><cite>{}</cite><sup> [{}]</sup></a>' \
                        .format(num_remark, str_tt, str_t, num_remark)
                str_remark += str_r + str_rr \
                        + '<a name="{}">[{}] {}</a><br>' \
                        .format(num_remark, num_remark, str_tt)
                num_remark += 1
            elif item[0] == ml_yacc.DEFINE:
                str_t, str_r = low_to_html_sub(item[2])
                str_tt, str_rr = low_to_html_sub(item[3][1])
                str_text += '<a href="#{}" title="{}"><b>{}</b><sup> [{}]</sup></a>' \
                        .format(num_remark, str_tt, str_t, num_remark)
                str_remark += str_r + str_rr \
                        + '<a name="{}">[{}] {}</a><br>' \
                        .format(num_remark, num_remark, str_tt)
                num_remark += 1
            elif item[0] == ml_yacc.REFFER:
                str_t, str_r = low_to_html_sub(item[2])
                str_tt, str_rr = low_to_html_sub(item[3][1])
                if str_tt[-3:] == ".ml":
                    str_tt = str_tt[:-2] + "html"
#                 str_ref = low_to_html_sub(item[3][1])
                str_text += '<a href="' + str_tt + '">' \
                        + str_t + '</a>'
                str_remark += str_r + str_rr
            elif item[0] == ml_yacc.APPLY:
                str_t, str_r = low_to_html_sub(item[2])
                str_tt, str_rr = low_to_html_sub(item[3][1])
                str_text += '<small>' + str_t + '</small>' \
                        + '<strong>' + str_tt + '</strong>'
                str_remark += str_r + str_rr
            else:
                assert False, "low_to_html_sub {}".format(item[1])
        elif type(item) is list:
            str_t, str_r = low_to_html_sub(item)
            str_text += str_t
            str_remark += str_r
        else:
            assert False, "low_to_html_sub {}".format(item)
#         d.dprint(str_text)
    d.dprint_method_end()
    return str_text, str_remark


if __name__ == '__main__':
    from ml_yacc import create_parser
    parser = create_parser()
    data = "(^あいう^)えお'n[かき'sく'n]けこ'n(^さし[す]せ^)そ"
    low_parse = parser.parse(data)

    str_text = low_to_plain(low_parse)
    print("str_text")
    print(str_text)
    print("")
    print("str_org")
    str_org = low_to_original(low_parse)
    print(str_org)
    print("")
    print("str_form")
    str_form = low_to_form(low_parse)
    print(str_form)
    str_md = low_to_markdown(low_parse)
    print("")
    print("str_md")
    print(str_md)
    str_html = low_to_html(low_parse)
    print("")
    print("str_html")
    print(str_html)
    print(low_parse)
