from collections import defaultdict
from typing import List

from daegu_bank.mydata_row import MyDataRow
from daegu_bank.transcation_type import TransactionType
from defs import ClassificationPolicies, special_exceptions


def contains(keywords: list, string: str):
    for keyword in keywords:
        if keyword in string and len(keyword) > 0:
            return True
    return False


class ClassificationStatistics:
    unclassified_rows = []

    class ClassifiedTransactions(list):
        def __init__(self):
            super().__init__()
            self.balance = 0
            self.loss = 0
            self.income = 0

        def process_data(self):
            for row in self:
                self.balance += row.income
                self.balance -= row.loss
                self.income += row.income
                self.loss += row.loss

        def convert_to_text(self, class_name: str):
            text = '\t\t{0: <24}: {1: 12,}원\n'.format(class_name, self.balance)
            return text

    def __init__(self, my_data_rows_group_by_month: List[MyDataRow]):
        self.data = my_data_rows_group_by_month
        self.classified_transactions_folder = defaultdict(ClassificationStatistics.ClassifiedTransactions)
        for row in self.data:
            not_classified = True

            date = str(row.transaction_datetime)
            if date in special_exceptions.keys():
                self.classified_transactions_folder[special_exceptions[date]].append(row)
                not_classified = False
            elif row.income > 0 and row.loss == 0:
                money_flow_type = 'I'
                for income_policy in ClassificationPolicies.Income.get_policies():
                    if income_policy.pass_filter(row):
                        self.classified_transactions_folder[income_policy.name()].append(row)
                        not_classified = False
                        break
            elif row.income == 0 and row.loss > 0:
                money_flow_type = 'L'
                for loss_policy in ClassificationPolicies.Loss.get_policies():
                    if loss_policy.pass_filter(row):
                        self.classified_transactions_folder[loss_policy.name()].append(row)
                        not_classified = False
                        break
            elif row.income == 0 and row.loss == 0:
                money_flow_type = 'N'
            else:
                assert False, repr(row)
            if not_classified:
                if row.transaction_type in [TransactionType.cash_dispenser, TransactionType.cash_dispenser_partner]:
                    self.classified_transactions_folder[f'{money_flow_type}-ATM'].append(row)
                else:
                    self.classified_transactions_folder[f'{money_flow_type}-other'].append(row)
                    ClassificationStatistics.unclassified_rows.append(row)

        for pair in self.classified_transactions_folder.items():
            pair[1].process_data()

    def __repr__(self):
        text = '\t<ClassificationStatistics>\n'
        for [class_name, classified_transactions] in self.classified_transactions_folder.items():
            if classified_transactions.balance != 0:
                text += classified_transactions.convert_to_text(class_name)
        return text
