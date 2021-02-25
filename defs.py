from daegu_bank.classification_policy import ClassificationModel, IncomePolicy, LossPolicy


class ClassificationPolicies:
    class Income(ClassificationModel):
        class PersonalMoneyTake(IncomePolicy):
            _name = '사적금전인수'

        class CashBack(IncomePolicy):
            _name = '캐쉬백'
            _note_filter = ['현금IC캐쉬백']

        class Salary(IncomePolicy):
            _name = '급여'
            _note_filter = ['급여변동상여', '(주)대구은행(인재개발부)', '급여연차보상금', '설고정상여금', '(주)대구은행']

        class Award(IncomePolicy):
            _name = '상금'
            _note_filter = ['우리(재)한국장학재단', '대구소프트웨']

        class SellForeignExchange(IncomePolicy):
            _name = '외화매도'
            _note_filter = ['외화적립지급']

        class SelfIncome(IncomePolicy):
            _name = '자체수입'
            _note_regex = ['.*윤재상.*']
            _note_filter = ['농협0125257']

    class Loss(ClassificationModel):
        class FixedSpending(LossPolicy):
            _name = '고정지출'
            _note_filter = ['한화생명02045', 'KT4333557702', '전기요금인터넷', '대성 김윤자', '아람머리방', 'DL HAIR', '헤어아트#']

        class SemiFixedSpending(LossPolicy):
            _name = '반고정지출'
            _note_filter = ['휴포레명품크리닝', ]

        class Shopping(LossPolicy):
            _name = '쇼핑'
            _note_filter = ['11번가', '장미가구사', '천냥앤디씨', '롯데하이마트(주)', '롯데역사(주)대구']

        class Consumption(LossPolicy):
            _name = '소비'
            _note_regex = ['(지에스|GS)25( 불로|드림병원|달서동화)점', '씨유(대구불로대로|밀양무안점|수성롯데캐슬)?', '(팔공)?(E-|이)마트(24 S대구은)?', '다이소대구이시']
            _note_filter = ['대백마트 (불로)']

        class Playing(LossPolicy):
            _name = '놀이'
            _note_filter = ['(주)마루홀딩스 3', '(주)글로벌스포츠', '앤유피씨(NU PC)']

        class Travel(LossPolicy):
            _name = '여행'
            _note_filter = ['(주)이비카드 택', '코레일유통(주)대', '(주)이비카드택시', '한국철도공사', '모바일 티머니 충', '(주)인터파크홀딩']

        class EatOut(LossPolicy):
            _name = '외식'
            _note_filter = ['(주)신세계푸드', '한상바다', '진배기원조할매국', '할리스 봉무공원', '(주)난성/롯데리']

        class Education(LossPolicy):
            _name = '교육'
            _note_filter = ['한국금융투자협회']

        class BuyForeignExchange(LossPolicy):
            _name = '외화매수'

        class PersonalMoneyGive(LossPolicy):
            _name = '사적금전인도'
            _note_regex = ['토스＿\S{3}']

        class SelfLost(LossPolicy):
            _name = '자체지출'
            _note_regex = ['.*윤재상.*']
            _note_filter = ['카카오페이　　　']

        class Fee(LossPolicy):
            _name = '수수료'
            _note_regex = ['\*{5} \d{4}년 \d{2}월 영플러스통장 수수료 면']
            _note_filter = []



special_exceptions = {
    '2021-01-19 11:58:01': 'L외화매수',
    '2021-01-14 20:11:10': 'L놀이',
    '2020-11-22 11:08:23': 'I사적금전인수',
    '2021-02-03 18:20:48': 'L사적금전인도',
    '2021-02-05 13:28:57': 'L외식',
    '2021-02-25 08:55:07': 'L소비',
}

analysis_start_date = '2020-10'
analysis_end_date = '2021-02'

'''     convenience =  ['씨유', 'GS25', '이마트24', '지에스25', '코리아세븐달'],
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
        'other_income': ['영플러스통장 수수료 면', '현금IC캐쉬백', '체크카드캐쉬백', '신한분홍앵두', '카뱅도쿄수박', '카뱅둥근바다', '신한달콤상추', '토스180'],'''
