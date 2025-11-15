from django.shortcuts import render

def appreciation(request):
    return render(request, 'appreciation/works_appreciation.html')
