from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, Http404
from kakeibo.models import Transaction
from kakeibo.forms import TransactionForm

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

@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    
    if transaction.user != request.user:    # 他人の取引ページにアクセスするのを禁ずる
        raise Http404
    
    return render(request, 'transactions/transaction_detail.html', {'transaction': transaction})

@login_required
def top(request):
    transactions = Transaction.objects.filter(user=request.user)    # 自身の取引のみフィルター
    context = {"transactions": transactions}
    return render(request, "transactions/top.html", context)
