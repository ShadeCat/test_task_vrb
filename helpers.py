from datetime import datetime
from decimal import Decimal
import xmltodict
import json
import requests
import hashlib

HEADERS = {
    'Content-Type': "application/x-www-form-urlencoded",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Accept-Encoding': "gzip, deflate",
    'Content-Length': "244",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
}


class BankCard:
    def __init__(self, pan=4000000000000002,
                 cvv=123,
                 cardholder='CARDHOLDER INCOGNITO',
                 exp_month=datetime.now().month,
                 exp_year=datetime.now().year):
        self.pan = pan
        self.cardholder = cardholder  # Любое слово на латинице
        self.cvv = cvv  # Любые три цифры
        self.exp_month = exp_month  # любое число от 0 до 12
        self.exp_year = exp_year  # четыре цифры
        # в совокупности месяц и год не должны ar быть меньше текущей даты


class Payment:
    #  Считаем, что деньги мы считаем копейками в int, а не Decimal,
    #  иначе непонятно как себя поведет токен
    def __init__(self, amount: Decimal,
                 merchant_id=702,
                 product_id=4870,
                 product_name='Test Product',
                 cf='Random string',
                 secret_word='sw',
                 ip_address='80.80.80.80'):
        self.merchant_id = merchant_id
        self.product_id = product_id
        self.product_name = product_name
        self.amount = amount
        self.cf = cf
        self.secret_word = secret_word
        self.ip_address = ip_address


class PaymentSender:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.response = None

    def make_payment_request(self, card: BankCard, payment: Payment,
                             rebill_aproved=0, rebill_freq=1, custom_token=False):
        if custom_token:
            token = custom_token
        else:
            token = self._get_token(payment)
        headers = HEADERS

        payload = {'opcode': '0',
                   'product_id': payment.product_id,
                   'amount': payment.amount,
                   'cf': payment.cf,
                   'ip_address': payment.ip_address,
                   'pan': card.pan,
                   'cvv': card.cvv,
                   'cardholder': card.cardholder,
                   'exp_month': card.exp_month,
                   'exp_year': card.exp_year,
                   'token': token,
                   'product_name': payment.product_name,
                   'user_rebill_approved': rebill_aproved,
                   'user_rebill_freq': rebill_freq
                   }

        res = requests.request("POST", self.endpoint, data=payload, headers=headers).text
        self.response = json.loads(json.dumps(xmltodict.parse(res)['response']))

    def make_rebill_request(self, payment: Payment):
        token = self._get_rebill_token(payment)
        headers = HEADERS

        payload = {'opcode': '6',
                   'payment_id': self.response['payment_id'],
                   'amount': payment.amount,
                   'token': token,
                   }

        res = requests.request("POST", self.endpoint, data=payload, headers=headers).text
        self.response = json.loads(json.dumps(xmltodict.parse(res)['response']))

    @staticmethod
    def _get_token(payment):
        token = hashlib.md5()
        key_string = (str(payment.merchant_id) + str(payment.product_id) +
                      str(payment.amount) + payment.cf + payment.secret_word).encode()
        token.update(key_string)
        return token.hexdigest()

    def _get_rebill_token(self, payment):
        token = hashlib.md5()
        key_string = (str(payment.merchant_id) + str(self.response['payment_id']) +
                      str(payment.amount) + payment.secret_word).encode()
        token.update(key_string)
        return token.hexdigest().lower()

    def response_status_should_be(self, ex_status):
        try:
            ac_status = self.response['status']
        except KeyError:
            raise AssertionError(f'Response status is not present, response - {self.response}')
        assert ex_status == ac_status, f'Expected response status - {ex_status}, response - {self.response}.'

    def transaction_status_should_be(self, ex_status):
        try:
            ac_status = self.response['transaction_status']
        except KeyError:
            raise AssertionError(f'Transaction status is not present, response - {self.response}')
        assert ac_status == ex_status, f'Expected transaction status - {ex_status}, response - {self.response}'

    def error_code_should_be(self, ex_code):
        try:
            ac_code = self.response['response_code']
        except KeyError:
            raise AssertionError(f'Response status not presented, response - {self.response}')
        assert ex_code == ac_code, f'Expected response status - {ex_code}, response - {self.response}'


if __name__ == '__main__':
    test_payment = Payment(Decimal(300))
    test_card = BankCard()
    test_sender = PaymentSender('https://gw.acqp.co')
    test_sender.make_payment_request(test_card, test_payment)
