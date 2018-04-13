
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from api.models.VerifiableClaim import VerifiableClaim
from api.models.VerifiableOrg import VerifiableOrg
from api.models.InactiveClaimReason import InactiveClaimReason
from api.models.IssuerService import IssuerService
from api.models.Jurisdiction import Jurisdiction
from api.models.LocationType import LocationType
from api.models.VerifiableClaimType import VerifiableClaimType
from api.models.VerifiableOrgType import VerifiableOrgType
from api import serializers


def health(request):
    """
    Health check for OpenShift
    """
    return HttpResponse(VerifiableClaim.objects.count())
