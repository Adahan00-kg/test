from django.contrib.auth.models import AbstractUser

from django.db import models

from django.core.validators import MaxValueValidator,MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField

class UserProfile(AbstractUser):

    age = models.PositiveSmallIntegerField(null=True,blank=True,
                                           validators=[MinValueValidator(15),
                                                       MaxValueValidator(110)])
    country = models.CharField(max_length=32,null=True,blank=True)
    phono_number = PhoneNumberField(null=True,blank=True,region='KG')
    date_register = models.DateField(auto_now_add=True,null=True,blank=True)
    STATUS_CHOiCES = (
        ('gold','Gold'),
        ('silver','Silver'),
        ('bronze','Bronze'),
        ('simple','Simple'),
    )

    status = models.CharField(max_length=10,choices=STATUS_CHOiCES,default='simple')

    def __str__(self):
        return f'{self.first_name} - {self.last_name}'


class Category(models.Model):
    category_name = models.CharField(max_length=16 )

    def __str__(self):
        return self.category_name

class Product(models.Model):
    product_name = models.CharField(max_length=32,unique=True)
    category = models.ForeignKey(Category,related_name='products',on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    active  = models.BooleanField(default=True,verbose_name='в наличии')
    product_video = models.FileField(upload_to='vid/',verbose_name='видео',null=True,blank=True)
    owner = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.product_name

    def get_average_rating(self):
        ratings = self.rating.all()
        if ratings.exists():
            return (round(sum(rating.stars for rating in ratings) / ratings.count(), 1))
        return 0


class ProductPhoto(models.Model):
    product = models.ForeignKey(Product,related_name='product',on_delete=models.CASCADE)


class Rating(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='ratings')
    stars = models.PositiveSmallIntegerField(choices=[(i ,str(i)) for i in range(11)],verbose_name='Рейтинг',null=True,blank=True)
    user  = models.ForeignKey(UserProfile,on_delete=models.CASCADE)


    def __str__(self):
        return f'{self.product} - {self.user} - {self.stars}'


class Review(models.Model):
    author = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,related_name='reviews',on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    parent_review = models.ForeignKey('self', related_name='replies', null=True, blank=True, on_delete=models.CASCADE)


    def __str__(self):
        return f'{self.author} - {self.text}'


class Cart(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}'

    def get_total_price(self):
        total_price = sum(item.get_total_price() for item in self.items.all())
        discount = 0
        if self.user.status == 'gold':
            discount = 0.75
        elif self.user.status == 'silver':
            discount = 0.5
        elif self.user.status == 'bronze':
            discount = 0.25
        final_price = total_price *(1-discount)
        return final_price


class CarItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    def get_total_price(self):
        return self.product.price * self.quantity

class name(models.Model):
    name = models.CharField(max_lenght=10)
