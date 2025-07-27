from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from . import viewsets

router = DefaultRouter()
router.register('receipts', viewset=viewsets.ReceiptsViewSet, basename='receipts')

app_name = 'user_api'
urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('receipts/image-upload/<uuid:pk>/', views.ReceiptImageUploadView.as_view(), name='receipt-image-upload'),

]

urlpatterns += router.urls
