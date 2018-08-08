import os
import os.path as osp
import glob
import logging
import base64
from odoo import models, fields, api, registry
import csv


_logger = logging.getLogger(__name__)


class IconographyImportWizard(models.TransientModel):
    _name = 'iconography.import.wizard'

    def _default_offset(self):
        return self.env['iconography.iconography'].search_count([]) + 1

    name = fields.Char('Base Directory', required=True)
    offset = fields.Integer('Start Row',
                            required=True,
                            default=_default_offset)
    length = fields.Integer('Nb Rows', required=True, default=10000)
    clean = fields.Boolean('Clean before import')

    @api.multi
    def action_import(self):
        filenames = glob.glob(
            osp.join(self.name,
                     '*.csv')
        )
        index = self._build_image_index()
        self._clean()
        for filename in filenames:
            self._import(filename, index)

    def _clean(self):
        if self.clean:
            cr = registry(self._cr.dbname).cursor()
            self = self.with_env(self.env(cr=cr))
            self.env['iconography.opus'].search([]).unlink()
            cr.commit()
            cr.close()

    def _build_image_index(self):
        index = {}
        for dirname, subdirs, filenames in os.walk(self.name):
            for name in filenames:
                extension = name.lower().split('.')[-1]
                if extension in ('gif', 'png', 'jpg', 'jpeg'):
                    index[name.lower()] = os.path.join(dirname, name)
        return index

    def _import(self, filename, index):
        _logger.info('reading file %s', filename)
        reader = csv.reader(open(filename))
        _logger.info('importing lines')
        cr = registry(self._cr.dbname).cursor()
        self = self.with_env(self.env(cr=cr))
        for num, row in enumerate(reader):
            if row[0] == 'ID':
                continue
            if num < self.offset:
                continue
            if num >= self.offset + self.length:
                break
            self._handle_row(row, index)
            if num % 100 == 0:
                self._cr.commit()
                _logger.info('COMMIT')
        self._cr.commit()
        self._cr.close()

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
        title = row[29].strip()
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
             ('editor', '=', editor)]
        )
        if not opus:
            opus = Opus.create(
                {'name': title,
                 'author': author,
                 'conservation_city': cons_town,
                 'conservation_place': cons_place,
                 'conservation_reference': cons_reference,
                 'author': author,
                 'opus_country': country,
                 'opus_area': city,
                 'destination': dest,
                 'date': date,
                 'editor': editor,
                 }
            )
        Icono.create(
            {'title': title,
             'subtitle': subtitle,
             'filename': filename,
             'filigrane': ('n' if filigrane.startswith('Sans')
                           else ('y' if filigrane.startswith('Avec')
                                 else '?')
                           ),
             'conservation_support': cons_supp,
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
