try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = 'MovieManager',
    version = '0.2',
    description = 'Automatic NZB downloader',
    author = 'Ruud Burger',
    author_email = 'ruud@crashdummy.nl',
    url = 'http://github.com/RuudBurger/Movie-Manager',
    install_requires = [
        "Pylons>=1.0",
        "SQLAlchemy>=0.5",
        "IMDbPY"
    ],
    setup_requires = ["PasteScript>=1.6.3"],
    packages = find_packages(exclude = ['ez_setup']),
    include_package_data = True,
    test_suite = 'nose.collector',
    package_data = {'moviemanager': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'moviemanager': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    zip_safe = False,
    paster_plugins = ['PasteScript', 'Pylons'],
    entry_points = """
    [paste.app_factory]
    main = moviemanager.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    
    """,
)
