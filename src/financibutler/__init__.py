# -*- coding: utf-8 -*-

"""Financibutler
By Lin Lucas zhilin.tang@qq.com

A financial management system. 
You can easily manage your bills. 
Click the button to operate. 
Supports the export of the files."""

__version__ = "0.1.4a"

from tkinter import *
from tkinter import messagebox as MB
from tkinter import simpledialog as SD
from tkinter import filedialog as FD

import sys
import os
import appdirs

import datetime

from decimal import Decimal

import datetime

# Define const

DATE = "date"
THING = "thing"
MONEY = "money"
BALABCE = "balance"
TODAY = datetime.date.today()

__all__ = ["date","thing","money","balance"]
payments = []

base_dir = os.path.dirname(__file__)
zhPath = os.path.join(base_dir, "zh_cn.lang")
# 获取应用程序的名称和作者
appname = "Financibutler"
appauthor = "Lin Lucas"

# 获取用户数据目录
user_data_dir = appdirs.user_data_dir(appname, appauthor)

# 确保用户数据目录存在
os.makedirs(user_data_dir, exist_ok=True)

# 修改 repr.dat 文件路径
reprPath = os.path.join(base_dir, "repr.dat")

class Payment:
    def __init__(self, date, thing, money, balance):
        self.date = date
        self.thing = thing
        self.money = money
        self.balance = balance

    def display(self):
        CONDITION = self.money > 0
        return str(self.date), self.money, self.balance, self.thing


def read_from_file():
    global payments
    with open(reprPath, encoding="utf-8") as fileObj:
        for line in fileObj:
            thing, money, _date, balance = line.split("/")

            money = Decimal(money)
            balance = Decimal(balance)

            Y, M, D = _date.split("-")
            Y = int(Y)
            M = int(M)
            D = int(D)

            date = datetime.date(Y, M, D)
            payments.append(Payment(date, thing, money, balance))


def write_to_file():
    with open(reprPath, encoding="utf-8", mode="w") as fileObj:
        for i in payments:
            writeStr = (
                i.thing
                + "/"
                + str(i.money)
                + "/"
                + str(i.date)
                + "/"
                + str(i.balance)
                + "\n"
            )
            fileObj.write(writeStr)


def total_in():
    _total: Decimal = Decimal("0.0")
    for i in payments:
        if i.money > 0:
            _total += i.money
    return _total


def total_out():
    _total: Decimal = Decimal("0.0")
    for i in payments:
        if i.money < 0:
            _total += i.money
    return _total


langDis = []


def read_lang_file(lang):
    global langDis
    with open(zhPath, encoding="utf-8") as langFile:
        for line in langFile:
            langDis.append(line.rstrip("\n"))
    display_payments()
    display_texts()
    root.update()


def _askDate():
    while True:
        try:
            _date = SD.askstring("ASK", langDis[0])
            if _date.lower() == "today":
                date = datetime.date.today()
            else:
                Y, M, D = _date.split("-")
                Y = int(Y)
                M = int(M)
                D = int(D)
                date = datetime.date(Y, M, D)
            return date
        except:
            continueIn = MB.askretrycancel("!!!", langDis[1])
            if continueIn:
                continue
            else:
                return -1


def add_payment():
    global last_balance
    global continueIn
    dateAns = _askDate()
    if dateAns == -1:
        return
    else:
        while True:
            try:
                money = SD.askstring("ASK", langDis[2])
                if "." in money:
                    intMoney, floatMoney = money.split(".")
                    money = Decimal(intMoney + "." + floatMoney)
                else:
                    money = Decimal(money + ".00")
                break
            except:
                MB.showwarning("!!!", langDis[3])

        thing = SD.askstring("ASK", langDis[4])

        balance = last_balance + money
        payments.append(Payment(dateAns, thing, money, balance))
        last_balance = payments[-1].balance

        write_to_file()
        display_payments()


def sub_payment():
    number = SD.askinteger("ASK", langDis[5], minvalue=1)
    payments.pop(number - 1)

    write_to_file()
    display_payments()


