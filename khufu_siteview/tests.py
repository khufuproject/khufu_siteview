import unittest


class MainTests(unittest.TestCase):

    def test_includeme(self):
        from khufu_siteview import includeme
        config = MockConfigurator()
        includeme(config)
        self.assertEqual(config.includes,
                         ['pyramid_jinja2'])
        self.assertEqual(config.directives.keys(),
                         ['add_templateview_route'])


class DirListerTests(unittest.TestCase):

    def setUp(self):
        from khufu_siteview.templatedir import DirLister
        self.lister = DirLister()

    def test_is_valid_file(self):
        self.assertTrue(self.lister.is_valid_file('foobar'))
        self.assertFalse(self.lister.is_valid_file('foobar~'))

    def test_listdir(self):
        self.lister.root_listdir = lambda x: ['abc', 'def', 'ghi~']
        self.assertEqual(self.lister.listdir(''), ['abc', 'def'])


class CurryTests(unittest.TestCase):

    def test_it(self):
        from khufu_siteview.templatedir import Curry

        def foo(x, y, z):
            return [x, y, z]
        c = Curry(foo, 10)
        self.assertEqual(c(20, 30), [10, 20, 30])


class TemplateDirViewTests(unittest.TestCase):

    def setUp(self):
        from khufu_siteview.templatedir import TemplateDirView

        self.existsflag = True
        self.dircontents = ['abc', 'def']

        class TestableTemplateDirView(TemplateDirView):
            test = self
            lister = Mock(listdir=lambda x: self.dircontents)

            def dir_exists(self, x):
                return self.test.existsflag

        self.makedirview = TestableTemplateDirView

    def test_baddir(self):
        self.existsflag = False
        self.assertRaises(ValueError, self.makedirview, '', 'sys')

    def test_it(self):
        import khufu_siteview
        view = self.makedirview('', khufu_siteview)
        self.assertEqual(view.assetspec, 'khufu_siteview:/')

    def test_render_listing(self):
        view = self.makedirview('', 'khufu_siteview')
        self.assertRaises(ValueError, view.render_listing,
                          Mock(application_url='foo',
                               url='foo/bar'), None)

    def test_find_index(self):
        view = self.makedirview('', 'khufu_siteview')
        self.assertEqual(view.find_index('foo'), None)
        self.dircontents.append('index.html')
        self.assertEqual(view.find_index('foo'), 'foo/index.html')

    def test_get_handler(self):
        from khufu_siteview.templatedir import Curry
        view = self.makedirview('', 'khufu_siteview')
        x = view.get_handler('foobar.jinja2', Mock(
                url='http://localhost/foo/hello/',
                application_url='http://localhost/foo/'))
        self.assertTrue(isinstance(x, Curry))
        x = view.get_handler('foobar.jinja2', Mock(
                url='http://localhost/foo/hello/',
                application_url='http://localhost/foo/'))
        self.assertTrue(isinstance(x, Curry))


class MockConfigurator(object):
    def __init__(self):
        self.includes = []
        self.directives = {}

    def include(self, s):
        self.includes.append(s)

    def add_directive(self, s, cb):
        self.directives[s] = cb


class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
