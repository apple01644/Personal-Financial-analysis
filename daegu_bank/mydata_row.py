import datetime

from .transcation_type import TransactionType


class MyDataRow:
    def __init__(self, pk: str, transaction_datetime: str, transaction_type: str, income: str, loss: str,
                 balance: str, note: str, memo: str, transaction_branch: str):
        self.pk = int(pk)

        self.transaction_datetime = datetime.datetime.strptime(transaction_datetime, '%Y-%m-%d [%H:%M:%S]')

        self.transaction_type = TransactionType.translate_keyword(transaction_type)

        self.income = int(income.replace(',', ''))
        self.loss = int(loss.replace(',', ''))
        self.balance = int(balance.replace(',', ''))
        self.note = note
        self.memo = memo

        self.transaction_branch = transaction_branch

    @staticmethod
    def from_row(cells: list):
        assert len(cells) == 9, f'{len(cells)} == 9'
        return MyDataRow(pk=cells[0], transaction_datetime=cells[1], transaction_type=cells[2],
                         loss=cells[3], income=cells[4], balance=cells[5], note=cells[6],
                         memo=cells[7], transaction_branch=cells[8])

    def __repr__(self):
        return f'<DaeguBank.MyDataRow pk="{self.pk}" transaction_datetime="{self.transaction_datetime}" ' \
               f'transaction_type="{self.transaction_type.name}" income="{self.income}" loss="{self.loss}" ' \
               f'balance="{self.balance}" note="{self.note}" memo="{self.note}" ' \
               f'transaction_branch="{self.transaction_branch}">'
