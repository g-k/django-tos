from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from tos.models import has_user_agreed_latest_tos, TermsOfService, UserAgreement


class TosView(TemplateView):
    template_name = "tos/tos.html"

    def get_context_data(self, **kwargs):
        context = super(TosView, self).get_context_data(**kwargs)
        context['tos'] = TermsOfService.objects.get_current_tos()
        return context


@csrf_protect
@never_cache
def check_tos(request, template_name='tos/tos_check.html'):
    tos = TermsOfService.objects.get_current_tos()

    redirect_to = request.GET.get('next', '/')

    if request.method == "POST":
        redirect_to = request.POST.get('next', '/')

        if request.POST.get("accept", "") == "accept":
            # Save the user agreement to the new TOS
            UserAgreement.objects.create(terms_of_service=tos, user=request.user)

            return redirect(redirect_to)
        else:
            messages.error(
                request,
                _(u"You cannot login without agreeing to the terms of this site.")
            )

    return render_to_response(template_name, {
        'tos': tos,
        'next': redirect_to,
    }, context_instance=RequestContext(request))
