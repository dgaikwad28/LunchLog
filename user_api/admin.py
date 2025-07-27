from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from user_api.models import Receipt, Restaurant

UserModel = get_user_model()

admin.site.unregister(Group)
admin.site.unregister(BlacklistedToken)
admin.site.unregister(EmailAddress)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialToken)
admin.site.unregister(OutstandingToken)


# Register your models here.
@admin.register(UserModel)
class UserAdminExtend(UserAdmin):
    list_display = ("username", "email")
    search_fields = ("username", "first_name", "last_name", "email")


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "price", "created", "updated")
    search_fields = ("id", "user__usernameusername", "user__email")
    list_filter = (("restaurant", admin.EmptyFieldListFilter),)

    @staticmethod
    def username(obj: Receipt) -> str:
        return obj.user.username

    @staticmethod
    def email(obj: Receipt) -> str:
        return obj.user.email


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "food_type", "receipts_count")
    search_fields = ("name", "food_type")

    @staticmethod
    def receipts_count(obj: Receipt) -> str:
        return obj.receipts.count()
