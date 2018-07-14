from odoo import models, api, fields, tools
import logging

_logger = logging.getLogger(__name__)


class IconographyOpus(models.Model):
    _name = 'iconography.opus'
    name = fields.Char('name', required=True)
    conservation_city = fields.Char('City of conservation')
    conservation_place = fields.Char('Place of conservation')
    conservation_reference = fields.Char('Conservation reference')
    date = fields.Char('Date')
    opus_country = fields.Char('Country')
    opus_area = fields.Char('Area / City')
    destination = fields.Char('Destination')
    author = fields.Char('Author')
    editor = fields.Char('Edit')
    iconography_ids = fields.One2many('iconography.iconography', 'opus_id')
    iconography_count = fields.Integer('Iconography count',
                                       compute='_compute_iconography_count')
    century = fields.Integer(compute='_compute_century',
                             store=True,
                             readonly=True)

    @api.depends('date')
    def _compute_century(self):
        for rec in self:
            date = rec.date.strip()
            if not date:
                rec.century = -1
                continue
            date += ' '
            try:
                century = int(date.replace('(', ' (').split()[0])
                rec.century = century
            except ValueError:
                if date.lower() == "gallo romain":
                    rec.century = 0
                elif date.lower() == "romain":
                    rec.century = 0

    def _compute_iconography_count(self):
        for rec in self:
            rec.iconography_count = len(rec.iconography_ids)

    def action_view_iconography(self):
        action = self.env.ref('iconography.action_view_iconography').read()[0]
        action['domain'] = [('opus_id', 'in', self.ids)]
        return action


class IconographyDocument(models.Model):
    _name = 'iconography.iconography'

    name = fields.Char(
        'name', related='opus_id.name', store=True, readonly=True
    )
    title = fields.Char('Title')
    subtitle = fields.Char('Subtitle')
    filename = fields.Char('filename', required=True)
    filigrane = fields.Selection([('y', 'Yes'),
                                  ('n', 'No'),
                                  ('?', 'Unknown')],
                                 required=True,
                                 default='?')
    folio = fields.Char('Folio')
    represents = fields.Char('Representation of')
    lang = fields.Char('Lang')
    opus_id = fields.Many2one('iconography.opus', ondelete='cascade')
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
    image_small = fields.Binary(
        "Small-sized image",
        compute='_compute_images',
        store=True,
        attachment=False)
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
    conservation_support = fields.Char('Conservation support')
    century = fields.Integer(related='opus_id.century',
                             store=True,
                             readonly=True)

    @api.depends('tag_ids')
    def _compute_description(self):
        for rec in self:
            rec.description = ' ; '.join(rec.mapped('tag_ids.name'))

    @api.one
    @api.depends('image')
    def _compute_images(self):
        try:
            resized_images = tools.image_get_resized_images(
                self.image,
                return_big=False,
                return_medium=False,
            )
        except Exception:
            _logger.exception('Error while resizing image')
            self.image_small = False
        else:
            self.image_small = resized_images['image_small']

    def _set_description(self):
        Tag = self.env['iconography.tag']
        for rec in self:
            tags = [t.strip() for t in rec.description.split(';')]
            rec_tags = self.env['iconography.tag']
            for tagname in tags:
                tag = Tag.search([('name', '=', tagname)])
                if not tag:
                    tag = Tag.create({'name': tagname})
                rec_tags += tag
            rec.tag_ids = rec_tags


class IconographyTag(models.Model):
    _name = 'iconography.tag'

    name = fields.Char('name', required=True, indexed=True)
    iconography_ids = fields.Many2many('iconography.iconography')
    iconography_count = fields.Integer('Iconography count',
                                       compute='_compute_iconography_count')

    def _compute_iconography_count(self):
        for rec in self:
            rec.iconography_count = len(rec.iconography_ids)

    def action_view_iconography(self):
        action = self.env.ref('iconography.action_view_iconography').read()[0]
        action['domain'] = [('tag_ids', 'in', self.ids)]
        return action
