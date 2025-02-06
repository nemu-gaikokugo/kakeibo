from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, Http404, HttpResponse
from django.utils.timezone import now
from datetime import datetime, date, timedelta
from kakeibo.models import Transaction
from kakeibo.forms import TransactionForm
import csv

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
    writer.writerow(['Transaction ID', 'User', 'Category', 'Amount', 'Currency', 'Account Type', 'Date', 'Description'])

    # ユーザー自身の取引データのみを取得して書き込み
    transactions = Transaction.objects.filter(user=request.user)

    for transaction in transactions:
        writer.writerow([
            transaction.transaction_id,
            transaction.user.username,  # ユーザー名を表示
            transaction.category.name if transaction.category else '',
            transaction.amount,
            transaction.currency.name if transaction.currency else '',
            transaction.account_type.name if transaction.account_type else '',
            transaction.date,
            transaction.description if transaction.description else ''
        ])

    return response