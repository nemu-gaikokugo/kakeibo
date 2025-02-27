from django.urls import path
from kakeibo import views

urlpatterns = [
    path("new/", views.transaction_new, name="transaction_new"),
    path("export/", views.export_transactions, name='export_transactions'),
    path("<int:transaction_id>/", views.transaction_detail, name="transaction_detail"),
    path("<int:transaction_id>/edit/", views.transaction_edit, name="transaction_edit"),
    path("bulk-entry/", views.bulk_transaction_entry, name="bulk_transaction_entry"),
    path("bulk-confirm/", views.bulk_transaction_confirm, name="bulk_transaction_confirm"),
    path("bulk-save", views.bulk_transaction_save, name="bulk_transaction_save"),
    path("compare-balance", views.compare_balance, name="compare_balance"),
    path("product/", views.products_list, name="products_list"),
    path("product/<int:product_id>", views.product_detail, name="product_detail"),
    path("product/<int:product_id>/edit/", views.product_edit, name="product_edit"),
]