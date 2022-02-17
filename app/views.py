from django.db.models.expressions import RawSQL
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from app.models import Match, User
from app.serializers import UserSerializer, MatchSerializer, UserListSerializer
from rest_framework.response import Response
from django_filters import rest_framework as filters

from app.services.send_email_to_user import check_match_between_users, send_email_to_user


class CreateUser(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateMatch(generics.CreateAPIView):
    serializer_class = MatchSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    def post(self, request, *args, **kwargs):
        # print(f'Request data: {request.data}')
        # print(f'Request user: {request.user}')
        serializer = MatchSerializer(data=request.data, context={
            'request': request,
            'liked_user_id': kwargs['pk']
        })
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            if check_match_between_users(user_id=kwargs['pk'], user_2_id=request.user.id):
                user_1 = User.objects.get(id=kwargs['pk'])
                user_2 = request.user
                data = {
                    'user1': (user_1.username, user_1.email),
                    'user2': (user_2.username, user_2.email)
                }
                send_email_to_user(data)
                return Response(data={'email': f'{user_1.username}'})
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserFilter(filters.FilterSet):
    gender = filters.ChoiceFilter(choices=User.genders)
    first_name_filed = filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name_filed = filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    distance = filters.NumberFilter(method='get_nearby_users', label='Distance')

    def get_nearby_users(self, queryset, field_name, value=None):

        # gcd = "SELECT ALL (6371 * acos(least(greatest(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)), -1), 1))) AS distance FROM app_user ORDER BY distance"
        # gcd = "SELECT ALL (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))) AS distance FROM app_user ORDER BY distance"
        gcd_formula = "6371 * acos(least(greatest(\
            cos(radians(%s)) * cos(radians(latitude)) \
            * cos(radians(longitude) - radians(%s)) + \
            sin(radians(%s)) * sin(radians(latitude)) \
            , -1), 1))"
        distance_raw_sql = RawSQL(
            gcd_formula, tuple(map(float, (self.request.user.latitude, self.request.user.longitude, self.request.user.latitude))))
        if value is not None:
            return queryset.annotate(
                distance=distance_raw_sql).filter(
                distance__lte=value).filter(
                ~Q(id=self.request.user.id)).order_by(
                'distance')
        return queryset.annotate(
            distance=distance_raw_sql).filter(
            ~Q(id=self.request.user.id)).order_by(
            'distance')

    class Meta:
        model = User
        fields = ('gender', 'first_name_filed', 'last_name_filed', 'distance')


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
