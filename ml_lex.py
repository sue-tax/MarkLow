# -*- encoding: utf-8 -*-
'''
マークロウの字句解析
Created on 2021/08/17
@author: sue-t
'''

import ply.lex as lex

import c
import d
import e


# 20211002 v0.21 #を追加
tokens = (
    'LHAT',
    'RHAT',
    'LPERCENT',
    'RPERCENT',
    'LDOLLAR',
    'RDOLLAR',
    'LPIPE',
    'RPIPE',
    'LAND',
    'RAND',
    'LDOUBLE_QUOTATION',
    'RDOUBLE_QUOTATION',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'LTILDE',
    'RTILDE',

    'KAIGYOU',
    'TAB',
    'SPACE_HANKAKU',
    'SPACE_ZENKAKU',
    'SHARP',

    'SPACE',
    'ALNUM',
    'OTHER',
    'OTHER2',
    'newline',  # 20210823
    'NO_RETURN',    # 20210907
)

states = (
    ('hankaku', 'exclusive'),)


t_LHAT = r'\(\^'
t_RHAT = r'\^\)'
t_LPERCENT = r'\(%'
t_RPERCENT = r'%\)'
t_LDOLLAR = r'\(\$'
t_RDOLLAR = r'\$\)'
t_LPIPE = r'\(\|'
t_RPIPE = r'\|\)'
t_LAND = r'\(&'
t_RAND = r'&\)'
t_LDOUBLE_QUOTATION = r'\("'
t_RDOUBLE_QUOTATION = r'"\)'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LTILDE = r'\(~'
t_RTILDE = r'~\)'



# 関数定義が優先されてしまうらしい
# def t_LPAREN(t):
#     r'\('
#     if c.logfile != None:
#         c.logfile.write("LPAREN: " + "(" + "\n")
#     return t

# def t_RPAREN(t):
#     r'\)'
#     if c.logfile != None:
#         c.logfile.write("RPAREN: " + ")" + "\n")
#     return t



t_SPACE = r'\ '
# t_ALNUM = r'[a-zA-Z0-9]+'
# t_ALNUM = r'[a-zA-Z0-9\-=|!]+'
# 2021/10/22 リンク用の|と被る、要検討
# t_ALNUM = r'[a-zA-Z0-9\-=!]+'
t_ALNUM = r'([a-zA-Z0-9\-=!]|(\|(?!\))))+'


t_TAB = r"'t"
t_SPACE_HANKAKU = r"'s[0-9]*"
t_SPACE_ZENKAKU = r"'S[0-9]*"
# 20211002 v0.21 #を追加
t_SHARP = r"\#"  # マークロウテキスト内での表示位置調整で使用

# 20211002 v0.21 #を追加
t_OTHER = r'[^\#^\'\^%\$\|&"\\\(\)\[\]_\ \na-zA-Z0-9\-=|!~]+'

def t_OTHER2(t):
    r'(\\\^|\\%|\\\$|\\&|\\\||\\"|\\~|\\\\|\\\(|\\\)|\\_)'
    t.value = t.value[1]
    return t

def t_KAIGYOU(t):
    r"'n\n?"
    if len(t.value) != 1:
        t.lexer.lineno += 1
        # 20210905
#         t.lexer.lexpos = 1
    t.value = t.value[:2]
    return t

def t_NO_RETURN(t):
    r"'N"
    t.lexer.lineno += 1
    t.value = t.value[:2]
    return t

def t_newline(t):
    r'\n'
    t.lexer.lineno += 1
    # 20210905
#     t.lexer.lexpos = 1
    return t    # 20210823

def t_error(t):
    e.eprint(r"エラー",
            r"エラー　'{}行目{}文字目　'{}'"  \
            .format(t.lineno, t.lexpos, t.value[0]))
    t.lexer.skip(1)


def t_begin_hankaku(t):
    r'_'
    t.lexer.begin('hankaku')

def t_hankaku_end(t):
    r'_'
    t.lexer.begin('INITIAL')

t_hankaku_OTHER = r'[^_\\]+'
# t_hankaku_OTHER2 = r'\\_+'

