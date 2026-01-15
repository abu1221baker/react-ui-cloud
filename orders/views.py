from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer
from products.models import Product


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_list(request):
    """
    Function-based view for listing and creating orders
    GET: List all orders for authenticated user
    POST: Create a new order
    """
    if request.method == 'GET':
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        data = request.data.copy()
        
        # Validate items
        items = data.get('items', [])
        if not items:
            return Response({
                'error': 'Order must contain at least one item'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total and validate products
        total_amount = 0
        for item in items:
            try:
                product = Product.objects.get(id=item['product_id'])
                if product.stock < item['quantity']:
                    return Response({
                        'error': f'Insufficient stock for {product.name}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Set price from product
                item['price'] = float(product.price)
                total_amount += item['price'] * item['quantity']
                
            except Product.DoesNotExist:
                return Response({
                    'error': f'Product with id {item["product_id"]} not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        data['total_amount'] = total_amount
        
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)
            
            # Update product stock
            for item in items:
                product = Product.objects.get(id=item['product_id'])
                product.stock -= item['quantity']
                product.save()
            
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    """
    Function-based view for retrieving and updating an order
    GET: Retrieve a specific order
    PUT: Update order status
    """
    try:
        order = Order.objects.get(pk=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found or you do not have permission to access it'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Only allow updating status and shipping address
        allowed_fields = ['status', 'shipping_address']
        data = {key: value for key, value in request.data.items() if key in allowed_fields}
        
        serializer = OrderSerializer(order, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
