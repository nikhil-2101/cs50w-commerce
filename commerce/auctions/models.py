from django.db import models
from django.contrib.auth.models import AbstractUser

CATEGORIES = (
    ('a', 'Gadgets'),
    ('b', 'Appliances'),
    ('c', 'Books'),
    ('d', 'Furniture'),
    ('e', 'Toys'),
    ('f', 'Sports'),
    ('g', 'Clothing'),
    ('h', 'Uncategorized'),
)

class User(AbstractUser):
    pass

class Listing(models.Model):
    item_name = models.CharField(max_length=64)
    item_description = models.CharField(max_length=255, blank=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    item_category = models.CharField(max_length=1, choices=CATEGORIES, default='f')
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    is_closed = models.BooleanField(default=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    image = models.ImageField(upload_to='listings/images/')
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    winner = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.item_name}: listed at {self.starting_price} by {self.seller}"

class Bid(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bid_listing')

    def __str__(self):
        return f"{self.bidder} bid {self.bid_amount} on {self.bid_listing.item_name}"

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment_title = models.CharField(max_length=25, default="")
    comment_body = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True, blank=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comment_listings')

    def __str__(self):
        return f"{self.commenter}: {self.comment_body[:20]}..."

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.listing.item_name}"
