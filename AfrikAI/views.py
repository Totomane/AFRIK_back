# backend/AfrikAI/views.py
from django.http import JsonResponse
from django.views import View

class AfrikAIHelloView(View):
	def get(self, request):
		return JsonResponse({"message": "Hello from AfrikAI!"})
