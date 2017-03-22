# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.base.res.res_request import referenceable_models
from odoo.exceptions import ValidationError

class Tag(models.Model):
    _name = 'todo.task.tag'
    _description = 'To-do Tag'
    _parent_store = True
    name = fields.Char(string='Name', size=40, translate=True)
    # Tag class relationship to Tasks:
    task_ids = fields.Many2many(comodel_name='todo.task', string='Tasks')
    
    # _parent_name = 'parent_id'
    parent_id = fields.Many2one(comodel_name='todo.task.tag', string='Parent Tag', ondelete='restrict')
    parent_left = fields.Integer('Parent Left', index=True)
    parent_right = fields.Integer('Parent Right', index=True)
    child_ids = fields.One2many(comodel_name='todo.task.tag', inverse_name='parent_id', string='Child Tags')
    
class Stage(models.Model):
    _name = 'todo.task.stage'
    _description = 'To-do Stage'
    _order = 'sequence,name'
    sequence = fields.Integer('Sequence')# String fields: 
    name = fields.Char('Name', size=40, translate=True)
    desc = fields.Text('Description') 
    state = fields.Selection([
        ('draft','New'), 
        ('open','Started'), 
        ('done','Closed'),
        ],'State') 
    docs = fields.Html('Documentation') 
    # Numeric fields: 
    sequence = fields.Integer('Sequence') 
    perc_complete = fields.Float('% Complete', (3, 2)) 
    # Date fields: 
    date_effective = fields.Date('Effective Date') 
    date_changed = fields.Datetime('Last Changed') 
    # Other fields: 
    fold = fields.Boolean('Folded?') 
    image = fields.Binary('Image')
    # Stage class relationship with Tasks:
    tasks = fields.One2many(comodel_name='todo.task', inverse_name='stage_id', string='Tasks in this stage')

class TodoTask(models.Model):
    _inherit = 'todo.task'
    
    stage_id = fields.Many2one(comodel_name='todo.task.stage', string='Stage')
    tag_ids = fields.Many2many(comodel_name='todo.task.tag', string='Tags')
    
    refers_to = fields.Reference(
        selection=referenceable_models,
        string='Refers to')
        
    stage_fold = fields.Boolean(
        'Stage Folded?',
        compute='_compute_stage_fold',
        # store=False,  # the default
        search='_search_stage_fold',
        inverse='_write_stage_fold')
        
    @api.depends('stage_id.fold')
    def _compute_stage_fold(self):
        for task in self:
            task.stage_fold = task.stage_id.fold
            
    def _search_stage_fold(self, operator, value):
        return [('stage_id.fold', operator, value)]

    def _write_stage_fold(self):
        self.stage_id.fold = self.stage_fold

    stage_state = fields.Selection(
        related='stage_id.state',
        string='Stage State')
        
    _sql_constraints = [ 
        ('todo_task_name_uniq', 
         'UNIQUE (name, active)', 
         'Task title must be unique!'),]
         
    @api.constrains('name')
    def _check_name_size(self):
        for todo in self:
            if len(todo.name) < 5:
                raise ValidationError('Must have 5 chars!')