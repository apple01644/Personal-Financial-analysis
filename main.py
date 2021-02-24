import calendar
import colorsys
import datetime
import enum
import math
import os
import sys
import time
import traceback

import pygame
import pygame.gfxdraw
import pygame.locals as locals

import defs

unclassified_note = set()


def contains(keywords: list, string: str):
    for keyword in keywords:
        if keyword in string and len(keyword) > 0:
            return True
    return False


class DaeguBank:
    class TransactionType(enum.Enum):
        substitute = enum.auto()
        internet = enum.auto()
        bc_card = enum.auto()
        cash_dispenser = enum.auto()
        cash_dispenser_partner = enum.auto()
        deposit_interest = enum.auto()
        open_banking = enum.auto()
        im_bank = enum.auto()
        firm_banking = enum.auto()
        automatic_pay = enum.auto()
        payment_gateway = enum.auto()
        mobile = enum.auto()

        @classmethod
        def translate_keyword(cls, keyword: str):
            if keyword == '대체':
                return cls.substitute
            if keyword == '인터넷':
                return cls.internet
            if keyword == 'BC':
                return cls.bc_card
            if keyword == 'C/D':
                return cls.cash_dispenser
            if keyword == 'CD공동':
                return cls.cash_dispenser_partner
            if keyword == '예금이자':
                return cls.deposit_interest
            if keyword == '오픈뱅킹':
                return cls.open_banking
            if keyword == 'IM뱅크':
                return cls.im_bank
            if keyword == '펌뱅킹':
                return cls.firm_banking
            if keyword == '모바일':
                return cls.mobile
            if keyword == '자동이체':
                return cls.automatic_pay
            if keyword == 'P/G결제':
                return cls.payment_gateway
            assert False, f'{keyword} is not valid TransactionType keyword.'

    class MyDataRow:
        def __init__(self, pk: str, transaction_datetime: str, transaction_type: str, income: str, loss: str,
                     balance: str, note: str, memo: str, transaction_branch: str):
            self.pk = int(pk)

            self.transaction_datetime = datetime.datetime.strptime(transaction_datetime, '%Y-%m-%d [%H:%M:%S]')

            self.transaction_type = DaeguBank.TransactionType.translate_keyword(transaction_type)

            self.income = int(income.replace(',', ''))
            self.loss = int(loss.replace(',', ''))
            self.balance = int(balance.replace(',', ''))
            self.note = note
            self.memo = memo

            self.transaction_branch = transaction_branch

        def __repr__(self):
            return f'<DaeguBank.MyDataRow pk="{self.pk}" transaction_datetime="{self.transaction_datetime}" ' \
                   f'transaction_type="{self.transaction_type.name}" income="{self.income}" loss="{self.loss}" ' \
                   f'balance="{self.balance}" note="{self.note}" memo="{self.note}" ' \
                   f'transaction_branch="{self.transaction_branch}">'

    class ClassificationStatistics:
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

            def convert_to_text(self, classname: str):
                text = '\t\t{0: <24}: {1: 12,}원\n'.format(classname, self.balance)
                return text

        def __init__(self, my_data_rows_group_by_month: list):
            global unclassified_note
            self.data = my_data_rows_group_by_month
            classes = {
                'convenience': ['씨유', 'GS25', '이마트24', '지에스25', '코리아세븐달'],
                'mart': ['대백마트', '천냥앤디씨', '팔공E-마트', '다이소대구이시'],
                'shopping': ['옥션윤재상      ', '11번가', '롯데하이마트(주)', '롯데역사(주)대구', '장미가구사', '토스페이먼츠(주)'],

                'trail': ['코레일유통(주)대', '한국철도공사'],
                'taxi': ['(주)이비카드 택', '(주)이비카드택시'],
                'bus and metro': ['모바일 티머니 충'],

                'monthly': ['한화생명02045', 'KT4333557702', '대성 김윤자', '전기요금인터넷'],
                'salary': ['급여변동상여', '급여연차보상금', '설고정상여금', '(주)대구은행'],
                'hair': ['헤어아트#', 'DL HAIR', '아람머리방'],
                'laundry': ['휴포레명품크리닝'],

                'eat out': ['진배기원조할매국', '(주)신세계푸드', '(주)난성/롯데리', '청도새마을휴게소', '한상바다'],
                'room charge': ['(주)인터파크홀딩', '(주)마루홀딩스 3'],
                'drink': ['할리스 봉무공원'],

                'sports': ['(주)글로벌스포츠'],
                'pc room': ['앤유피씨(NU PC)'],
                'education': ['한국금융투자협회'],
                'award': ['우리(재)한국장학재단', '대구소프트웨', '국민0046255'],

                'USD hedge': ['윤재상(537101106', '537101106608'],
                'USD unhedge': ['외화적립지급'],
                'office work': ['OTP발급수수료', '법원행정처', '공공기관', '현금카드발급', 'AM픽쳐스'],
                'transfer to another bank': ['토스＿윤재상\u3000\u3000', '농협윤재상', '카카오페이'],
                'personal transaction': ['농협김태윤', '토스＿김길자', '토스＿김정오', '농협윤여웅', '농협백승민', '농협김윤자', '농협0125257'],
                'other_loss': None,
                'other_income': ['영플러스통장 수수료 면', '현금IC캐쉬백', '체크카드캐쉬백', '신한분홍앵두', '카뱅도쿄수박', '카뱅둥근바다', '신한달콤상추', '토스180'],
            }
            self.classified_transactions_folder = {k: DaeguBank.ClassificationStatistics.ClassifiedTransactions() for k
                                                   in classes}
            for row in self.data:
                not_classified = True
                for [class_name, keywords] in classes.items():
                    if keywords is None:
                        continue
                    if contains(keywords, row.note):
                        not_classified = False
                        self.classified_transactions_folder[class_name].append(row)
                if not_classified:
                    unclassified_note.add(row.note)
                    if abs(row.income) > abs(row.loss):
                        self.classified_transactions_folder['other_income'].append(row)
                    else:
                        self.classified_transactions_folder['other_loss'].append(row)
            for pair in self.classified_transactions_folder.items():
                pair[1].process_data()

        def __repr__(self):
            text = '\t<ClassificationStatistics>\n'
            for [classname, classified_transactions] in self.classified_transactions_folder.items():
                if classified_transactions.balance != 0:
                    text += classified_transactions.convert_to_text(classname)
            return text

    class MonthlyStatistics:

        def __init__(self, date: str, my_data_rows_group_by_month: list):
            self.date = date
            self.data = my_data_rows_group_by_month
            if len(self.data) == 0:
                return

            my_data_rows_group_by_month.sort(key=lambda row: row.pk)
            self.start_balance = my_data_rows_group_by_month[0].balance - my_data_rows_group_by_month[0].income + \
                                 my_data_rows_group_by_month[0].loss
            self.end_balance = my_data_rows_group_by_month[-1].balance
            self.increase_rate = ((self.end_balance - self.start_balance) / self.start_balance * 100) \
                if self.start_balance > 0 else math.nan

            self.total_income = sum([row.income for row in my_data_rows_group_by_month])
            self.total_loss = -sum([row.loss for row in my_data_rows_group_by_month])
            self.total_delta = self.total_income + self.total_loss

            self.day_count = len(
                [day for day in calendar.Calendar().itermonthdays(year=int(self.date[0:4]), month=int(self.date[5:7]))
                 if day != 0])

            self.income_by_day = math.floor(self.total_income / self.day_count)
            self.loss_by_day = math.floor(self.total_loss / self.day_count)
            self.delta_by_day = math.floor(self.total_delta / self.day_count)

            self.classification_statistics = DaeguBank.ClassificationStatistics(self.data)

        def __repr__(self):
            if len(self.data) == 0:
                return f'<MonthlyStatistics {self.date} (empty)/>'
            text = f'<MonthlyStatistics {self.date}>' '\n'
            general_format = '\t{0: <15} = {1:12,}원\n'
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


