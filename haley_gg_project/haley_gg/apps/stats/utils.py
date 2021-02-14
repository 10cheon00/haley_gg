non_url_safe = [
    '"', '#', '$', '%', '&', '+',
    ',', '/', ':', ';', '=', '?',
    '@', '[', '\\', ']', '^', '`',
    '{', '|', '}', '~', "'", ' ', '-'
]


def slugify(text):
    return text.translate(text.maketrans('', '', u''.join(non_url_safe)))


def remove_space(text):
    return text.replace(' ', '')


def get_grouped_results(queryset):
    # Group result data by result name.
    grouped_result_dict = {}
    for result in queryset:
        name = result.match_name()
        if name not in grouped_result_dict:
            grouped_result_dict[name] = []
        grouped_result_dict[name].append(result)
    return grouped_result_dict


def get_rate(numerator, denominator):
    try:
        return round(numerator / denominator * 100, 2)
    except ZeroDivisionError:
        return 0
