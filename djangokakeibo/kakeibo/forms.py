from django import forms
from kakeibo.models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('category', 'amount', 'currency', 'date', 'description')
        