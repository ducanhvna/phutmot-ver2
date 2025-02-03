# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Gokul P I (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models

class ProjectDetails(models.Model):
    _name = 'project.details'
    _description = 'Project Details'

    project_id = fields.Many2one('project.project', string='Project')
    user_id = fields.Many2one('res.users', string='User')
    criteria = fields.Text(string='Criteria')
    evaluation = fields.Text(string='Evaluation')
    goals = fields.Text(string='Goals')
    vision = fields.Text(string='Vision')


class ProjectProject(models.Model):
    """Inherits the project Model for adding new fields and functions"""
    _inherit = "project.project"

    project_details_ids = fields.One2many('project.details', 'project_id', string='Project Details')
    code = fields.Char(string='Mã dự án')
    progressbar = fields.Float(string='Progress Bar',
                               compute='_compute_progress_bar',
                               help='Calculate the progress of the task '
                                    'based on the task stage')
    is_progress_bar = fields.Boolean(string='Is Progress Bar',
                                     help='Status of the task based the '
                                          'stage')
    employee_ids = fields.Many2many('hr.employee',
                                     string='Người tham gia')
    department_id = fields.Many2one('hr.department', string="phòng ban")
    is_daily = fields.Boolean(string="Công việc hằng ngày")

    @api.depends()
    def _compute_progress_bar(self):
        """Compute functionality for the task based on the progress bar"""
        for rec in self:
            progressbar_tasks = rec.task_ids.filtered(
                lambda progress: progress.stage_id.is_progress_stage == True)
            if progressbar_tasks:
                rec.progressbar = (sum(progressbar_tasks.mapped(
                    'progress_bar'))) / len(progressbar_tasks)
            else:
                rec.progressbar = 0


class DailyAdvice(models.Model):
    _name = 'daily.advice'
    _description = 'Daily Advice'

    user_id = fields.Many2one('res.users', string='User')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    project_advice = fields.Text(string='Project Advice')
    hrm_advice = fields.Text(string='Hrm Advice')
