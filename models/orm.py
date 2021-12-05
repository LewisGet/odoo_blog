from odoo import api, fields, models


class Orm(models.Model):
    _name = 'orm'
    _description = "get orm"

    @api.model
    def get(self):
        return self._cr
