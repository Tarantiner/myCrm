"""AcaSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
# from django.contrib import admin
from stark.service.v1 import site
from academy.views import account

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^', site.urls),
    url(r'^rbac/', include('rbac.urls', namespace='rbac')),
    url(r'login/$', account.login, name='login'),
    url(r'^logout/', account.logout, name='logout'),
    url(r'^index/', account.index, name='index'),
    url(r'^get_valid_code/', account.get_valid_code, name='get_valid_code'),
    url(r'^person_information/$', account.person_information, name='get_information'),
]
