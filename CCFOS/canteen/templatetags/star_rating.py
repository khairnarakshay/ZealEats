from django import template

register = template.Library()

@register.filter
def star_rating(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return '☆☆☆☆☆'

    full_stars = int(value)
    half_star = value - full_stars >= 0.5
    empty_stars = 5 - full_stars - int(half_star)

    return '★' * full_stars + ('½' if half_star else '') + '☆' * empty_stars
