# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import base64
import uuid
import requests as python_request
from datetime import *
import json
import logging
from urllib import response
import requests

_logger = logging.getLogger(__name__)

noUrl = "https://thumbs.dreamstime.com/b/aucune-ic%C3%B4ne-disponible-d-image-appareil-photo-de-plat-illustration-vecteur-132483141.jpg"

class ELearningCustom(http.Controller):
    def get_image_url(self, res_name, res_id, res_field):
        http.request.cr.execute(
                "SELECT id FROM ir_attachment WHERE name='{}' AND res_id={} AND res_model='{}'".format(
                    res_field, int(res_id), res_name))
        id_attachment1 = http.request.cr.fetchone()
        _logger.error(id_attachment1)
        _logger.error('pmmmm: {}'.format(res_name))
        try:
            http.request.cr.execute("UPDATE ir_attachment SET public=True WHERE id=%d" % (int(id_attachment1[0])))
            url = '/web/content/{}'.format(str(id_attachment1[0]))
        except:
            url = noUrl
        return url
    
    @http.route(['/elearning/create/user'], type='json', methods=['GET', 'POST', 'OPTIONS'], auth='public', csfr=False, cors='*',)
    def create_user(self, **kw):
        data = kw['data']
        # try:
        user_exists = request.env['res.users'].sudo().search([('login', '=', data['email'])])
        if user_exists:
            return {'status': False, 'msg': 'Un utilisateur avec ce login existe déjà.'}
        user = request.env['res.users'].sudo().create({
            'name': data['prenom'] + ' ' + data['nom'],
            'login': data['email'],
            'password': data['password'],
            'email': data['email'],
            'phone': data['number'],
        })
        return {'status': True, 'msg': 'L\'utilisateur a été créé avec succès.'}
        # except Exception as e:
        #     return {'status': False, 'msg': 'Impossible de se connecter au serveur. Veuillez réessayer plus tard.'}

    @http.route('/elearning/login/user', type='json', methods=['GET', 'POST', 'OPTIONS'], auth='public', csfr=False, cors='*')
    def user_login(self, **kwargs):
        login = kwargs.get('login')
        password = kwargs.get('password')
        db = kwargs.get('db')
        try:
            # Verify login credentials
            uid = request.session.authenticate(db, login, password)
            
            if uid is not False:
                # If login is successful, fetch user information
                user = request.env['res.users'].browse(uid)
                
                return {
                    'status': True,
                    # 'message': 'Logged in successfully',
                    'id': user.id,
                    'name': user.name,
                    'login': user.login,
                    'email': user.email,
                    'partner_id': user.partner_id.id,
                    'image': '/web/image?model=res.users&id={}&field=image_1920'.format(user.id)
                    # add more user fields if needed
                }
            else:
                return {
                    'status': False,
                    'msg': 'Login ou mot de passe incorrect, Avez vous un compte ?',
                }
        except Exception as e:
            return {
                'status': False,
                'msg': 'Login ou mot de passe incorrect, avez vous un compte ?',
            }
            
    
    @http.route(['/elearning/get/channel'], type='json', methods=['GET', 'POST', 'OPTIONS'], auth='public', csfr=False, cors='*',)
    def elearning_get_channel(self, **kw):
        response=[]
        domain = []
        # ('user_ids', 'in', [x.id for x in obj.user_ids])
        if kw['channel_id'] != 'all':
            domain = [('id', '=', int(kw['channel_id']))]
        all_channel = request.env['slide.channel'].sudo().search(domain)
        if all_channel: 
            for channel in all_channel:
                tags = []
                slides = []
                for tag in channel.tag_ids:
                    tags.append({
                        'id': tag.id,
                        'name': tag.name,
                        'color': tag.color,
                    })
                # if kw['channel_id'] == 'all':
                for slide in channel.slide_ids:
                    slide_vals = {
                        'id': slide.id,
                        'name': slide.name,
                        'type': slide.slide_type,
                        'active': slide.active,
                        'datas': slide.datas,
                        'date_published': slide.date_published,
                        'html_content': slide.html_content,
                        'dislikes': slide.dislikes,
                        'likes': slide.likes,
                        'external_url': slide.external_url,
                        'url': slide.url,
                    }
                    # if slide.slide_type == 'quiz':
                        
                    slides.append(slide_vals)
                
                is_subscrible = False
                if 'partner_id' in kw:
                    partner_id = kw['partner_id']
                    filtered_mbre = [p for p in channel.partner_ids if p.id == int(partner_id)]
                    if len(filtered_mbre) > 0:
                        is_subscrible = True
     
                response.append({
                    'id': channel.id,
                    'name': channel.name,
                    'description': channel.description,
                    # 'image': self.get_image_url('slide.channel', channel.id, 'image'),
                    'image': '/web/image?model=slide.channel&field=image_1920&id={}'.format(channel.id),
                    'slides': channel.slide_ids,
                    'tags': tags,
                    'slides': slides,
                    'time': channel.total_time,
                    'rating': {
                        'count': channel.rating_count,
                        'stars': channel.rating_avg_stars
                    },
                    'members_count': channel.members_count,
                    'nbr_certi': channel.nbr_certification,
                    'is_subscrible': is_subscrible,
                    'responsable': {
                        'id': channel.user_id.id,
                        'name': channel.user_id.name,
                        'image': '/web/image?model=res.users&field=image_1920&id={}'.format(channel.user_id.id),
                    },
                })
        _logger.error('GOood')
        return response
        
    @http.route(['/elearning/get/user/slides'], type='json', methods=['GET', 'POST', 'OPTIONS'], auth='public', csfr=False, cors='*',)
    def elearning_get_user_slides(self, **kw):
        response=[]
        domain = [('partner_id', '=', int(kw['partner_id']))]
        user_slides = request.env['slide.channel.partner'].sudo().search(domain)
        if user_slides: 
            for slide in user_slides:
                tags = []
                slides = []
                for tag in slide.channel_id.tag_ids:
                    tags.append({
                        'id': tag.id,
                        'name': tag.name,
                        'color': tag.color,
                    })
                
                # for sld in slide.channel_id.slide_ids:
                #     slides.append({
                #         'id': sld.id,
                #         'name': sld.name,
                #         'type': sld.slide_type,
                #         'active': sld.active,
                #         'datas': sld.datas,
                #         'date_published': sld.date_published,
                #         'html_content': sld.html_content,
                #         'dislikes': sld.dislikes,
                #         'likes': sld.likes,
                #         'external_url': sld.external_url,
                #     })
                    
                response.append({
                    'id': slide.id,
                    'create_date': slide.create_date,
                    'partner': {
                        'id': slide.partner_id.id,
                        'name': slide.partner_id.name,
                        'email': slide.partner_email,
                    },
                    'channel_id': slide.channel_id.id,
                    'channel_name': slide.channel_id.name,
                    'channel_responsable': {
                        'id': slide.channel_id.user_id.id,
                        'name': slide.channel_id.user_id.name,
                        'image': '/web/image?model=res.users&field=image_1920&id={}'.format(slide.channel_id.user_id.id),
                    },
                    'channel_description': slide.channel_id.description,
                    'channel_time': slide.channel_id.total_time,
                    # 'image': self.get_image_url('slide.channel', slide.channel_id.id, 'image'),
                    'channel_image': '/web/image?model=slide.channel&field=image_1920&id={}'.format(slide.channel_id.id),
                    'channel_slides': slide.channel_id.slide_ids,
                    'channel_tags': tags,
                    'channel_slides': slides,
                    'status': slide.completed,
                    'percent': slide.completion,
                })
        return response
        
        
    @http.route(['/elearning/get/forum'], type='json', methods=['GET', 'POST', 'OPTIONS'], auth='public', csfr=False, cors='*',)
    def elearning_get_forum(self, **kw):
        response=[]
        # forums = request.env['forum.forum'].sudo().search([('slide_channel_id', '=', int(kw['channel_id']))])
        forums = request.env['forum.forum'].sudo().search([])
        if forums: 
            for forum in forums:
                response.append({
                    'id': forum.id,
                    'total_posts': forum.total_posts,
                    'total_views': forum.total_views,
                    'total_answers': forum.total_answers,
                    'total_favorites': forum.total_favorites,
                    'name': forum.name,
                    'description': forum.description,
                })
        return response
    
    @http.route(['/elearning/get/forum/post'], type='json', methods=['GET', 'POST', 'OPTIONS'], auth='public', csfr=False, cors='*',)
    def elearning_get_forum_post(self, **kw):
        response=[]
        # forums = request.env['forum.forum'].sudo().search([('slide_channel_id', '=', int(kw['channel_id']))])
        forum_posts = request.env['forum.post'].sudo().search([('forum_id', '=', int(kw['forum_id']))])
        
        if forum_posts: 
            for forum_post in forum_posts:
                vals= {
                    'id': forum_post.id,
                    'total_posts': forum_post.total_posts,
                    'views': forum_post.views,
                    'child_count': forum_post.child_count,
                    'favourites_count': forum_post.favourites_count,
                    'name': forum_post.name,
                    'state': forum_post.state,
                    'create_uid': forum_post.create_uid.name,
                    'create_date': forum_post.create_date,
                    'write_uid': forum_post.write_uid.name,
                    'write_date': forum_post.write_date,
                    'parent_id': forum_post.parent_id,
                    'vote_count': forum_post.vote_count,
                }
                if forum_post.parent_id:
                    vals['parent_id'] = forum_post.parent_id.name
                    vals['name'] = forum_post.parent_id.name
                    
                response.append(vals)
        return response

    @http.route(['/elearning/create/forum/post'], type='json', methods=['GET', 'POST', 'OPTIONS'], auth='public', csfr=False, cors='*',)
    def elearning_create_forum_post(self, **kw):
        vals = {
            'name': kw['name'],
            'forum_id': int(kw['forum_id']),
            'user_id': int(kw['create_uid']),
        }
        if kw['parent_id'] != '':
            vals.update({
                'parent_id': int(kw['parent_id']),
            })
        
        request.env['forum.post'].sudo().create(vals)
        return {'status': True, 'msg': 'Message envoyé avec succès.'}
    
    @http.route(['/elearning/get/badges'], type='json', methods=['GET', 'POST', 'OPTIONS'], auth='public', csfr=False, cors='*',)
    def elearning_get_bagdes(self, **kw):
        response=[]
        # forums = request.env['forum.forum'].sudo().search([('slide_channel_id', '=', int(kw['channel_id']))])
        badges = request.env['gamification.badge'].sudo().search([])
        
        if badges: 
            for badge in badges:
                vals= {
                    'id': badge.id,
                    'name': badge.name,
                    'description': badge.description,
                    'granted_users_count': badge.granted_users_count,
                    'stat_my': badge.stat_my,
                    'level': badge.level,
                    'challenge_ids': badge.challenge_ids,
                }
                response.append(vals)
        return response

