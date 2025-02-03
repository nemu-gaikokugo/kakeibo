from django.contrib import admin
from kakeibo.models import Category
from kakeibo.models import Currency
from kakeibo.models import Transaction

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'updated_at')

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'created_at', 'updated_at')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user','category','amount','currency','date','description')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Transaction, TransactionAdmin)