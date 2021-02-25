import datetime
import math

from .classification_statistics import ClassificationStatistics


class MonthlyStatistics:

    def __init__(self, my_data_rows_group_by_month: list, date=None, span=None):
        self.date = date
        self.start_date = span[0]
        self.end_date = span[1]
        self.data = my_data_rows_group_by_month
        if len(self.data) == 0:
            return

        my_data_rows_group_by_month.sort(key=lambda row: row.pk)
        self.start_balance = \
            my_data_rows_group_by_month[0].balance - my_data_rows_group_by_month[0].income + \
            my_data_rows_group_by_month[0].loss
        self.end_balance = my_data_rows_group_by_month[-1].balance
        self.increase_rate = ((self.end_balance - self.start_balance) / self.start_balance * 100) \
            if self.start_balance > 0 else math.nan

        self.total_income = sum([row.income for row in my_data_rows_group_by_month])
        self.total_loss = -sum([row.loss for row in my_data_rows_group_by_month])
        self.total_delta = self.total_income + self.total_loss

        now_day = datetime.datetime.now().date()
        iter_day = self.start_date
        self.day_count = 1
        self.left_day_count = 0
        while iter_day != self.end_date:
            iter_day += datetime.timedelta(days=1)
            if iter_day >= now_day:
                self.left_day_count += 1
            self.day_count += 1

        self.income_by_day = math.floor(self.total_income / self.day_count)
        self.loss_by_day = math.floor(self.total_loss / self.day_count)
        self.delta_by_day = math.floor(self.total_delta / self.day_count)

        self.classification_statistics = ClassificationStatistics(self.data)

    def __repr__(self):
        if len(self.data) == 0:
            return f'<MonthlyStatistics {self.date} (empty)/>'
        text = f'<MonthlyStatistics {self.date}>' '\n'
        text += '\t{: <15} = {:12,}원 → {:12,}원({:+02.2f}%)\n'.format('start-end', self.start_balance,
                                                                     self.end_balance, self.increase_rate)
        text += '\t{: <15} = {:+12,}원  ({:+12,}원/{:+12,}원)\n'.format('total',
                                                                     self.total_delta,
                                                                     self.total_income,
                                                                     self.total_loss)
        text += '\t{: <15} = {:+12,}원  ({:+12,}원/{:+12,}원)\n'.format(f'DoD(days={self.day_count})',
                                                                     self.delta_by_day,
                                                                     self.income_by_day,
                                                                     self.loss_by_day)
        text += repr(self.classification_statistics)
        text += '</MonthlyStatistics>'
        return text
