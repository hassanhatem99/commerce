from django.contrib.auth.models import AbstractUser
from django.db import models
import os
from django.utils import timezone
from multiupload.fields import MultiImageField

def get_image_path(instance, filename):
    return os.path.join('images', filename)



CATEGORY_CHOICES = [
        ('', 'Select'),
        ('Electronics', 'Electronics'),
        ('Clothing', 'Clothing'),
        ('Books', 'Books'),
        ('Home', 'Home'),
        ('Furniture', 'Furniture'),
        ('Vehicles', 'Vehicles'),
        ('Toys', 'Toys'),
        ('Sports', 'Sports'),
        ('Beauty', 'Beauty'),
        ('Jewelry', 'Jewelry'),
        ('Health', 'Health'),
        ('Music', 'Music'),
        ('Movies', 'Movies'),
        ('Games', 'Games'),
        ('Collectibles', 'Collectibles'),
        ('Art', 'Art'),
        ('Crafts', 'Crafts'),
        ('Food', 'Food'),
        ('Pets', 'Pets'),
        ('Garden', 'Garden'),
        ('Tools', 'Tools'),
        ('Office', 'Office'),
        ('Education', 'Education'),
        ('Travel', 'Travel'),
        ('Outdoor', 'Outdoor'),
        ('Technology', 'Technology'),
        ('Instruments', 'Instruments'),
        ('Antiques', 'Antiques'),
        ('Services', 'Services'),
        ('other', 'Other'),
    ]


class Listing(models.Model):
    CATEGORY_CHOICES = [
        ('', 'Select'),
        ('Electronics', 'Electronics'),
        ('Clothing', 'Clothing'),
        ('Books', 'Books'),
        ('Home', 'Home'),
        ('Furniture', 'Furniture'),
        ('Vehicles', 'Vehicles'),
        ('Toys', 'Toys'),
        ('Sports', 'Sports'),
        ('Beauty', 'Beauty'),
        ('Jewelry', 'Jewelry'),
        ('Health', 'Health'),
        ('Music', 'Music'),
        ('Movies', 'Movies'),
        ('Games', 'Games'),
        ('Collectibles', 'Collectibles'),
        ('Art', 'Art'),
        ('Crafts', 'Crafts'),
        ('Food', 'Food'),
        ('Pets', 'Pets'),
        ('Garden', 'Garden'),
        ('Tools', 'Tools'),
        ('Office', 'Office'),
        ('Education', 'Education'),
        ('Travel', 'Travel'),
        ('Outdoor', 'Outdoor'),
        ('Technology', 'Technology'),
        ('Instruments', 'Instruments'),
        ('Antiques', 'Antiques'),
        ('Services', 'Services'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=256)
    description = models.TextField()
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES)
    seller = models.CharField(max_length=64)
    initial_price = models.DecimalField(default=0, decimal_places=2, max_digits=64)
    highest_bidder = models.CharField(max_length=64, default='No one yet')
    highest_bid = models.DecimalField(decimal_places=2, max_digits=64)
    is_closed = models.BooleanField(default=False)
    time_created = models.DateTimeField(default=timezone.now())

    def get_bidders(self):
        bidders = self.bids.values_list('bidder', flat=True)
        return list(bidders)


    def save(self, *args, **kwargs):
        if not self.pk:
            self.time_created = timezone.now()  # Set the current date and time
            self.highest_bid = self.initial_price
        super().save(*args, **kwargs)


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_image_path)




class User(AbstractUser):
    pass



class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')



class Bid(models.Model):
    bidder = models.CharField(max_length=64)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=0, related_name='bids')
    amount = models.DecimalField(decimal_places=2, max_digits=64)
    time_created = models.DateTimeField(auto_now_add=True)




class Comment(models.Model):
    text = models.TextField(max_length=500)
    commentor = models.CharField(max_length=64)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    time_created = models.DateTimeField(default=timezone.now())
