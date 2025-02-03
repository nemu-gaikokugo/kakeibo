from django.contrib import admin
from kakeibo.models import Transaction
from kakeibo.models import Category


admin.site.register(Transaction)
admin.site.register(Category)