import os
import sys
from paste.fileapp import FileApp
from pyramid.asset import abspath_from_asset_spec
from pyramid.renderers import render_to_response, RendererHelper
from pyramid.path import caller_package
from pyramid.httpexceptions import HTTPNotFound
import re
import logging

logger = logging.getLogger('khufu_templview')

excludes = [
    re.compile('^[.].*$'),
    re.compile('~$'),
    ]


def is_valid_file(v):
    for x in excludes:
        if x.search(v):
            logger.debug('Skipping "%s"' % v)
            return False
    return True


def listdir(path):
    return filter(is_valid_file, os.listdir(path))


class Curry(object):

    def __init__(self, callback, *cb_args, **cb_kwargs):
        self.callback = callback
        self.cb_args = cb_args
        self.cb_kwargs = cb_kwargs

    def __call__(self, *args, **kwargs):
        newargs = list(self.cb_args) + list(args)
        newkwargs = dict(self.cb_kwargs)
        newkwargs.update(kwargs)
        return self.callback(*newargs, **newkwargs)


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

        self.basepath = os.path.abspath(abspath_from_asset_spec(assetspec))
        if not os.path.isdir(self.basepath):
            raise ValueError('%s <-> %s does not exist as a directory'
                             % (assetspec, self.basepath))

    def _diritem_iter(self, path):
        for x in listdir(path):
            yield {'label': x, 'link': x}

    def render_listing(self, request, path):
        relative = request.url[len(request.application_url):]

        items = [x for x in self._diritem_iter(path)]
        return render_to_response('khufu_templview:templates/listing.jinja2',
                                  {'path': relative, 'items': items},
                                  request)

    def find_index(self, path):
        for x in listdir(path):
            if x.startswith('index.'):
                return os.path.join(path, x)
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
        path = os.path.abspath(abspath_from_asset_spec(asset))
        if not path.startswith(self.basepath):
            # make sure url scheme wasn't tricked into going into parent dirs
            return Curry(HTTPNotFound,
                         comment=request.url[len(request.application_url):])
        if os.path.isdir(path):
            index = self.find_index(path)
            if index:
                logger.debug('serving default index file: ' + index)
                return Curry(render_to_response, renderer_name=index, value={})
            return Curry(self.render_listing, path=path)
        if os.path.isfile(path):
            helper = RendererHelper(name=asset, registry=request.registry)
            try:
                if helper.renderer is not None:
                    return Curry(helper.render_to_response, value={},
                                 system_values={})
            except ValueError:
                pass

            def serve_file(request, application):
                return request.get_response(application)
            fileapp = FileApp(filename=path)
            return Curry(serve_file, application=fileapp)

        return Curry(HTTPNotFound,
                     comment=request.url[len(request.application_url):])

    def __call__(self, request):
        assetpath = self.assetspec + '/'.join(request.subpath)
        handler = self.get_handler(assetpath, request)
        return handler(request=request)


def real_caller_package():
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

    if package is not None:
        if package.__name__ == '__main__' and hasattr(package, '__package__'):
            package = sys.modules[package.__package__]

    return package


def add_templateview_route(config, assetspec, path):
    newpath = path
    if not path.endswith('/'):
        newpath += '/'
    newpath += '*subpath'
    config.add_route('templview', newpath,
                     view=TemplateDirView(assetspec,
                                          package=real_caller_package()))
