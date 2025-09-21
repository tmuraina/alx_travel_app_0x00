from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - used in nested serialization."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""
    
    reviewer = UserSerializer(read_only=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'listing', 'reviewer', 'reviewer_id', 
            'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['review_id', 'created_at']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def create(self, validated_data):
        """Create a new review."""
        if 'reviewer_id' in validated_data:
            validated_data['reviewer_id'] = validated_data.pop('reviewer_id')
        return super().create(validated_data)


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model."""
    
    host = UserSerializer(read_only=True)
    host_id = serializers.IntegerField(write_only=True, required=False)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'listing_id', 'host', 'host_id', 'title', 'description', 
            'location', 'price_per_night', 'max_guests', 'bedrooms', 
            'bathrooms', 'is_available', 'created_at', 'updated_at',
            'reviews', 'average_rating', 'review_count'
        ]
        read_only_fields = ['listing_id', 'created_at', 'updated_at']
    
    def get_review_count(self, obj):
        """Get the total number of reviews for this listing."""
        return obj.reviews.count()
    
    def validate_price_per_night(self, value):
        """Validate price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price per night must be positive.")
        return value
    
    def validate_max_guests(self, value):
        """Validate max guests is positive."""
        if value <= 0:
            raise serializers.ValidationError("Max guests must be at least 1.")
        return value
    
    def create(self, validated_data):
        """Create a new listing."""
        if 'host_id' in validated_data:
            validated_data['host_id'] = validated_data.pop('host_id')
        return super().create(validated_data)


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""
    
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.UUIDField(write_only=True)
    guest = UserSerializer(read_only=True)
    guest_id = serializers.IntegerField(write_only=True, required=False)
    duration_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'listing', 'listing_id', 'guest', 'guest_id',
            'check_in_date', 'check_out_date', 'num_guests', 
            'total_price', 'status', 'created_at', 'duration_days'
        ]
        read_only_fields = ['booking_id', 'created_at']
    
    def validate(self, data):
        """Custom validation for booking data."""
        from django.utils import timezone
        from datetime import date
        
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        
        # Validate dates
        if check_in and check_in < timezone.now().date():
            raise serializers.ValidationError({
                'check_in_date': 'Check-in date cannot be in the past.'
            })
        
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError({
                'check_out_date': 'Check-out date must be after check-in date.'
            })
        
        # Validate guest count against listing capacity
        listing_id = data.get('listing_id')
        num_guests = data.get('num_guests')
        
        if listing_id and num_guests:
            try:
                listing = Listing.objects.get(listing_id=listing_id)
                if num_guests > listing.max_guests:
                    raise serializers.ValidationError({
                        'num_guests': f'Number of guests cannot exceed {listing.max_guests}.'
                    })
            except Listing.DoesNotExist:
                raise serializers.ValidationError({
                    'listing_id': 'Invalid listing ID.'
                })
        
        # Check if listing is available
        if listing_id:
            try:
                listing = Listing.objects.get(listing_id=listing_id)
                if not listing.is_available:
                    raise serializers.ValidationError({
                        'listing_id': 'This listing is not available for booking.'
                    })
            except Listing.DoesNotExist:
                pass  # Already handled above
        
        return data
    
    def validate_total_price(self, value):
        """Validate total price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Total price must be positive.")
        return value
    
    def create(self, validated_data):
        """Create a new booking with automatic price calculation."""
        if 'guest_id' in validated_data:
            validated_data['guest_id'] = validated_data.pop('guest_id')
        
        # Auto-calculate total price if not provided
        if 'total_price' not in validated_data or not validated_data['total_price']:
            listing = Listing.objects.get(listing_id=validated_data['listing_id'])
            check_in = validated_data['check_in_date']
            check_out = validated_data['check_out_date']
            duration = (check_out - check_in).days
            validated_data['total_price'] = listing.price_per_night * duration
        
        return super().create(validated_data)


# Simplified serializers for list views (without nested data)
class ListingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing list views."""
    
    host_name = serializers.CharField(source='host.username', read_only=True)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = Listing
        fields = [
            'listing_id', 'title', 'location', 'price_per_night',
            'max_guests', 'bedrooms', 'bathrooms', 'is_available',
            'host_name', 'average_rating'
        ]


class BookingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for booking list views."""
    
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    guest_name = serializers.CharField(source='guest.username', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'listing_title', 'guest_name', 
            'check_in_date', 'check_out_date', 'status',
            'total_price', 'created_at'
        ]
