import enum


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
