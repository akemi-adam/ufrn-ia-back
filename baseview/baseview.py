from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class BaseView(APIView):
    permission_classes = [IsAuthenticated]
    model = None
    serializer_class = None

    def get_object(self, object_id):
        try:
            return self.model.objects.get(id=object_id)
        except self.model.DoesNotExist:
            return None

    def get(self, request, object_id=None):
        if object_id:
            obj = self.get_object(object_id)
            if not obj:
                return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.serializer_class(obj)
            return Response(serializer.data)

        objs = self.model.objects.all()
        serializer = self.serializer_class(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response(self.serializer_class(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
