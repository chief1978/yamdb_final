from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comment, Genre, Review, Title
from .custom_filters import CategoryFilter
from .mixins import BaseViewSet
from .permissions import AuthorOrAdminOrModerator, IsAdminOrReadOnly
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer, MyselfSerializer,
    ReviewSerializer, SignupUserSerializer, TitleGETSerializer,
    TitleSerializer, TokenSerializer, UsersSerializer,
)
from .tokens import default_token_generator

User = get_user_model()


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def send_confirmation_code(request):
    serializer = SignupUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    code = default_token_generator.make_token(serializer.instance)
    send_mail(
        subject='confirmation_code',
        message=(
            f'{serializer.instance.username} your '
            f'confirmation_code: {code}'
        ),
        from_email=settings.ADMIN_EMAIL,
        recipient_list=[serializer.instance.email]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.save()
    user = get_object_or_404(User, username=data['username'])
    user.password = ''
    user.save()
    token = str(AccessToken.for_user(user))
    return Response({'token': token}, status=status.HTTP_200_OK)


class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name', 'slug')
    search_fields = ('name', 'slug')
    lookup_field = 'slug'
    lookup_value_regex = "[^/]+"


class GenreViewSet(BaseViewSet):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name', 'slug')
    search_fields = ('name', 'slug')
    lookup_field = 'slug'
    lookup_value_regex = "[^/]+"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().order_by('id').annotate(
        rating=Avg('reviews__score')
    )
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = CategoryFilter
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return TitleGETSerializer
        return TitleSerializer


class UsersViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('id')
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = UsersSerializer
    lookup_field = 'username'
    lookup_url_kwargs = 'username'
    lookup_value_regex = r'[\w.@+-]+'

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        methods=('get', 'patch',),
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = MyselfSerializer(user)
            return Response(serializer.data)
        serializer = MyselfSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        AuthorOrAdminOrModerator,
    )

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review_id=review)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        get_object_or_404(Review, id=review_id)
        return Comment.objects.filter(review_id=review_id).order_by('id')


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AuthorOrAdminOrModerator,)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        get_object_or_404(Title, id=title_id)
        return Review.objects.filter(title=title_id).order_by('id')
