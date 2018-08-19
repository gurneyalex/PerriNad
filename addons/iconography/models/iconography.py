from odoo import models, api, fields, tools
import logging

_logger = logging.getLogger(__name__)


class IconographyOpus(models.Model):
    _name = 'iconography.opus'
    name = fields.Char('name', required=True, help="name of the work")
    conservation_city = fields.Char('City of conservation')
    conservation_place = fields.Char('Place of conservation')
    conservation_reference = fields.Char('Conservation reference')
    date = fields.Char('Date', help="date of realization (approximative)")
    opus_country = fields.Char('Country',
                               help="country where the work was made")
    opus_area = fields.Char('Area / City', help='area where the work was made')
    destination = fields.Char('Destination',
                              help="person for which the work was made")
    author = fields.Char('Author', help="author of the work")
    editor = fields.Char('Edit', help="editor of the work")
    iconography_ids = fields.One2many('iconography.iconography', 'opus_id',
                                      help="iconographies in the work")
    iconography_count = fields.Integer('Iconography count',
                                       compute='_compute_iconography_count')
    century = fields.Integer(compute='_compute_century',
                             store=True, group_operator=None,
                             readonly=True,
                             help="century of creation of the work")

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
        'name', related='opus_id.name', store=True, readonly=True,
        help="name of the work in which the iconography is present"
    )
    title = fields.Char('Title', help="title of the iconography")
    subtitle = fields.Char('Subtitle', help="subtitle of the iconography")
    filename = fields.Char('filename', required=True,
                           help="file name of the image")
    filigrane = fields.Selection(
        [('y', 'Yes'),
         ('n', 'No'),
         ('?', 'Unknown')],
        required=True,
        default='?',
        help="presence of a filigrane in the image file"
    )
    folio = fields.Char('Folio')
    represents = fields.Char('Representation of')
    lang = fields.Char('Lang')
    opus_id = fields.Many2one('iconography.opus', ondelete='cascade')
    zzz = fields.Char(
        'Zzz',
        help="mysterious field only Perrine knows what it is"
    )
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
    conservation_support = fields.Char(
        'Conservation support',
        help="not quite sure what this is, ask Perrine"
    )
    century = fields.Integer(related='opus_id.century',
                             store=True,
                             group_operator=None,
                             readonly=True)
    date = fields.Char(related='opus_id.date',
                       readonly=True)

    @api.depends('tag_ids')
    def _compute_description(self):
        for rec in self:
            rec.description = ' ;\n'.join(rec.mapped('tag_ids.name'))

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
    _order = 'name'

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
