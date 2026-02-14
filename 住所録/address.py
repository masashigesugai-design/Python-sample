import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = "address.db"

# -----------------------------------
# DB 初期化
# -----------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            office_name TEXT,
            zipcode TEXT,
            address TEXT,
            phone TEXT,
            fax TEXT,
            note TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            position TEXT,
            direct_phone TEXT,
            mobile_phone TEXT,
            email TEXT,
            note TEXT,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

# -----------------------------------
# 親テーブル：企業登録
# -----------------------------------
def add_company():
    data = (
        entry_company.get(),
        entry_office.get(),
        entry_zip.get(),
        entry_address.get(),
        entry_phone.get(),
        entry_fax.get(),
        entry_note.get()
    )

    if data[0] == "":
        messagebox.showwarning("入力エラー", "企業名は必須です。")
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO companies
        (company_name, office_name, zipcode, address, phone, fax, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

    clear_company_inputs()
    load_companies()

def clear_company_inputs():
    entry_company.delete(0, tk.END)
    entry_office.delete(0, tk.END)
    entry_zip.delete(0, tk.END)
    entry_address.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_fax.delete(0, tk.END)
    entry_note.delete(0, tk.END)

# -----------------------------------
# 親テーブル一覧読み込み
# -----------------------------------
def load_companies():
    for row in tree_company.get_children():
        tree_company.delete(row)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, company_name, office_name, phone FROM companies")
    rows = cur.fetchall()
    conn.close()

    for r in rows:
        tree_company.insert("", tk.END, values=r)

# -----------------------------------
# 子画面へ遷移
# -----------------------------------
def open_members_window():
    selected = tree_company.selection()
    if not selected:
        messagebox.showwarning("選択エラー", "企業を選択してください。")
        return

    item = tree_company.item(selected[0])
    company_id = item["values"][0]
    company_name = item["values"][1]

    MembersWindow(company_id, company_name)

# -----------------------------------
# 子画面クラス
# -----------------------------------
class MembersWindow:
    def __init__(self, company_id, company_name):
        self.company_id = company_id

        self.win = tk.Toplevel()
        self.win.title(f"社員一覧 - {company_name}")
        self.win.geometry("600x400")

        tk.Label(self.win, text=f"【{company_name}】の社員登録").pack(pady=5)

        frame = tk.Frame(self.win)
        frame.pack()

        tk.Label(frame, text="氏名").grid(row=0, column=0)
        self.entry_name = tk.Entry(frame, width=30)
        self.entry_name.grid(row=0, column=1)

        tk.Label(frame, text="役職").grid(row=1, column=0)
        self.entry_position = tk.Entry(frame, width=30)
        self.entry_position.grid(row=1, column=1)

        tk.Label(frame, text="直通電話").grid(row=2, column=0)
        self.entry_direct = tk.Entry(frame, width=30)
        self.entry_direct.grid(row=2, column=1)

        tk.Label(frame, text="携帯電話").grid(row=3, column=0)
        self.entry_mobile = tk.Entry(frame, width=30)
        self.entry_mobile.grid(row=3, column=1)

        tk.Label(frame, text="メール").grid(row=4, column=0)
        self.entry_email = tk.Entry(frame, width=30)
        self.entry_email.grid(row=4, column=1)

        tk.Label(frame, text="備考").grid(row=5, column=0)
        self.entry_note = tk.Entry(frame, width=30)
        self.entry_note.grid(row=5, column=1)

        tk.Button(frame, text="登録", command=self.add_member).grid(row=6, column=0, columnspan=2, pady=5)

        # 一覧
        columns = ("ID", "氏名", "役職", "携帯")
        self.tree = ttk.Treeview(self.win, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(self.win, text="選択した社員を削除", command=self.delete_member).pack(pady=5)

        self.load_members()

    def add_member(self):
        data = (
            self.company_id,
            self.entry_name.get(),
            self.entry_position.get(),
            self.entry_direct.get(),
            self.entry_mobile.get(),
            self.entry_email.get(),
            self.entry_note.get()
        )

        if data[1] == "":
            messagebox.showwarning("入力エラー", "氏名は必須です。")
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO members
            (company_id, name, position, direct_phone, mobile_phone, email, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()
        conn.close()

        self.load_members()

    def load_members(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, position, mobile_phone
            FROM members
            WHERE company_id = ?
        """, (self.company_id,))
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            self.tree.insert("", tk.END, values=r)

    def delete_member(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("選択エラー", "削除する社員を選んでください。")
            return

        item = self.tree.item(selected[0])
        member_id = item["values"][0]

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()
        conn.close()

        self.load_members()

# -----------------------------------
# メイン画面
# -----------------------------------
init_db()

root = tk.Tk()
root.title("住所録プリ（企業・社員管理）")
root.geometry("700x500")

# 入力欄
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="企業名").grid(row=0, column=0)
entry_company = tk.Entry(frame_input, width=30)
entry_company.grid(row=0, column=1)

tk.Label(frame_input, text="営業所名").grid(row=1, column=0)
entry_office = tk.Entry(frame_input, width=30)
entry_office.grid(row=1, column=1)

tk.Label(frame_input, text="郵便番号").grid(row=2, column=0)
entry_zip = tk.Entry(frame_input, width=30)
entry_zip.grid(row=2, column=1)

tk.Label(frame_input, text="住所").grid(row=3, column=0)
entry_address = tk.Entry(frame_input, width=30)
entry_address.grid(row=3, column=1)

tk.Label(frame_input, text="電話番号").grid(row=4, column=0)
entry_phone = tk.Entry(frame_input, width=30)
entry_phone.grid(row=4, column=1)

tk.Label(frame_input, text="FAX番号").grid(row=5, column=0)
entry_fax = tk.Entry(frame_input, width=30)
entry_fax.grid(row=5, column=1)

tk.Label(frame_input, text="備考").grid(row=6, column=0)
entry_note = tk.Entry(frame_input, width=30)
entry_note.grid(row=6, column=1)

tk.Button(frame_input, text="企業を登録", command=add_company).grid(row=7, column=0, columnspan=2, pady=5)

# 一覧
columns = ("ID", "企業名", "営業所名", "電話番号")
tree_company = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    tree_company.heading(col, text=col)
tree_company.pack(fill=tk.BOTH, expand=True)

tk.Button(root, text="選択した企業の社員一覧へ", command=open_members_window).pack(pady=5)

load_companies()
root.mainloop()