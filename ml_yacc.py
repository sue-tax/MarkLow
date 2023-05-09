# -*- encoding: utf-8 -*-
'''
マークロウのの構文解析
Created on 2021/08/17
@author: sue-t
'''

import ply.yacc as yacc

from ml_lex import tokens

import c
import d
import e


EMPHASIS = 1
INSERT = 2
SIMPLE = 3
ELLIPSIS = 4
HIDE = 5
REPLACE = 6
DEFINE = 7
REFFER = 8
APPLY = 9

RETURN = 17
TAB = 18
SPACE = 19
# 20211002 v0.21 #を追加
SHARP = 20  # マークロウテキスト内での表示位置調整で使用


def p_full0(p):
    '''
    full : block
        | all
        | return
    '''
    d.dprint_method_start()
    p[0] = [p[1]]
    d.dprint_method_end()

def p_full1(p):
    '''
    full : full block
        | full all
    '''
    d.dprint_method_start()
    p[0] = p[1]
    if (type(p[2]) is str) \
            and (type(p[1]) is list) \
            and (type(p[1][-1]) is str):
        p[0][-1] = p[0][-1] + p[2]
    else:
        p[0].append(p[2])
    d.dprint_method_end()

def p_full2(p):
    '''
    full : full return
    '''
    d.dprint_method_start()
    p[0] = p[1]
    p[0].append(p[2])
    d.dprint_method_end()


def p_block(p):
    '''
    block : block_emphasis
        | block_insert
        | block_ellipsis
        | block_hide
        | block_replace
        | block_define
        | block_reffer
        | block_apply
    '''
    d.dprint_method_start()
    p[0] = p[1]
    d.dprint_method_end()


def p_block_emphasis0(p):
    '''
    block_emphasis : LBRACKET full RBRACKET
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    p[0] = (EMPHASIS, '', p[2])
    d.dprint_method_end()

def p_block_emphasis1(p):
    '''
    block_emphasis : LBRACKET id SPACE full RBRACKET
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (EMPHASIS, p[2], p[4])
    d.dprint_method_end()

def p_block_emphasis2(p):
    '''
    block_emphasis : LBRACKET SPACE full RBRACKET
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (EMPHASIS, '', p[3])
    d.dprint_method_end()


def p_block_insert0(p):
    '''
    block_insert : LHAT full RHAT
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    p[0] = (INSERT, '', p[2])
    d.dprint_method_end()

def p_block_insert1(p):
    '''
    block_insert : LHAT id SPACE full RHAT
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (INSERT, p[2], p[4])
    d.dprint_method_end()

def p_block_insert2(p):
    '''
    block_insert : LHAT SPACE full RHAT
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (INSERT, '', p[3])
    d.dprint_method_end()


def p_block_ellipsis0(p):
    '''
    block_ellipsis : LPERCENT full RPERCENT
    '''
    d.dprint_method_start()
    p[0] = (ELLIPSIS, '', p[2])
    d.dprint_method_end()

def p_block_ellipsis1(p):
    '''
    block_ellipsis : LPERCENT id SPACE full RPERCENT
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (ELLIPSIS, p[2], p[4])
    d.dprint_method_end()

def p_block_ellipsis2(p):
    '''
    block_ellipsis : LPERCENT SPACE full RPERCENT
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (ELLIPSIS, '', p[3])
    d.dprint_method_end()


def p_block_hide0(p):
    '''
    block_hide : LTILDE full RTILDE
    '''
    d.dprint_method_start()
    p[0] = (HIDE, '', p[2])
    d.dprint_method_end()

def p_block_hide1(p):
    '''
    block_hide : LTILDE id SPACE full RTILDE
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    d.dprint(p[5])
    p[0] = (HIDE, p[2], p[4])
    d.dprint_method_end()

def p_block_hide2(p):
    '''
    block_hide : LTILDE SPACE full RTILDE
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (HIDE, '', p[3])
    d.dprint_method_end()


def p_block_replace0(p):
    '''
    block_replace : LDOLLAR full RDOLLAR phrase
    '''
    d.dprint_method_start()
    p[0] = (REPLACE, '', p[2], p[4])
    d.dprint_method_end()

