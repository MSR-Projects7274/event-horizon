from datetime import time, timedelta
from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Category, Event


EVENT_DATA = [
    # ---------------------------------------------------------
    # ADVENTURE
    # ---------------------------------------------------------
    {
        "category": "Adventure",
        "name": "Hidden History Walking Tour",
        "description": (
            "Explore the city's lesser-known history on a guided walk "
            "through forgotten streets, unusual landmarks and stories "
            "that rarely make it into the guidebooks."
        ),
        "location": "Town Hall Steps",
        "time": time(14, 0),
        "price": Decimal("15.00"),
        "capacity": 25,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "After Dark City Tour",
        "description": (
            "See the city from a different perspective as evening falls. "
            "Discover unusual landmarks, hidden corners and stories from "
            "the streets after dark."
        ),
        "location": "Old Town Gate",
        "time": time(19, 30),
        "price": Decimal("18.00"),
        "capacity": 20,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "Riverside Kayaking Experience",
        "description": (
            "Take to the water for a guided kayaking adventure along the "
            "river. Suitable for beginners, with equipment and instruction "
            "provided."
        ),
        "location": "Riverside Boathouse",
        "time": time(10, 0),
        "price": Decimal("42.00"),
        "capacity": 12,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "Sunset Woodland Walk",
        "description": (
            "Follow woodland trails as the day comes to an end, with a "
            "local guide sharing stories about the landscape and wildlife "
            "along the way."
        ),
        "location": "Pinewood Trail Entrance",
        "time": time(18, 30),
        "price": Decimal("12.00"),
        "capacity": 20,
        "is_special": False,
    },

    # ---------------------------------------------------------
    # ARTS & CULTURE
    # ---------------------------------------------------------
    {
        "category": "Arts & Culture",
        "name": "Beginner's Pottery Workshop",
        "description": (
            "Get your hands dirty in this relaxed introduction to pottery. "
            "Learn the basics of shaping, decorating and glazing clay while "
            "creating something you can take home."
        ),
        "location": "The Old Kiln Studio",
        "time": time(18, 30),
        "price": Decimal("32.00"),
        "capacity": 12,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Introduction to Watercolour",
        "description": (
            "Spend a peaceful afternoon learning the fundamentals of "
            "watercolour painting. No previous experience is needed, and "
            "all materials are provided."
        ),
        "location": "Riverside Arts Centre",
        "time": time(14, 0),
        "price": Decimal("24.00"),
        "capacity": 16,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Candle Making Evening",
        "description": (
            "Create your own scented candles while learning about waxes, "
            "fragrance and candle design. Choose your favourite scents and "
            "take your finished creations home."
        ),
        "location": "The Makers' Room",
        "time": time(19, 0),
        "price": Decimal("28.00"),
        "capacity": 14,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Local Artists Exhibition Night",
        "description": (
            "Meet local artists and explore a changing collection of "
            "paintings, photography and mixed-media work during an informal "
            "evening at the gallery."
        ),
        "location": "Eastside Gallery",
        "time": time(18, 0),
        "price": Decimal("8.00"),
        "capacity": 50,
        "is_special": False,
    },

    # ---------------------------------------------------------
    # FAMILY
    # ---------------------------------------------------------
    {
        "category": "Family",
        "name": "Family Science Day",
        "description": (
            "A hands-on day of experiments, demonstrations and curious "
            "discoveries designed to get the whole family asking questions "
            "and making things happen."
        ),
        "location": "Discovery Centre",
        "time": time(11, 0),
        "price": Decimal("10.00"),
        "capacity": 40,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Outdoor Treasure Hunt",
        "description": (
            "Grab your team and follow the clues through parks, paths and "
            "hidden corners in this family-friendly treasure hunt."
        ),
        "location": "Central Park Pavilion",
        "time": time(12, 0),
        "price": Decimal("9.00"),
        "capacity": 30,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Junior Nature Explorers",
        "description": (
            "Discover local wildlife and learn about the natural world "
            "during an interactive outdoor session designed especially "
            "for younger explorers."
        ),
        "location": "Meadowlands Visitor Centre",
        "time": time(10, 30),
        "price": Decimal("11.00"),
        "capacity": 24,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Family Movie Afternoon",
        "description": (
            "Settle in for a relaxed afternoon of family entertainment "
            "with snacks, comfortable seating and a big-screen favourite."
        ),
        "location": "The Grand Cinema",
        "time": time(14, 0),
        "price": Decimal("12.00"),
        "capacity": 80,
        "is_special": False,
    },

    # ---------------------------------------------------------
    # FOOD & DRINK
    # ---------------------------------------------------------
    {
        "category": "Food & Drink",
        "name": "Evening Street Food Tour",
        "description": (
            "Follow the flavours after dark as we explore some of the "
            "city's favourite street food spots. Expect plenty of samples, "
            "unexpected discoveries and a very full evening."
        ),
        "location": "Market Square",
        "time": time(18, 0),
        "price": Decimal("35.00"),
        "capacity": 18,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "Artisan Chocolate Workshop",
        "description": (
            "Learn how chocolate is tempered, decorated and transformed "
            "into delicious handmade treats. You'll make your own selection "
            "to take home at the end of the evening."
        ),
        "location": "Cocoa House",
        "time": time(18, 30),
        "price": Decimal("38.00"),
        "capacity": 12,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "Local Food & Market Walk",
        "description": (
            "Explore local producers, independent food stalls and hidden "
            "market favourites on a relaxed guided tasting walk."
        ),
        "location": "Central Market",
        "time": time(11, 0),
        "price": Decimal("22.00"),
        "capacity": 20,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "Seasonal Supper Club",
        "description": (
            "Enjoy a relaxed communal meal built around seasonal local "
            "ingredients, with a changing menu designed to showcase the "
            "best of the current season."
        ),
        "location": "The Green Kitchen",
        "time": time(19, 30),
        "price": Decimal("45.00"),
        "capacity": 24,
        "is_special": False,
    },

    # ---------------------------------------------------------
    # MUSIC & ENTERTAINMENT
    # ---------------------------------------------------------
    {
        "category": "Music & Entertainment",
        "name": "Live Acoustic Night",
        "description": (
            "Settle in for an intimate evening of live acoustic music "
            "featuring local performers, stripped-back arrangements and "
            "a relaxed atmosphere."
        ),
        "location": "The Lantern Room",
        "time": time(20, 0),
        "price": Decimal("16.00"),
        "capacity": 80,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Indie Unplugged",
        "description": (
            "A night of independent musicians performing their songs in "
            "their simplest form. Expect guitars, honest lyrics and a "
            "small room full of very good noise."
        ),
        "location": "The Backroom",
        "time": time(19, 30),
        "price": Decimal("14.00"),
        "capacity": 60,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Jazz Under the Stars",
        "description": (
            "Enjoy an evening of live jazz beneath the night sky, with "
            "classic standards, modern arrangements and a relaxed outdoor "
            "setting."
        ),
        "location": "Riverside Gardens",
        "time": time(20, 30),
        "price": Decimal("20.00"),
        "capacity": 100,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Comedy Club Night",
        "description": (
            "Spend the evening with a rotating line-up of comedians, "
            "rising performers and one or two acts you may recognise. "
            "Expect a loud room and plenty of questionable decisions."
        ),
        "location": "The Comedy Cellar",
        "time": time(20, 0),
        "price": Decimal("18.00"),
        "capacity": 70,
        "is_special": False,
    },

    # ---------------------------------------------------------
    # NOT FOR THE FAINT OF HEART
    # ---------------------------------------------------------
    {
        "category": "Not For the Faint of Heart",
        "name": "The Last Showing",
        "description": (
            "The cinema closed years ago. The projector still runs. "
            "Join us for one final screening in a venue where something "
            "seems to have gone very wrong. Not for the faint of heart."
        ),
        "location": "The Old Picture House",
        "time": time(23, 0),
        "price": Decimal("25.00"),
        "capacity": 24,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "After Midnight",
        "description": (
            "Some places feel different after midnight. Explore the "
            "forgotten corners of the old district with a guide who has "
            "a few stories they probably shouldn't be telling."
        ),
        "location": "Old District",
        "time": time(23, 30),
        "price": Decimal("22.00"),
        "capacity": 16,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "The Empty Room",
        "description": (
            "There is a room in the old building that nobody uses anymore. "
            "Tonight, you're invited inside. What happens next is probably "
            "better left unexplained."
        ),
        "location": "The Old Assembly Rooms",
        "time": time(21, 30),
        "price": Decimal("28.00"),
        "capacity": 12,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "The House at the End of the Lane",
        "description": (
            "Nobody has lived there for years. Nobody can quite agree "
            "why. Tonight, the door is open. You have been invited in."
        ),
        "location": "Blackthorn Lane",
        "time": time(22, 0),
        "price": Decimal("30.00"),
        "capacity": 10,
        "is_special": True,
    },

    # ---------------------------------------------------------
    # WORKSHOPS
    # ---------------------------------------------------------
    {
        "category": "Workshops",
        "name": "Leathercraft for Beginners",
        "description": (
            "Discover the basics of traditional leathercraft and make a "
            "small handmade item to take home. A practical workshop for "
            "anyone who enjoys making things from scratch."
        ),
        "location": "Forge & Foundry Workshop",
        "time": time(18, 0),
        "price": Decimal("36.00"),
        "capacity": 10,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Introduction to Wood Carving",
        "description": (
            "Learn the foundations of wood carving in a friendly, "
            "hands-on session. Explore basic tools and techniques before "
            "creating your own small carved piece."
        ),
        "location": "The Workshop Loft",
        "time": time(13, 30),
        "price": Decimal("30.00"),
        "capacity": 10,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Beginner's Photography Walk",
        "description": (
            "Learn how to get more from your camera while exploring the "
            "city with a practical photography walk covering composition, "
            "light and creative techniques."
        ),
        "location": "Riverside Bridge",
        "time": time(10, 0),
        "price": Decimal("20.00"),
        "capacity": 15,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Creative Writing Evening",
        "description": (
            "Put pen to paper in a relaxed creative writing session "
            "covering ideas, characters, setting and storytelling. "
            "No previous writing experience required."
        ),
        "location": "The Writers' Room",
        "time": time(19, 0),
        "price": Decimal("18.00"),
        "capacity": 16,
        "is_special": False,
    },
]


