from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from .tokens import default_token_generator

User = get_user_model()


class SignupUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email',)
        extra_kwargs = {'email': {'required': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                f'Пользователь с почтой {value} уже есть в базе'
            )
        return value

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя `me` в качестве username запрещено.'
            )
        return value


class TokenSerializer(serializers.Serializer):

    confirmation_code = serializers.CharField(max_length=30)
    username = serializers.CharField(max_length=30)

    def validate(self, data):
        user = get_object_or_404(
            User,
            username=data.get('username')
        )
        if not default_token_generator.check_token(
            user=user,
            token=data.get('confirmation_code')
        ):
            raise serializers.ValidationError(
                'Неверный `confirmation_code` или истёк его срок годности.'
            )
        return data

    def create(self, validated_data):
        return validated_data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ['id']
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ['id']
        model = Genre


class GenreTitleSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = GenreTitle


class TitleGETSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True, required=False)
    genre = GenreSerializer(many=True, read_only=True, required=False)
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')


class TitleSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
    )
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name', 'last_name',
            'bio', 'role',
        )
        extra_kwargs = {'email': {'required': True}}

    def validate(self, data):
        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError(
                'Пользователь с таким `email` уже зарегистрирован.'
            )
        return data


class MyselfSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name', 'last_name',
            'bio', 'role',
        )
        extra_kwargs = {'role': {'read_only': True}}


class ReviewSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'

    def validate_score(self, value):
        if value not in range(1, 11):
            raise serializers.ValidationError(
                "Оценка должна быть в диапазоне [1, 10]"
            )
        return value

    def validate(self, data):
        if (
            Review.objects.filter(
                author=self.context.get('request').user,
                title_id=self.context.get('view').kwargs.get('title_id')
            ).exists()
            and self.context.get('request').method == 'POST'
        ):
            raise serializers.ValidationError(
                'Можно оставить только один отзыв на проиведение.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    review_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {'text': {'required': True}}
