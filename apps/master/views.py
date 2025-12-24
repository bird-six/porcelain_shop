from django.shortcuts import render

def master(request):

    return render(request, 'master/master.html')

def customize(request):

    return render(request, 'master/customize.html')

def master_detail(request):

    return render(request, 'master/master_detail.html')
