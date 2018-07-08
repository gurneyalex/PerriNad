from odoo import models, api, fields


class IconographyDocument(models.Model):
    _name = 'iconography.iconography'

    name = fields.Char('name', related='opus_id.name', store=True)
    name_alt = fields.Char('Subtitle')
    filename = fields.Char('filename', required=True)
    filigrane = fields.Selection([('y', 'Yes'), ('n', 'No'), ('?', 'Unknown')], required=True, default='?')
    folio = fields.Char('Folio')
    represents = fields.Char('Representation of')
    lang = fields.Char('Lang')
    opus_id = fields.Many2one('iconography.opus')
    zzz = fields.Char('Zzz')
    location = fields.Char('Location')
    genre = fields.Char('Genre')
    origin = fields.Char('Origin')
    description = fields.Text(
        'Description',
        compute='_compute_description',
        inverse='_set_description'
    )
    image = fields.Binary('Image', attachment=True)
    color = fields.Boolean('Color')
    width = fields.Integer('Width')
    height = fields.Integer('Height')
    reso_x = fields.Integer('Horizontal resolution')
    reso_y = fields.Integer('Vertical resolution')
    deco_author = fields.Char('Decorator')
    opus_author = fields.Char(
        related="opus_id.author", readonly=True, store=True,
    )
    tag_ids = fields.Many2many('iconography.tag', string='Tags')

    @api.depends('tag_ids')
    def _compute_description(self):
        for rec in self:
            rec.description = ','.join(rec.mapped('tag_ids.name'))

    def _set_description(self):
        Tag = self.env['iconography.tag']
        for rec in self:
            tags = rec.description.split(',')
            rec_tags = self.env['iconography.tag']
            for tagname in tags:
                tagname = tagname.strip()
                tag = Tag.search([('name', '=', tagname)])
                if not tag:
                    tag = Tag.create({'name': tagname})
                rec_tags += tag
            rec.tag_ids = rec_tags


class IconographyTag(models.Model):
    _name = 'iconography.tag'

    name = fields.Char('name', required=True, indexed=True)
    iconography_ids = fields.Many2many('iconography.iconography')
    iconography_count = fields.Integer('Iconography count', compute='_compute_iconography_count')

    def _compute_iconography_count(self):
        for rec in self:
            rec.iconography_count = len(rec.iconography_ids)

    def action_view_iconography(self):
        action = self.env.ref('iconography.action.view_iconography').read()[0]
        action['domain'] = [('tag_ids', 'in', self.ids)]
        return action

class IconographyOpus(models.Model):
    _name = 'iconography.opus'
    name = fields.Char('name', required=True)
    conservation_city = fields.Char('City of conservation')
    conservation_place = fields.Char('Place of conservation')
    conservation_reference = fields.Char('Conservation reference')
    conservation_support = fields.Char('Conservation support')
    date = fields.Char('Date')
    opus_country = fields.Char('Country')
    opus_area = fields.Char('Area / City')
    destination = fields.Char('Destination')
    author = fields.Char('Author')
    editor = fields.Char('Edit')
    iconography_ids = fields.One2many('iconography.iconography', 'opus_id')
    iconography_count = fields.Integer('Iconography count', compute='_compute_iconography_count')


    def _compute_iconography_count(self):
        for rec in self:
            rec.iconography_count = len(rec.iconography_ids)

    def action_view_iconography(self):
        action = self.env.ref('iconography.action.view_iconography').read()[0]
        action['domain'] = [('opus_id', 'in', self.ids)]
        return action
