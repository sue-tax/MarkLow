# -*- encoding: utf-8 -*-
'''
マークロウの初期処理用の字句解析
Created on 2021/08/27
@author: sue-t
'''

import ply.lex as lex

import c
import d
import e


tokens = (
    'KUHAKU_HTML',
    'HIDARI_KAKKO',
    'MIGI_KAKKO',
    'MARU',
    'TEN',
    'KAIGYOU',
    'OTHER',
)

states = (
    ('kakkonai', 'inclusive'),)


t_KUHAKU_HTML = b'a0'   # スペース     &nbsp;     &#160
# t_HIDARI_KAKKO = r'（'
# t_MIGI_KAKKO = r'）'
t_MARU = r'。'
t_TEN = r'、'

def t_KAIGYOU(t):
    r'\n'
    t.lexer.lineno += 1
    return t

t_OTHER = r'[^（）。、\n]+'

# def t_eof(t):

def t_error(t):
    e.eprint(r"エラー",
            r"{}行目{}文字目　{}"  \
            .format(t.lineno, t.lexpos, t.value[0]))
    t.lexer.skip(1)


def t_HIDARI_KAKKO(t):  # begin_kakkonai(t):
    r'（'
    t.lexer.begin('kakkonai')
    t.lexer.level = 1
    return t

def t_kakkonai_MIGI_KAKKO(t):
    r'）'
    t.lexer.level -= 1
    if t.lexer.level == 0:
        t.lexer.begin('INITIAL')
    return t

def t_kakkonai_HIDARI_KAKKO(t):
    r'（'
    t.lexer.level += 1
    return t

def t_kakkonai_eof(t):
    e.eprint(r"括弧の数が合いません",
            r"右括弧が{}個、足りません。".format(t.lexer.level))
    t.lexer.begin('INITIAL')

def t_kakkonai_error(t):
    e.eprint(r"エラー",
            r"括弧内のエラー　'{}行目{}文字目　{}'"  \
            .format(t.lineno, t.lexpos, t.value[0]))
    t.lexer.skip(1)


lexer = lex.lex()


if __name__ == '__main__':

#     data = 'これは、テストです。（の処理が）うまく（いく（のだろう）か）？'
    data = '''
これは、テストです。
（の処理が）うまく（いく（のだろう）か）？
ＯＫ？
'''
    data = '''
これは、テストです。
（の処理が）うまく（いく（のだろうか）？
エラーのはず
'''
    print(data)
    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            # これ以上トークンはない
            break
        print(tok)
