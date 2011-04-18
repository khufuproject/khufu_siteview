import khufu_templview.templateview


def includeme(config):
    config.include('pyramid_jinja2')
    config.add_directive('add_templateview_route',
                         khufu_templview.templateview.add_templateview_route)
