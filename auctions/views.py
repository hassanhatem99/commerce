import datetime
import pytz 
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.db.models import Subquery, OuterRef



from .models import User, Listing, Bid, Comment, WatchlistItem, CATEGORY_CHOICES, ListingImage
from .forms import BidForm, CommentForm, ListingForm, Search
import geoip2.database


from geopy.geocoders import Nominatim

from .time_utils import get_timezone_by_ip, set_timezone





@set_timezone
def index(request):
    user = request.user
    listings = Listing.objects.filter(is_closed = False).order_by('-time_created')
    for listing in listings:
        listing.time_created = timezone.localtime(listing.time_created)
    if user.is_authenticated:
        watchlist_items = WatchlistItem.objects.filter(user=user, listing__in=listings).values_list('listing_id', flat=True)
        if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()        
        else:
            return render(request, "auctions/index.html", {
                "listings": listings,
                "user": user,
                "watchlist_items": watchlist_items,
                "search_form": Search,
                "search_icon": "🔎",
                
            })
    else:
        return redirect("login")



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")





@set_timezone
@login_required(login_url='/login')

def watchlist(request):
    user = request.user
    if user.is_authenticated:
        watchlist_items = WatchlistItem.objects.filter(user=user).order_by('-timestamp')
        listings = [item.listing for item in watchlist_items]
        if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()
        return render(request, "auctions/watchlist.html", {
            "listings": listings,
            "watchlist_items": watchlist_items,
            "search_form": Search,
            "search_icon": "🔎"
        })




@set_timezone
@login_required(login_url='/login')

def categories(request):
    if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()
    return render(request, "auctions/categories.html", {
        "categories": CATEGORY_CHOICES[1:],
        "search_form": Search,
            "search_icon": "🔎"
    })




@set_timezone

def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = request.user
    listings = Listing.objects.all()
    comments = list(Comment.objects.filter(listing=listing).order_by('-id')[:10])
    total_bids = Bid.objects.filter(listing=listing).count()
    if user.is_authenticated:
        watchlist_items = WatchlistItem.objects.filter(user=user, listing__in=listings).values_list('listing_id', flat=True)
        username = request.user.username
    if request.method == "POST":
            if request.user.is_authenticated:
                if listing.is_closed:
                    redirect(f"{listing_id}/fail") # Redirect to a fail page
                else:
                    form = BidForm(request.POST)
                    if form.is_valid():
                        amount = form.cleaned_data["amount"]
                        if (amount > listing.highest_bid) or (amount == listing.initial_price and listing.highest_bidder == 'No one yet'):
                            bid = Bid(bidder=username, amount=amount, listing=listing)
                            bid.save()
                            listing.highest_bid = amount
                            listing.save()
                            listing.highest_bidder = username
                            listing.save()
                            return redirect(f"{listing_id}/success")  # Redirect to a success page
                        else:
                            return redirect(f"{listing_id}/fail") # Redirect to a fail page
            else:
                return redirect("login") 

    else:
        form = BidForm()
        return render(request, "auctions/listing.html",{
            "listing": listing,
            "form": form,
            "watchlist_items": watchlist_items,
            "comments": comments,
            "total_bids": total_bids
        })    
 


@set_timezone
@login_required(login_url='/login')

