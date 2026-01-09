#Services
from common.error_messages import *
from repositories.nota_avulsa_repository import EmpresaRepository, NotaEntradaRepository, AnaliseNotaMessageRepository
from enums.default_return_messages import *
from common.custom_exception import CustomException
from models.schema_nota_avulsa import *
import xml.etree.ElementTree as ET
import re
from sqlalchemy import text
import base64
#Libs
from flask import jsonify, Response
import requests
import os


URL_NOTA_AVULSA = os.getenv('URL_NOTA_AVULSA')

class IntegrationApiService():
    def __init__(self, db_session):
        self.session = db_session
        self.empresa_repository = EmpresaRepository(db_session)
        self.nota_repository = NotaEntradaRepository(db_session)
        self.analise_nota_message = AnaliseNotaMessageRepository(db_session)

    def get_namespace(self, tag):
        m = re.match(r'\{.*\}', tag)
        return m.group(0) if m else ''

    def get_tag_text_first_or_default(self,
                                      root,
                                      tag_name,
                                      default_returned_value=None):
        for x in root.iter():
            namespace = self.get_namespace(x.tag)
            if x.tag == (namespace + tag_name):
                return x.text
        return default_returned_value

    def parse_xml_str(self, nota):
        root = ET.fromstring(nota)
        return root
    
    def create_nota(self, cnpjEmpresa, arquivoXml, tipoNota):

        empresa = self.empresa_repository.empresa(cnpjEmpresa)
        xml = base64.b64decode(arquivoXml).decode("utf-8")
        root = self.parse_xml_str(xml)
        chave = self.get_tag_text_first_or_default(root, 'chNFe')

        # Dados da requisição
        payload = {
            "arquivoXml": arquivoXml,
            "cnpjEmpresa": cnpjEmpresa,  
            "idEmpresa": empresa.id,  
            "tipoNota": tipoNota
        }

        # Cabeçalhos, se necessários
        headers = {
            'Content-Type': 'application/json',
            }  

        # Enviando a requisição POST
        try:
            response = requests.post(f'{URL_NOTA_AVULSA}/api/v1/notas-entrada/uploadNota', json=payload, headers=headers)
            if response.status_code != 200:
                raise CustomException('fail', 400)
            nota = self.nota_repository.get_first_mf([NotaEntrada.chave == chave])
            procedure = self.session.execute(text(f'CALL mtw_analise."analise_nota"({nota.id_nota_entrada});'))
            response = self.analise_nota_message.get_analisys(nota.id_nota_entrada)
            return jsonify(response)

        except Exception as err:
            raise CustomException('fail', 400)