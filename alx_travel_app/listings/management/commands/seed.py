from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from listings.models import Listing, Booking, Review
from decimal import Decimal
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create'
        )
        parser.add_argument(
            '--listings',
            type=int,
            default=20,
            help='Number of listings to create'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=30,
            help='Number of bookings to create'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=40,
            help='Number of reviews to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        self.stdout.write('Starting database seeding...')
        
        with transaction.atomic():
            users = self.create_users(options['users'])
            listings = self.create_listings(users, options['listings'])
            bookings = self.create_bookings(users, listings, options['bookings'])
            reviews = self.create_reviews(users, listings, options['reviews'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'  - {len(users)} users\n'
                f'  - {len(listings)} listings\n'
                f'  - {len(bookings)} bookings\n'
                f'  - {len(reviews)} reviews'
            )
        )
    
    def clear_data(self):
        """Clear existing seeded data."""
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        # Keep superuser, only delete regular users
        User.objects.filter(is_superuser=False).delete()
    
    def create_users(self, count):
        """Create sample users."""
        self.stdout.write(f'Creating {count} users...')
        
        users = []
        user_data = [
            ('john_doe', 'John', 'Doe', 'john@example.com'),
            ('jane_smith', 'Jane', 'Smith', 'jane@example.com'),
            ('mike_wilson', 'Mike', 'Wilson', 'mike@example.com'),
            ('sarah_johnson', 'Sarah', 'Johnson', 'sarah@example.com'),
            ('david_brown', 'David', 'Brown', 'david@example.com'),
            ('lisa_davis', 'Lisa', 'Davis', 'lisa@example.com'),
            ('tom_miller', 'Tom', 'Miller', 'tom@example.com'),
            ('anna_garcia', 'Anna', 'Garcia', 'anna@example.com'),
            ('chris_martinez', 'Chris', 'Martinez', 'chris@example.com'),
            ('emily_taylor', 'Emily', 'Taylor', 'emily@example.com'),
        ]
        
        for i in range(min(count, len(user_data))):
            username, first_name, last_name, email = user_data[i]
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
        
        # Create additional random users if needed
        for i in range(len(user_data), count):
            username = f'user_{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': f'User',
                    'last_name': f'{i+1}',
                    'email': f'user{i+1}@example.com',
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
        
        return users
    
    def create_listings(self, users, count):
        """Create sample listings."""
        self.stdout.write(f'Creating {count} listings...')
        
        listing_templates = [
            {
                'title': 'Cozy Downtown Apartment',
                'description': 'A beautiful apartment in the heart of the city with modern amenities.',
                'location': 'New York, NY',
                'price_per_night': Decimal('120.00'),
                'max_guests': 2,
                'bedrooms': 1,
                'bathrooms': 1,
            },
            {
                'title': 'Luxury Beach House',
                'description': 'Stunning beachfront property with panoramic ocean views.',
                'location': 'Miami, FL',
                'price_per_night': Decimal('250.00'),
                'max_guests': 8,
                'bedrooms': 4,
                'bathrooms': 3,
            },
            {
                'title': 'Mountain Cabin Retreat',
                'description': 'Peaceful cabin surrounded by nature, perfect for a getaway.',
                'location': 'Aspen, CO',
                'price_per_night': Decimal('180.00'),
                'max_guests': 6,
                'bedrooms': 3,
                'bathrooms': 2,
            },
            {
                'title': 'Historic City Loft',
                'description': 'Charming loft in a historic building with exposed brick walls.',
                'location': 'Boston, MA',
                'price_per_night': Decimal('95.00'),
                'max_guests': 4,
                'bedrooms': 2,
                'bathrooms': 1,
            },
            {
                'title': 'Modern Studio in Tech Hub',
                'description': 'Sleek studio apartment perfect for business travelers.',
                'location': 'San Francisco, CA',
                'price_per_night': Decimal('150.00'),
                'max_guests': 2,
                'bedrooms': 1,
                'bathrooms': 1,
            },
        ]
        
        additional_locations = [
            'Chicago, IL', 'Seattle, WA', 'Austin, TX', 'Portland, OR',
            'Nashville, TN', 'Denver, CO', 'Atlanta, GA', 'Philadelphia, PA'
        ]
        
        listings = []
        
        for i in range(count):
            if i < len(listing_templates):
                template = listing_templates[i].copy()
            else:
                template = {
                    'title': f'Property #{i+1}',
                    'description': f'A wonderful place to stay in location #{i+1}.',
                    'location': random.choice(additional_locations),
                    'price_per_night': Decimal(str(random.randint(50, 300))),
                    'max_guests': random.randint(1, 8),
                    'bedrooms': random.randint(1, 4),
                    'bathrooms': random.randint(1, 3),
                }
            
            listing = Listing.objects.create(
                host=random.choice(users),
                **template,
                is_available=random.choice([True, True, True, False])  # 75% available
            )
            listings.append(listing)
        
        return listings
    
    def create_bookings(self, users, listings, count):
        """Create sample bookings."""
        self.stdout.write(f'Creating {count} bookings...')
        
        bookings = []
        
        for i in range(count):
            listing = random.choice(listings)
            guest = random.choice([u for u in users if u != listing.host])
            
            # Generate random booking dates
            start_date = timezone.now().date() + timedelta(
                days=random.randint(-30, 60)
            )
            duration = random.randint(1, 14)
            end_date = start_date + timedelta(days=duration)
            
            num_guests = random.randint(1, min(listing.max_guests, 4))
            total_price = listing.price_per_night * duration
            
            status_choices = ['pending', 'confirmed', 'canceled', 'completed']
            # Weight status choices to have more confirmed bookings
            status_weights = [0.1, 0.6, 0.1, 0.2]
            status = random.choices(status_choices, weights=status_weights)[0]
            
            try:
                booking = Booking.objects.create(
                    listing=listing,
                    guest=guest,
                    check_in_date=start_date,
                    check_out_date=end_date,
                    num_guests=num_guests,
                    total_price=total_price,
                    status=status
                )
                bookings.append(booking)
            except Exception as e:
                # Skip bookings that fail validation
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipped booking {i+1}: {str(e)}'
                    )
                )
                continue
        
        return bookings
    
    def create_reviews(self, users, listings, count):
        """Create sample reviews."""
        self.stdout.write(f'Creating {count} reviews...')
        
        review_comments = [
            "Great place to stay! Very clean and comfortable.",
            "Amazing location and the host was very responsive.",
            "Perfect for our family vacation. Highly recommended!",
            "The property was exactly as described. Will book again!",
            "Good value for money. Minor issues but overall satisfied.",
            "Exceptional service and beautiful property.",
            "Could use some updates but the location is unbeatable.",
            "Host went above and beyond to make our stay perfect.",
            "Clean, comfortable, and great amenities.",
            "Would definitely stay here again on our next visit.",
        ]
        
        reviews = []
        created_reviews = set()  # Track user-listing pairs to avoid duplicates
        
        for i in range(count):
            max_attempts = 10
            attempts = 0
            
            while attempts < max_attempts:
                listing = random.choice(listings)
                reviewer = random.choice([u for u in users if u != listing.host])
                
                review_key = (reviewer.id, listing.listing_id)
                
                if review_key not in created_reviews:
                    rating = random.choices(
                        [1, 2, 3, 4, 5],
                        weights=[0.05, 0.05, 0.15, 0.35, 0.40]  # Skewed toward higher ratings
                    )[0]
                    
                    comment = random.choice(review_comments)
                    
                    try:
                        review = Review.objects.create(
                            listing=listing,
                            reviewer=reviewer,
                            rating=rating,
                            comment=comment
                        )
                        reviews.append(review)
                        created_reviews.add(review_key)
                        break
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Skipped review {i+1}: {str(e)}'
                            )
                        )
                        break
                
                attempts += 1
            
            if attempts >= max_attempts:
                self.stdout.write(
                    self.style.WARNING(
                        f'Could not create unique review {i+1} after {max_attempts} attempts'
                    )
                )
        
        return reviews
