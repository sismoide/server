from django.shortcuts import render

from web_res.serializers import IntensitySerializer
from mobile_res.models import Report
from rest_framework import generics, mixins, viewsets
from rest_framework.response import Response

import datetime as dt

# Create your views here.


class ReportList(mixins.ListModelMixin, viewsets.GenericViewSet):

	queryset = Report.objects.all()
	serializer_class = IntensitySerializer

	def list(self, request, *args, **kwargs):
		start_date = request.query_params.get('start', "2018-01-01T00:00")
		end_date = request.query_params.get('end', "2100-12-31T23:59")
		start_date = dt.datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
		end_date = dt.datetime.strptime(end_date, "%Y-%m-%dT%H:%M")
		queryset = self.get_queryset().filter(created_on__range=(start_date, end_date))
		serializer = IntensitySerializer(queryset, many=True)
		return Response(serializer.data)
