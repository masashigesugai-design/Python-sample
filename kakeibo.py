# Step 4: CSV保存/読込つき 家計簿（完成版）
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

DATA_FILE = Path("kakeibo.csv")  # 同じフォルダに保存される

expenses: list[dict[str, object]] = []

def input_int(prompt: str) -> int:
    """整数を安全に入力する（空・文字・負数を防ぐ）"""
    while True:
        s = input(prompt).strip()
        try:
            value = int(s)
            if value < 0:
                print("0以上で入力してください。")
                continue
            return value
        except ValueError:
            print("数字で入力してください。")

def load_csv():
    """CSVから expenses を復元する"""
    expenses.clear()
    if not DATA_FILE.exists():
        return

    with DATA_FILE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # amountは文字列で入ってくるのでintに戻す
            row["amount"] = int(row["amount"])
            expenses.append(row)

def save_csv():
    """expenses をCSVに保存する"""
    with DATA_FILE.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["date", "amount", "category", "memo"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in expenses:
            writer.writerow(e)

def add_expense():
    print("\n[支出の追加]")
    ymd = input("日付(YYYY-MM-DD) 空なら今日: ").strip()
    if ymd == "":
        ymd = date.today().isoformat()

    amount = input_int("金額(円): ")
    category = input("カテゴリ（例: 食費/交通/娯楽）: ").strip() or "未分類"
    memo = input("メモ（空OK）: ").strip()

    expenses.append({"date": ymd, "amount": amount, "category": category, "memo": memo})
    save_csv()
    print("追加しました。（保存しました）")

def list_expenses():
    print("\n[一覧]")
    if not expenses:
        print("データがありません。")
        return

    total = 0
    for i, e in enumerate(expenses, start=1):
        total += int(e["amount"])
        print(f'{i:>2}. {e["date"]}  {int(e["amount"]):>7}円  {e["category"]:<6}  {e["memo"]}')
    print("-" * 40)
    print(f"合計: {total}円（{len(expenses)}件）")

def summary_by_category():
    print("\n[カテゴリ別集計]")
    if not expenses:
        print("データがありません。")
        return

    totals: dict[str, int] = {}
    grand = 0
    for e in expenses:
        cat = str(e["category"])
        amt = int(e["amount"])
        totals[cat] = totals.get(cat, 0) + amt
        grand += amt

    for cat, amount in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        ratio = amount / grand * 100 if grand else 0
        print(f"{cat:<8}: {amount:>8}円  ({ratio:>5.1f}%)")
    print("-" * 40)
    print(f"総計: {grand}円")

def delete_expense():
    print("\n[削除]")
    if not expenses:
        print("データがありません。")
        return

    list_expenses()
    idx = input_int("削除する番号: ")
    if not (1 <= idx <= len(expenses)):
        print("範囲外です。")
        return

    removed = expenses.pop(idx - 1)
    save_csv()
    print(f'削除しました: {removed["date"]} {removed["amount"]}円 {removed["category"]} {removed["memo"]}')

def show_menu():
    print("\n=== 家計簿（完成版）===")
    print("1) 支出を追加")
    print("2) 一覧表示")
    print("3) カテゴリ別集計")
    print("4) 削除")
    print("0) 終了")

def main():
    load_csv()
    print(f"データ件数: {len(expenses)}件（{DATA_FILE.name}）")
    while True:
        show_menu()
        choice = input("選択: ").strip()
        if choice == "1":
            add_expense()
        elif choice == "2":
            list_expenses()
        elif choice == "3":
            summary_by_category()
        elif choice == "4":
            delete_expense()
        elif choice == "0":
            print("終了します。")
            break
        else:
            print("0,1,2,3,4のいずれかを選んでください。")

if __name__ == "__main__":
    main()
