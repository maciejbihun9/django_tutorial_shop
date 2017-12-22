from decimal import Decimal
from django.conf import settings
from shop.models import Product
from coupons.models import Coupon
import web_pdb

# to nie jest klasa modelowa
# to jest klasa zwykła
class Cart(object):

    def __init__(self, request):
        """
        Inicjalizacja koszyka na zakupy.
        """
        # przypisanie sesji do obieku klasy
        # teraz ten obiekt to ten sam obiekt
        self.session = request.session
        # pobranie danych json z sesji i konwertowanie tego do obiektu dict.
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Zapis pustego koszyka na zakupy w sesji.
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # Przechowywanie aktualnie zastosowanego kuponu.
        # pobranie id kuponu z sesji
        self.coupon_id = self.session.get('coupon_id')

    # ta metoda zwraca listę, ale pod postacią generatora
    # return nie trzeba pisać, bo jest nadmiarowe
    # element można pozyskać tylko podczas iteracji elementów
    # elementy są zwracane po kolei
    def __iter__(self):
        """
        Iteracja przez elementy koszyka na zakupy i pobranie produktów z bazy danych.
        """
        product_ids = self.cart.keys()
        # Pobranie obiektów produktów i dodanie ich do koszyka na zakupy.
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product
        # Dla każdego produktu w karcie.
        for item in self.cart.values():
            # parsowanie na wartość dziesiętną ze stringa
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Obliczenie liczby wszystkich elementów w koszyku na zakupy.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def __str__(self):
        return str(len(self.cart.items()))

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def save(self):
        # Uaktualnienie koszyka sesji.
        # przypisanie pod id tej karty karty z nowymi produktami.
        # zmiana zawartości danych w obiekcie request
        self.session[settings.CART_SESSION_ID] = self.cart
        # Oznaczenie sesji jako "zmodyfikowanej", aby upewnić się o jej zapisaniu.
        self.session.modified = True

    def remove(self, product):
        """
        Usunięcie produktu z koszyka na zakupy.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
        self.save()

    def clear(self):
    # Usunięcie koszyka na zakupy z sesji.
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def add(self, product, quantity=1, update_quantity=False):
        """
        Dodawanie produktu do koszyka lub zmiana jego ilości.
        """
        # każdy produkt w sklepie ma jedno id.
        # user odwołuje się do produktu po id

        product_id = str(product.id)
        # jęsli nie ma produktu o podanym id w koszyku to...
        if product_id not in self.cart:
            # utworzenie go w koszyku z ilością 0.
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        # poprawianie ilości elementów
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    @property
    def coupon(self):
        if self.coupon_id:
            return Coupon.objects.get(id=self.coupon_id)
        return None

    def get_discount(self):
            if self.coupon:
                return (self.coupon.discount / Decimal('100')) \
                       * self.get_total_price()
            return Decimal('0')

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
