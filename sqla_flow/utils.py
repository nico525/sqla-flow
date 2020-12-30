from slugify import slugify as _slugify


def slugify(column_name):
    def default_function(context):
        return _slugify(context.current_parameters.get(column_name))
    return default_function
