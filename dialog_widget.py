'''
Created on 2021/09/13
ml_editorのwidgetサイズ変更用ダイアログ
@author: sue-t
'''

from tkinter import Toplevel, Button, Label, Entry, W, NORMAL, DISABLED
import re


class DialogWidget(object):
    '''
    widgetのサイズを入力するダイアログ
    '''

    def __init__(self, editor, height, width):
        self.editor = editor
        self.dialog = Toplevel()
        self.dialog.title("マークロウ・整形テキスト欄の大きさ")
        self.dialog.geometry("550x100")
        self.dialog.grab_set()
        self.dialog.grid()
        self.dialog.protocol("WM_DELETE_WINDOW",
                self.cancel)
        self.re_alnum = re.compile(r'^[0-9]*$')
        self.set_format(height, width)
        self.set_button()

    def validate_command(self, string):
        return self.re_alnum.match(string) is not None

    def set_format(self, height, width):
        Label(self.dialog, text="高さ") \
                .grid(row=0, column=0)
        Label(self.dialog, text="幅") \
                .grid(row=0, column=2)

        vc = self.editor.root.register(self.validate_command)
        self.entry_height = Entry(self.dialog, width=5,
                validate='key', validatecommand=(vc, "%P"))
        self.entry_height.insert(0, str(height))
        self.entry_height.configure(font=("MS ゴシック", 12))
        self.entry_height.grid(row=0, column=1, sticky=W)
        self.entry_width = Entry(self.dialog, width=5,
                validate='key', validatecommand=(vc, "%P"))
        self.entry_width.insert(0, str(width))
        self.entry_width.configure(font=("MS ゴシック", 12))
        self.entry_width.grid(row=0, column=4, sticky=W)

    def set_button(self):
        btOK = Button(
                self.dialog,
                text='OK',
                command=lambda : self.ok())
        btOK.grid(row=1, column=3, pady=5)
        btCancel = Button(
                self.dialog,
                text='Cancel',
                command=lambda : self.cancel())
        btCancel.grid(row=1, column=4, pady=6)

    def ok(self):
        height = int(self.entry_height.get())
        width = int(self.entry_width.get())
        self.editor.entry_form.config(height=height, width=width)
        self.editor.entry_low.config(height=height, width=width)
        self.editor.text_height = height
        self.editor.text_width = width
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()

