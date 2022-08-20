from .models import FacebookPages,FacebookLeadDataDumping
from rest_framework.serializers import ModelSerializer


class FacebookPagesSerializers(ModelSerializer):
    class Meta:
        model = FacebookPages
        exclude = ('created_at',)

class FacebookLeadDataDumpingSerializers(ModelSerializer):
    class Meta:
        model = FacebookLeadDataDumping
        exclude = ('created_at','is_lead_sent')
