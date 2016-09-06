from django.contrib.contenttypes.models import ContentType
from guardian.models import UserObjectPermission
from django.contrib.auth.models import Permission
import re
import logging
import functools
from django.core.cache import cache

log = logging.getLogger(__name__)

def get_content_type(model):
    content_type = ContentType.objects.get_for_model(model)
    return content_type

def get_object_permissions(instance, model):
    content_type = get_content_type(model)
    content_id = content_type.id
    permissions = UserObjectPermission.objects.filter(content_type=content_id, object_pk = instance.pk)
    return permissions

def copy_permissions(base_instance, base_model, new_instance, new_model):
    base_permissions = get_object_permissions(base_instance, base_model)
    new_content_type = get_content_type(new_model)
    for permission in  base_permissions:
        content_type = new_content_type
        object_pk = new_instance.pk
        new_permission_name = generate_new_permission(permission.permission.codename, new_content_type.name)
        django_permission = Permission.objects.get(codename=new_permission_name)
        permission_obj = django_permission
        perm_dict = {
            'user' : permission.user,
            'content_type' : content_type,
            'permission' : permission_obj,
            'object_pk' : object_pk,
            }
        perm, created = UserObjectPermission.objects.get_or_create(**perm_dict)

def generate_new_permission(permission_name, new_model_name):
    new_model_name = re.sub(r"[_\W]", "", new_model_name).lower()
    permission_list = permission_name.split("_")
    permission_list = permission_list[0:(len(permission_list)-1)]
    permission_list += [new_model_name]
    new_permission = "_".join(permission_list)
    return new_permission

def single_instance_task(timeout):
    def task_exc(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_id = "celery-single-instance-" + func.__name__
            acquire_lock = lambda: cache.add(lock_id, "true", timeout)
            release_lock = lambda: cache.delete(lock_id)
            if acquire_lock():
                try:
                    func(*args, **kwargs)
                finally:
                    release_lock()
        return wrapper
    return task_exc