'''Serices for processing Admin Items'''
import logging
from flask import(
    abort
)

from app.settings_cache import get_setting

from app.etcconnect.repositories.etcconnect_repositories import (
    ETCConnectRepository
)

from app.functions import(
    udp_connect
)

log = logging.getLogger(__name__)

class ETCConnectService:

    '''Managing ETC API commands.'''
    # These might belong in ETC area
    # but it's really more of an admin task.

    @staticmethod
    def list_all():
        '''Get list of ETC API commands'''
        return ETCConnectRepository.list_all()

    @staticmethod
    def add_command(data):
        '''Add a new command'''
        new_command_id = ETCConnectRepository.add_command(data)
        return {'index_id':new_command_id}

    @staticmethod
    def update_command(data):
        '''Update command info'''
        return ETCConnectRepository.update_command(data)


    @staticmethod
    def fire_cue_rest(remote_ip, api_key, data):
        '''Fire a lighting cue coming over the REST Api.'''
        etc_api_client_ip = get_setting('etc_api_client_ip')
        etc_api_key = get_setting('etc_api_key')

        response = {}

        if remote_ip != str(etc_api_client_ip):
            log.warning("Unauthorized access attempt from IP %s", remote_ip)
            abort(403)

        if api_key != str(etc_api_key):
            log.warning("Unauthorized access attempt with API key")
            abort(403)


        if data and 'command' in data:
            etc_ip = str(get_setting('etc_ip'))
            etc_port = int(get_setting('etc_port'))
            command = data['command']
            command_parameters = ETCConnectRepository.get_etc_api_command(command)
            if command_parameters:
                message = '/eos'
                param1 = command_parameters.get('parameter_1')
                param2 = command_parameters.get('parameter_2')
                param3 = command_parameters.get('parameter_3')
                if param1:
                    message += '/' + param1
                if param2:
                    message += '/' + param2

                udp_connect(etc_ip, etc_port, message, param3)
            log.warning("Command trigger: %s from %s to %s", command, remote_ip, etc_ip)

            response =  {
                'text': "Cue fired via REST endpoint with command: " + command,
                'result': 1
            }

        return response


    @staticmethod
    def set_level(data):
        '''Get the value of a specific setting'''
        ip = str(get_setting('etc_ip'))
        port = int(get_setting('etc_port'))

        mode = data['mode']
        target = str(data['target'])
        level = str(data['level'])

        mode_code = ''
        return_text = ''

        if mode == 'channel':
            mode_code = 'chan'
            return_text = 'Channel ' + target +' is @ '+ level
        elif mode == 'address':
            mode_code = 'addr'
            return_text = 'Address ' + target +' is @ '+ level
        elif mode == 'cue':
            mode_code = mode
            return_text = 'Cue ' + level + ' is active'

        message = "/eos/"+ mode_code + "/" + target + "/"

        udp_connect(ip, port, message, level)

        etc_result = 1

        return {
            'text': return_text,
            'result': etc_result
            }
