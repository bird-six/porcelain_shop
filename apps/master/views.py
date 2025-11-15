from django.shortcuts import render

def master(request):

    return render(request, 'master/master.html')
