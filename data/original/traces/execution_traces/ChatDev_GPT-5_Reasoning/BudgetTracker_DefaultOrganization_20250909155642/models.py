'''
Domain models for the Budget Tracker application.
Defines Transaction and BudgetModel classes.
'''
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Dict, Optional, Iterable, Tuple
@dataclass
class Transaction:
    id: int
    date: date
    ttype: str  # "Income" or "Expense"
    category: str
    description: str
    amount: float  # always positive; sign is inferred by ttype
    def to_row(self) -> Tuple[int, date, str, str, str, float]:
        return (self.id, self.date, self.ttype, self.category, self.description, float(self.amount))
    @staticmethod
    def from_row(row: Iterable) -> "Transaction":
        # Row: ID, Date, Type, Category, Description, Amount
        rid = int(row[0])
        rdate = row[1]
        if isinstance(rdate, datetime):
            rdate = rdate.date()
        elif isinstance(rdate, str):
            rdate = datetime.strptime(rdate, "%Y-%m-%d").date()
        elif not isinstance(rdate, date):
            # fallback to today
            rdate = date.today()
        ttype = str(row[2])
        category = str(row[3]) if row[3] is not None else "General"
        description = str(row[4]) if row[4] is not None else ""
        amount = float(row[5]) if row[5] is not None else 0.0
        if amount < 0:
            amount = abs(amount)
        return Transaction(rid, rdate, ttype, category, description, amount)
class BudgetModel:
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.categories: List[str] = ["General"]
        self.savings_goal: float = 0.0
        self._next_id: int = 1
    def load(self, transactions: List[Transaction], categories: Iterable[str], savings_goal: float = 0.0) -> None:
        self.transactions = list(transactions)
        # Unique, keep order (stable unique)
        seen = set()
        cat_list = []
        for c in categories:
            c = str(c).strip()
            if c and c not in seen:
                seen.add(c)
                cat_list.append(c)
        if "General" not in seen:
            cat_list.insert(0, "General")
        self.categories = cat_list
        self.savings_goal = float(savings_goal) if savings_goal is not None else 0.0
        # next id
        self._next_id = (max((t.id for t in self.transactions), default=0) + 1)
    def ensure_category(self, name: str) -> None:
        name = name.strip()
        if name and name not in self.categories:
            self.categories.append(name)
    def generate_next_id(self) -> int:
        nid = self._next_id
        self._next_id += 1
        return nid
    def add_transaction(self, tdate: date, ttype: str, category: str, description: str, amount: float) -> Transaction:
        ttype = "Income" if ttype.lower().startswith("inc") else "Expense"
        amount = abs(float(amount))
        category = category.strip() or "General"
        self.ensure_category(category)
        tx = Transaction(
            id=self.generate_next_id(),
            date=tdate,
            ttype=ttype,
            category=category,
            description=description.strip(),
            amount=amount,
        )
        self.transactions.append(tx)
        # Keep sorted by date then id for consistent UI
        self.transactions.sort(key=lambda x: (x.date, x.id))
        return tx
    def edit_transaction(self, tx_id: int, tdate: date, ttype: str, category: str, description: str, amount: float) -> bool:
        tx = self.get_transaction(tx_id)
        if not tx:
            return False
        ttype = "Income" if ttype.lower().startswith("inc") else "Expense"
        amount = abs(float(amount))
        category = category.strip() or "General"
        self.ensure_category(category)
        tx.date = tdate
        tx.ttype = ttype
        tx.category = category
        tx.description = description.strip()
        tx.amount = amount
        self.transactions.sort(key=lambda x: (x.date, x.id))
        return True
    def delete_transaction(self, tx_id: int) -> bool:
        before = len(self.transactions)
        self.transactions = [t for t in self.transactions if t.id != tx_id]
        return len(self.transactions) < before
    def get_transaction(self, tx_id: int) -> Optional[Transaction]:
        for t in self.transactions:
            if t.id == tx_id:
                return t
        return None
    def set_savings_goal(self, goal: float) -> None:
        self.savings_goal = max(0.0, float(goal))
    def totals(self) -> Dict[str, float]:
        income = sum(t.amount for t in self.transactions if t.ttype == "Income")
        expenses = sum(t.amount for t in self.transactions if t.ttype == "Expense")
        net = income - expenses
        return {"income": income, "expenses": expenses, "net": net}
    def category_totals(self) -> Dict[str, float]:
        totals: Dict[str, float] = {}
        for t in self.transactions:
            sign = 1 if t.ttype == "Income" else -1
            totals[t.category] = totals.get(t.category, 0.0) + sign * t.amount
        return totals
    def filtered_transactions(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        ttype: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Transaction]:
        ttype_norm = None
        if ttype:
            t = ttype.strip().lower()
            if t in ("income", "expense"):
                ttype_norm = "Income" if t == "income" else "Expense"
        cat_norm = category.strip() if category else None
        search_norm = search.strip().lower() if search else None
        res = []
        for t in self.transactions:
            if year and t.date.year != year:
                continue
            if month and t.date.month != month:
                continue
            if ttype_norm and t.ttype != ttype_norm:
                continue
            if cat_norm and cat_norm != "All" and t.category != cat_norm:
                continue
            if search_norm and search_norm not in (t.description or "").lower():
                continue
            res.append(t)
        return res