from tkinter import *
from tkinter import ttk
from ldap3 import Connection, MODIFY_REPLACE, SUBTREE, MODIFY_DELETE
import re
import getpass


class EntryPopup(ttk.Entry):
    def __init__(self, parent, iid, column, text, **kw):
        ttk.Style().configure('pad.TEntry', padding='1 1 1 1')
        super().__init__(parent, style='pad.TEntry', **kw)
        self.tv = parent
        self.iid = iid
        self.column = column
        self.insert(0, text)
        # self['state'] = 'readonly'
        # self['readonlybackground'] = 'white'
        # self['selectbackground'] = '#1BA1E2'
        self['exportselection'] = False
        self.focus_force()
        self.bind("<Return>", self.on_return)
        # self.bind("<Button-1>", lambda *ignore: self.destroy())
        self.bind("<Escape>", lambda *ignore: self.destroy())

    def on_return(self, event):
        rowid = self.tv.focus()
        vals = self.tv.item(rowid, 'values')
        vals = list(vals)

        connect_ad = connect_ldap()
        connect_ad.search(
            'OU= ,OU=,DC=,DC=local', f'(cn={vals[0]})')
        dn = str(connect_ad.entries)
        start_index = dn.find("CN")
        end_index = dn.find("local") + len("local")
        distinguishedName = dn[start_index:end_index]

        if self.get() == '':
            if vals[self.column] == vals[2]:
                connect_ad.modify(distinguishedName, {
                                  'title': [(MODIFY_DELETE, [vals[self.column]])]})
            if vals[self.column] == vals[3]:
                connect_ad.modify(distinguishedName, {'telephoneNumber': [
                                  (MODIFY_DELETE, [vals[self.column]])]})
            if vals[self.column] == vals[4]:
                connect_ad.modify(distinguishedName, {'mobile': [
                                  (MODIFY_DELETE, [vals[self.column]])]})
        else:
            vals[self.column] = self.get()
            if vals[self.column] == vals[2]:
                connect_ad.modify(distinguishedName, {
                                  'title': [(MODIFY_REPLACE, [vals[self.column]])]})
            if vals[self.column] == vals[3]:
                connect_ad.modify(distinguishedName, {'telephoneNumber': [
                                  (MODIFY_REPLACE, [vals[self.column]])]})
            if vals[self.column] == vals[4]:
                connect_ad.modify(distinguishedName, {'mobile': [
                                  (MODIFY_REPLACE, [vals[self.column]])]})
        connect_ad.unbind()
        self.tv.item(rowid, values=vals)
        self.destroy()


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.create_widgets()
        self.bind("<Button-1>", lambda *event: self.entryPopup_destroy(event))
        self.bind("<Button-2>", lambda *event: self.entryPopup_destroy(event))
        self.bind("<Button-3>", lambda *event: self.entryPopup_destroy(event))

    def create_widgets(self):
        self.label_input = Label(
            self, text='Введите информацию для поиска:', font=("Arial Bold", 20))
        self.search_var = StringVar()
        self.search_var.trace("w", self.update_list)
        self.entry = Entry(self, textvariable=self.search_var,
                           width=20, font=("Arial Bold", 20),)
        columns = ('Фамилия Имя Отчество', 'Подразделение',
                   'Должность', 'Внутренний телефон', 'Мобильный телефон')
        self.s = ttk.Style()
        self.s.theme_use('clam')
        self.tree = ttk.Treeview(
            self, columns=columns, show='headings', height=25)
        self.vsb = ttk.Scrollbar(
            self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)
        self.tree.column(column='#1', width=225, anchor=W,)
        self.tree.heading('Фамилия Имя Отчество', text='Фамилия Имя Отчество',
                          command=lambda: self.tree_sort_column(0, False))
        self.tree.column(column='#2', width=275, anchor=W, )
        self.tree.heading('Подразделение', text='Подразделение',
                          command=lambda: self.tree_sort_column(1, False))
        self.tree.column(column='#3', width=225, anchor=W)
        self.tree.heading('Должность', text='Должность',
                          command=lambda: self.tree_sort_column(2, False))
        self.tree.column(column='#4', width=140, anchor=S)
        self.tree.heading('Внутренний телефон', text='Внутренний телефон',
                          command=lambda: self.tree_sort_column(3, False))
        self.tree.column(column='#5', width=140, anchor=S)
        self.tree.heading('Мобильный телефон', text='Мобильный телефон',
                          command=lambda: self.tree_sort_column(4, False))
        self.tree.bind("<Double-1>", lambda event: self.onDoubleClick(event))
        self.tree.bind(
            "<Escape>", lambda event: self.entryPopup_destroy(event))
        self.tree.bind(
            "<Button-1>", lambda *event: self.entryPopup_destroy(event))
        self.tree.bind(
            "<Button-2>", lambda *event: self.entryPopup_destroy(event))
        self.tree.bind(
            "<Button-3>", lambda *event: self.entryPopup_destroy(event))
        self.entry.bind(
            "<Button-1>", lambda *event: self.entryPopup_destroy(event))
        self.entry.bind(
            "<Button-2>", lambda *event: self.entryPopup_destroy(event))
        self.entry.bind(
            "<Button-3>", lambda *event: self.entryPopup_destroy(event))
        self.label_input.bind(
            "<Button-1>", lambda *event: self.entryPopup_destroy(event))
        self.label_input.bind(
            "<Button-2>", lambda *event: self.entryPopup_destroy(event))
        self.label_input.bind(
            "<Button-3>", lambda *event: self.entryPopup_destroy(event))
        self.vsb.bind(
            "<Button-1>", lambda *event: self.entryPopup_destroy(event))
        self.vsb.bind(
            "<Button-2>", lambda *event: self.entryPopup_destroy(event))
        self.vsb.bind(
            "<Button-3>", lambda *event: self.entryPopup_destroy(event))
        self.label_input.grid(row=0, column=0, columnspan=2,
                              padx=10, pady=12, sticky=E)
        self.entry.grid(row=0, column=2, padx=40, pady=12, sticky=W)
        self.tree.grid(row=1, column=0, columnspan=3)
        self.vsb.grid(row=1, column=5, rowspan=25, columnspan=3, sticky=NS)

        self.entry.focus_set()
        self.update_list()

    def tree_sort_column(self, col, reverse):
        try:
            data_list = [(int(self.tree.set(k, col)), k)
                         for k in self.tree.get_children("")]
        except Exception:
            data_list = [(self.tree.set(k, col), k)
                         for k in self.tree.get_children("")]

        data_list.sort(reverse=reverse)

        for index, (val, k) in enumerate(data_list):
            self.tree.move(k, '', index)

        self.tree.heading(
            col, command=lambda: self.tree_sort_column(col, not reverse))

    def update_list(self, *args):

        search_term = self.search_var.get()
        connect_ad = connect_ldap()
        connect_ad.search(search_base='OU= ,OU=,DC=,DC=local', search_filter='(cn=*)',
                          search_scope=SUBTREE, attributes=['department', 'telephoneNumber', 'title', 'mobile'])
        cn_list = []
        department_list = []
        telephoneNumber_list = []
        title_list = []
        mobile_list = []
        for entry in connect_ad.entries:
            cn_list.append(str(re.findall(
                r'CN=([^,]+)', str(entry))).replace('[', '').replace(']', '').replace("'", ''))
            department_list.append(str(re.findall(
                r'department: ([^\r]+)', str(entry))).replace('[', '').replace(']', '').replace("'", ''))
            telephoneNumber_list.append(str(re.findall(
                r'telephoneNumber: ([^\r]+)', str(entry))).replace('[', '').replace(']', '').replace("'", ''))
            title_list.append(str(re.findall(
                r'title: ([^\r]+)', str(entry))).replace('[', '').replace(']', '').replace("'", ''))
            mobile_list.append(str(re.findall(
                r'mobile: ([^\r]+)', str(entry))).replace('[', '').replace(']', '').replace("'", ''))
        users_list = list(zip(cn_list, department_list,
                          title_list, telephoneNumber_list, mobile_list))

        for i in self.tree.get_children():
            self.tree.delete(i)

        for cn, dep, pos, tel, mob in users_list:
            if (search_term.lower() in str(cn).lower())\
                    or (search_term.lower() in str(dep).lower())\
                    or (search_term.lower() in str(pos).lower())\
                    or (search_term.lower() in str(tel).lower())\
                    or (search_term.lower() in str(mob).lower()):
                self.tree.insert('', 'end', values=(cn, dep, pos, tel, mob))

    def entryPopup_destroy(self, event):
        try:
            self.entryPopup.destroy()
        except AttributeError:
            pass

    def onDoubleClick(self, event):
        try:
            self.entryPopup.destroy()
        except AttributeError:
            pass
        rowid = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not rowid:
            return
        if column == '#1' or column == '#2':
            return
        x, y, width, height = self.tree.bbox(rowid, column)
        pady = height // 2
        text = self.tree.item(rowid, 'values')[int(column[1:])-1]
        self.entryPopup = EntryPopup(self.tree, rowid, int(column[1:])-1, text)
        self.entryPopup.place(x=x, y=y+pady, width=width,
                              height=height, anchor='w')


