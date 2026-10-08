"""报销记账小程序：运行 python3 bookkeeping.py。"""

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


DATA_FILE = Path(__file__).with_name("reimbursements.json")


def load_records():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open(encoding="utf-8") as file:
        records = json.load(file)
    if not isinstance(records, list):
        raise ValueError("数据格式不正确")
    for record in records:
        if (
            not isinstance(record, dict)
            or not isinstance(record.get("id"), int)
            or not isinstance(record.get("project"), str)
            or record.get("status") not in ("待报销", "已报销")
            or not Decimal(record["amount"]).is_finite()
        ):
            raise ValueError("记录格式不正确")
    return records


def save_records(records):
    # 先写临时文件再替换，避免写入中断损坏原来的记录。
    temporary = DATA_FILE.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temporary.replace(DATA_FILE)


def register(records):
    project = input("请输入需要报销的项目：").strip()
    if not project:
        print("项目不能为空，未登记。")
        return
    try:
        amount = Decimal(input("请输入金额（元，最多两位小数）：").strip())
        if (
            not amount.is_finite()
            or amount <= 0
            or amount > Decimal("1000000000")
            or amount != amount.quantize(Decimal("0.01"))
        ):
            raise ValueError
    except (InvalidOperation, ValueError):
        print("金额须大于 0、不超过 10 亿元，且最多两位小数，未登记。")
        return
    record = {
        "id": max((item["id"] for item in records), default=0) + 1,
        "project": project,
        "amount": format(amount, ".2f"),
        "status": "待报销",
    }
    updated = records + [record]
    save_records(updated)
    records[:] = updated
    print(f"登记成功！编号：{record['id']}，状态：待报销。")


def show_records(records, status):
    selected = [record for record in records if record["status"] == status]
    print(f"\n===== {status} =====")
    if not selected:
        print("暂无记录。")
        return
    for record in selected:
        print(f"编号 {record['id']} | {record['project']} | {record['amount']} 元")
    total = sum((Decimal(record["amount"]) for record in selected), Decimal("0"))
    print(f"共 {len(selected)} 笔，合计：{total:.2f} 元")


def query(records):
    while True:
        print("\n===== 查询 =====\n1. 待报销\n2. 已报销\n3. 返回主菜单")
        choice = input("请选择：").strip()
        if choice == "1":
            show_records(records, "待报销")
            if not any(record["status"] == "待报销" for record in records):
                continue
            number = input("输入编号标记为已报销（直接回车返回）：").strip()
            if not number:
                continue
            target = next(
                (record for record in records
                 if str(record["id"]) == number and record["status"] == "待报销"),
                None,
            )
            if target is None:
                print("没有这个待报销编号。")
                continue
            updated = [
                {**record, "status": "已报销"} if record is target else record.copy()
                for record in records
            ]
            save_records(updated)
            records[:] = updated
            print(f"编号 {number} 已标记为已报销。")
        elif choice == "2":
            show_records(records, "已报销")
        elif choice == "3":
            return
        else:
            print("请输入 1、2 或 3。")


def main():
    try:
        records = load_records()
    except (OSError, ValueError, KeyError, TypeError, InvalidOperation) as error:
        print(f"无法读取记账数据：{error}。请检查 {DATA_FILE}，原数据未修改。")
        return 1
    try:
        while True:
            print("\n===== 报销记账 =====\n1. 登记\n2. 查询\n3. 退出")
            choice = input("请选择：").strip()
            try:
                if choice == "1":
                    register(records)
                elif choice == "2":
                    query(records)
                elif choice == "3":
                    print("已退出，再见！")
                    return 0
                else:
                    print("请输入 1、2 或 3。")
            except OSError as error:
                print(f"保存失败：{error}。此次修改未生效，请检查文件权限或磁盘空间。")
    except (EOFError, KeyboardInterrupt):
        print("\n已退出，已保存的记录会保留。")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
