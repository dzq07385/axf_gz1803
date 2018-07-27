from django.conf.urls import url
from .apis_v1 import *

urlpatterns = [
    url(r"^register$", RegisterAPI.as_view(), name="api_register"),
    url(r"^active/(.+)", active),
    url(r"^login$", LoginAPI.as_view()),
    url(r"^logout$", LogoutAPI.as_view(), name="logout"),
    url(r"^cart$", cart_api),
    url(r"^cart_item$", cart_item_api),
    url(r"^cart_item_status$", CartItemStatusAPI.as_view()),
    url(r"^cart_all_select$", CartAllItemStatusAPI.as_view())
]