# def t_hankaku_OTHER2(t):
#     r'\\_'
#     t.value = t.value[1]
#     return t
# ver.0.22 2021/10/07
def t_hankaku_OTHER2(t):
    r'(\\_|\\\\)'
    t.value = t.value[1]
    return t

def t_hankaku_newline(t):
    r'\n'
    t.lexer.lineno += 1
    # 20210905
#     t.lexer.lexpos = 1
    return t

def t_hankaku_error(t):
    e.eprint(r"エラー",
            r"_内 エラー　'{}行目{}文字目　'{}'"  \
            .format(t.lineno, t.lexpos, t.value[0]))
    t.lexer.skip(1)

# lexer を構築
global lexer
lexer = lex.lex()


if __name__ == '__main__':
#     import re
#
#     pattern = re.compile(r'^([AB]|(\|(?!\))))+')
#
#     print(bool(pattern.search('|)AABB')))
#     print(bool(pattern.search('|aAABB')))
#     print(bool(pattern.search('BAABB')))
#     exit()

#     data = '''
# （配当等とみなす金額）
# 第二十五条
# 　"|法人|(houjin （<法人税法第二条第六号（定義）>(法人税法第２条.ml)に規定する公益法人等及び人格のない社団等を除く。以下この項において同じ。）)"(株式会社森商事) の'n
# "株主等"(森一郎)が当該法人の次に掲げる事由により'n
# 金銭~~その他の資産~~の交付を受けた場合において、'n
# その金銭の額~~及び金銭以外の資産の価額~~'n
# ( （同条第十二号の十五に規定する適格現物分配に係る資産にあつては、当該法人のその交付の直前の当該資産の帳簿価額に相当する金額） )'n
# の"合計額"(goukei 100万円)が'n
# 当該法人の<同条第十六号>(法人税法第２条.ml)に規定する資本金等の額
# ~~又は同条第十七号の二に規定する連結個別資本金等の額~~
# のうちその交付の基因となつた当該法人の株式~~又は出資~~に対応する部分の"金額"( 50万円)を超えるときは、'n
# この法律の規定の適用については、'n
# その超える部分の金額に係る金銭~~その他の資産~~は、'n
# 前条第一項に規定する剰余金の配当、利益の配当、剰余金の分配又は金銭の分配とみなす。
# '''
#     data = r'\$あいう\|'
#     data = r"^資産'nの's4譲渡等'Sが^"
# #     data = r"^資産^"
#
# #     data = '''
# # &（配当等の額とみなす金額）&(_https://www.nta.go.jp/about/organization/ntc/kenkyu/ronsou/58/02/hajimeni.htm_)'n
# # '''
#
# #     data = r'てすと_adaf838ｄ\_adaf_終了'
# #     data = r'てすと_adaf838ｄadaf_終了'
# #     data = r"&（配当等の額とみなす金額）&(_https://www.nta.go.jp/about/organization/ntc/kenkyu/ronsou/58/02/hajimeni.htm_)'n"
#     data = r"テスト[強調]テスト"
#     data = '''
#  三十一'n
# 　[ひとり親]'n
# 　現に婚姻をしていない者又は配偶者の生死の明らかでない者で'n
# &政令で定めるもの&(11 |前条各号に掲げる者|(一　太平洋戦争の終結の当時もとの陸海軍に属していた者で、まだ国内に帰らないもの
# 二　前号に掲げる者以外の者で、太平洋戦争の終結の当時国外にあつてまだ国内に帰らず、かつ、その帰らないことについて同号に掲げる者と同様の事情があると認められるもの
# 三　船舶が沈没し、転覆し、滅失し若しくは行方不明となつた際現にその船舶に乗つていた者若しくは船舶に乗つていてその船舶の航行中に行方不明となつた者又は航空機が墜落し、滅失し若しくは行方不明となつた際現にその航空機に乗つていた者若しくは航空機に乗つていてその航空機の航行中に行方不明となつた者で、三月以上その生死が明らかでないもの
# 四　前号に掲げる者以外の者で、死亡の原因となるべき危難に遭遇した者のうちその危難が去つた後一年以上その生死が明らかでないもの
# 五　前各号に掲げる者のほか、三年以上その生死が明らかでない者)の配偶者)のうち、次に掲げる要件を満たすものをいう。'n
# 'tイ　その者と生計を一にする子で&政令で定めるもの&(その年分の総所得金額、退職所得金額及び山林所得金額の合計額が四十八万円以下の子（他の者の同一生計配偶者又は扶養親族とされている者を除く。）)を有すること。'n
# 'tロ　合計所得金額が五百万円以下であること。'n
# 'tハ　その者と事実上婚姻関係と同様の事情にあると認められる者として'n
# &財務省令で定めるもの&(次の各号に掲げる場合の区分に応じ当該各号に定める者とする。
# 一　その者が住民票に世帯主と記載されている者である場合　その者と同一の世帯に属する者の住民票に世帯主との続柄が世帯主の未届の夫又は未届の妻である旨その他の世帯主と事実上婚姻関係と同様の事情にあると認められる続柄である旨の記載がされた者
# 二　その者が住民票に世帯主と記載されている者でない場合　その者の住民票に世帯主との続柄が世帯主の未届の夫又は未届の妻である旨その他の世帯主と事実上婚姻関係と同様の事情にあると認められる続柄である旨の記載がされているときのその世帯主)がいないこと。'n
# '''
#     data = '''
#  三十一'n
# 　[ひとり親]'n
# 　現に婚姻をしていない者'n
# '''
#     data = '''
# （国等に対して財産を寄附した場合の譲渡所得等の非課税）
# 第４０条
# ^第１項^
# 　国又は地方公共団体に対し財産の贈与又は遺贈があつた場合には、'n
# 所得税法第５９条第１項第１号の規定の適用については、'n
# 当該[財産の贈与又は遺贈がなかつたものとみなす]。'n
# %公益社団法人、%~公益財団法人、~'n
# 特定一般法人（法人税法別表第２に掲げる一般社団法人及び一般財団法人で、同法第２条第９号の二イに掲げるものをいう。）'n
# %その他の公益を目的とする事業（以下この項から第３項まで及び第５項において「公益目的事業」という。）を行う法人%'n
# （%外国法人に該当するものを除く。%以下この条において「公益法人等」という。）'n
# に対する財産%（国外にある土地その他の政令で定めるものを除く。以下この条において同じ。）%'n
# の贈与%又は遺贈（当該公益法人等を設立するためにする財産の提供を含む。以下この条において同じ。）%で、'n
# 当該贈与又は遺贈が'n
# 教育又は科学の振興、文化の向上、社会福祉への貢献その他公益の増進に著しく寄与すること、'n
# 当該贈与又は遺贈に係る財産'n
# （当該財産につき第３３条第１項に規定する収用等があつたことその他の政令で定める理由により当該財産の譲渡をした場合において、'n
# 当該譲渡による収入金額の全部に相当する金額をもつて取得した当該財産に代わるべき資産として政令で定めるものを取得したときは、'n
# 当該資産（次項、第３項及び第１６項において「代替資産」という。））が、'n
# 当該贈与又は遺贈があつた日から２年を経過する日までの期間'n
# （当該期間内に当該公益法人等の当該公益目的事業の用に直接供することが困難である場合として政令で定める事情があるときは、政令で定める期間。次項において同じ。）内に、
# 当該公益法人等の当該公益目的事業の用に直接供され、又は供される見込みであることその他の政令で定める要件を満たすものとして'n
# 国税庁長官の承認を受けたものについても、また同様とする。
# '''

