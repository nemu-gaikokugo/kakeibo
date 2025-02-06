from django.contrib import admin
from django.urls import path, include

from kakeibo.views import top

urlpatterns = [
    path('', top, name='top'),
    path('<int:year>/<int:month>/', top, name='top_by_month'),
    path('transaction/', include('kakeibo.urls')),
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")),
]
