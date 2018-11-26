=============
ckanext-helixtheme
=============

Ckan theming plugin to work alongside `ckanext-helix` extension.


------------
Prerequisites
------------

1. Create a group named `featured-datasets`    


------------
Installation
------------


To install ckanext-helixtheme:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-helixtheme Python package into your virtual environment::

     pip install ckanext-helixtheme

3. Add ``helixtheme`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


