'''Serices for processing Admin Items'''
import logging

from app.functions import(
    udp_connect
)

from app.settings_cache import get_setting

log = logging.getLogger(__name__)

class QlabService:
    '''Processing Qlab Commands'''

    @staticmethod
    def activate_cue(data):
        '''Trigger (or cancel) qlab cue'''
        output_result = 1
        this_text = "All Cues stopped"
        ip = str(get_setting('qlab_ip'))
        port = int(get_setting('qlab_port'))
        log.warning(ip)
        log.warning(port)
        action = data['action']
        if action == 'fire_qlab_cue':
            cue_number = str(data['cue_number'])
            message = '/cue/'+cue_number+'/start'
            this_text = 'Cue '+cue_number+' has been triggered'
        elif action == 'stop_qlab_cue':
            cue_number = str(data['cue_number'])
            message = '/cue/' + cue_number + '/stop'
            this_text = 'Cue ' + cue_number + ' has been stopped'
        else:
            message = '/'+action
        udp_connect(ip, port, message, 1)
        if action == 'go':
            this_text = 'GO button pressed'
        response =  {
            'text': this_text,
            'result': output_result
        }

        return response


    @staticmethod
    def placeholder():
        '''Keeping pylint happy'''
        message = 'keeping pylint happy'
        return message