class Command(BaseCommand):
    help = "Create a collection of sample events for Event Horizon."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=len(EVENT_DATA),
            help="Number of events to create.",
        )

        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing events before creating new ones.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        clear = options["clear"]

        if count < 1:
            self.stdout.write(
                self.style.ERROR("Count must be at least 1.")
            )
            return

        if clear:
            deleted, _ = Event.objects.all().delete()

            self.stdout.write(
                self.style.WARNING(
                    f"Deleted {deleted} existing event record(s)."
                )
            )

        # Make sure every category used by the event data exists.
        categories = {}

        for event_data in EVENT_DATA:
            category_name = event_data["category"]

            if category_name not in categories:
                category, _ = Category.objects.get_or_create(
                    name=category_name
                )
                categories[category_name] = category

        # Group events by category so we can guarantee that every
        # category is represented when enough events are requested.
        category_events = {}

        for event_data in EVENT_DATA:
            category_name = event_data["category"]

            category_events.setdefault(
                category_name,
                []
            ).append(event_data)

        categories_list = list(category_events.keys())

        selected_events = []

        # If we request at least as many events as we have categories,
        # start by selecting one event from every category.
        if count >= len(categories_list):
            for category_name in categories_list:
                selected_events.append(
                    random.choice(
                        category_events[category_name]
                    )
                )

            # Fill the remaining places from the complete catalogue.
            remaining = count - len(selected_events)

            if remaining > 0:
                selected_events.extend(
                    random.choices(
                        EVENT_DATA,
                        k=remaining
                    )
                )

        # If fewer events than categories are requested, simply choose
        # a random selection.
        else:
            selected_events = random.sample(
                EVENT_DATA,
                count
            )

        # Start events one week from today so we don't accidentally
        # create events in the past.
        start_date = timezone.localdate() + timedelta(days=7)

        created = 0

        for event_data in selected_events:
            event_date = start_date + timedelta(
                days=random.randint(0, 60)
            )

            event = Event.objects.create(
                category=categories[event_data["category"]],
                name=event_data["name"],
                description=event_data["description"],
                location=event_data["location"],
                date=event_date,
                time=event_data["time"],
                price=event_data["price"],
                capacity=event_data["capacity"],
                active=True,
                is_special=event_data["is_special"],
            )

            created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created: {event.name} "
                    f"({event.date})"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully created {created} event(s)."
            )
        )