def p_block_replace1(p):
    '''
    block_replace : LDOLLAR id SPACE full RDOLLAR phrase
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (REPLACE, p[2], p[4], p[6])
    d.dprint_method_end()

def p_block_replace2(p):
    '''
    block_replace : LDOLLAR SPACE full RDOLLAR phrase
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (REPLACE, '', p[3], p[5])
    d.dprint_method_end()


def p_block_define0(p):
    '''
    block_define : LPIPE full RPIPE phrase
    '''
    d.dprint_method_start()
    p[0] = (DEFINE, '', p[2], p[4])
    d.dprint_method_end()

def p_block_define1(p):
    '''
    block_define : LPIPE id SPACE full RPIPE phrase
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (DEFINE, p[2], p[4], p[6])
    d.dprint_method_end()

def p_block_define2(p):
    '''
    block_define : LPIPE SPACE full RPIPE phrase
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    d.dprint(p[5])
    p[0] = (DEFINE, '', p[3], p[5])
    d.dprint_method_end()


def p_block_reffer0(p):
    '''
    block_reffer : LAND full RAND phrase
    '''
    d.dprint_method_start()
    p[0] = (REFFER, '', p[2], p[4])
    d.dprint_method_end()

def p_block_reffer1(p):
    '''
    block_reffer : LAND id SPACE full RAND phrase
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (REFFER, p[2], p[4], p[6])
    d.dprint_method_end()

def p_block_reffer2(p):
    '''
    block_reffer : LAND SPACE full RAND phrase
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    d.dprint(p[5])
    p[0] = (REFFER, '', p[3], p[5])
    d.dprint_method_end()


def p_block_apply0(p):
    '''
    block_apply : LDOUBLE_QUOTATION full RDOUBLE_QUOTATION phrase
    '''
    d.dprint_method_start()
    p[0] = (APPLY, '', p[2], p[4])
    d.dprint_method_end()

def p_block_apply1(p):
    '''
    block_apply : LDOUBLE_QUOTATION id SPACE full RDOUBLE_QUOTATION phrase
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = (APPLY, p[2], p[4], p[6])
    d.dprint_method_end()

def p_block_apply2(p):
    '''
    block_apply : LDOUBLE_QUOTATION SPACE full RDOUBLE_QUOTATION phrase
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    d.dprint(p[5])
    p[0] = (APPLY, '', p[3], p[5])
    d.dprint_method_end()


def p_phrase0(p):
    '''
    phrase : LPAREN full RPAREN
    '''
#     phrase : LPAREN without_paren RPAREN
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    p[0] = ('', p[2])
    d.dprint_method_end()

def p_phrase1(p):
    '''
    phrase : LPAREN id SPACE full RPAREN
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    d.dprint(p[5])
    p[0] = (p[2], p[4])
    d.dprint_method_end()

def p_phrase2(p):
    '''
    phrase : LPAREN SPACE full RPAREN
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    d.dprint(p[2])
    d.dprint(p[3])
    d.dprint(p[4])
    p[0] = ('', p[3])
    d.dprint_method_end()


def p_id(p):
    '''
    id : ALNUM
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    p[0] = p[1]
    if c.logfile != None:
        c.logfile.write("id: " + p[1] + "\n")
    d.dprint_method_end()


def p_return0(p):
    '''
    return : KAIGYOU
    '''
    d.dprint_method_start()
    p[0] = (RETURN, 0)  # 20210823 本当の改行は1
    if c.logfile != None:
        c.logfile.write("return0: " + r"'n\n" + "\n")
    d.dprint_method_end()

def p_return1(p):
    '''
    return : newline
    '''
    d.dprint_method_start()
    p[0] = (RETURN, 1)
    if c.logfile != None:
        c.logfile.write("return1: " + r"\n" + "\n")
    d.dprint_method_end()

def p_return2(p):
    '''
    return : NO_RETURN
    '''
    d.dprint_method_start()
    p[0] = (RETURN, 2)
    if c.logfile != None:
        c.logfile.write("return2: " + r"'N\n" + "\n")
    d.dprint_method_end()

def p_tab(p):
    '''
    tab : TAB
    '''
    d.dprint_method_start()
    p[0] = TAB
    if c.logfile != None:
        c.logfile.write("tab: " + "'t" + "\n")
    d.dprint_method_end()

def p_space_hankaku(p):
    '''
    space_hankaku : SPACE_HANKAKU
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    if len(p[1]) == 2:
        p[0] = (SPACE, 0, 1)
        if c.logfile != None:
            c.logfile.write("space_hankaku: " + "'s" + "\n")
    else:
        p[0] = (SPACE, 0, int(p[1][2:]))
        if c.logfile != None:
            c.logfile.write("space_hankaku: " + "'s{}".format(int(p[1][2:])) + "\n")
    d.dprint_method_end()

