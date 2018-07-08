import os
import os.path as osp
import glob
import logging
import base64
from odoo import models, fields, api
#from odoo.addons.base_import.models.odf_ods_reader import ODSReader
import csv


_logger = logging.getLogger(__name__)


class IconographyImportWizard(models.TransientModel):
    _name = 'iconography.import.wizard'

    name = fields.Char('Base Directory', required=True)

    @api.multi
    def action_import(self):
        filenames = glob.glob(
            osp.join(self.name,
                     '*.csv')
        )
        index = self._build_image_index()
        for filename in filenames:
            self._import(filename, index)

    def _build_image_index(self):
        index = {}
        for dirname, subdirs, filenames in os.walk(self.name):
            for name in filenames:
                if name.lower().split('.')[-1] in ('gif', 'png', 'jpg', 'jpeg'):
                    index[name.lower()] = os.path.join(dirname, name)
        return index
    
    def _import(self, filename, index):
        _logger.info('reading file %s', filename)
        reader = csv.reader(open(filename))
        _logger.info('importing lines')
        for row in reader:
            if row[0] == 'ID':
                continue
            self._handle_row(row, index)

    def _handle_row(self, row, index):
        id = row[0].strip()
        _logger.info('processing row %s', id)
        filename = row[1].strip()
        path = index.get(filename.lower())
        if path is not None:
            data = base64.encodebytes(open(path, 'rb').read())
        else:
            data = False
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
                 'destination': dest,
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
             'color': color_mode.lower() == 'rgb',
             'width': int(width),
             'height': int(height),
             'reso_x': hrez,
             'reso_y': vrez,
             'deco_author': author_deco,
             'image': data
             }
        )