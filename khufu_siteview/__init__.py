

def includeme(config):
    config.include('pyramid_jinja2')

    # don't bother doing import unless includeme() is being invoked
    import khufu_siteview.templatedir
    config.add_directive('add_templateview_route',
                         khufu_siteview.templatedir.add_templateview_route)
