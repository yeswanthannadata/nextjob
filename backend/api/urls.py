from django.conf.urls import include, url 
from django.contrib import admin

urlpatterns = [ 
    # Examples:
    url(r'^jds','api.views.jds', name="jds"),
    url(r'^candidates','api.views.candidates', name="candidates"),
    url(r'^add_candidate','api.views.add_candidate', name="add"),
    url(r'^update_candidate','api.views.update_candidate', name="update"),
    url(r'^upload/','api.views.excel_upload'),
    url(r'^can_status/','api.views.status'),
    url(r'^status_dropdown/','api.views.candidate_status_dropdown'),
    url(r'^delete_candidate/','api.views.delete_candidate'),
    url(r'^get_candidate_log/','api.views.status_log'),
]
