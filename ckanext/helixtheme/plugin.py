# -*- coding: utf-8 -*-

import datetime
import copy
import sets
import string

from pylons import config
from ckan.common import request

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.datapreview as datapreview
from ckan import model
from ckan.lib import helpers, munge
from ckan.lib.base import c
from ckan.lib.helpers import render_datetime, resource_preview, url_for_static
from ckan.logic import NotFound

import ckanext.helix.lib.template_helpers as ext_template_helpers


import logging
log1 = logging.getLogger(__name__)


def most_recent_datasets(limit=10):
    datasets = toolkit.get_action('package_search')(
        data_dict={'sort': 'metadata_modified desc', 'rows': limit})

    # Add terms for translation and call get_translation_terms
    #locale = helpers.lang()
    #translated = get_translated_dataset_groups(datasets.get('results'), locale)

    return datasets.get('results')


def get_featured_datasets(limit=4):
    
    group_name = 'featured-datasets'
    try: 
        datasets = toolkit.get_action('group_package_show')(data_dict={'id': group_name})
    except NotFound as ex:
        log1.warn("No featured datasets: group \"%s\" is empty!" % (group_name))
        datasets = []

    # Add terms for translation and call get_translation_terms
    #locale = helpers.lang()
    #translated = get_translated_dataset_groups(datasets.get('results'), locale)

    return datasets

# pluralize


def pluralize(name):
    if name.endswith('y'):
        name = name[:-1] + 'ies'
    elif not name.endswith('s'):
        name = name + 's'
    return name

# remove featured-datasets and other types of groups


def get_topics(package_id):
    dataset = toolkit.get_action('package_show')(
        data_dict={'id': package_id})
    groups = dataset['groups']
    for group in groups:
        temp_group = toolkit.get_action('group_show')(
            data_dict={'id': group['id']})
        if temp_group['type'] != 'group' or temp_group['name'] == 'featured-datasets':
            groups.remove(group)

    return groups

# get communities user is member of


def get_communities(username):
    groups = toolkit.get_action('group_list_authz')(
        data_dict={'am_member': True})
    log1.debug('Groups are: %s', groups)    
    groups_copy = copy.copy(groups)
    delete_indexes = []
    for group in groups_copy:
        log1.debug('Group: %s', group['display_name'])
        temp_group = toolkit.get_action('group_show')(
            data_dict={'id': group['id']})
        users = temp_group['users']
        if temp_group['type'] != 'communities':
            groups.remove(group)
        else:
            members = toolkit.get_action('member_list')(
                data_dict={'id': group['id'], 'object_type': 'user'})
            remove = True
            # check if user is in groups members
            for m in members:
                if username in m:
                    remove = False
                    break
            if remove:
                groups.remove(group)
    return groups


def update_facets():
    facets = OrderedDict()

    default_facet_titles = {
        'organization': _('Organizations'),
        'groups': _('Groups'),
        'tags': _('Tags'),
        'res_format': _('Formats'),
        'license_id': _('Licenses'),
    }

    for facet in h.facets():
        if facet in default_facet_titles:
            facets[facet] = default_facet_titles[facet]
        else:
            facets[facet] = facet
    # Facet titles
    for plugin in p.PluginImplementations(p.IFacets):
        facets = plugin.dataset_facets(facets, package_type)

    c.facet_titles = facets
    data_dict = {
        'q': q,
        'fq': fq.strip(),
        'facet.field': facets.keys(),
        'rows': limit,
        'start': (page - 1) * limit,
        'sort': sort_by,
        'extras': search_extras,
        'include_private': asbool(config.get(
            'ckan.search.default_include_private', True)),
    }

    query = get_action('package_search')(context, data_dict)
    c.sort_by_selected = query['sort']

    c.page = h.Page(
        collection=query['results'],
        page=page,
        url=pager_url,
        item_count=query['count'],
        items_per_page=limit
    )
    c.search_facets = query['search_facets']


