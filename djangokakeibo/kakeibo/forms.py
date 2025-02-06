from django import forms
from kakeibo.models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('category', 'amount', 'currency', 'account_type', 'date', 'description')
        labels = {
            'category': 'カテゴリ',
            'amount': '金額',
            'currency': '通貨',
            'account_type': '資金形態',
            'date': '取引日',
            'description': '説明'
        }