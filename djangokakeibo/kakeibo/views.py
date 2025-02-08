from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, Http404, HttpResponse
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db.models import Sum, F
from datetime import datetime, date, timedelta
from kakeibo.models import Transaction, Category, Currency, AccountType, Denomination, CashHolding, AccountBalance
from kakeibo.forms import TransactionForm, CompareCashBalanceForm, CompareAccountsBalanceForm
import csv
import json

# 取引登録ページ
@login_required
def transaction_new(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect(transaction_detail,transaction_id=transaction.pk)
    else:
        form = TransactionForm()
    return render(request, "transactions/transaction_new.html", {'form': form})

# 取引編集ページ
@login_required
def transaction_edit(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    if transaction.user_id != request.user.id:
        return HttpResponseForbidden("この取引の編集は許可されていません。")

    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('top')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'transactions/transaction_edit.html', {'form': form})

# 取引詳細ページ
@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    
    if transaction.user != request.user:    # 他人の取引ページにアクセスするのを禁ずる
        raise Http404
    
    return render(request, 'transactions/transaction_detail.html', {'transaction': transaction})

# トップページ（今月の取引を全て表示）
@login_required
def top(request, year=None, month=None):
    today = now().date()
    
    # 指定がなければ今月をデフォルトにする
    if year is None or month is None:
        year = today.year
        month = today.month

    # 今月のデータを取得
    start_of_month = date(year, month, 1)
    # start_of_month = datetime(year, month, 1).date()
    if month == 12:
        end_of_month = date(year+1, 1, 1)
    else:
        end_of_month = date(year, month+1, 1)

    # 自身の取引かつ今月の取引のみフィルター
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=start_of_month,
        date__lt=end_of_month
        )
    
    # 前月・翌月の計算
    previous_month = start_of_month - timedelta(days=1)
    next_month = end_of_month

    # 最新の月かどうかを判定（次の月に進めないようにする）
    is_latest_month = (year == today.year and month == today.month)

    context = {
        "transactions": transactions,
        "summary": transaction_summary(request.user, year, month),
        "current_month": month,
        "current_year": year,
        "previous_month": previous_month.month,
        "previous_year": previous_month.year,
        "next_month": next_month.month,
        "next_year": next_month.year,
        "is_latest_month": is_latest_month,
        }
    
    return render(request, "transactions/top.html", context)

# 収支計算用関数
def transaction_summary(user,year,month):

    # 今月のデータを取得
    start_of_month = datetime(year, month, 1).date()
    if month == 12:
        end_of_month = date(year+1, 1, 1)
    else:
        end_of_month = date(year, month+1, 1)
    monthly_transactions = Transaction.objects.filter(user=user, date__gte=start_of_month, date__lt=end_of_month)

    # 収入と支出を計算（収入はプラス、支出はマイナスと仮定）
    monthly_income = sum(t.amount for t in monthly_transactions if t.amount > 0)
    monthly_expense = sum(t.amount for t in monthly_transactions if t.amount < 0)
    monthly_balance = monthly_income + monthly_expense  # 今月の収支

    # 累計残金（表示期間までの合計）
    total_balance = sum(t.amount for t in Transaction.objects.filter(user=user, date__lt=end_of_month))

    return {
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'monthly_balance': monthly_balance,
        'total_balance': total_balance,
    }

# CSVファイルエクスポート用ページ
def export_transactions(request):
    # ヘッダーを設定し、CSVファイルとしてレスポンスを作成
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    # CSVの出力先をresponseに設定
    writer = csv.writer(response)
    
    # CSVのヘッダー（カラム名）
    writer.writerow(['Transaction ID', 'Category', 'Amount', 'Currency', 'Account Type', 'Date', 'Description'])

    # ユーザー自身の取引データのみを取得して書き込み
    transactions = Transaction.objects.filter(user=request.user)

    for transaction in transactions:
        writer.writerow([
            transaction.transaction_id,
            # transaction.user.username,  # ユーザー名は表示しない（ユーザーにユーザー名を認識する必要がないようにするため
            transaction.category.name if transaction.category else '',
            transaction.amount,
            transaction.currency.name if transaction.currency else '',
            transaction.account_type.name if transaction.account_type else '',
            transaction.date,
            transaction.description if transaction.description else ''
        ])

    return response


