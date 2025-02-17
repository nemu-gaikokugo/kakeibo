from django.contrib import admin
from kakeibo.models import Category
from kakeibo.models import Currency
from kakeibo.models import Transaction
from kakeibo.models import AccountType
from kakeibo.models import Denomination
from kakeibo.models import CashHolding
from kakeibo.models import AccountBalance
from kakeibo.models import Counterparty
from kakeibo.models import Product
from kakeibo.models import ProductRecord
from kakeibo.models import ConsumptionTax

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'updated_at')

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'created_at', 'updated_at')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user','category','amount','currency','date','description')

class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')

class DenominationAdmin(admin.ModelAdmin):
    list_display = ('currency', 'value', 'denomination_type')

class CashHoldingAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'denomination', 'quantity', 'created_at', 'updated_at')

class AccountBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type', 'currency', 'balance', 'created_at', 'updated_at')

class CounterpartyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_at', 'updated_at')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'reference', 'created_at', 'updated_at')

class ProductRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction', 'product', 'price', 'currency', 'created_at', 'updated_at')

class ConsumptionTaxAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'tax_rate', 'created_at', 'updated_at')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(AccountType, AccountTypeAdmin)
admin.site.register(Denomination, DenominationAdmin) 
admin.site.register(CashHolding, CashHoldingAdmin)
admin.site.register(AccountBalance, AccountBalanceAdmin)
admin.site.register(Counterparty, CounterpartyAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductRecord, ProductRecordAdmin)
admin.site.register(ConsumptionTax, ConsumptionTaxAdmin)