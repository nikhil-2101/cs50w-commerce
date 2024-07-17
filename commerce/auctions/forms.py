from django import forms
from .models import Listing, Bid, Comment, Watchlist

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'item_name', 
            'item_description', 
            'starting_price', 
            'item_category', 
            'image'
        ]
        widgets = {
            'item_description': forms.Textarea(attrs={'cols': 80, 'rows': 10, 'style': 'vertical-align: top;'}),  # Adjust vertical alignment
        }   

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_amount']

    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop('listing', None)
        super().__init__(*args, **kwargs)

    def clean_bid_amount(self):
        bid_amount = self.cleaned_data.get('bid_amount')
        if self.listing:
            if bid_amount <= max(self.listing.current_bid or 0, self.listing.starting_price):
                raise forms.ValidationError("Bid amount must be higher than the current bid.")
        return bid_amount

    def clean(self):
        cleaned_data = super().clean()
        bid_amount = cleaned_data.get('bid_amount')
        if bid_amount and bid_amount <= 0:
            raise forms.ValidationError("Bid amount must be a positive number.")

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_title', 'comment_body']

class WatchlistForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ['listing']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['listing'].queryset = Listing.objects.exclude(watchlist__user=self.user)
