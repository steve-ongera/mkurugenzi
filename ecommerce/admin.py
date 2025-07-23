from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, SubCategory, Brand, Color, Size, Product, ProductVariant, 
    ProductImage, Customer, Address, Order, OrderItem, Cart, CartItem, 
    Wishlist, WishlistItem, Review, Coupon, Newsletter
)


# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


# SubCategory Admin
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'is_active', 'product_count', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'category__name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


# Brand Admin
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'website', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


# Color Admin
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code', 'color_preview']
    search_fields = ['name', 'hex_code']
    
    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
                obj.hex_code
            )
        return '-'
    color_preview.short_description = 'Preview'


# Size Admin
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'size_type', 'region', 'numeric_value']
    list_filter = ['size_type', 'region']
    search_fields = ['name']


# Product Image Inline
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'color', 'alt_text', 'is_primary', 'order']
    readonly_fields = ['created_at']


# Product Variant Inline
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['color', 'size', 'sku', 'stock_quantity', 'price_adjustment', 'is_active']
    readonly_fields = ['created_at']


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'brand', 'category', 'gender', 'current_price', 
        'discount_percentage', 'is_featured', 'is_active', 'variant_count'
    ]
    list_filter = [
        'category', 'subcategory', 'brand', 'gender', 'is_featured', 
        'is_active', 'created_at'
    ]
    search_fields = ['name', 'sku', 'description', 'brand__name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'current_price', 'discount_percentage']
    filter_horizontal = []
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'brand', 'category', 'subcategory')
        }),
        ('Product Details', {
            'fields': (
                'description', 'short_description', 'gender', 'material', 
                'care_instructions', 'weight'
            )
        }),
        ('Pricing', {
            'fields': ('base_price', 'discount_price', 'current_price', 'discount_percentage')
        }),
        ('Status & Features', {
            'fields': ('is_featured', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    inlines = [ProductVariantInline, ProductImageInline]
    
    def variant_count(self, obj):
        return obj.variants.count()
    variant_count.short_description = 'Variants'


# Product Variant Admin
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'color', 'size', 'sku', 'stock_quantity', 
        'final_price', 'is_in_stock', 'is_active'
    ]
    list_filter = ['product__category', 'color', 'size', 'is_active', 'created_at']
    search_fields = ['product__name', 'sku', 'color__name', 'size__name']
    readonly_fields = ['created_at', 'final_price', 'is_in_stock']


# Product Image Admin
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'image_preview', 'is_primary', 'order', 'created_at']
    list_filter = ['product__category', 'color', 'is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']
    readonly_fields = ['created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview'


# Address Inline
class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ['address_type', 'first_name', 'last_name', 'city', 'country', 'is_default']


# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'get_full_name', 'get_email', 'phone', 'gender', 
        'newsletter_subscription', 'order_count', 'created_at'
    ]
    list_filter = ['gender', 'newsletter_subscription', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [AddressInline]
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or '-'
    get_full_name.short_description = 'Full Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def order_count(self, obj):
        return obj.orders.count()
    order_count.short_description = 'Orders'


# Address Admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'customer', 'address_type', 'first_name', 'last_name', 
        'city', 'country', 'is_default', 'created_at'
    ]
    list_filter = ['address_type', 'country', 'is_default', 'created_at']
    search_fields = [
        'customer__user__username', 'first_name', 'last_name', 
        'city', 'country', 'postal_code'
    ]
    readonly_fields = ['created_at']


# Order Item Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price', 'created_at']
    fields = [
        'product_variant', 'product_name', 'color_name', 'size_name', 
        'quantity', 'unit_price', 'total_price'
    ]


# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer', 'status', 'payment_status', 
        'total_amount', 'item_count', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at', 'shipped_at', 'delivered_at']
    search_fields = ['order_number', 'customer__user__username', 'customer__user__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'payment_status')
        }),
        ('Addresses', {
            'fields': ('billing_address', 'shipping_address'),
            'classes': ['collapse']
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount')
        }),
        ('Shipping', {
            'fields': ('tracking_number', 'shipped_at', 'delivered_at')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    inlines = [OrderItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


# Order Item Admin
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'product_name', 'color_name', 'size_name', 
        'quantity', 'unit_price', 'total_price', 'created_at'
    ]
    list_filter = ['created_at', 'color_name', 'size_name']
    search_fields = ['order__order_number', 'product_name', 'product_sku']
    readonly_fields = ['total_price', 'created_at']


# Cart Item Inline
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price', 'added_at', 'updated_at']


# Cart Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['customer', 'total_items', 'total_amount', 'created_at', 'updated_at']
    search_fields = ['customer__user__username', 'customer__user__email']
    readonly_fields = ['total_items', 'total_amount', 'created_at', 'updated_at']
    
    inlines = [CartItemInline]


# Cart Item Admin
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        'cart', 'product_variant', 'quantity', 'total_price', 
        'added_at', 'updated_at'
    ]
    list_filter = ['added_at', 'updated_at']
    search_fields = ['cart__customer__user__username', 'product_variant__product__name']
    readonly_fields = ['total_price', 'added_at', 'updated_at']


# Wishlist Item Inline
class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ['added_at']


# Wishlist Admin
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['customer', 'item_count', 'created_at']
    search_fields = ['customer__user__username', 'customer__user__email']
    readonly_fields = ['created_at']
    
    inlines = [WishlistItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


# Wishlist Item Admin
@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['wishlist', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['wishlist__customer__user__username', 'product__name']
    readonly_fields = ['added_at']


# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'customer', 'rating', 'title', 'is_verified_purchase', 
        'is_approved', 'created_at'
    ]
    list_filter = [
        'rating', 'is_verified_purchase', 'is_approved', 'created_at'
    ]
    search_fields = [
        'product__name', 'customer__user__username', 'title', 'comment'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_approved']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'customer', 'rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('is_verified_purchase', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )


# Coupon Admin
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'discount_type', 'discount_value', 'usage_limit', 
        'used_count', 'valid_from', 'valid_to', 'is_active'
    ]
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_to', 'created_at']
    search_fields = ['code', 'description']
    readonly_fields = ['used_count', 'created_at']
    date_hierarchy = 'valid_from'
    
    fieldsets = (
        ('Coupon Information', {
            'fields': ('code', 'description')
        }),
        ('Discount Settings', {
            'fields': (
                'discount_type', 'discount_value', 'minimum_order_amount', 
                'maximum_discount_amount'
            )
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'used_count')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_to', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ['collapse']
        })
    )


# Newsletter Admin
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at']
    list_editable = ['is_active']


# Customize admin site headers
admin.site.site_header = "Ecommerce Administration"
admin.site.site_title = "Ecommerce Admin"
admin.site.index_title = "Welcome to Ecommerce Administration"