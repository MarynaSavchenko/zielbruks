
import os
print("Import base by init")
from zielbruks.settings.base import *

SECRET_KEY = 'hmw*j+x*54t2bjud*(tdfl$no@m5w$d%k*gbzi3cf^usdq87wj'

environment: str = os.environ.get("zielbruksenv", "production")

if environment == "development":
    from zielbruks.settings.development import *
else:
    from zielbruks.settings.production import *
