import os
import sys
from paste.fileapp import FileApp
from pyramid.asset import abspath_from_asset_spec
from pyramid.renderers import render_to_response, RendererHelper
from pyramid.path import caller_package
from pyramid.httpexceptions import HTTPNotFound
import logging

logger = logging.getLogger('khufu_templview')


class TemplateDirView(object):
    def __init__(self, assetspec, package=None):
        pname = package
        if not isinstance(package, basestring) \
                and hasattr(package, '__name__'):
            pname = pname.__name__

        if ':' not in assetspec and package:
            assetspec = pname + ':' + assetspec

        if not assetspec.endswith('/'):
            assetspec += '/'

        self.assetspec = assetspec

        self.basepath = abspath_from_asset_spec(assetspec, package)
        if not os.path.isdir(self.basepath):
            raise ValueError('%s <-> %s does not exist as a directory')

    def _diritem_iter(self, path):
        for x in os.listdir(path):
            yield {'label': x, 'link': x}

    def render_listing(self, request, path):
        relative = request.url[len(request.application_url):]

        return render_to_response(
            'khufu_templview:templates/listing.jinja2',
            {'path': relative, 'items': [x for x in self._diritem_iter(path)]},
            request
            )

    def find_index(self, path):
        for x in os.listdir(path):
            if x.startswith('index.'):
                return x
        return None

    def get_handler(self, asset, request):
        if not hasattr(self, '_cache'):
            self._cache = {}
        cache = self._cache

        res = cache.get(asset)
        if res is None:
            res = cache[asset] = self._build_handler(asset, request)
        else:
            logger.info('Cache hit for: %s' % asset)

        return res

    def _build_handler(self, asset, request):
        path = abspath_from_asset_spec(asset)
        if os.path.isdir(path):
            index = self.find_index(path)
            if index:
                return lambda request, index=index: render_to_response(index, {}, request)
            return lambda request, path=path: self.render_listing(request, path)
        if os.path.isfile(path):
            helper = RendererHelper(name=asset, registry=request.registry)
            try:
                if helper.renderer is not None:
                    return lambda request, helper=helper: helper.render_to_response({}, None, request=request)
            except ValueError:
                pass

            fileapp = FileApp(filename=path)
            return lambda request, fileapp=fileapp: request.get_response(fileapp)

        return lambda request: HTTPNotFound(comment=request.url[len(request.application_url):])

    def __call__(self, request):
        assetpath = self.assetspec + '/'.join(request.subpath)
        handler = self.get_handler(assetpath, request)
        return handler(request)


def add_templateview_route(config, assetspec, path):
    exclude = ('pdb', 'pyramid', 'khufu_templview')
    package = None
    for x in range(20):
        m = caller_package(x)
        mname = m.__name__
        bad = False
        for ex in exclude:
            if mname == ex or mname.startswith(ex + '.'):
                bad = True
                break

        if not bad:
            package = m
            break

    if package.__name__ == '__main__' and hasattr(package, '__package__'):
        package = sys.modules[package.__package__]

    newpath = path
    if not path.endswith('/'):
        newpath += '/'
    newpath += '*subpath'
    config.add_route('templview', newpath,
                     view=TemplateDirView(assetspec, package=package))


def includeme(config):
    config.include('pyramid_jinja2')
    config.add_directive('add_templateview_route',
                         add_templateview_route)