def success(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()
    return render(request, "auctions/success.html",{
        "listing": listing,
        "search_form": Search,
        "search_icon": "🔎"
    })



@set_timezone
@login_required(login_url='/login')

def fail(request, listing_id):
    if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()
    listing = Listing.objects.get(id=listing_id)
    return render(request, "auctions/fail.html",{
        "listing": listing,
        "search_form": Search,
        "search_icon": "🔎"
    })



@set_timezone
@login_required(login_url='/login')

def comment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    comments = list(Comment.objects.filter(listing=listing))[::-1]
    if request.user.is_authenticated:
        username = request.user.username
    if request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data["text"]
                new_comment = Comment(text=text, commentor=username, listing=listing, time_created = timezone.now())
                new_comment.save()
                return redirect(f"/{listing_id}/comment")
        else:
            return redirect("login")
    else:
        form = CommentForm()
        return render(request, "auctions/comment.html",{
            "listing": listing,
            "form": form,
            "comments": comments
    })



@set_timezone
@login_required(login_url='/login')
def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = request.user

    # Check if the WatchlistItem already exists
    watchlist_item, created = WatchlistItem.objects.get_or_create(user=user, listing=listing)

    if created:
        # Item was newly created, perform any additional logic here if needed
        pass

    # Redirect to the previous URL with the listing anchor
    previous_url = request.META.get('HTTP_REFERER')
    if previous_url:
        return redirect(previous_url + '#listing-' + str(listing.id))
    else:
        return redirect('index')


@set_timezone
@login_required(login_url='/login')
def remove_from_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = request.user

    # Remove the watchlist item associated with the user and listing
    watchlist_item = WatchlistItem.objects.get(user=user, listing=listing)
    watchlist_item.delete()

    # Redirect to the previous URL with the listing anchor
    previous_url = request.META.get('HTTP_REFERER')
    if previous_url:
        return redirect(previous_url + '#listing-' + str(listing.id))
    else:
        return redirect('index')



@set_timezone
@login_required(login_url='/login')
def create_listing(request):
    user = request.user
    if request.method == "POST":
        if user.is_authenticated:
            form = ListingForm(request.POST, request.FILES)
            if form.is_valid():
                listing = form.save(commit=False)  # Save the form data but don't commit it to the database yet
                listing.seller = user  # Set the seller field to the current user
                listing.highest_bidder = "No one yet"
                listing.save()  # Save the listing with the updated fields
                images = request.FILES.getlist('image')  # Get the list of uploaded images
                for image in images:
                    ListingImage.objects.create(listing=listing, image=image)  # Create a ListingImage object for each image
                return render(request, "auctions/created.html", {
                    "listing": listing
                })
        else:
            return redirect("login")
    else:
        form = ListingForm()
    return render(request, "auctions/create_listing.html", {
        "form": form
    })




@set_timezone
@login_required(login_url='/login')

def created(request):
    if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()
    return render(request, "auctions/created.html", {
        "listing": listing
    })



@set_timezone
@login_required(login_url='/login')
def category(request, ctgr):
        user = request.user
        listings = Listing.objects.all().order_by("-time_created")
        in_category = []
        for listing in listings:
            if listing.category == ctgr and not listing.is_closed:
                in_category.append(listing.id)
        if user.is_authenticated:
            watchlist_items = WatchlistItem.objects.filter(user=user, listing__in=listings).values_list('listing_id', flat=True)
        
        if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()
        return render(request, "auctions/category.html", {
            "listings" :listings,
            "ctgr": ctgr,
            "watchlist_items": watchlist_items,
            "in_category": in_category,
            "search_form": Search,
            "search_icon": "🔎"
            
        })


@set_timezone
@login_required(login_url='/login')
def close_auction(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.user.is_authenticated:
        username = request.user.username
    if username == listing.seller:
        listing.is_closed = True
        listing.save()
    return render(request, "auctions/closed.html", {
        "listing": listing
    })  # Redirect to a success page
    


@set_timezone
@login_required(login_url='/login')
def my_listings(request):
    user = request.user
    listings = Listing.objects.filter(seller=user).order_by("-time_created")
    if user.is_authenticated:
        watchlist_items = WatchlistItem.objects.filter(user=user, listing__in=listings).values_list('listing_id', flat=True)
        
        if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()
        return render(request, "auctions/my_listings.html", {
            "listings": listings,
            "user": user,
            "watchlist_items": watchlist_items,
            "search_form": Search,
            "search_icon": "🔎"
        })
    

@set_timezone
@login_required(login_url='/login')
def seller_listings(request, seller):
    user = request.user
    listings = Listing.objects.filter(seller=seller).order_by("-time_created")
    if user.is_authenticated:
        watchlist_items = WatchlistItem.objects.filter(user=user, listing__in=listings).values_list('listing_id', flat=True)
        return render(request, "auctions/seller_listings.html", {
            "listings": listings,
            "user": user,
            "watchlist_items": watchlist_items,
            "seller": seller,
            "search_form": Search,
            "search_icon": "🔎"
        })



@set_timezone

def search_results(request, query):
    user = request.user
    listings = Listing.objects.filter(
        Q(seller__icontains=query) |
        Q(title__icontains=query) |
        Q(category__icontains=query) |
        Q(description__icontains=query)
    ).exclude(is_closed=True).order_by("-time_created")
    
    if user.is_authenticated:
        watchlist_items = WatchlistItem.objects.filter(user=user, listing__in=listings).values_list('listing_id', flat=True)
    if request.method == "POST":
        form = Search(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            return redirect(f"/search_results/{query}")
    else:
        form = Search(initial={"query": query})

    return render(request, "auctions/search_results.html", {
        "listings": listings,
        "watchlist_items": watchlist_items,
        "query": query,
        "search_form": form,
        "search_icon": "🔎"
    })


@set_timezone

def my_bids(request):
    user = request.user
    latest_bids = Bid.objects.filter(listing=OuterRef('pk')).order_by('-time_created')
    listings = Listing.objects.filter(bids__bidder=request.user.username).annotate(
        latest_bid_time_created=Subquery(latest_bids.values('time_created')[:1])
    ).order_by('-latest_bid_time_created')

    # Convert the queryset to a set to eliminate duplicates
    listings_set = set(listings)
    sorted_listings = sorted(listings_set, key=lambda x: x.latest_bid_time_created, reverse=True)
    
    if user.is_authenticated:
        watchlist_items = WatchlistItem.objects.filter(user=user, listing__in=listings).values_list('listing_id', flat=True)
        if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()        
        else:
            # Subquery to get the latest bid for each listing
            latest_bids = Bid.objects.filter(listing=OuterRef('pk')).order_by('-time_created')
            
            return render(request, "auctions/my_bids.html", {
                "listings": sorted_listings,
                "user": user,
                "watchlist_items": watchlist_items,
                "latest_bids": latest_bids,  # Pass the subquery to the template
                "search_form": Search,
                "search_icon": "🔎",
            })
    else:
        return redirect("login")
