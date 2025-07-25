from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from . import viewsets

router = DefaultRouter()
router.register('receipts', viewset=viewsets.ReceiptsViewSet, basename='receipts')

urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('receipts/image-upload/<uuid:pk>/', views.ReceiptImageUploadView.as_view(), name='signup'),

]

urlpatterns += router.urls
