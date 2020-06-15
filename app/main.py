from typing import List

import uvicorn  # for debug
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Field, AnyHttpUrl

router = APIRouter()

fake_db = [
    {
        "version_id": "1.0",
        "detailed_version": "https://github.com/BuildingSMART/BCF-API"
    },
    {
        "version_id": "2.1",
        "detailed_version": "https://github.com/BuildingSMART/BCF-API"
    }
]


##########
# 3.1 Versions Service
##########

class Version(BaseModel):
    version_id: str = Field(description='Identifier of the version')
    # None because required = false
    detailed_version: AnyHttpUrl = Field(None, description='Url to specification on GitHub')

    class Config:
        schema_extra = {
            "example":
                {
                    "version_id": "1.0",
                    "detailed_version": "https://github.com/BuildingSMART/BCF-API",
                }
        }


class Versions(BaseModel):
    versions: List[Version]

    class Config:
        schema_extra = {
            "example":
                {"versions": [{
                    "version_id": "1.0",
                    "detailed_version": "https://github.com/BuildingSMART/BCF-API",
                }, {
                    "version_id": "2.1",
                    "detailed_version": "https://github.com/BuildingSMART/BCF-API",
                }]}
        }


@router.get(
    "/versions",
    response_model=Versions,
    description="Returns a list of all supported BCF API versions of the server.",
    tags=["Public Services"]
)
async def get_versions():
    versions = [Version(**item) for item in fake_db]
    return Versions(versions=versions)


##########
# 3.2 Authentication Services
# 3.2.1 Obtaining Authentication Information
##########

class AuthenticationInGet(BaseModel):
    oauth2_auth_url: AnyHttpUrl = Field(None, description="URL to authorization page (used for Authorization Code "
                                                          "Grant and Implicit Grant OAuth2 flows)")
    oauth2_token_url: AnyHttpUrl = Field(None, description="URL for token requests")
    oauth2_dynamic_client_reg_url: AnyHttpUrl = Field(None, description="URL for automated client registration")
    http_basic_supported: bool = Field(None, description="Indicates if Http Basic Authentication is supported")
    supported_oauth2_flows: List[str] = Field(None, description="array of supported OAuth2 flows")

    class Config:
        schema_extra = {
            "example":
                {
                    "oauth2_auth_url": "https://example.com/bcf/oauth2/auth",
                    "oauth2_token_url": "https://example.com/bcf/oauth2/token",
                    "oauth2_dynamic_client_reg_url": "https://example.com/bcf/oauth2/reg",
                    "http_basic_supported": True,
                    "supported_oauth2_flows": [
                        "authorization_code_grant",
                        "implicit_grant",
                        "resource_owner_password_credentials_grant"
                    ]
                }
        }


@router.get(
    "/{version}/auth",
    response_model=AuthenticationInGet,
    tags=["Public Services"]
)
async def get_auth():
    """
    If oauth2_auth_url is present, then oauth2_token_url must also be present and vice versa.
    If properties are not present in the response, clients should assume that the functionality is not supported by
    the server, e.g. a missing http_basic_supported property would indicate that Http basic authentication
    is not available on the server.

    OAuth2 flows are described in detail in the [OAuth2 specification](https://tools.ietf.org/html/rfc6749).
    BCF API servers may support the following workflows:
    
    - **authorization_code_grant** - [4.1 - Authorization Code Grant](https://tools.ietf.org/html/rfc6749#section-4.1)  
    - **implicit_grant** - [4.2 - Implicit Grant](https://tools.ietf.org/html/rfc6749#section-4.2)  
    - **resource_owner_password_credentials_grant** - [4.3 - Resource Owner Password 
    Credentials Grant](https://tools.ietf.org/html/rfc6749#section-4.3)
    
    The [OAuth2 Client Credentials Grant (section 4.4)](https://tools.ietf.org/html/rfc6749#section-4.4)
    is not supported since it does not contain any user identity. Also the [Extension Grants (section 
    4.5)](https://tools.ietf.org/html/rfc6749#section-4.5) are not supported.
    """
    return AuthenticationInGet.Config.schema_extra['example']


app = FastAPI(
    title='BCF REST API',
    description='BCF is a format for managing issues on a BIM project. The BCF-API supports the exchange of BCF issues '
                'between software applications via a RESTful web interface, which means ...',
    version='2.1',
)
app.include_router(router, prefix='/bcf')

# for debug:
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
