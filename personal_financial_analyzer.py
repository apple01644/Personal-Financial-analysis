import calendar
import datetime

import defs
from daegu_bank.monthly_statistics import MonthlyStatistics
from daegu_bank.mydata_row import MyDataRow


class PersonalFinancialAnalyzer:
    calendar = calendar.Calendar()

    def __init__(self):
        my_data_rows = self.load_my_data('mydata.txt')
        self.analysis_target_dates = self.define_analysis_target_dates()
        self.deposit_size_timeline = []

        my_data_rows_group_by_date = {k: [] for k in self.analysis_target_dates}

        total_seconds = (my_data_rows[-1].transaction_datetime - my_data_rows[0].transaction_datetime).total_seconds()
        for row in my_data_rows:
            date = row.transaction_datetime.date()
            for [target_date, target_span] in self.analysis_target_dates.items():
                if target_span[0] <= date <= target_span[1]:
                    my_data_rows_group_by_date[target_date].append(row)
                    self.deposit_size_timeline.append({
                        'x': (row.transaction_datetime - my_data_rows[
                            0].transaction_datetime).total_seconds() / total_seconds,
                        'y': row.balance
                    })
                    break
        self.start_datetime = my_data_rows[0].transaction_datetime
        self.end_datetime = my_data_rows[-1].transaction_datetime
        self.monthly_statistics_folder = {
            date: MonthlyStatistics(my_data_rows_group_by_date[date], date=date, span=span) for
            [date, span] in self.analysis_target_dates.items()}
        # for monthly_statistics in self.monthly_statistics_folder.values():
        #     print(monthly_statistics)

    def find_payday(self, date: str) -> datetime.date:
        target_payday = 21

        year = int(date[0:4])
        month = int(date[5:7])
        days_of_month = [x for x in self.calendar.itermonthdays(year=year, month=month)]
        idx = days_of_month.index(target_payday)
        while True:
            day = days_of_month[idx]
            some_date = datetime.date(year=year, month=month, day=day)
            weekday = some_date.weekday()
            if weekday in [5, 6]:
                idx -= 1
                continue
            else:
                break
        pay_date = datetime.date(year=year, month=month, day=days_of_month[idx])
        return pay_date

    def find_payday_span(self, date: str):
        next_date = [int(date[0:4]), int(date[5:7])]
        next_date[1] += 1
        if next_date[1] > 12:
            next_date[1] = 1
            next_date[0] += 1

        this_pay_date = self.find_payday(date)
        next_pay_date = self.find_payday(f'{next_date[0]}-{next_date[1]}') - datetime.timedelta(days=1)
        return [this_pay_date, next_pay_date]

    @staticmethod
    def convert_to_mm_yy_format(data):
        if type(data) == list:
            assert len(data) == 2, f'{len(data)} == 2'
            return '{0:04d}-{1:02d}'.format(data[0], data[1])
        elif type(data) == datetime.datetime:
            return '{0:04d}-{1:02d}'.format(data.year, data.month)
        else:
            assert False, f'convert_to_mm_yy_format doesn\'t support {type(data)}, a type.'

    def define_analysis_target_dates(self) -> dict:
        analysis_iterator_date = [int(defs.analysis_start_date[0:4]), int(defs.analysis_start_date[5:7])]
        analysis_end_date = [int(defs.analysis_end_date[0:4]), int(defs.analysis_end_date[5:7])]
        certain_date = self.convert_to_mm_yy_format(analysis_iterator_date)
        analysis_target_dates = {certain_date: self.find_payday_span(certain_date)}

        while True:
            analysis_iterator_date[1] += 1
            if analysis_iterator_date[1] > 12:
                analysis_iterator_date[0] += 1
                analysis_iterator_date[1] = 1
            certain_date = self.convert_to_mm_yy_format(analysis_iterator_date)
            analysis_target_dates[certain_date] = self.find_payday_span(certain_date)

            if analysis_iterator_date == analysis_end_date:
                break
        return analysis_target_dates

    @staticmethod
    def load_my_data(filename: str):
        my_data_rows = []
        buffer_my_data = open(filename).read()

        for row in buffer_my_data.split('\n')[1:]:
            cells = row.split('|')
            if cells[0] == '합계':
                break
            assert len(cells) == 9, f'{len(cells)} == 9'
            my_data_rows.append(MyDataRow.from_row(cells))
        return my_data_rows
