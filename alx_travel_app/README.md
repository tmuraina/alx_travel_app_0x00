# ALX Travel App - Database Modeling and Seeding

This Django application demonstrates essential backend components for a travel booking platform, including database models, API serializers, and data seeding functionality.

## Project Structure

```
alx_travel_app_0x00/
├── alx_travel_app/
│   ├── listings/
│   │   ├── models.py              # Database models
│   │   ├── serializers.py         # DRF serializers
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── seed.py        # Database seeding command
│   │   └── ...
│   └── ...
└── README.md
```

## Models

### Listing Model
Represents properties available for booking with the following key features:
- **UUID primary key** for better security and distributed systems
- **Foreign key relationship** to User (host)
- **Pricing and capacity** information
- **Location and description** fields
- **Availability status** tracking
- **Automatic timestamps** for creation and updates
- **Database indexes** for performance optimization

### Booking Model
Manages reservation data with:
- **UUID primary key**
- **Foreign key relationships** to Listing and User (guest)
- **Date validation** to ensure logical check-in/out dates
- **Status tracking** (pending, confirmed, canceled, completed)
- **Price calculation** and guest count validation
- **Database constraints** to ensure data integrity

### Review Model
Handles user feedback with:
- **UUID primary key**
- **Rating system** (1-5 stars with validation)
- **Comment field** for detailed feedback
- **Unique constraint** to prevent duplicate reviews per user-listing pair
- **Timestamp tracking**

## Key Features

### Data Relationships
- **One-to-Many**: User → Listings (host relationship)
- **One-to-Many**: User → Bookings (guest relationship)
- **One-to-Many**: Listing → Bookings
- **One-to-Many**: User → Reviews (reviewer relationship)
- **One-to-Many**: Listing → Reviews

### Data Validation
- **Date validation**: Prevents past check-in dates and invalid date ranges
- **Capacity validation**: Ensures guest count doesn't exceed listing capacity
- **Price validation**: Enforces positive pricing values
- **Rating validation**: Restricts ratings to 1-5 range
- **Availability checks**: Prevents booking unavailable listings

### Database Optimization
- **Indexes** on frequently queried fields (location, price, dates)
- **Database constraints** for data integrity
- **Efficient querying** with proper relationships

## Serializers

### ListingSerializer
- **Full serialization** with nested host and reviews data
- **Write operations** with validation
- **Calculated fields** like average rating and review count
- **Read-only fields** for system-generated data

### BookingSerializer
- **Comprehensive validation** for booking logic
- **Automatic price calculation** based on duration and nightly rate
- **Status management** and date validation
- **Nested serialization** for related objects

### Additional Serializers
- **List serializers** for optimized list views
- **User serializer** for consistent user representation
- **Review serializer** with rating validation

## Management Commands

### Seed Command
Populates the database with realistic sample data:

```bash
# Basic usage
python manage.py seed

# Custom quantities
python manage.py seed --users 20 --listings 50 --bookings 100 --reviews 150

# Clear existing data first
python manage.py seed --clear

# Help
python manage.py seed --help
```

#### Command Options:
- `--users`: Number of users to create (default: 10)
- `--listings`: Number of listings to create (default: 20)
- `--bookings`: Number of bookings to create (default: 30)
- `--reviews`: Number of reviews to create (default: 40)
- `--clear`: Remove existing data before seeding

#### Sample Data Features:
-
