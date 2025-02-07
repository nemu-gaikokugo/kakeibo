from django import forms
from kakeibo.models import Transaction, Denomination

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

class CompareBalanceForm(forms.Form):
    # Denominationごとにフィールドを作成
    # 各金種（例：10000円、5000円など）ごとの入力欄を定義
    for denomination in Denomination.objects.all():
        locals()[f'denomination_{denomination.value}'] = forms.IntegerField(
            initial=0,
            required=False,
            label=f"{denomination.value}円",
            widget=forms.NumberInput(attrs={'placeholder': '枚数を入力'})
        )