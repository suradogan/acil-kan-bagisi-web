from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """
    Bir string'i belirtilen ayırıcıya göre parçalara böler ve liste olarak döndürür.
    
    Örnek Kullanım:
    {% for item in "a,b,c"|split:"," %}
        {{ item }}
    {% endfor %}
    """
    return value.split(delimiter) 