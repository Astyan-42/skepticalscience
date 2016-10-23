# order

NEW = 'new'
CANCELLED = 'cancelled'
PAYMENT_PENDING = 'payment-pending'
FULLY_PAID = 'fully-paid'

ORDER_CHOICES = [
    (NEW, 'Processing'),
    (CANCELLED, 'Cancelled'),
    (PAYMENT_PENDING, 'Payment pending'),
    (FULLY_PAID, 'Fully paid')]

# item name

PUBLICATION = 'publication'
SCIENTIST_ACCOUNT = 'scientist-account'

ITEM_CHOICES = [
    (PUBLICATION, 'Publication'),
    (SCIENTIST_ACCOUNT, 'Scientist account')
]

# duration of refound
REFUND_DAYS = 14

# default price
SCIENTIST_ACCOUNT_PRICE = 100.
PUBLICATION_PRICE_MAX = 5000.
COUNTRY_MIN_PERCENT = 10.
PPP_90_PERCENT = 40000
PPP_20_PERCENT = 10000


def COUNTRY_PPP_TO_PERCENT(min_ppp, max_ppp, own_ppp):
    if own_ppp >= PPP_90_PERCENT:
        # richest
        range_ppp = max_ppp - PPP_90_PERCENT
        own_ppp_corrected = own_ppp - PPP_90_PERCENT
        percent = own_ppp_corrected/range_ppp
        percent = percent*10 + (100.-COUNTRY_MIN_PERCENT)
    elif own_ppp <= PPP_20_PERCENT:
        # poorest
        range_ppp = PPP_20_PERCENT - min_ppp
        own_ppp_corrected = own_ppp - min_ppp
        percent = own_ppp_corrected/range_ppp
        percent = percent*10 + COUNTRY_MIN_PERCENT
    else:
        # middle ground
        range_ppp = PPP_90_PERCENT - PPP_20_PERCENT
        own_ppp_corrected = own_ppp - PPP_20_PERCENT
        percent = own_ppp_corrected/range_ppp
        percent = percent*70 + 20.
    res = round(percent/100., 4)
    return res


PRODUCTS_PRICES = { PUBLICATION: PUBLICATION_PRICE_MAX,
                    SCIENTIST_ACCOUNT: SCIENTIST_ACCOUNT_PRICE
}

# discount type
PERCENT = 'percent'
FIXED = 'fixed'

DISCOUNT_CHOICES = [
    (PERCENT, 'percent'),
    (FIXED, 'fixed')
]

# tax
TAX = 20

PAYMENT_CONSTANTS_TEMPLATE = {
    NEW: "NEW",
    CANCELLED: "CANCELLED",
    PAYMENT_PENDING: "PAYMENT_PENDING",
    FULLY_PAID: "FULLY_PAID",
    PUBLICATION: "PUBLICATION",
    SCIENTIST_ACCOUNT: "SCIENTIST_ACCOUNT",
    SCIENTIST_ACCOUNT_PRICE: "SCIENTIST_ACCOUNT_PRICE",
    PUBLICATION_PRICE_MAX: "PUBLICATION_PRICE_MAX",
    COUNTRY_MIN_PERCENT: "COUNTRY_MIN_PERCENT",
    PERCENT: "PERCENT",
    FIXED: "FIXED"
}