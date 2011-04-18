==============
khufu_siteview
==============

Overview
========

*khufu_siteview* is an addon for Pyramid hows the registration of a
view that can be used to serve all ``.jinja2`` files out of a directory
as subviews without the need to map them directly.

Usage
=====

Standard setup is to ``Configurator.include`` the *khufu_siteview*
package and then add new views as necessary.

Example::

  from pyramid.config import Configurator
  
  def app(global_conf, **settings):
      config = Configurator(settings=settings)
      config.include('khufu_siteview')
      config.add_templateview_route('/some/path/to/site', '/')
      return config.make_wsgi_app()

The previous example mounts the view at the root of the new Pyramid
application.  The following example url's would work::

  http://127.0.0.1:8080/favicon.ico   ->  /some/path/to/site/favicon.ico
  http://127.0.0.1:8080/somepage.jinja2   ->  /some/path/to/site/somepage.jinja2

Static assets such as gif's and ico's will be looked up as if the view was static.

Credits
=======

Created and maintained by Rocky Burt <rocky AT serverzen DOT com>.