#     data ="(|あいうえお|)(ＡＢＣ)"

#     print(lexer.lexstate)# = 'INITIAL'     # Current lexer state
#     print(lexer.lexstatestack)# = []       # Stack of lexer states
#     print(lexer.lexstateinfo)# = None      # State information
#     print(lexer.lexstateignore)# = {}      # Dictionary of ignored characters for each state
#     print(lexer.lexstateerrorf)# = {}      # Dictionary of error functions for each state
#     print(lexer.lexstateeoff)# = {}        # Dictionary of eof functions for each state



    data = "(|五年施行日|)(ID|OK 令和五年十月一日)"
    print(data)
    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            # これ以上トークンはない
            break
        print(tok)

#     print(lexer.lexstate)# = 'INITIAL'     # Current lexer state
#     print(lexer.lexstatestack)# = []       # Stack of lexer states
#     print(lexer.lexstateinfo)# = None      # State information
#     print(lexer.lexstateignore)# = {}      # Dictionary of ignored characters for each state
#     print(lexer.lexstateerrorf)# = {}      # Dictionary of error functions for each state
#     print(lexer.lexstateeoff)# = {}        # Dictionary of eof functions for each state

    data = "_abc_def_"
    print(data)
    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            # これ以上トークンはない
            break
        print(tok)

