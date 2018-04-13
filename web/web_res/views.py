from django.shortcuts import render

from web_res.serializers import IntensitySerializer, EmergencySerializer, ThreatSerializer
from mobile_res.models import Report, EmergencyReport, ThreatReport
from rest_framework import generics, mixins, viewsets
from rest_framework.response import Response

import datetime as dt

# Create your views here.


def get_date(request, type, default):
	date = request.query_params.get(type, default)
	return dt.datetime.strptime(date, "%Y-%m-%dT%H:%M")


class ReportList(mixins.ListModelMixin, viewsets.GenericViewSet):

	queryset = Report.objects.all()
	serializer_class = IntensitySerializer

	def list(self, request, *args, **kwargs):
		#start_date = request.query_params.get('start', "2018-01-01T00:00")
		#end_date = request.query_params.get('end', "2100-12-31T23:59")
		#start_date = dt.datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
		#end_date = dt.datetime.strptime(end_date, "%Y-%m-%dT%H:%M")
		end_date, start_date = self.getdates(request)
		queryset = self.get_queryset().filter(created_on__range=(start_date, end_date))
		serializer = IntensitySerializer(queryset, many=True)
		return Response(serializer.data)

	def getdates(self, request):
		start_date = get_date(request, 'start', "1918-01-01T00:00")
		end_date = get_date(request, 'end', "2100-12-31T23:59")
		return end_date, start_date


class EmergencyList(mixins.ListModelMixin, viewsets.GenericViewSet):

	queryset = EmergencyReport.objects.all()
	serializer_class = EmergencySerializer

	def list(self, request, *args, **kwargs):
		start_date = get_date(request, 'start', "1918-01-01T00:00")
		end_date = get_date(request, 'end', "2100-12-31T23:59")
		queryset = self.get_queryset().filter(report__created_on__range=(start_date, end_date))
		serializer = EmergencySerializer(queryset, many=True)
		return Response(serializer.data)


class ThreatList(mixins.ListModelMixin, viewsets.GenericViewSet):

	queryset = ThreatReport.objects.all()
	serializer_class = ThreatSerializer

	def list(self, request, *args, **kwargs):
		start_date = get_date(request, 'start', "1918-01-01T00:00")
		end_date = get_date(request, 'end', "2100-12-31T23:59")
		queryset = self.get_queryset().filter(report__created_on__range=(start_date, end_date))
		serializer = ThreatSerializer(queryset, many=True)
		return Response(serializer.data)
