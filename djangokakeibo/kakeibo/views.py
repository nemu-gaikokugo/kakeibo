from django.shortcuts import render
from django.http import HttpResponse
from kakeibo.models import Transaction

def top(request):
    transactions = Transaction.objects.all()
    context = {"transactions": transactions}
    return render(request, "transactions/top.html", context)