@login_required
def bulk_transaction_entry(request):

    # 入力値に問題があって戻ってきた場合はデータとエラーメッセージを取得
    transactions_data = request.session.pop('bulk_transactions', None)
    errors = request.session.pop('bulk_errors', [])
    print(transactions_data)
        
    return render(request, 'transactions/bulk_entry.html', {
        'transactions_json': json.dumps(transactions_data), # JavaScriptで扱うためJSON形式に変換
        'errors': errors})

@login_required
def bulk_transaction_confirm(request):
    if request.method=='POST':
        try:
            transactions_data = request.POST.get("transactions")
            transactions_json = json.loads(transactions_data)
            transactions = []
            errors=[]
            for index, row in enumerate(transactions_json):

                # 表から取得した文字列データを格納
                category_value = row[0]
                amount_value=row[1]
                currency_value=row[2]
                account_type_value=row[3]
                date_value=row[4]
                description_value=row[5]

                # 以下バリデーション
                
                # カテゴリのバリデーション
                category = Category.objects.filter(name=category_value).first()
                if not category:
                    errors.append(f"{index+1}行目：カテゴリ '{category_value}' は存在しません。存在するカテゴリを入力してください。")

                # 金額のバリデーション
                try:
                    amount=float(amount_value)
                except ValueError:
                    errors.append(f"{index+1}行目：金額 '{amount_value}' は無効な値です。数値を入力してください。")
                
                # 通貨のバリデーション
                currency = Currency.objects.filter(name=currency_value).first()
                if not currency:
                    errors.append(f"{index+1}行目：通貨 '{currency_value}' は存在しません。存在する通貨を入力してください。")
                
                # 資金形態のバリデーション
                account_type = AccountType.objects.filter(name=account_type_value).first()
                if not account_type:
                    errors.append(f"{index+1}行目：資金形態 '{account_type_value}' は存在しません。存在する資金形態を入力してください。")

                # 日付のバリデーション
                try:
                    datetime.strptime(date_value, '%Y-%m-%d')
                except ValueError:
                    errors.append(f"{index+1}行目：日付 '{date_value}' は無効な形式です。(YYYY-MM-DD)形式で入力してください。")

                # "説明"に関してはバリデーションを設けない

                # 入力値に問題がなければ取引データを追加
                transactions.append({
                    'category': category_value,
                    'amount': amount_value,
                    'currency': currency_value,
                    'account_type': account_type_value,
                    'date': date_value,
                    'description': description_value
                })
            
            # セッションにデータを保存
            request.session['bulk_transactions'] = transactions
            request.session['bulk_errors'] = errors
            
            # エラーがあった場合は入力値を保持しつつ入力画面へ遷移
            if errors:
                return redirect('bulk_transaction_entry')
            
            return render(request, 'transactions/bulk_confirm.html', {'transactions':transactions})
        except json.JSONDecodeError:
            return redirect('bulk_transaction_entry')
        
    return redirect('bulk_transaction_entry')

@login_required
def bulk_transaction_save(request):
    if 'bulk_transactions' in request.session:
        # セッションから取引データを取得
        transactions_data = request.session.pop('bulk_transactions')

        # 取得した取引データをDjangoが読み取り可能な形に変換
        transactions = []
        for data in transactions_data:
            category_value=data.get('category')
            currency_value=data.get('currency')
            account_type_value=data.get('account_type')

            transaction = Transaction(
                user=request.user,
                category=Category.objects.filter(name=category_value).first(),
                amount=data.get('amount'),
                currency=Currency.objects.filter(name=currency_value).first(),
                account_type=AccountType.objects.filter(name=account_type_value).first(),
                date=data.get('date'),
                description=data.get('description')
            )
            transactions.append(transaction)

        # リスト形式でDBへ一挙に登録
        Transaction.objects.bulk_create(transactions)
    
    return redirect('top')

