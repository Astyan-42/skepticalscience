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

# default price
SCIENTIST_ACCOUNT_PRICE = 100.
PUBLICATION_PRICE_MAX = 5000.
COUNTRY_REDUCTION_MAX_PERCENT = 90.

def COUNTRY_PIB_TO_PERCENT(min_pib, max_pib, own_pib):
    range_pib = max_pib-min_pib
    own_pib_corrected = own_pib-min_pib
    min_percent = 100. - COUNTRY_REDUCTION_MAX_PERCENT
    print((own_pib_corrected/range_pib)*COUNTRY_REDUCTION_MAX_PERCENT)
    res = round(((own_pib_corrected/range_pib)*COUNTRY_REDUCTION_MAX_PERCENT + min_percent)/100, 2)
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
    COUNTRY_REDUCTION_MAX_PERCENT: "COUNTRY_REDUCTION_MAX_PERCENT",
    PERCENT: "PERCENT",
    FIXED: "FIXED"
}