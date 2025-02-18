from django import forms
from kakeibo.models import Transaction, Denomination, AccountType, ProductRecord

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

class CompareCashBalanceForm(forms.Form):
    def __init__(self, *args, currency=None, **kwargs):
        """
        currency: フォーム生成時に渡す通貨（例: "円"）
        """
        super().__init__(*args, **kwargs)

        # currency に応じて Denomination を取得し、動的にフィールドを追加
        if currency:
            denominations = Denomination.objects.filter(currency=currency)  # 通貨ごとの金種
        else:
            denominations = Denomination.objects.all()  # 通貨指定なしなら全て

        for denomination in denominations:
            field_name = f'denomination_{denomination.value}'
            self.fields[field_name] = forms.IntegerField(
                initial=0,
                required=True,
                label=f"{denomination.value} {denomination.currency}",
                widget=forms.NumberInput(attrs={'placeholder': '枚数を入力'})
            )

class CompareAccountsBalanceForm(forms.Form):
    for account_type in AccountType.objects.all():
        if account_type.name != '現金':
            locals()[account_type.name] = forms.IntegerField(
                initial=0,
                required=True,
                label=account_type.name
            )

class ProductRecordForm(forms.ModelForm):
    class Meta:
        model = ProductRecord
        fields = {'category', 'product', 'price', 'currency'}
        labels = {
            'category': 'カテゴリ',
            'product': '商品名',
            'price': '価格',
            'currency': '通貨',
        }