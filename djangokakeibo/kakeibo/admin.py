from django.contrib import admin
from kakeibo.models import Category
from kakeibo.models import Currency
from kakeibo.models import Transaction
from kakeibo.models import AccountType
from kakeibo.models import Denomination
from kakeibo.models import CashHolding

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
    list_display = ('user', 'currency', 'denomination', 'quantity')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(AccountType, AccountTypeAdmin)
admin.site.register(Denomination, DenominationAdmin) 
admin.site.register(CashHolding, CashHoldingAdmin)