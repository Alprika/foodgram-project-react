from api.pagination import RecipePagination
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User
from recipes.models import (Recipe)

from .users_serializers import FollowRecipeSerializer, SubscriptionSerializer
from .recipes_serializers import RecipeReadSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all().order_by('id')
    pagination_class = RecipePagination
    search_fields = ('username',)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            user = request.user
            author = self.get_object()
            if user == author:
                data = {'errors': 'Ошибка: подписка на себя'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(
                user=user,
                author=author,
            ).exists():
                data = {'errors': 'Вы подписаны на данного пользователя'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(
                user=user,
                author=author,
            )
            serializer = SubscriptionSerializer(
                author,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            user = request.user
            author = self.get_object()
            subscription = Subscription.objects.filter(
                user=user,
                author=author,
            )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            data = {'errors': 'Вы не подписаны на данного пользователя'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=('post', 'delete'),
        url_path='subscribe',
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            data = {'user': user.id, 'author': id}
            serializer = FollowRecipeSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        following = get_object_or_404(Subscription, user=user, author=author)
        following.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=('GET'),
        url_path='subscribe2',
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        posts=Recipe.objects.filter(author=author)
        data = RecipeReadSerializer(posts, many=True)
        return Response(data.data)
