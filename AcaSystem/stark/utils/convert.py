from django.urls import reverse


def name2url(namespace, name, *args, **kwargs):
    full_name = '%s:%s' % (namespace, name)
    return reverse(full_name, args=args, kwargs=kwargs)