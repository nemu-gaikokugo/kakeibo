from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, Http404
from django.utils.timezone import now
from datetime import datetime
from kakeibo.models import Transaction
from kakeibo.forms import TransactionForm

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
def top(request):

    today = now().date()
    start_of_month = datetime(today.year, today.month, 1).date()           
    transactions = Transaction.objects.filter(user=request.user, date__gte=start_of_month)    # 自身の取引かつ今月の取引のみフィルター
    context = {
        "transactions": transactions,
        "summary": transaction_summary(request.user),
        "current_month": today.strftime('%m')
        }
    
    return render(request, "transactions/top.html", context)


def transaction_summary(user):
    today = now().date()

    # 今月のデータを取得
    start_of_month = datetime(today.year, today.month, 1).date()
    monthly_transactions = Transaction.objects.filter(user=user, date__gte=start_of_month)

    # 収入と支出を計算（収入はプラス、支出はマイナスと仮定）
    monthly_income = sum(t.amount for t in monthly_transactions if t.amount > 0)
    monthly_expense = sum(t.amount for t in monthly_transactions if t.amount < 0)
    monthly_balance = monthly_income + monthly_expense  # 今月の収支

    # 累計残金（全期間の合計）
    total_balance = sum(t.amount for t in Transaction.objects.filter(user=user))

    return {
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'monthly_balance': monthly_balance,
        'total_balance': total_balance,
    }