@login_required
def compare_balance(request):
    # デフォルトの通貨は円とする
    default_currency = Currency.objects.filter(name="円").first()
    
    # 所持している現金情報の取得
    cash_holdings = CashHolding.objects.filter(user=request.user, currency=default_currency)
    
    # 所持している現金の初期値（値がなければ0）
    cash_data = {
        f"denomination_{holding.denomination.value}": holding.quantity for holding in cash_holdings
    }
    
    # 現金以外の所持金の初期値（値がなければ0）
    account_balances = AccountBalance.objects.filter(user=request.user, currency=default_currency)
    
    account_data = {
        balance.account_type.name: balance.balance for balance in account_balances
    }
    
    total_entered = 0
    total_balance = sum(t.amount for t in Transaction.objects.filter(user=request.user, date__lt=calculate_end_of_month(now().date())))
    
    # 入力フォームのボタンを押した場合（ユーザーがフォームに入力した場合を想定）
    if request.method == 'POST':
        # フォームに入力された現金の枚数を取得
        cash_form = CompareCashBalanceForm(request.POST)
        # ユーザーが入力した現金の金額の合計を計算
        if cash_form.is_valid():
            for denomination in Denomination.objects.filter(currency=default_currency):
                denomination_value = denomination.value
                entered_value = cash_form.cleaned_data.get(f'denomination_{denomination_value}', 0) or 0
                total_entered += denomination_value * entered_value
                # CashHolding のデータが既にある場合は更新、なければ作成
                cash_holding, created = CashHolding.objects.get_or_create(
                    user=request.user,
                    currency=default_currency,
                    denomination=denomination,
                    defaults={'quantity': entered_value}
                )
                if not created:
                    cash_holding.quantity = entered_value
                    cash_holding.save()
        
        # フォームに入力された口座類の残高を取得
        account_form = CompareAccountsBalanceForm(request.POST)
        # ユーザーが入力した口座類の残高の合計を計算
        if account_form.is_valid():
            for account_type in AccountType.objects.all():
                entered_value = account_form.cleaned_data.get(account_type.name) or 0
                total_entered += entered_value
                # AccountBalance のデータが既にある場合は更新、なければ作成
                account_balance, created = AccountBalance.objects.get_or_create(
                    user=request.user,
                    currency=default_currency,
                    account_type=account_type,
                    defaults={'balance': entered_value}
                )
                if not created:
                    account_balance.balance = entered_value
                    account_balance.save()


    # リンクを押して遷移したりURL直打ちで遷移してきた場合
    else:
        # データベースから前回入力した値を取得
        cash_form = CompareCashBalanceForm(initial=cash_data)
        account_form = CompareAccountsBalanceForm(initial=account_data)

        # 前回入力した現金の所持金の総和を計算
        for denomination in Denomination.objects.filter(currency=default_currency):
            for cash_holding in CashHolding.objects.filter(user=request.user, currency=default_currency, denomination=denomination):
                total_entered += denomination.value * cash_holding.quantity
        # 前回入力した口座類の残高の総和を計算
        for account_balance in AccountBalance.objects.filter(user=request.user, currency=default_currency):
            total_entered += account_balance.balance
                
    
    # 差額計算
    difference = total_balance - total_entered
    
    # 計算結果をビューに渡す
    return render(request, 'transactions/compare_balance.html', {
        'cash_form': cash_form,
        'account_form': account_form,
        'cash_holdings': cash_holdings,
        'total_balance': total_balance,
        'total_entered': total_entered,
        'difference': difference,
    })

def calculate_end_of_month(today):
    year = today.year
    month = today.month

    # start_of_month = datetime(year, month, 1).date()
    if month == 12:
        end_of_month = date(year+1, 1, 1)
    else:
        end_of_month = date(year, month+1, 1)
    
    return end_of_month