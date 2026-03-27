from rest_framework import viewsets, permissions, generics
from .models import Product, Wishlist
from .serializers import ProductSerializer, WishlistSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.db.models import Min
from django_filters import rest_framework as filters

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny, )

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        if product_id:
            existing = Wishlist.objects.filter(user=request.user, product_id=product_id).first()
            if existing:
                serializer = self.get_serializer(existing)
                return Response(serializer.data)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProductPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="prices__price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="prices__price", lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['brand', 'brand__name', 'sector', 'sector__name', 'cpu', 'ram', 'storage', 'gpu', 'screen_size', 'gpu_brand', 'min_price', 'max_price']

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all() 
    serializer_class = ProductSerializer
    authentication_classes = [] 
    permission_classes = [permissions.AllowAny] 
    pagination_class = ProductPagination 
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'brand__name']
    ordering_fields = ['price', 'created_at']

    def get_queryset(self):
        return Product.objects.annotate(price=Min('prices__price')).all()

    @action(detail=False, methods=['get'])
    def compare(self, request):
        ids = request.query_params.get('ids', '')
        if not ids:
            return Response([])
        
        try:
            id_list = [int(x) for x in ids.split(',') if x.strip().isdigit()]
            products = Product.objects.filter(id__in=id_list)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class FilterViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def list(self, request):
        def get_distinct(field):
            query = Product.objects.exclude(**{f"{field}__isnull": True})
            # Only exclude empty strings for text fields (avoid ID filter crash)
            if field not in ['sector', 'brand', 'current_price']: 
                query = query.exclude(**{f"{field}__exact": ""})

            # Handle FKs by returning names
            if field in ['sector', 'brand']:
                 return sorted(list(set(query.values_list(f"{field}__name", flat=True))))

            return sorted(list(query.values_list(field, flat=True).distinct()))

        filters = {
            "brands": sorted(list(Product.objects.values_list('brand__name', flat=True).distinct())),
            "sectors": get_distinct('sector'),
            "cpus": get_distinct('cpu'),
            "rams": get_distinct('ram'),
            "storages": get_distinct('storage'),
            "gpus": get_distinct('gpu'),
            "screens": get_distinct('screen_size'),
        }
        return Response(filters)