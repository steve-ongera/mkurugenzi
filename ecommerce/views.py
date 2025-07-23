from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from decimal import Decimal
import json

from .models import (
    Product, Category, Brand, ProductVariant, Cart, CartItem, 
    Customer, Order, OrderItem, Color, Size, Coupon
)


def index(request):
    """Homepage with featured products, categories, and search"""
    # Get search query
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    brand_filter = request.GET.get('brand', '')
    
    # Base queryset for products
    products = Product.objects.filter(is_active=True).select_related('brand', 'category')
    
    # Apply search filter
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Apply category filter
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    # Apply brand filter
    if brand_filter:
        products = products.filter(brand__slug=brand_filter)
    
    # Get featured products
    featured_products = products.filter(is_featured=True)[:8]
    
    # Get latest products
    latest_products = products.order_by('-created_at')[:12]
    
    # Get categories with product count
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    )
    
    # Get brands with product count
    brands = Brand.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    )
    
    # Pagination for search results
    if search_query or category_filter or brand_filter:
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        page_products = paginator.get_page(page_number)
    else:
        page_products = None
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'categories': categories,
        'brands': brands,
        'search_query': search_query,
        'category_filter': category_filter,
        'brand_filter': brand_filter,
        'page_products': page_products,
        'is_search': bool(search_query or category_filter or brand_filter),
    }
    
    return render(request, 'ecommerce/index.html', context)


def product_detail(request, slug):
    """Product detail page with variants and reviews"""
    product = get_object_or_404(
        Product.objects.select_related('brand', 'category')
        .prefetch_related('variants__color', 'variants__size', 'images', 'reviews__customer__user'),
        slug=slug,
        is_active=True
    )
    
    # Get product variants grouped by color
    variants_by_color = {}
    for variant in product.variants.filter(is_active=True):
        color_name = variant.color.name
        if color_name not in variants_by_color:
            variants_by_color[color_name] = {
                'color': variant.color,
                'sizes': []
            }
        variants_by_color[color_name]['sizes'].append({
            'size': variant.size,
            'variant': variant,
            'in_stock': variant.is_in_stock
        })
    
    # Get product images
    images = product.images.all().order_by('order')
    
    # Get reviews with ratings
    reviews = product.reviews.filter(is_approved=True).select_related('customer__user')
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    rating_counts = {i: reviews.filter(rating=i).count() for i in range(1, 6)}
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:6]
    
    context = {
        'product': product,
        'variants_by_color': variants_by_color,
        'images': images,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'rating_counts': rating_counts,
        'related_products': related_products,
    }
    
    return render(request, 'ecommerce/product.html', context)


@login_required
@require_POST
def add_to_cart(request):
    """Add product variant to cart"""
    try:
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not variant_id:
            return JsonResponse({'success': False, 'message': 'Please select size and color'})
        
        variant = get_object_or_404(ProductVariant, id=variant_id, is_active=True)
        
        # Check stock
        if variant.stock_quantity < quantity:
            return JsonResponse({
                'success': False, 
                'message': f'Only {variant.stock_quantity} items available'
            })
        
        # Get or create customer
        customer, created = Customer.objects.get_or_create(user=request.user)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(customer=customer)
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > variant.stock_quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot add more than {variant.stock_quantity} items'
                })
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Product added to cart successfully',
            'cart_count': cart.total_items
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred'})


@login_required
def cart_view(request):
    """Shopping cart page"""
    try:
        customer = Customer.objects.get(user=request.user)
        cart = Cart.objects.get(customer=customer)
        cart_items = cart.items.select_related(
            'product_variant__product',
            'product_variant__color',
            'product_variant__size'
        )
    except (Customer.DoesNotExist, Cart.DoesNotExist):
        cart_items = []
        cart = None
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    shipping_cost = Decimal('5.00') if subtotal < 50 else Decimal('0.00')
    total = subtotal + shipping_cost
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
    }
    
    return render(request, 'ecommerce/cart.html', context)


