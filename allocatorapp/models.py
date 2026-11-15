
from django.db import models


class Resource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):

    SIDE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIALLY_FILLED', 'Partially Filled'),
        ('FILLED', 'Filled'),
        ('CANCELLED', 'Cancelled'),
        ('REJECTED', 'Rejected'),
    ]

    customer_code = models.CharField(max_length=50)
    resource = models.ForeignKey(Resource, on_delete=models.PROTECT, related_name='orders')
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    quantity = models.PositiveIntegerField()
    remaining_quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_code} - {self.resource.name} - {self.side}"


class Trade(models.Model):

    buy_order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='buy_trades')
    sell_order = models.ForeignKey( Order, on_delete=models.PROTECT,related_name='sell_trades')
    # Trade execution details
    quantity = models.PositiveIntegerField()
    trade_price = models.DecimalField(max_digits=12, decimal_places=2)
    executed_at = models.DateTimeField(auto_now_add=True)
    transaction_reference = models.CharField(max_length=100,unique=True)
    transaction_status = models.CharField(max_length=20, default='COMPLETED')
    transaction_amount = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f"Trade #{self.id} - {self.transaction_reference}"
