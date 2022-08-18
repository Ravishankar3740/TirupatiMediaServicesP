from .models import FacebookPages
from rest_framework.serializers import ModelSerializer


class FacebookPagesSerializers(ModelSerializer):
    class Meta:
        model = FacebookPages
        exclude = ('created_at',)

