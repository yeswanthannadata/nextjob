from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(Location)
admin.site.register(Company)
#admin.site.register(JD)
#admin.site.register(Agent)
#admin.site.register(Candidate)
admin.site.register(SPOC)
#admin.site.register(Status)
admin.site.register(StatusType)

#class CandidateAdmin(admin.ModelAdmin):
#    list_display = ["fname","jd","walk_in_date","mobile_number","status"]
#admin.site.register(Candidate, CandidateAdmin)

class AgentAdmin(admin.ModelAdmin):
    list_display = ["name","id"]
admin.site.register(Agent,AgentAdmin)

class JDAdmin(admin.ModelAdmin):
    list_display = ["job_title","id","candidates_req","start_date","end_date"]
admin.site.register(JD, JDAdmin)

class UserAdmin(UserAdmin):
    list_display = ["username","id"]
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# Register your models here.

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

class UserCreationFormExtended(UserCreationForm): 
    def __init__(self, *args, **kwargs): 
        super(UserCreationFormExtended, self).__init__(*args, **kwargs) 
        self.fields['first_name'] = forms.CharField(label=_("First Name"), max_length=30)
        self.fields['last_name'] = forms.CharField(label=_("Last Name"), max_length=30)
        self.fields['email'] = forms.EmailField(label=_("E-mail"), max_length=75)

UserAdmin.add_form = UserCreationFormExtended
UserAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)
    }),
)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
