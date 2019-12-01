from decimal import Decimal
import time
import pytest
from helpers import PaymentSender, BankCard, Payment

MIN_AMOUNT = Decimal('5.00')
MAX_AMOUNT = Decimal('500.00')
AVG_AMOUNT = Decimal('300.00')

ENDPOINT = 'https://gw.acqp.co'


@pytest.fixture(scope='function', autouse=True)
def test_slower():
    time.sleep(2)


def test_success_payment_min_amount():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(MIN_AMOUNT)
    card = BankCard()
    sender.make_payment_request(card, payment)
    sender.response_status_should_be('OK')


def test_success_payment_min_verge_amount():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(MIN_AMOUNT + Decimal('0.01'))
    card = BankCard()
    sender.make_payment_request(card, payment)
    sender.response_status_should_be('OK')


def test_success_payment_max_amount():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(MAX_AMOUNT)
    card = BankCard()
    sender.make_payment_request(card, payment)
    sender.response_status_should_be('OK')


def test_success_payment_max_verge_amount():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(MAX_AMOUNT - Decimal('0.01'))
    card = BankCard()
    sender.make_payment_request(card, payment)
    sender.response_status_should_be('OK')


def test_payment_amount_less_than_acceptable_status():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(MIN_AMOUNT - 1)
    card = BankCard()
    sender.make_payment_request(card, payment)
    sender.response_status_should_be('KO')


def test_payment_amount_less_than_acceptable_transaction_status():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(MIN_AMOUNT - 1)
    card = BankCard()
    sender.make_payment_request(card, payment)
    sender.transaction_status_should_be('DECLINE')


def test_payment_amount_less_than_acceptable_error_code():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(MIN_AMOUNT - 1)
    card = BankCard()
    sender.make_payment_request(card, payment)
    sender.error_code_should_be('A115')


def test_payment_amount_more_than_acceptable_status():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(MIN_AMOUNT + 1)
    card = BankCard()
    sender.make_payment_request(card, payment)
    sender.response_status_should_be('KO')


def test_payment_amount_more_than_acceptable_transaction_status():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(MIN_AMOUNT + 1)
    card = BankCard()
    sender.make_payment_request(card, payment)
    sender.transaction_status_should_be('DECLINE')


def test_payment_amount_more_than_acceptable_error_code():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(MIN_AMOUNT + 1)
    card = BankCard()
    sender.make_payment_request(card, payment)
    sender.error_code_should_be('A115')


def test_success_rebill():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(AVG_AMOUNT)
    card = BankCard()
    sender.make_payment_request(card, payment, rebill_aproved=1, rebill_freq=1)
    sender.make_rebill_request(payment)
    sender.response_status_should_be('REBILL_OK')

#  Bonus


def test_invalid_token_status():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(AVG_AMOUNT)
    card = BankCard()
    sender.make_payment_request(card, payment, custom_token='random_string')
    sender.response_status_should_be('KO')


def test_invalid_token_error_code():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(AVG_AMOUNT)
    card = BankCard()
    sender.make_payment_request(card, payment, custom_token='random_string')
    sender.error_code_should_be('A114')


def test_invalid_pan_status():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(AVG_AMOUNT)
    card = BankCard(pan=4000000000000003)
    sender.make_payment_request(card, payment)
    sender.response_status_should_be('KO')


def test_invalid_pan_error_code():
    sender = PaymentSender(ENDPOINT)
    payment = Payment(AVG_AMOUNT)
    card = BankCard(pan=40000000000000031)
    sender.make_payment_request(card, payment)
    sender.error_code_should_be('A101')