def display_texts():
    global root
    global addBtn
    global subBtn
    global saveBtn
    global exitBtn
    global disTitle

    root.title(langDis[14])
    addBtn.config(text=langDis[15])
    subBtn.config(text=langDis[16])
    saveBtn.config(text=langDis[17])
    exitBtn.config(text=langDis[18])
    disTitle = langDis[6]


def display_payments():
    textCanvas.delete(ALL)
    global langDis
    global disTitle
    global last_balance
    dates = []
    moneys = []
    balances = []
    things = []

    for i in payments:
        date, money, balance, thing = i.display()
        dates.append(date)
        moneys.append(str(money))
        balances.append(str(balance))
        things.append(thing)

    disTitle = (
        langDis[6].format(len(payments), total_in(), total_out(), last_balance)
        + "\n\n"
        + langDis[7]
        + "\n"
        + langDis[8]
    )

    TEXT_HEIGHT = 100

    TEXT_TITLE = textCanvas.create_text(240, 50, text=disTitle)

    for j, i in enumerate(dates):
        text = str(j + 1) + "       " + str(i)
        textCanvas.create_text(130, (TEXT_HEIGHT + j * 17), text=text)

    for j, i in enumerate(moneys):
        is_out = i.startswith("-")
        color = "green" if is_out else "red"
        text = i if is_out else "+" + i
        textCanvas.create_text(230, (TEXT_HEIGHT + j * 17), text=text, fill=color)

    for j, i in enumerate(balances):
        text = str(i)
        textCanvas.create_text(313, (TEXT_HEIGHT + j * 17), text=text)

    for j, i in enumerate(things):
        text = str(i)
        textCanvas.create_text(390, (TEXT_HEIGHT + j * 17), text=text)


def save_to_file():
    saveFileName = FD.asksaveasfilename(
        defaultextension=".csv", filetypes=[(langDis[9], ".csv")]
    )
    writeStr = f"{langDis[10]}\n"
    with open(saveFileName, encoding="utf-8",mode="w") as fileObj:
        for j, i in enumerate(payments):
            writeStr += f"{j+1},{i.date},{i.thing},{i.money},{i.balance}\n"
        fileObj.write(writeStr + "\n")


def init_balance():
    global last_balance
    if len(payments) == 0:
        last_balance = SD.askstring("ASK", langDis[13])
        if "." in last_balance:
            intBalance, floatBalance = last_balance.split(".")
            last_balance = Decimal(intBalance + "." + floatBalance)
        else:
            last_balance = Decimal(last_balance + ".00")
    else:
        last_balance = payments[-1].balance


def main():
    global root,textCanvas,addBtn,subBtn,saveBtn,exitBtn
    root = Tk()
    root.title("财务管家")

    menuBar = Menu(root)
    langChooseMenu = Menu(menuBar, tearoff=False)
    menuBar.add_cascade(label="语言/languege", menu=langChooseMenu)
    langChooseMenu.add_command(
    label="简体中文", command=lambda x="zh_cn": read_lang_file(x)
)
    langChooseMenu.add_command(label="English", command=lambda x="en_us": read_lang_file(x))

    textCanvas = Canvas(root, width=500, height=500)
    textCanvas.pack()

    addBtn = Button(root, width=10, height=2, bd=5, bg="green", command=add_payment)
    # addBtn.grid(column=0,row=0)
    addBtn.pack(side=LEFT)

    subBtn = Button(root, width=10, height=2, bd=5, bg="yellow", command=sub_payment)
    subBtn.pack(side=LEFT)

    saveBtn = Button(
    root, width=10, height=2, bd=5, bg="blue", foreground="white", command=save_to_file
)
    saveBtn.pack(side=LEFT)

    exitBtn = Button(root, width=10, height=2, bd=5, bg="red", command=sys.exit)
    # exitBtn.grid(row=0, column=1)
    exitBtn.pack(side=RIGHT)

    read_from_file()
    init_balance()
    read_lang_file("zh_cn")

    DIS_STR = {False: langDis[12], True: langDis[11]}

    # Mainloop

    #root.config(menu=menuBar)
    root.bind("<Alt-F4>", root.destroy)
    root.mainloop()
if __name__ == "__main__":
    main()