from app.core.config import settings
from app.integrations.ati_su.mock import MockAtiSuProvider


def get_ati_provider():
    if settings.provider_mode == "mock":
        return MockAtiSuProvider(mode=settings.mock_mode)

    raise NotImplementedError("Real ATI provider not implemented yet")