def list_menu_items(limit=21):
    groups = toolkit.get_action('group_list')(
        data_dict={'sort': 'name desc', 'all_fields': True})
    groups = groups[:limit]
    c.groups = groups

    return groups


def friendly_date(date_str):
    return render_datetime(date_str, '%d %B %Y')


def get_contact_point(pkg):

    # If there, INSPIRE metadata take precedence
    name = None
    email = None
    if pkg.get('dataset_type') == 'inspire':
        name = pkg.get('inspire.contact.0.organization', '')
        email = pkg.get('inspire.contact.0.email')

    # If not there, use maintainer or organization info

    if not name:
        name = pkg.get('maintainer') or pkg['organization']['title']

    if not email:
        email = pkg.get('maintainer_email') or config.get('email_to')

    return dict(name=name, email=email)


_feedback_form_en = None
_feedback_form_el = None
_maps_url = None
_maps_db = None


def get_maps_db():
    return _maps_db


def feedback_form():
    locale = helpers.lang()
    if locale == 'el':
        return _feedback_form_el
    else:
        return _feedback_form_en


def get_maps_url(package_id=None, resource_id=None):
    locale = helpers.lang()
    if _maps_url:
        if package_id and resource_id:
            return('{0}?package={1}&resource={2}&locale={3}'.format(_maps_url, package_id, resource_id, locale))
        else:
            return('{0}?locale={1}'.format(_maps_url, locale))
    else:
        return '/'


def redirect_wp(page):
    locale = helpers.lang()
    if page:
        # check if page includes a subpage
        splitted = page.split('/')
        if not locale == 'el':
            splitted[0] = '{0}-{1}'.format(splitted[0], locale)
        return('/content/{0}/'.format('/'.join(splitted)))
    else:
        return('/content/')


def friendly_name(name):
    max_chars = 15
    if len(name) > max_chars:
        friendly_name = name.split(" ")[0]
        if len(friendly_name)+3 >= max_chars:
            friendly_name = friendly_name[:max_chars-4] + "..."
    else:
        friendly_name = name

    return friendly_name

#_previewable_formats = ['wms', 'wfs']
# def get_previewable_formats():
#    return _previewable_formats


# Returns the most suitable preview by checking whether ingested resources provide a better preview visualization
def preview_resource_or_ingested(pkg, res):
    snippet = resource_preview(res, pkg)
    data_dict = copy.copy(pkg)
    data_dict.update({'resource': res})

    if not _resource_preview(data_dict):
        raster_resources = ext_template_helpers.get_ingested_raster(pkg, res)
        vector_resources = ext_template_helpers.get_ingested_vector(pkg, res)

        for ing_res in raster_resources:
            # for ing_res in pkg.get('resources'):
            data_dict.update({'resource': ing_res})
            if _resource_preview(data_dict):
                snippet = resource_preview(ing_res, pkg)
                break
        for ing_res in vector_resources:
            data_dict.update({'resource': ing_res})
            if _resource_preview(data_dict):
                snippet = resource_preview(ing_res, pkg)
                break
    return snippet


def can_preview_resource_or_ingested(pkg, res):
    previewable = res.get('can_be_previewed')
    if not previewable:
        raster_resources = ext_template_helpers.get_ingested_raster(pkg, res)
        vector_resources = ext_template_helpers.get_ingested_vector(pkg, res)

        for ing_res in raster_resources:
            # for ing_res in pkg.get('resources'):
            if ing_res.get('can_be_previewed'):
                previewable = True
                break
        for ing_res in vector_resources:
            if ing_res.get('can_be_previewed'):
                previewable = True
                break
    return previewable


def _resource_preview(data_dict):
    return bool(datapreview.res_format(data_dict['resource'])
                in datapreview.direct() + datapreview.loadable()
                or datapreview.get_preview_plugin(
        data_dict, return_first=True))