def p_space_zenkaku(p):
    '''
    space_zenkaku : SPACE_ZENKAKU
    '''
    d.dprint_method_start()
    if len(p[1]) == 2:
        p[0] = (SPACE, 1, 1)
        if c.logfile != None:
            c.logfile.write("space_zenkaku: " + "'S" + "\n")
    else:
        p[0] = (SPACE, 1, int(p[1][2:]))
        if c.logfile != None:
            c.logfile.write("space_zenkaku: " + "'S{}".format(int(p[1][2:])) + "\n")
    d.dprint_method_end()

# 20211002 v0.21 #を追加
# マークロウテキスト内での表示位置調整で使用
def p_sharp(p):
    '''
    sharp : SHARP
    '''
    p[0] = SHARP
    if c.logfile != None:
        c.logfile.write("sharp: " + "#" + "\n")

def p_all0(p):
    '''
    all : OTHER
        | OTHER2
        | tab
        | space_hankaku
        | space_zenkaku
        | sharp
    '''
    d.dprint_method_start()
    d.dprint(p[1])
    if c.logfile != None:
        c.logfile.write("all0: " + p[1] + "\n")
    p[0] = p[1]
    d.dprint_method_end()

def p_error(p):
    if c.logfile != None:
        if p:
            c.logfile.write("構文エラー: " + str(p.value) + "\n")
        else:
            c.logfile.write("構文エラー: " \
                    + "対応するものがないうちに、文章の最後に到達" + "\n")
    if p:
        e.eprint("マークロウ構文エラー", "{} 行目の '{}'".format(p.lineno, p.value))
#         exit()
    else:
        e.eprint("マークロウ構文エラー", '対応するものがないうちに、文章の最後に到達')

def create_parser(start=None):
    return yacc.yacc(start=start)


if __name__ == '__main__':
    parser = yacc.yacc()

#     result = parser.parse(r"^資産'nの's4譲渡等'Sが^")
#     result = parser.parse(r"^1 資産^の^譲渡等^が^ 国内^")
#     result = parser.parse(r"&（配当等の額とみなす金額）&(_https://www.nta.go.jp/about/organization/ntc/kenkyu/ronsou/58/02/hajimeni.htm_)'n")
#     print(result)
#     result = parser.parse(r"$1 資産の%譲渡等%$(ab3 資産譲渡貸付役務提供)")
#     print(result)
#     result = parser.parse(r"$1 資産の%譲渡等%$( 資産譲渡貸付役務提供)")
#     print(result)

#     result = parser.parse(r"^文字(列^挿入^テスト)１２^")

