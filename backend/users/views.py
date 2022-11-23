from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User
from .pagination import UsersPagination
from .serializers import SubscribeSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all().order_by('id')
    pagination_class = UsersPagination
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
            serializer = SubscribeSerializer(
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
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        subscriptions_list = self.paginate_queryset(
            self.request.user.subscribe.all()
        )
        serializer = SubscribeSerializer(
            subscriptions_list, many=True, context={
                'request': request
            }
        )
        return self.get_paginated_response(serializer.data)
