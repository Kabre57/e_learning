# -*- coding: utf-8 -*-

import errno
from odoo import http, SUPERUSER_ID, _
from odoo.http import request, route
from odoo.addons.website.controllers.main import Website
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo import api, fields, models, _


import logging
_logger = logging.getLogger(__name__)

class ElearningCustomWebsite(Website):
    
    @http.route(website=True, auth="public")

    def web_login(self, redirect=None, *args, **kw):

        response = super(ElearningCustomWebsite, self).web_login(redirect=redirect, *args, **kw)

        if not redirect and request.params['login_success']:

            
            if request.env['res.users'].browse(request.uid).has_group('e_learning_custom.group_bcpi_user'):
                redirect = '/slides'
                
            elif request.env['res.users'].browse(request.uid).has_group('base.group_user'):

                redirect = b'/web?' + request.httprequest.query_string

            else:
                redirect = f'/profile/user/{request.uid}'

            return http.redirect_with_hash(redirect)

        return response
    

class ElearningCustomPortal(CustomerPortal):
    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        redirect = f'/profile/user/{request.uid}'
        return http.redirect_with_hash(redirect)
