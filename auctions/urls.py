from django.urls import path
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("<int:listing_id>/success", views.success, name="success"),
    path("<int:listing_id>/fail", views.fail, name="fail"),
    path("<int:listing_id>/comment", views.comment, name="comment"),
    path("<int:listing_id>/add", views.add_to_watchlist, name="add"),
    path("<int:listing_id>/remove", views.remove_from_watchlist, name="remove"),
    path("created", views.created, name="created"),
    path("categories/<str:ctgr>", views.category, name="category"),
    path("<int:listing_id>/close", views.close_auction, name="close"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("seller_listings/<str:seller>", views.seller_listings, name="seller_listings"),
    path("search_results/<str:query>", views.search_results, name="search_results"),
    path("my_bids", views.my_bids, name="my_bids")
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)