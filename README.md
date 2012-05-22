Password safe
=============

Written by Olli Jarva, Sebastién Piquemal, Marja Käpyaho

Installation
------------

* Install Django >= 1.3
* fastcgi script is located in *bin* folder.

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

License
-------

MIT license

Copyright (C) 2010-2012 Futurice Ltd, Olli Jarva, Sebastien Piquemal, 
Marja Käpyaho

Permission is hereby granted, free of charge, to any person obtaining a 
copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the 
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in 
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.

Libraries
---------

* picnet: http://www.picnet.com.au/picnet-table-filter.html , licensed under MIT license
* ldapdb: http://opensource.bolloretelecom.eu/projects/django-ldapdb/ , 3-clause BSD license
* bootstrap: http://twitter.github.com/bootstrap/ , Apache license v2.0
* chosen: https://github.com/harvesthq/chosen/ , MIT license


