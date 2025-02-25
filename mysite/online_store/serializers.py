from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password','first_name', 'last_name', 'age',
        'date_register', 'phono_number', 'status']

        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные учетные данные")

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }



class UserProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name','last_name']


class ProductPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhoto
        fields = '__all__'



class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format='%d - %m - %Y  %H:%M')
    class Meta:
        model = Review
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']

class ProductListSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format='%d-%m-%Y')
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = ['id','product_name','price','date','category']



class ProductDetailSerializer(serializers.ModelSerializer):

    owner = UserProfileSerializer()
    category = CategorySerializer()
    product = ProductPhotoSerializer(many=True,read_only=True)
    ratings = RatingSerializer(many=True,read_only=True)
    reviews = ReviewSerializer(many=True,read_only=True)
    date = serializers.DateTimeField(format='%d-%m-%Y')
    class Meta:
        model = Product
        fields = ['product_name','description','category','price','active','product_video',
                  'date','owner','product','ratings','reviews']

    # def get_average_rating(self,obj):
    #     return obj.get_average_rating()



class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),write_only=True,source='product')

    class Meta:
        model = CarItem
        fields = ['id','product','product_id','get_total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id','user','items','total_price']


    def get_total_price(self,obj):
        return obj.get_total_price()