def get_translated_dataset_groups(datasets):
    desired_lang_code = helpers.lang()
    terms = sets.Set()
    for dataset in datasets:
        groups = dataset.get('groups')
        organization = dataset.get('organization')
        if groups:
            terms.add(groups[0].get('title'))
        if organization:
            terms.add(organization.get('title'))
    # Look up translations for all datasets in one db query.
    translations = toolkit.get_action('term_translation_show')(
        {'model': model},
        {'terms': terms,
            'lang_codes': (desired_lang_code)})

    for dataset in datasets:
        groups = dataset.get('groups')
        organization = dataset.get('organization')
        items = []
        if groups:
            items.append(groups[0])
        if organization:
            items.append(organization)
        for item in items:
            matching_translations = [translation for
                                     translation in translations
                                     if translation['term'] == item.get('title')
                                     and translation['lang_code'] == desired_lang_code]
            if matching_translations:
                assert len(matching_translations) == 1
                item['title'] = (
                    matching_translations[0]['term_translation'])
    return datasets

# Helper function to ask for specific term to be translated


def get_term_translation(term):
    desired_lang_code = helpers.lang()
    translations = toolkit.get_action('term_translation_show')(
        {'model': model},
        {'terms': term,
            'lang_codes': (desired_lang_code)})
    matching_translations = [translation for
                             translation in translations
                             if translation['term'] == term
                             and translation['lang_code'] == desired_lang_code]
    if matching_translations:
        assert len(matching_translations) == 1
        term = (
            matching_translations[0]['term_translation'])
    return term


class HelixthemePlugin(plugins.SingletonPlugin):
    '''Theme plugin for helix.
    '''

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'newest_datasets': most_recent_datasets,
            'featured_datasets': get_featured_datasets,
            'correct_facets': update_facets,
            'list_menu_items': list_menu_items,
            'friendly_date': friendly_date,
            'friendly_name': friendly_name,
            'feedback_form': feedback_form,
            'redirect_wp': redirect_wp,
            'get_maps_url': get_maps_url,
            'preview_resource_or_ingested': preview_resource_or_ingested,
            'can_preview_resource_or_ingested': can_preview_resource_or_ingested,
            'get_translated_dataset_groups': get_translated_dataset_groups,
            'get_term_translation': get_term_translation,
            'pluralize': pluralize,
            'get_topics': get_topics,
            'get_communities': get_communities,
        }

    # IConfigurer

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('public', 'ckanext-helix-theme')

    # IConfigurable

    def configure(self, config):
        '''Pass configuration to plugins and extensions'''
        return

    # IRoutes

    def before_map(self, mapper):
        mapper.connect(
            'dataset_apis', '/dataset/developers/{id}', controller='ckanext.helixtheme.controllers.package:PackageController', action='package_apis')
        
        return mapper

    # IPackageController
    def before_view(self, pkg_dict):
        list_menu_items()
        return pkg_dict

    # IPackageController
    # this has been moved here from ckanext/multilingual MultilingualDataset
    def after_search(self, search_results, search_params):

        # Translte the unselected search facets.
        facets = search_results.get('search_facets')
        if not facets:
            return search_results

        desired_lang_code = request.environ['CKAN_LANG']
        fallback_lang_code = config.get('ckan.locale_default', 'en')

        # Look up translations for all of the facets in one db query.
        terms = sets.Set()
        for facet in facets.values():
            for item in facet['items']:
                terms.add(item['display_name'])
        translations = toolkit.get_action('term_translation_show')(
            {'model': model},
            {'terms': terms,
             # 'lang_codes': (desired_lang_code, fallback_lang_code)})
             'lang_codes': (desired_lang_code)})

        # Replace facet display names with translated ones.
        for facet in facets.values():
            for item in facet['items']:
                matching_translations = [translation for
                                         translation in translations
                                         if translation['term'] == item['display_name']
                                         and translation['lang_code'] == desired_lang_code]
                if not matching_translations:
                    matching_translations = [translation for
                                             translation in translations
                                             if translation['term'] == item['display_name']
                                             and translation['lang_code'] == fallback_lang_code]
                if matching_translations:
                    assert len(matching_translations) == 1
                    item['display_name'] = (
                        matching_translations[0]['term_translation'])

        return search_results
