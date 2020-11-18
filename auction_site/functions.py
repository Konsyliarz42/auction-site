def value_form(form, key, default_value=None):
    try:
        value = form[key]
    except KeyError:
        value = default_value
    finally:
        return value
