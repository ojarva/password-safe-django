Password safe
=============

Written by Olli Jarva, Sebastién Piquemal, Marja Käpyaho

Installation
------------

* Install Django >= 1.4
* fastcgi script is located under *bin* folder.

In the production environment, the media files (css, js) should be served 
to a directory called *static* in the root of the service. If you change any
static files, do so under *passwords/static* and run

```
python manage.py collectstatic
```

* Initialize database

```
python manage.py syncdb
```

* Change *base_dn* from *passwords/models.py*

License
-------

MIT license. See LICENSE.txt.

Libraries
---------

* picnet: http://www.picnet.com.au/picnet-table-filter.html , licensed under MIT license
* ldapdb: http://opensource.bolloretelecom.eu/projects/django-ldapdb/ , 3-clause BSD license
* bootstrap: http://twitter.github.com/bootstrap/ , Apache license v2.0
* chosen: https://github.com/harvesthq/chosen/ , MIT license


