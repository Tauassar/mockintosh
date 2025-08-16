#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
.. module:: __init__
    :synopsis: module that contains classes that build the configuration objects.
"""

from typing import (
    List,
    Union,
    Dict,
    Any
)

from mockintosh.constants import PYBARS
from mockintosh.config import (
    ConfigAsyncService,
    ConfigActor,
    ConfigConsume,
    ConfigProduce,
    ConfigMultiProduce,
    ConfigDataset,
    ConfigSchema,
    ConfigHeaders,
    ConfigAmqpProperties,
    ConfigResponse,
    ConfigMultiResponse,
    ConfigBody,
    ConfigEndpoint,
    ConfigHttpService,
    ConfigManagement,
    ConfigGlobals,
    ConfigPerformanceProfile,
    ConfigRoot,
    ConfigExternalFilePath
)


class ConfigRootBuilder:

    def build_config_external_file_path(self, data: Union[str, None], service: Any = None) -> Union[ConfigExternalFilePath, None]:
        if data is None:
            return None
        config_external_file_path = ConfigExternalFilePath(path=data)
        return config_external_file_path

    def build_config_schema(self, data: Union[dict, None], service: Any = None) -> Union[ConfigSchema, None]:
        if data is None:
            return None
        config_schema = ConfigSchema(payload=data)
        return config_schema

    def build_config_headers(self, data: Union[dict, None], service: Any = None) -> Union[ConfigHeaders, None]:
        if data is None:
            return None
        config_headers = ConfigHeaders(payload=data)
        return config_headers

    def build_config_amqp_properties(self, data: Union[dict, None]) -> Union[ConfigAmqpProperties, None]:
        if data is None:
            return None
        config_amqp_properties = ConfigAmqpProperties(**data)
        return config_amqp_properties

    def build_config_consume(self, data: Union[dict, None], service: Any = None) -> Union[ConfigConsume, None]:
        if data is None:
            return None
        config_consume = ConfigConsume(
            queue=data['queue'],
            group=data.get('group', None),
            key=data.get('key', None),
            schema=self.build_config_schema(data.get('schema', None), service=service),
            value=data.get('value', None),
            headers=self.build_config_headers(data.get('headers', None), service=service),
            amqp_properties=self.build_config_amqp_properties(data.get('amqpProperties', None)),
            capture=data.get('capture', 1)
        )
        return config_consume

    def build_config_produce(self, data: Union[dict, None], service: Any = None) -> Union[ConfigProduce, None]:
        if data is None:
            return None
        config_produce = ConfigProduce(
            queue=data['queue'],
            value=data['value'],
            create=data.get('create', False),
            tag=data.get('tag', None),
            key=data.get('key', None),
            headers=self.build_config_headers(data.get('headers', None), service=service),
            amqp_properties=self.build_config_amqp_properties(data.get('amqpProperties', None))
        )
        return config_produce

    def build_config_multi_produce(self, data: Union[dict, None], service: Any = None) -> Union[ConfigMultiProduce, None]:
        if data is None:
            return None
        produce_list = []
        for produce in data['produceList']:
            produce_config = self.build_config_produce(produce, service=service)
            if produce_config is not None:
                produce_list.append(produce_config)
        config_multi_produce = ConfigMultiProduce(produce_list=produce_list)
        return config_multi_produce

    def build_config_dataset(self, data: Union[list, str, None], service: Any = None) -> Union[ConfigDataset, None]:
        if data is None:
            return None
        if isinstance(data, str):
            config_dataset = ConfigDataset(payload=data)
        else:
            config_dataset = ConfigDataset(payload=data)
        return config_dataset

    def build_config_actor(self, data: dict, service: Any = None) -> ConfigActor:
        config_actor = ConfigActor(
            name=data.get('name', None),
            dataset=self.build_config_dataset(data.get('dataset', None), service=service),
            produce=self.build_config_multi_produce(data.get('produce', None), service=service) if 'produceList' in data.get('produce', {}) else self.build_config_produce(data.get('produce', None), service=service),
            consume=self.build_config_consume(data.get('consume', None), service=service),
            delay=data.get('delay', None),
            limit=data.get('limit', None),
            multi_payloads_looped=data.get('multiPayloadsLooped', True),
            dataset_looped=data.get('datasetLooped', True)
        )
        return config_actor

    def build_config_async_service(self, data: dict, internal_service_id: Union[int, None] = None) -> ConfigAsyncService:
        config_service = ConfigAsyncService(
            type=data['type'],
            address=data.get('address', None),
            actors=[self.build_config_actor(actor, service=config_service) for actor in data.get('actors', [])],
            name=data.get('name', None),
            ssl=data.get('ssl', False),
            internal_service_id=internal_service_id
        )
        return config_service

    def build_config_response(self, data: dict, service: Any = None) -> ConfigResponse:
        if data is None:
            return ConfigResponse()
        
        response_data = data
        if isinstance(data, str):
            response_data = {'body': data}
        
        config_response = ConfigResponse(
            headers=self.build_config_headers(response_data.get('headers', None), service=service),
            status=response_data.get('status', 200),
            body=response_data.get('body', None),
            use_templating=response_data.get('useTemplating', True),
            templating_engine=response_data.get('templatingEngine', PYBARS),
            tag=response_data.get('tag', None),
            trigger_async_producer=response_data.get('triggerAsyncProducer', None)
        )
        return config_response

    def build_config_multi_response(self, data: Union[list, None], service: Any = None) -> Union[ConfigMultiResponse, None]:
        if data is None:
            return None
        config_multi_response = ConfigMultiResponse(
            payload=[self.build_config_response(response, service=service) if isinstance(response, dict) else response for response in data]
        )
        return config_multi_response

    def build_config_body(self, data: Union[dict, None], service: Any = None) -> Union[ConfigBody, None]:
        if data is None:
            return None
        config_body = ConfigBody(
            schema=self.build_config_schema(data.get('schema', None), service=service),
            text=data.get('text', None),
            graphql_query=data.get('graphqlQuery', None),
            graphql_variables=data.get('graphqlVariables', None),
            urlencoded=data.get('urlencoded', None),
            multipart=data.get('multipart', None)
        )
        return config_body

    def build_config_endpoint(self, endpoint: dict, service: Any = None) -> ConfigEndpoint:
        response = endpoint.get('response', None)
        if isinstance(response, list):
            response = self.build_config_multi_response(response, service=service)
        elif isinstance(response, dict):
            response = self.build_config_response(response, service=service)
        elif response is None:
            response = ConfigResponse()

        return ConfigEndpoint(
            path=endpoint['path'],
            _id=endpoint.get('id', None),
            comment=endpoint.get('comment', None),
            method=endpoint.get('method', 'GET'),
            query_string=endpoint.get('queryString', {}),
            headers=endpoint.get('headers', {}),
            body=self.build_config_body(endpoint.get('body', None), service=service),
            dataset=self.build_config_dataset(endpoint.get('dataset', None), service=service),
            response=response,
            multi_responses_looped=endpoint.get('multiResponsesLooped', True),
            dataset_looped=endpoint.get('datasetLooped', True),
            performance_profile=endpoint.get('performanceProfile', None)
        )

    def build_config_http_service(self, service: dict, internal_service_id: Union[int, None] = None) -> ConfigHttpService:
        oas = self.build_config_external_file_path(service.get('oas', None))
        config_service = ConfigHttpService(
            port=service['port'],
            name=service.get('name', None),
            hostname=service.get('hostname', None),
            ssl=service.get('ssl', False),
            ssl_cert_file=service.get('sslCertFile', None),
            ssl_key_file=service.get('sslKeyFile', None),
            management_root=service.get('managementRoot', None),
            oas=oas,
            endpoints=[],
            performance_profile=service.get('performanceProfile', None),
            fallback_to=service.get('fallbackTo', None),
            internal_service_id=internal_service_id
        )

        config_service.endpoints = [self.build_config_endpoint(endpoint, service=config_service) for endpoint in service.get('endpoints', [])]

        return config_service

    def build_config_management(self, data: dict) -> Union[ConfigManagement, None]:
        config_management = None
        if 'management' in data:
            data_management = data['management']
            config_management = ConfigManagement(
                port=data_management['port'],
                ssl=data_management.get('ssl', False),
                ssl_cert_file=data_management.get('sslCertFile', None),
                ssl_key_file=data_management.get('sslKeyFile', None)
            )
        return config_management

    def build_config_globals(self, data: dict) -> Union[ConfigGlobals, None]:
        config_globals = None
        if 'globals' in data:
            data_globals = data['globals']
            config_globals = ConfigGlobals(
                headers=self.build_config_headers(data_globals),
                performance_profile=data_globals.get('performance_profile', None)
            )
        return config_globals

    def build_config_performance_profile(self, data: dict) -> ConfigPerformanceProfile:
        return ConfigPerformanceProfile(
            ratio=data['ratio'],
            delay=data.get('delay', 0.0),
            faults=data.get('faults', {})
        )

    def build_config_service(self, service: dict, internal_service_id: Union[int, None] = None) -> Union[ConfigHttpService, ConfigAsyncService]:
        _type = service.get('type', 'http')
        if _type == 'http':
            return self.build_config_http_service(service, internal_service_id)
        else:
            return self.build_config_async_service(service, internal_service_id)

    def build_config_root(self, data: dict) -> ConfigRoot:
        config_services = []
        for i, service in enumerate(data['services']):
            config_services.append(self.build_config_service(service, internal_service_id=i))
        config_management = self.build_config_management(data)
        config_templating_engine = data.get('templatingEngine', PYBARS)
        config_globals = self.build_config_globals(data)

        config_performance_profiles = {}
        if 'performanceProfiles' in data:
            config_performance_profiles = {}
            for key, value in data['performanceProfiles'].items():
                config_performance_profiles[key] = self.build_config_performance_profile(value)

        return ConfigRoot(
            services=config_services,
            management=config_management,
            templating_engine=config_templating_engine,
            _globals=config_globals,
            performance_profiles=config_performance_profiles
        )

    def build(self, data: dict) -> ConfigRoot:
        return self.build_config_root(data)
