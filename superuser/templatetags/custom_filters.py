from django import template
from num2words import num2words

register = template.Library()

@register.filter
def filter_incoming(details_set):
    return details_set.filter(direction='incoming')

@register.filter
def filter_outgoing(details_set):
    return details_set.filter(direction='outgoing')

@register.filter
def filter_logicalGrnStore(details_set):
    return details_set.filter(logical_grn_store=1)

@register.filter
def number_to_words(value):
    """
    Converts a number to words, handling decimal amounts.
    For example:
    - 11800.00 -> "Eleven thousand, eight hundred"
    - 11800.50 -> "Eleven thousand, eight hundred and 50 paisa"
    """
    try:
        # Separate the integer and decimal parts
        integer_part = int(value)
        decimal_part = round(value - integer_part, 2) * 100

        # Convert the integer part to words
        integer_words = num2words(integer_part, lang='en').capitalize()

        if decimal_part > 0:
            # Convert the decimal part to words (as paisa)
            decimal_words = f"{int(decimal_part)} paisa"
            return f"{integer_words} and {decimal_words}"
        else:
            return integer_words
    except (TypeError, ValueError):
        return "Invalid number"