class PassApplication(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.user_label = Label(
            self, text=f'{getpass.getuser()}', font=("Arial Bold", 30))
        self.pass_input = Entry(self, show='*', width=14,
                                font=("Arial Bold", 20))
        self.pass_btn = Button(self, text='Вход', command=self.pass_check,
                               width=12, height=1, font=("Arial Bold", 21), foreground='indigo')
        self.user_label.grid(row=1, column=0, columnspan=1,
                             padx=5, pady=12, sticky=S)
        self.pass_input.grid(row=2, column=0, columnspan=2,
                             padx=10, pady=5, sticky=S)
        self.pass_btn.grid(row=3, column=0, columnspan=2,
                           padx=10, pady=12, sticky=S)
        self.pass_input.bind("<Return>", self.pass_check)
        self.pass_input.focus_set()

    def pass_check(self, *args):
        global pass_ad
        pass_ad = self.pass_input.get()
        try:
            connect_ldap()
            pass_root.destroy()
            root = Tk()

            root.title(
                f'Редактор атрибутов        Пользователь: {getpass.getuser()}')
            w, h = 1060, 600
            root.geometry(
                f"{w}x{h}+{(root.winfo_screenwidth()-w)//2}+{(root.winfo_screenheight()-h)//2}")
            root.resizable(width=False, height=False)
            app = Application(master=root)
            app.entry.focus_force()
            app.mainloop()
        except:
            self.pass_input.delete(0, END)
            pass_false_root = Tk()

            pass_false_root.title(f'{getpass.getuser()}')
            w, h = 300, 50
            pass_false_root.geometry(
                f"{w}x{h}+{(pass_false_root.winfo_screenwidth()-w)//2}+{(pass_false_root.winfo_screenheight()-h)//2}")
            pass_false_root.resizable(width=False, height=False)
            user_label = Label(
                pass_false_root, text=f'Неправильный пароль', font=("Arial Bold", 20))
            user_label.grid(column=0, row=0)
            user_label.pack()
            pass_false_root.after(800, pass_false_root.destroy)
            pass_false_root.mainloop()


def connect_ldap():
    return Connection('', user=f'\\{getpass.getuser()}', password=pass_ad, auto_bind=True)


pass_root = Tk()
# pass_root.iconbitmap(r'icon.ico')
pass_root.title(f'{getpass.getuser()}')
w, h = 300, 200
pass_root.geometry(
    f"{w}x{h}+{(pass_root.winfo_screenwidth()-w)//2}+{(pass_root.winfo_screenheight()-h)//2}")
pass_root.resizable(width=False, height=False)
pass_app = PassApplication(master=pass_root)
pass_app.mainloop()
