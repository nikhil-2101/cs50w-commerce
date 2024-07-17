from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.db import IntegrityError
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist



from .models import *
from .forms import *

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
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

@login_required
def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": CATEGORIES
    })

@login_required
def category_listings(request, category):
    category_name = dict(CATEGORIES).get(category)  # Get category name from code
    listings = Listing.objects.filter(item_category=category, is_closed=False)
    return render(request, "auctions/individualCategories.html", {
        "listings": listings,
        "category": category_name  
    })


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            return redirect("index")
    else:
        form = ListingForm()
    return render(request, "auctions/createListing.html", {
        "form": form
    })

@login_required
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comment_form = CommentForm()
    is_in_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    bid_count = listing.bid_listing.count()

    is_seller = (request.user == listing.seller)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comment_form": comment_form,
        "comments": listing.comment_listings.all(),
        "is_in_watchlist": is_in_watchlist,
        "redirect_to_watchlist": reverse("watchlist"),
        "bid_count": bid_count,
        "bid_amount": listing.current_bid,
        "message": "",
        "is_seller": is_seller 
    })

@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.method == 'POST':
        bid_form = BidForm(request.POST, listing=listing)
        
        if bid_form.is_valid():
            bid_amount = bid_form.cleaned_data['bid_amount']
            
            if bid_amount > listing.current_bid:

                listing.current_bid = bid_amount
                listing.save()

                bid = bid_form.save(commit=False)
                bid.bidder = request.user
                bid.bid_listing = listing
                bid.save()

                bid_count = listing.bid_listing.count()

                messages.success(request, "Your bid has been placed successfully.")
                return redirect('listing', listing_id=listing_id)
            else:
                messages.error(request, "Your bid must be higher than the current bid.")
        else:
            messages.error(request, "Invalid bid form.")

    bid_count = listing.bid_listing.count()  
    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'bid_form': bid_form,
        'bid_count': bid_count,  
    })

    
@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.commenter = request.user
            comment.listing = listing
            comment.save()
            return redirect("listing", listing_id=listing_id)
    else:
        form = CommentForm()
    return render(request, "auctions/newComment.html", {
        "form": form,
        "listing_id": listing_id
    })

@login_required
def display_watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {"watchlist_items": watchlist_items})


@login_required
def add_to_watchlist(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        if Watchlist.objects.filter(user=request.user, listing=listing).exists():
            messages.info(request, "Listing is already in your watchlist.")
        else:
            Watchlist.objects.create(user=request.user, listing=listing)
            messages.success(request, "Listing added to your watchlist.")
    return redirect("watchlist")

@login_required
def remove_from_watchlist(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        watchlist_item = Watchlist.objects.filter(user=request.user, listing=listing)
        if watchlist_item.exists():
            watchlist_item.delete()
            messages.success(request, "Listing removed from your watchlist.")
        else:
            messages.info(request, "Listing is not in your watchlist.")
    return redirect("watchlist")


@login_required
def close_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == "POST":
        if listing.is_closed:
            return redirect('listing', listing_id=listing_id)

        highest_bid = Bid.objects.filter(bid_listing=listing).order_by('-bid_amount').first()

        listing.is_closed = True
        if highest_bid:
            listing.winner = highest_bid.bidder.username
        else:
            listing.winner = None 

        listing.save()

        messages.success(request, "Auction closed successfully.")
        return redirect('listing', listing_id=listing_id)

    return redirect('listing', listing_id=listing_id)


