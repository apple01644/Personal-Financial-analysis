import math
import os
import sys
import time
import traceback

import pygame
import pygame.gfxdraw
import pygame.gfxdraw
import pygame.locals

from daegu_bank.classification_statistics import ClassificationStatistics
from daegu_bank.monthly_statistics import MonthlyStatistics
from personal_financial_analyzer import PersonalFinancialAnalyzer


class Viewer:
    client_w = 1920 * 2 // 3
    client_h = 1080 * 2 // 3
    client_x = - (client_w - 1920) // 2 - 1920
    client_y = - (client_h - 1080) // 2

    def __init__(self, pfa: PersonalFinancialAnalyzer):
        self.pfa = pfa
        self.running = True
        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{Viewer.client_x},{Viewer.client_y}'
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
            precision = max(30, int(abs(stop_angle - start_angle)))
            for z in range(precision + 1):
                polygon.append(([
                    x + int(math.cos(z / precision * delta_radian + start_angle / 180 * math.pi) * r),
                    y + int(math.sin(z / precision * delta_radian + start_angle / 180 * math.pi) * r)
                ]))
            pygame.gfxdraw.filled_polygon(surface, polygon, color)
            # pygame.gfxdraw.pie(surface, x, y, r, start_angle, stop_angle, color)

        pygame.gfxdraw.filled_pie = filled_pie

    @property
    def target_date(self) -> str:
        return [k for k in pfa.analysis_target_dates.keys()][self.selected_date_index]

    @property
    def monthly_statistics(self) -> MonthlyStatistics:
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
                if e.type == pygame.locals.QUIT:
                    self.running = False
                elif e.type == pygame.locals.KEYUP:
                    if e.key == pygame.locals.K_ESCAPE:
                        self.running = False
                    elif e.key == pygame.locals.K_PAGEDOWN:
                        self.button_up_target_date()
                    elif e.key == pygame.locals.K_PAGEUP:
                        self.button_down_target_date()
            self.surf.fill([0xAf, 0xAf, 0xAf])
            self.event_draw()
            pygame.display.update()

    def draw_text(self, font: pygame.font.Font, text: str, x: int, y: int, color=None, background=None, center=False):
        if color is None:
            color = [0, 0, 0]
        font_surf = font.render(str(text), True, color, background)
        pos = [x, y]
        if center:
            rect = font_surf.get_rect()
            pos[0] -= rect[2] // 2
            pos[1] -= rect[3] // 2
        self.surf.blit(font_surf, pos)

    def draw_h1(self, text, x, y, **kwargs):
        self.draw_text(self.font_title, text, x, y, **kwargs)

    def draw_h2(self, text, x, y, **kwargs):
        self.draw_text(self.font_small_title, text, x, y, **kwargs)

    def draw_h3(self, text, x, y, **kwargs):
        self.draw_text(self.font_desc, text, x, y, **kwargs)

    # @staticmethod
    # def blend(alpha: float, colorA: list, colorB: list):
    #     assert 0 <= alpha <= 1, f'0 <= {alpha} <= 1'

    def event_draw(self):

        green_text = [0, 150, 0]
        red_text = [150, 0, 0]
        total_abstract_balance = sum([abs(classified_transaction.balance) \
                                      for classified_transaction in
                                      self.monthly_statistics.classification_statistics.classified_transactions_folder.values()])

        self.draw_h1(self.target_date, 0, 0)
        self.draw_h3('{}/{}({}/{})'.format(self.monthly_statistics.start_date, self.monthly_statistics.end_date,
                                           self.monthly_statistics.day_count - self.monthly_statistics.left_day_count,
                                           self.monthly_statistics.day_count),
                     4, 40)
        self.draw_h2('월수입: {: >+12,}원'.format(self.monthly_statistics.total_income), 0, 55 + 30 * 0, color=green_text)
        self.draw_h2('월지출: {: >+12,}원'.format(self.monthly_statistics.total_loss), 0, 55 + 30 * 1, color=red_text)
        self.draw_h2('월손익: {: >+12,}원'.format(self.monthly_statistics.total_delta), 0, 55 + 30 * 2,
                     color=(green_text if self.monthly_statistics.total_delta >= 0 else red_text))
        self.draw_h3('DoD수입: {: >+12,}원'.format(self.monthly_statistics.income_by_day), 4, 140 + 18 * 0,
                     color=green_text)
        self.draw_h3('DoD지출: {: >+12,}원'.format(self.monthly_statistics.loss_by_day), 4, 140 + 18 * 1, color=red_text)
        self.draw_h3('DoD손익: {: >+12,}원'.format(self.monthly_statistics.delta_by_day), 4, 140 + 18 * 2,
                     color=(green_text if self.monthly_statistics.delta_by_day >= 0 else red_text))
        self.draw_h3('시작예금: {: >12,}원'.format(self.monthly_statistics.start_balance), 4, 140 + 18 * 3)
        self.draw_h3('종료예금: {: >12,}원'.format(self.monthly_statistics.end_balance), 4, 140 + 18 * 4)

        self.draw_h3('{: >24,}원/p'.format(total_abstract_balance // 100), 4, 140 + 18 * 5)

        if self.monthly_statistics.left_day_count > 0:
            x = int(self.monthly_statistics.end_balance / self.monthly_statistics.left_day_count)
            self.draw_h3('일일소진액(전액소진 도달): {: >12,}원'.format(x), 4, 140 + 18 * 6)
            x = int((
                                self.monthly_statistics.end_balance - self.monthly_statistics.start_balance) / self.monthly_statistics.left_day_count)
            self.draw_h3('일일소진액(이월잔액 도달): {: >12,}원'.format(x), 4, 140 + 18 * 7,
                         color=[0, 0, 0] if x > 0 else [255, 0, 0])

        self.render_pie_graph()
        self.render_graph()

        pass

    def render_pie_graph(self):
        total_abstract_balance = sum([abs(classified_transaction.balance) \
                                      for classified_transaction in
                                      self.monthly_statistics.classification_statistics.classified_transactions_folder.values()])
        total_abstract_balance += self.monthly_statistics.start_balance
        increment_abstract_balance = 0
        graph_radius = int(Viewer.client_h * 0.9 / 2)
        graph_center = [Viewer.client_w // 2, Viewer.client_h // 2]

        # pygame.draw.circle(self.surf, (200, 200, 200), graph_center, graph_radius)

        text_buffer = []
        outline_y = 10

        good_colors = []
        bad_colors = []
        main_tone = 255
        sub_tone = 150
        main_linear = 20
        sub_linear = 20
        for x in range(5):
            for y in range(5):
                for z in range(5):
                    good_colors.append(
                        [sub_tone - x * sub_linear, main_tone - y * main_linear, sub_tone - z * sub_linear])
                    bad_colors.append(
                        [main_tone - x * main_linear, sub_tone - y * sub_linear, sub_tone - z * sub_linear])
        good_colors.sort(key=lambda t: t[0] + t[1] * 2 + t[2])
        bad_colors.sort(key=lambda t: t[0] * 2 + t[1] + t[2])

        for [class_name,
             classified_transaction] in sorted(
            self.monthly_statistics.classification_statistics.classified_transactions_folder.items(),
            key=lambda item: abs(item[1].balance)):
            abstract_balance = abs(classified_transaction.balance)
            bias_degree = round(270) - round(
                math.atan2(10 - Viewer.client_h / 2, Viewer.client_w - 430 - Viewer.client_w / 2) * 180 / math.pi)
            start_degree = round(increment_abstract_balance / total_abstract_balance * 360)
            end_degree = round((increment_abstract_balance + abstract_balance) / total_abstract_balance * 360)
            mid_degree = (start_degree + end_degree) / 2
            delta_degree = end_degree - start_degree

            if class_name == 'L-other':
                pie_color = [110, 110, 110]
            elif class_name == 'I-other':
                pie_color = [90, 90, 90]
            else:
                if classified_transaction.balance > 0:
                    pie_color = good_colors[0]
                    del good_colors[0]
                else:
                    pie_color = bad_colors[0]
                    del bad_colors[0]

            text_center = [int(round(p)) for p in [
                graph_center[0] + graph_radius * 0.7 * math.cos((mid_degree + bias_degree) / 180 * math.pi),
                graph_center[1] + graph_radius * 0.7 * math.sin((mid_degree + bias_degree) / 180 * math.pi)
            ]]

            if delta_degree > 360 * 0.05:
                pygame.gfxdraw.filled_pie(self.surf, graph_center[0], graph_center[1], graph_radius,
                                          start_degree + bias_degree,
                                          end_degree + bias_degree, pie_color)
                # pygame.gfxdraw.pie(self.surf, graph_center[0], graph_center[1], graph_radius,
                #                   start_degree + bias_degree, end_degree + bias_degree,
                #                   [100, 255, 100] if classified_transaction.balance > 0 else [255, 100, 100])
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

                target_text = '{: <8}:{: >9,}원({: >4.2f}%)'.format(class_name,
                                                                   (classified_transaction.income) + abs(
                                                                       classified_transaction.loss),
                                                                   delta_degree / 360 * 100)
                self.draw_h3(target_text, Viewer.client_w - 250, outline_y,
                             background=pie_color)

                circle_end_point = [
                    graph_center[0] + graph_radius * math.cos((mid_degree + bias_degree) / 180 * math.pi),
                    graph_center[1] + graph_radius * math.sin((mid_degree + bias_degree) / 180 * math.pi)
                ]

                circle_extend_point = [
                    graph_center[0] + (graph_radius + 32) * math.cos((mid_degree + bias_degree) / 180 * math.pi),
                    graph_center[1] + (graph_radius + 32) * math.sin((mid_degree + bias_degree) / 180 * math.pi)
                ]

                text_point = [Viewer.client_w - 250, outline_y + 10]

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

            increment_abstract_balance += abstract_balance
        if self.monthly_statistics.start_balance / total_abstract_balance >= 0.01:  # Draw balance
            abstract_balance = abs(self.monthly_statistics.start_balance)
            bias_degree = round(270) - round(
                math.atan2(10 - Viewer.client_h / 2, Viewer.client_w - 430 - Viewer.client_w / 2) * 180 / math.pi)
            start_degree = round(increment_abstract_balance / total_abstract_balance * 360)
            end_degree = round((increment_abstract_balance + abstract_balance) / total_abstract_balance * 360)
            pygame.gfxdraw.filled_pie(self.surf, graph_center[0], graph_center[1], graph_radius,
                                      start_degree + bias_degree,
                                      end_degree + bias_degree, [200, 200, 200])
            delta_degree = end_degree - start_degree
            mid_degree = (start_degree + end_degree) / 2
            text_center = [int(round(p)) for p in [
                graph_center[0] + graph_radius * 0.7 * math.cos((mid_degree + bias_degree) / 180 * math.pi),
                graph_center[1] + graph_radius * 0.7 * math.sin((mid_degree + bias_degree) / 180 * math.pi)
            ]]
            text_buffer.append({
                'x': text_center[0],
                'y': text_center[1],
                'class_name': '이월 잔액',
                'percent': delta_degree / 360 * 100,
                'abs_value': abstract_balance
            })
            increment_abstract_balance += abstract_balance
        for text_data in text_buffer:
            self.draw_h2(text_data['class_name'], text_data['x'], text_data['y'] - 12, center=True)
            self.draw_h2('{:12,}원({: >4.2f}%)'.format(text_data['abs_value'], text_data['percent']), text_data['x'],
                         text_data['y'] + 12, center=True)

    def render_graph(self):
        canvas = [0, Viewer.client_h - 200, 300, 200]
        pygame.draw.rect(self.surf, (255, 255, 255), canvas)
        for x in range(3):
            pygame.draw.line(self.surf, (80, 80, 80), (canvas[0], canvas[1] + int(canvas[3] * (x + 1) / 4)), (
                canvas[0] + canvas[2], canvas[1] + int(canvas[3] * (x + 1) / 4)), 2)
        for x in range(23):
            pygame.draw.line(self.surf, (160, 160, 160), (canvas[0], canvas[1] + int(canvas[3] * (x + 1) / 20)), (
                canvas[0] + canvas[2], canvas[1] + int(canvas[3] * (x + 1) / 20)))

        '''x = ((self.monthly_statistics.start_date - self.pfa.start_datetime).total_seconds() / (
                self.pfa.end_datetime - self.pfa.start_datetime
        ).total_seconds() * 0.75
        if 0 < x < 1:
            pygame.draw.line(self.surf, (80, 80, 80), (canvas[0] + int(canvas[2] * x), canvas[1]),
                             (canvas[0] + int(canvas[2] * x), canvas[1] + canvas[3]))
        x = (datetime.datetime(self.monthly_statistics.end_date, 0) - self.pfa.start_datetime).total_seconds() / (
                self.pfa.end_datetime - self.pfa.start_datetime
        ).total_seconds() * 0.75'''
        if 0 < x < 1:
            pygame.draw.line(self.surf, (80, 80, 80), (canvas[0] + int(canvas[2] * x), canvas[1]),
                             (canvas[0] + int(canvas[2] * x), canvas[1] + canvas[3]))

        last_point = [canvas[0], canvas[1] + int(canvas[3] * (1 - self.pfa.deposit_size_timeline[0]['y'] / 4000000))]
        for timeline in self.pfa.deposit_size_timeline:
            new_point = [canvas[0] + int(canvas[2] * timeline['x'] * 0.75),
                         canvas[1] + int(canvas[3] * (1 - timeline['y'] / 4000000))]
            pygame.draw.line(self.surf, (80, 255, 80) if -new_point[1] >= -last_point[1] else (255, 80, 80),
                             last_point, new_point, 2)
            last_point = new_point


try:
    pfa = PersonalFinancialAnalyzer()
    for x in sorted(ClassificationStatistics.unclassified_rows, key=lambda row: abs(row.income) + abs(row.loss)):
        if abs(x.income) + abs(x.loss) >= 10:
            print(f'"{x}"')
    viewer = Viewer(pfa)
    viewer.main_loop()
except:
    sys.stdout.flush()
    time.sleep(0.01)
    print(traceback.format_exc(), file=sys.stderr)