class PersonalFinancialAnalyzer:
    def __init__(self):
        my_data_rows = self.load_my_data('mydata.txt')
        self.analysis_target_dates = self.define_analysis_target_dates()
        self.deposit_size_timeline = []

        my_data_rows_group_by_date = {k: [] for k in self.analysis_target_dates}

        total_seconds = (my_data_rows[-1].transaction_datetime - my_data_rows[0].transaction_datetime).total_seconds()
        for row in my_data_rows:
            date = self.convert_to_mm_yy_format(row.transaction_datetime)
            if date in self.analysis_target_dates:
                my_data_rows_group_by_date[date].append(row)
            self.deposit_size_timeline.append({
                'x': (row.transaction_datetime - my_data_rows[0].transaction_datetime).total_seconds() / total_seconds,
                'y': row.balance
            })
        self.start_datetime = my_data_rows[0].transaction_datetime
        self.end_datetime = my_data_rows[-1].transaction_datetime
        self.monthly_statistics_folder = {date: DaeguBank.MonthlyStatistics(date, my_data_rows_group_by_date[date]) for
                                          date in self.analysis_target_dates}
        for monthly_statistics in self.monthly_statistics_folder.values():
            print(monthly_statistics)

    @staticmethod
    def convert_to_mm_yy_format(data):
        if type(data) == list:
            assert len(data) == 2, f'{len(data)} == 2'
            return '{0:04d}-{1:02d}'.format(data[0], data[1])
        elif type(data) == datetime.datetime:
            return '{0:04d}-{1:02d}'.format(data.year, data.month)
        else:
            assert False, f'convert_to_mm_yy_format doesn\'t support {type(data)}, a type.'

    def define_analysis_target_dates(self):
        analysis_iterator_date = [int(defs.analysis_start_date[0:4]), int(defs.analysis_start_date[5:7])]
        analysis_end_date = [int(defs.analysis_end_date[0:4]), int(defs.analysis_end_date[5:7])]
        analysis_target_dates = [self.convert_to_mm_yy_format(analysis_iterator_date)]

        while True:
            analysis_iterator_date[1] += 1
            if analysis_iterator_date[1] > 12:
                analysis_iterator_date[0] += 1
                analysis_iterator_date[1] = 1
            analysis_target_dates.append(self.convert_to_mm_yy_format(analysis_iterator_date))

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
            if len(cells) == 9:
                my_data_row = DaeguBank.MyDataRow(pk=cells[0], transaction_datetime=cells[1], transaction_type=cells[2],
                                                  loss=cells[3], income=cells[4], balance=cells[5], note=cells[6],
                                                  memo=cells[7], transaction_branch=cells[8])
                my_data_rows.append(my_data_row)
        return my_data_rows


