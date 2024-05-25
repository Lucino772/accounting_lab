import decimal
import enum
from typing import Literal

from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import datetime_tz, intpk


class LedgerAccount(Base):
    __tablename__ = "ledger_account"

    class Type(enum.Enum):
        ASSET = 1
        LIABILITY = 2
        REVENUE = 4
        EXPENSE = 5

    # Columns
    id: Mapped[intpk]
    account: Mapped[str] = mapped_column(unique=True)
    label: Mapped[str]
    type: Mapped[Type]

    # Relationships
    items: Mapped[list["LedgerEntryItem"]] = relationship(back_populates="account")

    @property
    def type_as_string(self) -> str:
        return {
            self.Type.ASSET: "Asset",
            self.Type.LIABILITY: "Liability",
            self.Type.REVENUE: "Revenue",
            self.Type.EXPENSE: "Expense",
        }[self.type]

    @property
    def balance(self) -> tuple[Literal["debit", "credit"], decimal.Decimal]:
        balance = decimal.Decimal("0")
        for item in self.items:
            if item.type == LedgerEntryItem.Type.DEBIT:
                balance += item.amount
            else:
                balance -= item.amount
        balance_type = "debit" if balance >= 0 else "credit"
        return balance_type, abs(balance)


class LedgerEntry(Base):
    __tablename__ = "ledger_entry"

    # Columns
    id: Mapped[intpk]
    date: Mapped[datetime_tz]

    # Relationships
    items: Mapped[list["LedgerEntryItem"]] = relationship(back_populates="entry")


class LedgerEntryItem(Base):
    __tablename__ = "ledger_entry_item"
    __table_args__ = (
        ForeignKeyConstraint(["account_id"], [LedgerAccount.id]),
        ForeignKeyConstraint(["entry_id"], [LedgerEntry.id]),
    )

    class Type(enum.Enum):
        DEBIT = "D"
        CREDIT = "C"

    # Columns
    id: Mapped[intpk]
    date: Mapped[datetime_tz]
    account_id: Mapped[int]
    type: Mapped[Type]
    amount: Mapped[decimal.Decimal]
    entry_id: Mapped[int]

    # Relationshipts
    account: Mapped[LedgerAccount] = relationship(back_populates="items")
    entry: Mapped[LedgerEntry] = relationship(back_populates="items")

    @property
    def is_debit(self) -> bool:
        return self.type == self.Type.DEBIT

    @property
    def is_credit(self) -> bool:
        return self.type == self.Type.CREDIT
