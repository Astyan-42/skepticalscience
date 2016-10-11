
NEW = 'new'
CANCELLED = 'cancelled'
PAYMENT_PENDING = 'payment-pending'
FULLY_PAID = 'fully-paid'

ORDER_CHOICES = [
        (NEW, 'Processing'),
        (CANCELLED, 'Cancelled'),
        (PAYMENT_PENDING, 'Payment pending'),
        (FULLY_PAID, 'Fully paid')]