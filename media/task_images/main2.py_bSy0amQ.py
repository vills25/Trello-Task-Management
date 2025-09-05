from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import re

def validate_mobile_number(value):
    if not re.match(r'^[0-9]{10}$', value):
        raise ValidationError('Mobile number must be 10 digits')

class User(AbstractUser):
    pass

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="sellers/", default="default.jpg")
    mobile_no = models.CharField(max_length=10, validators=[validate_mobile_number], unique=True)
    address = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="buyers/", default="default.jpg")
    mobile_no = models.CharField(max_length=10, validators=[validate_mobile_number], unique=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Product(models.Model):
    ITEM_CATEGORIES = [
        ('CLOTHE', 'Clothing'),
        ('ELECTRONICS', 'Electronics'),
        ('BOOKS', 'Books'),
        ('BEAUTY', 'Beauty'),
        ('MEN_ACCESSORIES', "Men's Accessories"),
        ('WOMEN_ACCESSORIES', "Women's Accessories"),
        ('FURNITURE', 'Furniture'),
        ('GARDEN', 'Garden'),
    ]
    
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    images = models.JSONField(default=list)  # Stores list of image URLs
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    sale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.01)]
    )
    quantity = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=ITEM_CATEGORIES)
    sub_category = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    tags = models.CharField(max_length=255, blank=True)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=20, blank=True)
    fabric = models.CharField(max_length=50, blank=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.sale_price and self.sale_price >= self.price:
            raise ValidationError("Sale price must be less than regular price")
        if self.quantity < 0:
            raise ValidationError("Quantity cannot be negative")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    dispatch_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=50, blank=True)
    shipping_company = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)

    def clean(self):
        if self.quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        if self.price <= 0:
            raise ValidationError("Price must be greater than 0")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('COD', 'Cash on Delivery'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('NET_BANKING', 'Net Banking'),
        ('UPI', 'UPI'),
        ('WALLET', 'Wallet'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_date = models.DateTimeField(auto_now_add=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment #{self.transaction_id}"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'buyer')

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review for {self.product.name} by {self.buyer.user.username}"
    
# ------------------------------changed--------------------

class Product(models.Model):
    ITEM_CATEGORIES = [
        ('CLOTHE', 'Clothing'),
        ('ELECTRONICS', 'Electronics'),
        ('BOOKS', 'Books'),
        ('BEAUTY', 'Beauty'),
        ('MEN_ACCESSORIES', "Men's Accessories"),
        ('WOMEN_ACCESSORIES', "Women's Accessories"),
        ('FURNITURE', 'Furniture'),
        ('GARDEN', 'Garden'),
    ]

    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    images = models.ImageField()
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0.01)])
    quantity = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=ITEM_CATEGORIES)
    sub_category = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    tags = models.CharField(max_length=255, blank=True)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=20, blank=True)
    fabric = models.CharField(max_length=50, blank=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'subcategory_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'subcategory_updated_by')

    def clean(self):
        if self.sale_price and self.sale_price >= self.price:
            raise ValidationError("Sale price must be less than regular price")
        if self.quantity < 0:
            raise ValidationError("Quantity cannot be negative")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    dispatch_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=50, blank=True)
    shipping_company = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Order #{self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)
    
    def clean(self):
        if self.quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        if self.price <= 0:
            raise ValidationError("Price must be greater than 0")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('COD', 'Cash on Delivery'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('NET_BANKING', 'Net Banking'),
        ('UPI', 'UPI'),
        ('WALLET', 'Wallet'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_date = models.DateTimeField(auto_now_add=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment #{self.transaction_id}"

# class ProductReview(models.Model):
#     product_review_id = models.AutoField(primary_key=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
#     rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
#     comment = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_approved = models.BooleanField(default=False)

#     class Meta:
#         unique_together = ('product', 'buyer')

#     def __str__(self):
#         return f"Review for {self.product.name} by {self.buyer.user.username}"

# class ProductReviewSerializer(serializers.ModelSerializer):
#     buyer = BuyerSerializer()
#     product = ProductSerializer()
    
#     class Meta:
#         model = ProductReview
#         fields = ['id', 'product', 'buyer', 'rating', 'comment', 'is_approved', 'created_at', 'updated_at']
#         read_only_fields = fields