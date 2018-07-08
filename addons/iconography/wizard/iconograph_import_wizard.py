import os.path as osp
import glob
from odoo import models, fields, api.multi
from odoo.addons.base_import.models.odf_ods_reader import ODSReader


class IconographyImportWizard(models.TransientModel):
    _name = 'iconography.import.wizard'

    name = fields.Char('Base Directory', required=True)

    @api.multi
    def action_import(self):
        filenames = glob.glob(
            osp.join(self.name,
                     '*.ods')
        )
        for filename in filenames:
            self._import(filename)

    def _import(self, filename):
        reader = ODSReader(filename)
        sheet = reader.getFirstSheet()
        for row in sheet[1:]:
            self._handle_row(row)

    def _handle_row(row):
        id = row[0].strip()
        filename = row[1].strip()
        description = row[5].strip()
        color_mode = row[17].strip()
        hrez = row[18].strip()
        vrez = row[19].strip()
        width = row[20].strip()
        height = row[21].strip()
        filigrane = row[23].strip()
        cons_town = row[25].strip()
        cons_place = row[26].strip()
        cons_reference = row[27].strip()
        folio = row[28].strip()
        name = row[29].strip()
        represents = row[30].strip()
        cons_supp = row[31].strip()
        lang = row[32].strip()
        author = row[33].strip()
        title = row[34].strip()
        date = row[35].strip()
        country = row[36].strip()
        city = row[37].strip()
        author_deco = row[38].strip()
        dest = row[39].strip()
        zzz = row[41].strip()
        editor = row[42].strip()
        location = row[43].strip()
        genre = row[44].strip()
        origin = row[45].strip()
        subtitle = row[46].strip()

        Opus = self.env['iconography.opus']
        Icono = self.env['iconography.iconography']

        opus = Opus.search(
            [('name', '=', title),
             ('author', '=', author),
             ('conservation_city', '=', cons_town),
             ('conservation_place', '=', cons_place),
             ('conservation_support', '=', cons_supp),
             ('editor', '=', editor)]
        )
        if not opus:
            opus = Opus.create(
                {'name': title,
                 'author': author,
                 'conservation_city': cons_town,
                 'conservation_place': cons_place,
                 'conservation_support': cons_supp,
                 'author': author,
                 'opus_country': country,
                 'opus_area': '',
                 'destination': destination,
                 'date': date,
                 'editor': editor,
                 }
            )
        work = Icono.create(
            {'name': title,
             'name_alt': subtitle,
             'filename': filename,
             'filigrane': 'n' if filigrane.startswith('Sans') else ('y' if filigrane.startswith('Avec') else '?'),
             'folio': folio,
             'represents': represents,
             'lang': lang,
             'opus_id': opus.id,
             'zzz': zzz,
             'location': location,
             'genre': genre,
             'origin': origin,
             'description': description,
             'color': color.lower() == 'rgb',
             'width': int(width),
             'height': int(height),
             'reso_x': hrez,
             'reso_y': vrez,
             'deco_author': author_deco,
             }
        )
