#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>           
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

import time
from osv import fields, osv
from tools.translate import _

class project_task(osv.osv):
    _inherit = 'project.task'
    
    def _get_issue(self, cr, uid, ids, fieldname, arg, context=None):
        print 'CAMBIO LA TAREA EN EL ISSUE'
        if context is None: context = {}
        res = {}
        pi_obj = self.pool.get('project.issue')
        
        for id in ids:
            pi_ids = pi_obj.search(cr, uid, [('task_id','=',id)]) or []
            res[id] = pi_ids and pi_ids[0] or None
            
        return res

    def _get_task_in_issue(self, cr, uid, ids, context=None):
        if context is None: context = {}
        pi_obj = self.pool.get('project.issue')
        return [pi_brw.task_id.id for pi_brw in pi_obj.browse(cr, uid, ids, context=context) if pi_brw.task_id]
        

    _columns = {
        'issue_id':fields.function(
            _get_issue,
            method = True,
            type = 'many2one',
            relation='project.issue',
            string = 'Project issue',
            store = {
                'project.issue':(_get_task_in_issue,['task_id'],15),
                'project.task':(lambda self, cr, uid, ids,c={}: ids,[],45),
                }),
    }
project_task()

class project_task_work(osv.osv):
    _inherit = 'project.task.work'

    def _get_project(self, cr, uid, ids, fieldname, arg, context=None):
        if context is None: context = {}
        res = {}
        for ptw_brw in self.browse(cr, uid, ids, context=context):
            
            res[ptw_brw.id] = ptw_brw.task_id and ptw_brw.task_id.issue_id and ptw_brw.task_id.issue_id.project_id and ptw_brw.task_id.issue_id.project_id.id or None 
            
        return res

    def _get_issue(self, cr, uid, ids, fieldname, arg, context=None):
        if context is None: context = {}
        res = {}
        pi_obj = self.pool.get('project.issue')
        ptw_brws = self.browse(cr, uid, ids, context=context)
        for ptw_brw in ptw_brws:
            pi_ids = ptw_brw.task_id and pi_obj.search(cr, uid, [('task_id','=',ptw_brw.task_id.id)]) or []
            
            res[ptw_brw.id] = pi_ids and pi_ids[0] or None
        return res

    def _get_work_in_task(self, cr, uid, ids, context=None):
        print 'ENTRO A BUSCAR A TRABAJO EN TAREAS'
        if context is None: context = {}
        res=[]
        pt_obj = self.pool.get('project.task')
        for pt_brw in pt_obj.browse(cr, uid, ids, context=context):
            res+=[work_brw.id for work_brw in pt_brw.work_ids]
        return list(set(res))
        
    def _get_work_in_issue(self, cr, uid, ids, context=None):
        print 'ENTRO A BUSCAR TRABAJOS EN  EL ISSUE'
        if context is None: context = {}
        res=[]
        pi_obj = self.pool.get('project.issue')
        pt_ids = [pi_brw.task_id.id for pi_brw in pi_obj.browse(cr, uid, ids, context=context) if pi_brw.task_id]
        return self.pool.get('project.task.work')._get_work_in_task(cr, uid, pt_ids, context=context)


    _columns = {
        'project_id':fields.function(
            _get_project,
            method = True,
            type = 'many2one',
            relation='project.project',
            string = 'Project',
            store = {
                'project.issue':(_get_work_in_issue,['task_id','project_id'],15),
                'project.task.work':(lambda self, cr, uid, ids,c={}: ids,[],45),
                }),
        'state':fields.selection([  ('done','Collected'),
                                    ('draft', 'Uncollected'),
                                    ('cancel', 'Cancel'),], 
                                    readonly = False, 
                                    required = True, 
                                    string = 'State'),
        'issue_id':fields.function(
            _get_issue,
            method = True,
            type = 'many2one',
            relation='project.issue',
            string = 'Project Issue',
            store = {
                #~ 'project.issue':(_get_work_in_issue,['task_id','project_id'],15),
                'project.task':(_get_work_in_task,[],30),
                'project.task.work':(lambda self, cr, uid, ids,c={}: ids,[],45),
                }),
        'partner_id':fields.related(
            'issue_id',
            'partner_id',
            type='many2one',
            relation='res.partner',
            readonly=True,
            store = True,
            string = 'Partner',
        ),
    }
    
    _defaults = {
        'state': 'draft',
    }
    
project_task_work()
