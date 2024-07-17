from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('categories/', views.categories, name='categories'),
    path('categories/<str:category>/', views.category_listings, name='category_listings'),
    path('listing/create/', views.create_listing, name='create_listing'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing'),
    path('listing/<int:listing_id>/bid/', views.place_bid, name='place_bid'),
    path('listing/<int:listing_id>/comment/', views.add_comment, name='add_comment'),
    path('watchlist/', views.display_watchlist, name='watchlist'),
    path('listing/<int:listing_id>/watchlist/add/', views.add_to_watchlist, name='add_to_watchlist'),
    path('listing/<int:listing_id>/watchlist/remove/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('listing/<int:listing_id>/close/', views.close_bid, name='close_bid'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