#     result = parser.parse(r"テスト[強調]テスト")
#     print(result)

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

    data = '''
（国等に対して財産を寄附した場合の譲渡所得等の非課税）
第４０条
^第１項^
　国又は地方公共団体に対し財産の贈与又は遺贈があつた場合には、'n
所得税法第５９条第１項第１号の規定の適用については、'n
当該[財産の贈与又は遺贈がなかつたものとみなす]。'n
%公益社団法人、%~公益財団法人、~'n
特定一般法人（法人税法別表第２に掲げる一般社団法人及び一般財団法人で、同法第２条第９号の二イに掲げるものをいう。）'n
%その他の公益を目的とする事業（以下この項から第３項まで及び第５項において「公益目的事業」という。）を行う法人%'n
（%外国法人に該当するものを除く。%以下この条において「公益法人等」という。）'n
に対する財産%（国外にある土地その他の政令で定めるものを除く。以下この条において同じ。）%'n
の贈与%又は遺贈（当該公益法人等を設立するためにする財産の提供を含む。以下この条において同じ。）%で、'n
当該贈与又は遺贈が'n
教育又は科学の振興、文化の向上、社会福祉への貢献その他公益の増進に著しく寄与すること、'n
当該贈与又は遺贈に係る財産'n
（当該財産につき第３３条第１項に規定する収用等があつたことその他の政令で定める理由により当該財産の譲渡をした場合において、'n
当該譲渡による収入金額の全部に相当する金額をもつて取得した当該財産に代わるべき資産として政令で定めるものを取得したときは、'n
当該資産（次項、第３項及び第１６項において「代替資産」という。））が、'n
当該贈与又は遺贈があつた日から２年を経過する日までの期間'n
（当該期間内に当該公益法人等の当該公益目的事業の用に直接供することが困難である場合として政令で定める事情があるときは、政令で定める期間。次項において同じ。）内に、
当該公益法人等の当該公益目的事業の用に直接供され、又は供される見込みであることその他の政令で定める要件を満たすものとして'n
国税庁長官の承認を受けたものについても、また同様とする。
'''
#     data = "に対する財産（%国外にある土地その他の政令で定めるものを除く。%以下この条において同じ。）'n"
    data = '''
第三十七条^第一項^'n
　"内国法人"(Ａ社)が'n
各事業年度において支出した[寄附金の額]'n
（~次項の規定の適用を受ける寄附金の額を除く。~）の合計額のうち、'n
%その内国法人の当該事業年度終了の時の資本金等の額又は当該事業年度の所得の金額を基礎として%&政令&(法人税法施行令第７３条第１項_.ml_)で定めるところにより$計算した金額$(限度額)を'n
超える部分の金額は、'n
当該"内国法人"(Ａ社)の各事業年度の所得の金額の計算上、'n
[損金の額に算入しない]。'n
'''

    data = '(|あいうえお|)(ＡＢＣ)'
    data = "(&〔措置法第４０条第３項関係〕&)(_https://www.nta.go.jp/law/tsutatsu/kobetsu/shotoku/sochiho/800423/12\_2.htm#a-23-2_)"
    result = parser.parse(data)
    print(result)
    from MarkLow import low_to_form
    text = low_to_form(result)
    print(text)
#     result = parser.parse(
#         "３　資産の譲渡等が国内において行われたかどうかの判定は、"
#         "次の各号に掲げる場合の区分に応じ"
#         "当該各号に定める場所が国内にあるかどうかにより行うものとする。"
#         "ただし、第三号に掲げる場合において、"
#         "同号に定める場所がないときは、"
#         "当該資産の譲渡等は国内以外の地域で行われたものとする。"
#         "一　資産の譲渡又は貸付けである場合　当該譲渡又は貸付けが行われる時において当該資産が所在していた場所（当該資産が船舶、航空機、鉱業権、特許権、著作権、国債証券、株券その他の資産でその所在していた場所が明らかでないものとして政令で定めるものである場合には、政令で定める場所）"
#         "二　役務の提供である場合（次号に掲げる場合を除く。）　当該役務の提供が行われた場所（当該役務の提供が国際運輸、国際通信その他の役務の提供で当該役務の提供が行われた場所が明らかでないものとして政令で定めるものである場合には、政令で定める場所）"
#         "三　電気通信利用役務の提供である場合　当該電気通信利用役務の提供を受ける者の住所若しくは居所（現在まで引き続いて一年以上居住する場所をいう。）又は本店若しくは主たる事務所の所在地",
#         )
#     print(result)

#     result = parser.parse(
#         "２　保税地域から引き取られる外国貨物には、"
#         "この法律により、消費税を課する。"
#         )
#     print(result)
#
#     result = parser.parse(
#         "３　資産の譲渡等が国内において行われたかどうかの判定は、"
#         "次の各号に掲げる場合の区分に応じ"
#         "当該各号に定める場所が国内にあるかどうかにより行うものとする。"
#         "ただし、第三号に掲げる場合において、"
#         "同号に定める場所がないときは、"
#         "当該資産の譲渡等は国内以外の地域で行われたものとする。"
#         )
#     print(result)
