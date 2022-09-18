from django.shortcuts import render, render_to_response


def erorr500(request):
    return render(request, 'core/500.html')


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=""):
    response = render_to_response('core/403csrf.html', {})
    response.status_code = 403
    return response

# def csrf_failure(request, reason=''):
#     return render(request, 'core/403csrf.html')

# def internal_server_error()
