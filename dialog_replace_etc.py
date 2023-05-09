'''
Created on 2021/08/20
マークロウ(MarkLow, MarkLaw)の読替他用ダイアログ
@author: sue-t
'''

from tkinter import Toplevel, Button, Label, Entry, W, NORMAL, DISABLED
import re


class DialogReplaceEtc(object):
    '''
    読替等する文字列を入力するダイアログ
    '''

    def __init__(self, editor, file_name, command, str_title, str_org):
        self.editor = editor
        self.file_name = file_name if file_name is not None else ""
        self.dialog = Toplevel()
        self.command = command
        self.dialog.title(str_title)
        self.dialog.geometry("550x100")
        self.dialog.grab_set()
        self.dialog.grid()
        self.dialog.protocol("WM_DELETE_WINDOW",
                self.cancel)
        self.set_format(str_org)
        self.set_button()
#         self.re_alnum = re.compile(r'^[a-zA-Z0-9_\-]*$')
        # ver.0.22 2021/10/08
        self.re_alnum = re.compile(r'^[a-zA-Z0-9\-=|!]*$')

    def validate_command(self, string):
        return self.re_alnum.match(string) is not None

    def set_format(self, str_org):
        Label(self.dialog, text="指定文字列") \
                .grid(row=0, column=0)
#         Label(self.dialog, text=str_org) \
#                 .grid(row=0, column=1)
        # 20210831 ver 0.11
        Label(self.dialog, text=str_org) \
                .grid(row=0, column=1, columnspan=3, sticky=W)

        Label(self.dialog, text="ID") \
                .grid(row=1, column=0)
        vc = self.editor.root.register(self.validate_command)
        self.entry_id = Entry(self.dialog, width=10,
                validate='key', validatecommand=(vc, "%P"))
        self.entry_id.configure(font=("MS ゴシック", 12))
#         self.entry_id.grid(row=1, column=1)
        # 20210831 ver 0.11
        self.entry_id.grid(row=1, column=1, columnspan=1, sticky=W)
        Label(self.dialog, text="文字列") \
                .grid(row=2, column=0, sticky=W)
        self.entry_string = Entry(self.dialog, width=50)
        self.entry_string.configure(font=("MS ゴシック", 12))
        self.entry_string.grid(row=2, column=1, columnspan=3, sticky=W)

    def set_button(self):
        btOK = Button(
                self.dialog,
                text='OK',
                command=lambda : self.ok())
        btOK.grid(row=3, column=2, pady=5)
        btCancel = Button(
                self.dialog,
                text='Cancel',
                command=lambda : self.cancel())
        btCancel.grid(row=3, column=3, pady=6)

    def ok(self):
        id_code = self.entry_id.get()
        string = self.entry_string.get()
        # ver.0.22 2021/10/07
        from ml_parse import parse_init_alnum
        string = parse_init_alnum(string)
        start = self.editor.entry_low.index('sel.first')
        end = self.editor.entry_low.index('sel.last')
        self.editor.undo_str = self.editor.entry_low.get('1.0', 'end -1c')
        if self.command == "replace":
            if id_code == '':
                self.editor.entry_low.insert(end, "$)(" + string + ")")
            else:
                self.editor.entry_low.insert(end, \
                        "$)(" + id_code + ' ' + string + ")")
            self.editor.entry_low.insert(start, '($')
        elif self.command == "define":
            if id_code == '':
                self.editor.entry_low.insert(end, "|)(" + string + ")")
            else:
                self.editor.entry_low.insert(end, \
                        "|)(" + id_code + ' ' + string + ")")
            self.editor.entry_low.insert(start, '(|')
        elif self.command == "reffer":
            if id_code == '':
                self.editor.entry_low.insert(end, "&)(" + string + ")")
            else:
                self.editor.entry_low.insert(end, \
                        "&)(" + id_code + ' ' + string + ")")
            self.editor.entry_low.insert(start, '(&')
        elif self.command == "apply":
            if id_code == '':
                self.editor.entry_low.insert(end, '")(' + string + ")")
            else:
                self.editor.entry_low.insert(end, \
                        '")(' + id_code + ' ' + string + ")")
            self.editor.entry_low.insert(start, '("')
        global edit_flag, low_parse
        edit_flag = True
        low_parse = None
        from ml_editor import set_title
        set_title(self.editor, True, self.file_name)
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()

