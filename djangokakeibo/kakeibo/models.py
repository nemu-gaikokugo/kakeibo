from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField("カテゴリ名", max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)    # ユーザーごとにカテゴリを管理
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField("貨幣名", max_length=50)
    symbol = models.CharField(max_length=1)
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return self.name


class AccountType(models.Model):
    name = models.CharField("資金形態", max_length=50)
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return self.name

    
class Denomination(models.Model):
    currency = models.ForeignKey(Currency, related_name='denominations', on_delete=models.CASCADE)
    value = models.IntegerField()  # 札や硬貨の金額（例：10000, 5000, 1000）
    denomination_type = models.CharField(max_length=10, choices=[('bill', '札'), ('coin', '硬貨')])
    # created_at = models.DateTimeField("作成日", auto_now_add=True)
    # updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return f"{self.currency.symbol} {self.value} - {self.denomination_type}"


class CashHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ユーザー
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)  # 通貨
    denomination = models.ForeignKey(Denomination, on_delete=models.CASCADE)  # 金種
    quantity = models.PositiveIntegerField()  # 所持金額（その金種の枚数）
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.currency.symbol} {self.denomination.value} x {self.quantity}"
    

class AccountBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=24, decimal_places=2)
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_type.name}: {self.balance} {self.currency.name}"


class Counterparty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField("取引相手名",max_length=255)
    # ↓そのうち追加する！
    # location = 
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    reference = models.TextField("参考情報")
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return self.name

class ConsumptionTax(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField("税の種類", max_length=255)
    tax_rate = models.FloatField(null=False)
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    account_type = models.ForeignKey(AccountType, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    counterparty = models.ForeignKey(Counterparty, on_delete=models.SET_NULL, null=True)
    consumption_tax = models.ForeignKey(ConsumptionTax, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return f"ID:{self.transaction_id}"


class ProductRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return self.product.name