class Viewer:
    client_w = 1920 * 2 // 3
    client_h = 1080 * 2 // 3

    def __init__(self, pfa: PersonalFinancialAnalyzer):
        self.pfa = pfa
        self.running = True
        os.environ['SDL_VIDEO_WINDOW_POS'] = f'-1920,30'
        pygame.init()

        pygame.font.init()
        self.font_title = pygame.font.Font('batang.ttc', 40)
        self.font_small_title = pygame.font.Font('batang.ttc', 25)
        self.font_desc = pygame.font.Font('batang.ttc', 15)

        pygame.display.init()
        pygame.display.set_mode([Viewer.client_w, Viewer.client_h])
        self.surf = pygame.display.get_surface()

        self.selected_date_index = 0

        def filled_pie(surface, x, y, r, start_angle, stop_angle, color):
            polygon = [[x, y]]
            delta_radian = (stop_angle - start_angle) / 180 * math.pi
            precision = 30
            for z in range(precision + 1):
                polygon.append(([
                    x + int(math.cos(z / precision * delta_radian + start_angle / 180 * math.pi) * r),
                    y + int(math.sin(z / precision * delta_radian + start_angle / 180 * math.pi) * r)
                ]))
            pygame.gfxdraw.filled_polygon(surface, polygon, color)
            pygame.gfxdraw.pie(surface, x, y, r, start_angle, stop_angle, color)

        pygame.gfxdraw.filled_pie = filled_pie

    @property
    def target_date(self) -> str:
        return pfa.analysis_target_dates[self.selected_date_index]

    @property
    def monthly_statistics(self) -> DaeguBank.MonthlyStatistics:
        return pfa.monthly_statistics_folder[self.target_date]

    def button_up_target_date(self):
        if self.selected_date_index + 1 < len(pfa.analysis_target_dates):
            self.selected_date_index += 1

    def button_down_target_date(self):
        if self.selected_date_index > 0:
            self.selected_date_index -= 1

    def main_loop(self):
        self.event_step()
        pygame.font.quit()
        pygame.quit()

    def event_step(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == locals.QUIT:
                    self.running = False
                elif e.type == locals.KEYUP:
                    if e.key == locals.K_ESCAPE:
                        self.running = False
                    elif e.key == locals.K_PAGEDOWN:
                        self.button_up_target_date()
                    elif e.key == locals.K_PAGEUP:
                        self.button_down_target_date()
            self.surf.fill([0xAf, 0xAf, 0xAf])
            self.event_draw()
            pygame.display.update()

    def event_draw(self):
        def draw_text(font: pygame.font.Font, text: str, x: int, y: int, color=None, background=None, center=False):
            if color is None:
                color = [0, 0, 0]
            font_surf = font.render(str(text), True, color, background)
            pos = [x, y]
            if center:
                rect = font_surf.get_rect()
                pos[0] -= rect[2] // 2
                pos[1] -= rect[3] // 2
            self.surf.blit(font_surf, pos)

        def draw_h1(text, x, y, **kwargs):
            draw_text(self.font_title, text, x, y, **kwargs)

        def draw_h2(text, x, y, **kwargs):
            draw_text(self.font_small_title, text, x, y, **kwargs)

        def draw_h3(text, x, y, **kwargs):
            draw_text(self.font_desc, text, x, y, **kwargs)

        def blend(alpha: float, colorA: list, colorB: list):
            assert 0 <= alpha <= 1, f'0 <= {alpha} <= 1'

        green_text = [0, 150, 0]
        red_text = [150, 0, 0]

        draw_h1(self.target_date, 0, 0)
        draw_h2('월수입: {: >+12,}원'.format(self.monthly_statistics.total_income), 0, 40 + 30 * 0, color=green_text)
        draw_h2('월지출: {: >+12,}원'.format(self.monthly_statistics.total_loss), 0, 40 + 30 * 1, color=red_text)
        draw_h2('월손익: {: >+12,}원'.format(self.monthly_statistics.total_delta), 0, 40 + 30 * 2,
                color=(green_text if self.monthly_statistics.total_delta >= 0 else red_text))
        draw_h3('DoD수입: {: >+12,}원'.format(self.monthly_statistics.income_by_day), 4, 130 + 18 * 0, color=green_text)
        draw_h3('DoD지출: {: >+12,}원'.format(self.monthly_statistics.loss_by_day), 4, 130 + 18 * 1, color=red_text)
        draw_h3('DoD손익: {: >+12,}원'.format(self.monthly_statistics.delta_by_day), 4, 130 + 18 * 2,
                color=(green_text if self.monthly_statistics.delta_by_day >= 0 else red_text))

        total_abstract_balance = sum([abs(classified_transaction.balance) for classified_transaction in
                                      self.monthly_statistics.classification_statistics.classified_transactions_folder.values()])
        increasement_abstract_balance = 0
        graph_radius = int(Viewer.client_h * 0.9 / 2)
        graph_center = [Viewer.client_w // 2, Viewer.client_h // 2]
        graph_rect = (
            Viewer.client_w // 2 - graph_radius, Viewer.client_h // 2 - graph_radius, graph_radius * 2, graph_radius * 2
        )
        pygame.draw.circle(self.surf, (200, 200, 200), graph_center, graph_radius)

        text_buffer = []
        outline_y = 10

        for [class_name,
             classified_transaction] in sorted(
            self.monthly_statistics.classification_statistics.classified_transactions_folder.items(),
            key=lambda item: abs(item[1].balance)):
            abstract_balance = abs(classified_transaction.balance)
            bias_degree = round(270) - round(
                math.atan2(10 - Viewer.client_h / 2, Viewer.client_w - 430 - Viewer.client_w / 2) * 180 / math.pi)
            start_degree = round(increasement_abstract_balance / total_abstract_balance * 360)
            end_degree = round((increasement_abstract_balance + abstract_balance) / total_abstract_balance * 360)
            mid_degree = (start_degree + end_degree) / 2
            delta_degree = end_degree - start_degree

            if class_name == 'other_loss':
                pie_color = [255, 0, 0]
            elif class_name == 'other_income':
                pie_color = [0, 255, 0]

            elif class_name == 'shopping':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.10, 0.80, 0.90)]
            elif class_name == 'convenience':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.10, 0.80, 0.70)]
            elif class_name == 'mart':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.10, 0.80, 0.50)]

            elif class_name == 'eat out':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.15, 0.80, 0.90)]
            elif class_name == 'education':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.15, 0.80, 0.70)]
            elif class_name == 'sports':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.15, 0.80, 0.50)]

            elif class_name == 'salary':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.30, 0.80, 0.90)]
            elif class_name == 'award':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.30, 0.80, 0.70)]

            elif class_name == 'taxi':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.85, 0.80, 0.90)]
            elif class_name == 'trail':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.85, 0.80, 0.70)]
            elif class_name == 'bus and metro':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.85, 0.80, 0.50)]

            elif class_name == 'monthly':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.00, 0.80, 0.90)]
            elif class_name == 'office work':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.00, 0.80, 0.70)]
            elif class_name == 'hair':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.00, 0.80, 0.50)]
            elif class_name == 'laundry':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.00, 0.60, 0.90)]
            elif class_name == 'room charge':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.00, 0.60, 0.70)]

            elif class_name == 'USD hedge':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.60, 0.80, 0.90)]
            elif class_name == 'transfer to another bank':
                pie_color = [int(f * 255) for f in colorsys.hsv_to_rgb(0.60, 0.80, 0.70)]

            else:
                pie_color = [50, 70, 50] if classified_transaction.balance > 0 else [70, 50, 50]

            text_center = [int(round(p)) for p in [
                graph_center[0] + graph_radius * 0.7 * math.cos((mid_degree + bias_degree) / 180 * math.pi),
                graph_center[1] + graph_radius * 0.7 * math.sin((mid_degree + bias_degree) / 180 * math.pi)
            ]]

            if delta_degree > 360 * 0.05:
                pygame.gfxdraw.filled_pie(self.surf, graph_center[0], graph_center[1], graph_radius,
                                          start_degree + bias_degree,
                                          end_degree + bias_degree, pie_color)
                pygame.gfxdraw.pie(self.surf, graph_center[0], graph_center[1], graph_radius,
                                   start_degree + bias_degree, end_degree + bias_degree,
                                   [100, 255, 100] if classified_transaction.balance > 0 else [255, 100, 100])
                text_buffer.append({
                    'x': text_center[0],
                    'y': text_center[1],
                    'class_name': class_name,
                    'percent': delta_degree / 360 * 100,
                    'abs_value': abs(classified_transaction.income) + abs(classified_transaction.loss)
                })

                if classified_transaction.income > 0 and classified_transaction.loss > 0:
                    font_rect = self.font_small_title.render(class_name, False, [0, 0, 0]).get_rect()
                    font_rect[0] += text_center[0] - font_rect[2] // 2
                    font_rect[1] += text_center[1] - 12 + font_rect[3] // 2
                    green_bar_width = classified_transaction.income / (
                            classified_transaction.income + classified_transaction.loss)
                    pygame.draw.rect(self.surf, [0, 255, 0], [
                        font_rect[0], font_rect[1],
                        int(font_rect[2] * green_bar_width), 2
                    ])
                    pygame.draw.rect(self.surf, [255, 0, 0], [
                        font_rect[0] + int(font_rect[2] * green_bar_width), font_rect[1],
                        int(font_rect[2] * (1 - green_bar_width)), 2
                    ])
            elif delta_degree / 360 * 100 >= 0.01:
                pygame.gfxdraw.filled_pie(self.surf, graph_center[0], graph_center[1], graph_radius,
                                          start_degree + bias_degree,
                                          end_degree + bias_degree, pie_color)
                '''pygame.gfxdraw.pie(self.surf, graph_center[0], graph_center[1], graph_radius,
                                   start_degree + bias_degree,
                                   end_degree + bias_degree,
                                   [100, 255, 100] if classified_transaction.balance > 0 else [255, 100, 100])'''

                target_text = '{} {: <2.2f}%'.format(class_name, delta_degree / 360 * 100)
                draw_h3(target_text, Viewer.client_w - 230, outline_y,
                        background=pie_color)

                circle_end_point = [
                    graph_center[0] + graph_radius * math.cos((mid_degree + bias_degree) / 180 * math.pi),
                    graph_center[1] + graph_radius * math.sin((mid_degree + bias_degree) / 180 * math.pi)
                ]

                circle_extend_point = [
                    graph_center[0] + (graph_radius + 32) * math.cos((mid_degree + bias_degree) / 180 * math.pi),
                    graph_center[1] + (graph_radius + 32) * math.sin((mid_degree + bias_degree) / 180 * math.pi)
                ]

                text_point = [Viewer.client_w - 235, outline_y + 10]

                pygame.draw.line(self.surf, [0, 0, 0], [int(f) for f in circle_end_point],
                                 [int(f) for f in circle_extend_point])
                pygame.draw.line(self.surf, [0, 0, 0], [int(f) for f in circle_extend_point],
                                 [int(f) for f in text_point])

                if classified_transaction.income > 0 and classified_transaction.loss > 0:
                    font_rect = self.font_desc.render(target_text, False, [0, 0, 0]).get_rect()
                    font_rect[0] += text_point[0] + 5
                    font_rect[1] += text_point[1] + font_rect[3] // 2 - 2
                    green_bar_width = classified_transaction.income / (
                            classified_transaction.income + classified_transaction.loss)
                    pygame.draw.rect(self.surf, [0, 255, 0], [
                        font_rect[0], font_rect[1],
                        int(font_rect[2] * green_bar_width), 2
                    ])
                    pygame.draw.rect(self.surf, [255, 0, 0], [
                        font_rect[0] + int(font_rect[2] * green_bar_width), font_rect[1],
                        int(font_rect[2] * (1 - green_bar_width)), 2
                    ])

                outline_y += 30

            increasement_abstract_balance += abstract_balance
        for text_data in text_buffer:
            draw_h2(text_data['class_name'], text_data['x'], text_data['y'] - 12, center=True)
            draw_h2('{:12,}원({: <2.2f}%)'.format(text_data['abs_value'], text_data['percent']), text_data['x'],
                    text_data['y'] + 12, center=True)

        canvas = [0, Viewer.client_h - 200, 300, 200]
        pygame.draw.rect(self.surf, (255, 255, 255), canvas)
        for x in range(3):
            pygame.draw.line(self.surf, (80, 80, 80), (canvas[0], canvas[1] + int(canvas[3] * (x + 1) / 4)), (
                canvas[0] + canvas[2], canvas[1] + int(canvas[3] * (x + 1) / 4)), 2)
        for x in range(23):
            pygame.draw.line(self.surf, (160, 160, 160), (canvas[0], canvas[1] + int(canvas[3] * (x + 1) / 20)), (
                canvas[0] + canvas[2], canvas[1] + int(canvas[3] * (x + 1) / 20)))

        x = (datetime.datetime.strptime(self.target_date, '%Y-%m') - self.pfa.start_datetime).total_seconds() / (
                self.pfa.end_datetime - self.pfa.start_datetime
        ).total_seconds() * 0.75
        for _ in range(2):
            if 0 < x < 1:
                pygame.draw.line(self.surf, (80, 80, 80), (canvas[0] + int(canvas[2] * x), canvas[1]),
                                 (canvas[0] + int(canvas[2] * x), canvas[1] + canvas[3]))
            x += datetime.timedelta(days=30.5).total_seconds() / (self.pfa.end_datetime - self.pfa.start_datetime
                                                                  ).total_seconds()

        last_point = [canvas[0], canvas[1] + int(canvas[3] * (1 - self.pfa.deposit_size_timeline[0]['y'] / 4000000))]
        for timeline in self.pfa.deposit_size_timeline:
            new_point = [canvas[0] + int(canvas[2] * timeline['x']  * 0.75),
                         canvas[1] + int(canvas[3] * (1 - timeline['y'] / 4000000))]
            pygame.draw.line(self.surf, (80, 255, 80) if new_point[1] > last_point[1] else (255, 80, 80),
                             last_point, new_point, 2)
            last_point = new_point

        pass


try:
    pfa = PersonalFinancialAnalyzer()
    print(unclassified_note.difference({''}))
    viewer = Viewer(pfa)
    viewer.main_loop()
except:
    sys.stdout.flush()
    time.sleep(0.01)
    print(traceback.format_exc(), file=sys.stderr)