#     print(lexer.lexstate)# = 'INITIAL'     # Current lexer state
#     print(lexer.lexstatestack)# = []       # Stack of lexer states
#     print(lexer.lexstateinfo)# = None      # State information
#     print(lexer.lexstateignore)# = {}      # Dictionary of ignored characters for each state
#     print(lexer.lexstateerrorf)# = {}      # Dictionary of error functions for each state
#     print(lexer.lexstateeoff)# = {}        # Dictionary of eof functions for each state

    state = 'INITIAL'
    lexer.lexre = lexer.lexstatere[state]             # Master regular expression. This is a list of
#                                 tuples (re, findex) where re is a compiled
#                                 regular expression and findex is a list
#                                 mapping regex group numbers to rules
    lexer.lexretext = lexer.lexstateretext[state]         # Current regular expression strings
#     lexer.lexstatere = {}          # Dictionary mapping lexer states to master regexs
#     lexer.lexstateretext = {}      # Dictionary mapping lexer states to regex strings
#     lexer.lexstaterenames = {}     # Dictionary mapping lexer states to symbol names
    lexer.lexstate = state     # Current lexer state
    lexer.lexstatestack = []       # Stack of lexer states
#     lexer.lexstateinfo = None      # State information
#     lexer.lexstateignore = {}      # Dictionary of ignored characters for each state
#     lexer.lexstateerrorf = {}      # Dictionary of error functions for each state
#     lexer.lexstateeoff = {}        # Dictionary of eof functions for each state
#     lexer.lexreflags = 0           # Optional re compile flags
#     lexer.lexdata = None           # Actual input data (as a string)
#     lexer.lexpos = 0               # Current position in input text
#     lexer.lexlen = 0               # Length of the input text
    lexer.lexerrorf = lexer.lexstateerrorf.get(state, None)         # Error rule (if any)
    lexer.lexeoff = lexer.lexstateeoff.get(state, None)           # EOF rule (if any)
#     lexer.lextokens = None         # List of valid tokens
    lexer.lexignore = lexer.lexstateignore.get(state, '')          # Ignored characters
#     lexer.lexliterals = ''         # Literal characters that can be passed through
#     lexer.lexmodule = None         # Module
#     lexer.lineno = 1               # Current line number
#     lexer.lexoptimize = False      # Optimized mode
#         self.lexre = self.lexstatere[state]
#         self.lexretext = self.lexstateretext[state]
#         self.lexignore = self.lexstateignore.get(state, '')
#         self.lexerrorf = self.lexstateerrorf.get(state, None)
#         self.lexeoff = self.lexstateeoff.get(state, None)
#         self.lexstate = state

#     print(lexer.lexstate)# = 'INITIAL'     # Current lexer state
#     print(lexer.lexstatestack)# = []       # Stack of lexer states
#     print(lexer.lexstateinfo)# = None      # State information
#     print(lexer.lexstateignore)# = {}      # Dictionary of ignored characters for each state
#     print(lexer.lexstateerrorf)# = {}      # Dictionary of error functions for each state
#     print(lexer.lexstateeoff)# = {}        # Dictionary of eof functions for each state

    data = "_abc\_def_"
    print(data)
    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            # これ以上トークンはない
            break
        print(tok)
