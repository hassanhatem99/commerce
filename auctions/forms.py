from django import forms
from .models import User, Listing, Bid, Comment, ListingImage

class Search(forms.Form):
    query = forms.CharField(label="Search",
                            max_length=64,
                            widget=forms.TextInput(attrs=
                                                    {'placeholder': 'Search for listings, categories, brands, or sellers...',
                                                    'style': 'width: 380px'
                                                    }
                                                  )
                            )

class CommentForm(forms.ModelForm):
    text = forms.CharField(label='Comment', widget=forms.Textarea(attrs={'class': 'expandable-textarea', 'rows': 3, 'cols': 30}))
    class Meta:
        model = Comment
        fields = ('text',)

class BidForm(forms.ModelForm):
    amount = forms.DecimalField(label='Bid')
    class Meta:
        model = Bid
        fields = ('amount',)


class ListingForm(forms.ModelForm):
    title = forms.CharField(label='Title', widget=forms.Textarea(attrs={'rows': 4}))
    initial_price = forms.DecimalField(label='Starting Price')
    image = forms.ImageField(label="Image(s)")
    category = forms.ChoiceField(choices=Listing.CATEGORY_CHOICES, label='Category')
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 8}), required=False)

    class Meta:
        model = Listing
        fields = ('title', 'category', 'initial_price', 'image', 'description')
    
    def save(self, commit=True):
        listing = super().save(commit=commit)
        images = self.cleaned_data.get('images')
        if images:
            for image in images:
                ListingImage.objects.create(listing=listing, image=image)

        return listing

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False
        self.fields['category'].required = False
        self.fields['description'].required = False

