"""App level forms."""
from flask_wtf import FlaskForm
from wtforms import (
    SubmitField
)

class SiteForm(FlaskForm):
    '''Forms used through the app'''

    see_all_records = SubmitField(
                'See All Records (including inactive)',
                render_kw={
                    'data-span-label':'label-all',
                    'class':
                        'w3-button '
                        'w3-aqua '
                        'w3-round '
                        'w3-hover-aqua '
                        'w3-medium '
                        'w3-show '
                        'active-selector'
                }
            )

    see_active_records = SubmitField(
        'See Active Records Only',
        render_kw={
            'data-span-label':'label-active',
            'class':
                'w3-button '
                'w3-aqua '
                'w3-round '
                'w3-hover-aqua '
                'w3-medium, '
                'w3-hide '
                'active-selector ' 
        }
    )

    cancel_add = SubmitField('Cancel',
        render_kw={
            'class':
                'admin_action '
                'w3-button '
                'w3-orange '
                'w3-round '
                'w3-hover-amber '
                'w3-small '
                'w3-hide '
            }
        )
