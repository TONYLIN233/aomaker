import pytest
from fastapi.dependencies.utils import request_body_to_args

from aomaker.storage import cache
from mockapitest.apis.mock2.auth.apis import LoginForAccessTokenApiLoginTokenPostAPI
from attrs import define, field
from aomaker.core.router import router
from aomaker.core.api_object import BaseAPIObject

