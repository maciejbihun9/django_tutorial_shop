from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class CartAddProductForm(forms.Form):

    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)

    # element, który się nie wyświetla, pozwala on zmiany statusów jakiś operacji
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
