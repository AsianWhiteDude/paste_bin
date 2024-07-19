from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def set_placeholder(field, text):
    field.field.widget.attrs.update({'placeholder': text})
    return field