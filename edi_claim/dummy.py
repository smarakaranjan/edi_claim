import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edi_claim.settings")
django.setup()

from superbill.models import EDIClaim, EDIPayer
from superbill.edi_engine import EDIEngine   # adjust import if needed

# 1️⃣ Fetch objects
claim = EDIClaim.objects.get(id=1)           # or claim_number=...
payer = EDIPayer.objects.get(name="Default Payer")

# 2️⃣ Generate EDI
engine = EDIEngine(claim=claim, payer=payer)
edi_text = engine.generate()

# 3️⃣ Output
print(edi_text)


 