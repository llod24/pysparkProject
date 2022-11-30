from django.shortcuts import render
from twitter import tweet
import json
from django.http import HttpResponse
from django.http import JsonResponse
# Create your views here.
from django.views.decorators.csrf import csrf_exempt

a = {1: 'a'}
def index(request):
	return render(request, 'chart.html')

@csrf_exempt
def getData(request):
	obj = json.loads(request.body)
	num = obj.get('number')
		
	T = tweet.Tweet(int(num))
	context = T.do(["football", "worldcup", "soccer"])
	return HttpResponse(context)