@login_required
@require_POST
def update_cart(request):
    """Update cart item quantity"""
    try:
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer__user=request.user)
        
        if quantity <= 0:
            cart_item.delete()
            return JsonResponse({'success': True, 'message': 'Item removed from cart'})
        
        if quantity > cart_item.product_variant.stock_quantity:
            return JsonResponse({
                'success': False,
                'message': f'Only {cart_item.product_variant.stock_quantity} items available'
            })
        
        cart_item.quantity = quantity
        cart_item.save()
        
        # Recalculate totals
        cart = cart_item.cart
        subtotal = sum(item.total_price for item in cart.items.all())
        shipping_cost = Decimal('5.00') if subtotal < 50 else Decimal('0.00')
        total = subtotal + shipping_cost
        
        return JsonResponse({
            'success': True,
            'message': 'Cart updated successfully',
            'item_total': cart_item.total_price,
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'total': total,
            'cart_count': cart.total_items
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred'})


@login_required
@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    try:
        item_id = request.POST.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer__user=request.user)
        cart_item.delete()
        
        return JsonResponse({'success': True, 'message': 'Item removed from cart'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred'})


@login_required
def checkout(request):
    """Checkout page"""
    try:
        customer = Customer.objects.get(user=request.user)
        cart = Cart.objects.get(customer=customer)
        cart_items = cart.items.select_related(
            'product_variant__product',
            'product_variant__color',
            'product_variant__size'
        )
        
        if not cart_items:
            messages.error(request, 'Your cart is empty')
            return redirect('ecommerce:cart')
            
    except (Customer.DoesNotExist, Cart.DoesNotExist):
        messages.error(request, 'Your cart is empty')
        return redirect('ecommerce:cart')
    
    # Get customer addresses
    addresses = customer.addresses.all()
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    tax_rate = Decimal('0.08')  # 8% tax
    tax_amount = subtotal * tax_rate
    shipping_cost = Decimal('5.00') if subtotal < 50 else Decimal('0.00')
    total = subtotal + tax_amount + shipping_cost
    
    if request.method == 'POST':
        # Process checkout
        billing_address_id = request.POST.get('billing_address')
        shipping_address_id = request.POST.get('shipping_address')
        coupon_code = request.POST.get('coupon_code', '').strip()
        
        if not billing_address_id or not shipping_address_id:
            messages.error(request, 'Please select billing and shipping addresses')
        else:
            try:
                billing_address = customer.addresses.get(id=billing_address_id)
                shipping_address = customer.addresses.get(id=shipping_address_id)
                
                # Apply coupon if provided
                discount_amount = Decimal('0.00')
                if coupon_code:
                    try:
                        coupon = Coupon.objects.get(code=coupon_code)
                        if coupon.is_valid() and subtotal >= coupon.minimum_order_amount:
                            if coupon.discount_type == 'percentage':
                                discount_amount = subtotal * (coupon.discount_value / 100)
                                if coupon.maximum_discount_amount:
                                    discount_amount = min(discount_amount, coupon.maximum_discount_amount)
                            else:
                                discount_amount = coupon.discount_value
                            
                            # Update coupon usage
                            coupon.used_count += 1
                            coupon.save()
                        else:
                            messages.error(request, 'Invalid or expired coupon code')
                    except Coupon.DoesNotExist:
                        messages.error(request, 'Invalid coupon code')
                
                # Recalculate total with discount
                final_total = subtotal + tax_amount + shipping_cost - discount_amount
                
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    billing_address={
                        'first_name': billing_address.first_name,
                        'last_name': billing_address.last_name,
                        'address_line_1': billing_address.address_line_1,
                        'address_line_2': billing_address.address_line_2,
                        'city': billing_address.city,
                        'state': billing_address.state,
                        'postal_code': billing_address.postal_code,
                        'country': billing_address.country,
                    },
                    shipping_address={
                        'first_name': shipping_address.first_name,
                        'last_name': shipping_address.last_name,
                        'address_line_1': shipping_address.address_line_1,
                        'address_line_2': shipping_address.address_line_2,
                        'city': shipping_address.city,
                        'state': shipping_address.state,
                        'postal_code': shipping_address.postal_code,
                        'country': shipping_address.country,
                    },
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    discount_amount=discount_amount,
                    total_amount=final_total
                )
                
                # Create order items
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product_variant=cart_item.product_variant,
                        product_name=cart_item.product_variant.product.name,
                        product_sku=cart_item.product_variant.sku,
                        color_name=cart_item.product_variant.color.name,
                        size_name=cart_item.product_variant.size.name,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product_variant.final_price
                    )
                    
                    # Update stock
                    variant = cart_item.product_variant
                    variant.stock_quantity -= cart_item.quantity
                    variant.save()
                
                # Clear cart
                cart_items.delete()
                
                messages.success(request, f'Order {order.order_number} placed successfully!')
                return redirect('ecommerce:order_success', order_number=order.order_number)
                
            except Exception as e:
                messages.error(request, 'An error occurred while processing your order')
    
    context = {
        'cart_items': cart_items,
        'addresses': addresses,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'shipping_cost': shipping_cost,
        'total': total,
    }
    
    return render(request, 'ecommerce/checkout.html', context)


@login_required
def order_success(request, order_number):
    """Order success page"""
    order = get_object_or_404(Order, order_number=order_number, customer__user=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'ecommerce/order_success.html', context)


@login_required
def apply_coupon(request):
    """Apply coupon code via AJAX"""
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()
        
        if not coupon_code:
            return JsonResponse({'success': False, 'message': 'Please enter a coupon code'})
        
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            customer = Customer.objects.get(user=request.user)
            cart = Cart.objects.get(customer=customer)
            
            subtotal = sum(item.total_price for item in cart.items.all())
            
            if not coupon.is_valid():
                return JsonResponse({'success': False, 'message': 'Invalid or expired coupon code'})
            
            if subtotal < coupon.minimum_order_amount:
                return JsonResponse({
                    'success': False, 
                    'message': f'Minimum order amount is ${coupon.minimum_order_amount}'
                })
            
            # Calculate discount
            if coupon.discount_type == 'percentage':
                discount_amount = subtotal * (coupon.discount_value / 100)
                if coupon.maximum_discount_amount:
                    discount_amount = min(discount_amount, coupon.maximum_discount_amount)
            else:
                discount_amount = coupon.discount_value
            
            return JsonResponse({
                'success': True,
                'message': 'Coupon applied successfully',
                'discount_amount': discount_amount,
                'coupon_description': coupon.description
            })
            
        except (Coupon.DoesNotExist, Customer.DoesNotExist, Cart.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Invalid coupon code'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def get_variant_info(request):
    """Get variant information via AJAX"""
    color_id = request.GET.get('color_id')
    size_id = request.GET.get('size_id')
    product_id = request.GET.get('product_id')
    
    if not all([color_id, size_id, product_id]):
        return JsonResponse({'success': False, 'message': 'Missing parameters'})
    
    try:
        variant = ProductVariant.objects.get(
            product_id=product_id,
            color_id=color_id,
            size_id=size_id,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'variant_id': variant.id,
            'price': variant.final_price,
            'stock': variant.stock_quantity,
            'in_stock': variant.is_in_stock,
            'sku': variant.sku
        })
        
    except ProductVariant.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Variant not available'})