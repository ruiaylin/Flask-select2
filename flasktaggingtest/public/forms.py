# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import SelectMultipleField


class TagDBForm(Form):
    tags_field = SelectMultipleField(
        label='Tags',
        choices=[
            ('MySQL', 'MySQL'),
            ('SQLServer', 'SQLServer'),
            ('percona', 'percona'),
            ('mariadb', 'mariadb'),
            ('pg', 'pg'),
            ('db2', 'db2'),
        ])


class TaggingForm(Form):
    tags_field = SelectMultipleField(
        label='Tags')
