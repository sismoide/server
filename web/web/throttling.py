from rest_framework.views import APIView


# todo: algo

class ContactListView(APIView):
    throttle_scope = 'contacts'


class ContactDetailView(APIView):
    throttle_scope = 'contacts'


class UploadView(APIView):
    throttle_scope = 'uploads'
