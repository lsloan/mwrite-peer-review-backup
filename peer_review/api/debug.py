from django import forms
from django.conf import settings
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from toolz.functoolz import thread_last


class LtiParamsForm(forms.Form):
    custom_canvas_course_id = forms.CharField(label='Course ID')
    custom_canvas_user_id = forms.CharField(label='User ID')
    roles = forms.CharField(label='Roles')
    lis_person_contact_email_primary = forms.EmailField(label='Email')
    context_title = forms.CharField(label='Course Name')


class DebugLtiParamsView(LoginRequiredMixin, FormView):
    template_name = 'debug_lti.html'
    success_url = settings.LTI_APP_REDIRECT
    form_class = LtiParamsForm

    def get_form(self, form_class=None):
        lti_launch_params = dict(self.request.session.get('lti_launch_params') or {})
        if 'roles' in lti_launch_params:
            lti_launch_params['roles'] = ','.join(lti_launch_params['roles'])
        return LtiParamsForm(initial=lti_launch_params, data=self.request.POST or None)

    def form_valid(self, form):
        lti_launch_params = self.request.session.get('lti_launch_params') or {}
        roles = thread_last(form.cleaned_data['roles'], lambda rs: rs.split(','), (map, lambda s: s.strip()), list)
        form.cleaned_data['roles'] = roles
        self.request.session['lti_launch_params'] = {**form.cleaned_data, **lti_launch_params}
        return super(DebugLtiParamsView, self).form_valid(form)
