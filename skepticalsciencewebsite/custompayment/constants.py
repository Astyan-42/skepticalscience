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
SCIENTIST_ACCOUNT_PRICE = 100
PUBLICATION_PRICE = 1000

PRODUCTS_PRICES = [
    (PUBLICATION, PUBLICATION_PRICE),
    (SCIENTIST_ACCOUNT, SCIENTIST_ACCOUNT_PRICE)
]

# discount type
PERCENT = 'percent'
FIXED = 'fixed'

DISCOUNT_CHOICES = [
    (PERCENT, 'percent'),
    (FIXED, 'fixed')
]