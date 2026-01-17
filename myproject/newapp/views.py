from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from .serializer import *
from .decorators import role_required
from rest_framework.permissions import IsAuthenticatedOrReadOnly

# --- Authentication Views ---

@api_view(['POST'])
@permission_classes([AllowAny])
def registration_view(request):
    serializer = ProfileSerializer(data=request.data)
    if serializer.is_valid():
        profile = serializer.save()
        user = profile.user
        
        # Assign default role 'Customer'
        group, _ = Group.objects.get_or_create(name='Customer')
        user.groups.add(group)
        
        # Create 'Manager' group just in case it's needed later
        Group.objects.get_or_create(name='Manager')

        # Generate Tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User registered successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'role': list(user.groups.values_list('name', flat=True))
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# --- Product Views ---

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_list_create_view(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Only Manager can create products
        @role_required(allowed_roles=['Manager'])
        def create_product(req):
            serializer = ProductSerializer(data=req.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return create_product(request)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PUT':
        @role_required(allowed_roles=['Manager'])
        def update_product(req):
            serializer = ProductSerializer(product, data=req.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return update_product(request)

    elif request.method == 'DELETE':
        @role_required(allowed_roles=['Manager'])
        def delete_product(req):
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return delete_product(request)


# --- Order Views ---

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_list_create_view(request):
    if request.method == 'GET':
        # Managers see all orders, Customers see their own
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'Manager' in user_groups:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    # Check permission: Manager or Owner
    user_groups = request.user.groups.values_list('name', flat=True)
    if 'Manager' not in user_groups and order.user != request.user:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@role_required(allowed_roles=['Manager'])
def order_status_update_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.data.get('status')
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        return Response({"message": f"Order status updated to {new_status}"})
    return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)


# --- Wishlist Views ---

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def wishlist_list_create_view(request):
    if request.method == 'GET':
        wishlist = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        product_id = request.data.get('product')
        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, pk=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            return Response({"message": "Product already in wishlist"}, status=status.HTTP_200_OK)
        
        serializer = WishlistSerializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def wishlist_delete_view(request, pk):
    wishlist_item = get_object_or_404(Wishlist, pk=pk, user=request.user)
    wishlist_item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# --- Profile Views ---

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

