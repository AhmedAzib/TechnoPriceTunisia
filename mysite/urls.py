from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet, WishlistViewSet, FilterViewSet, UserCreate
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Create a router and register our viewset with it.
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'filters', FilterViewSet, basename='filters')

urlpatterns = [
    path('admin/', admin.site.urls),
    # The router generates URLs for both list (/products/) and detail (/products/5/)
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', UserCreate.as_view(), name='user_register'),
]