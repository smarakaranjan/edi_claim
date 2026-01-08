# Django setup if running in standalone shell
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edi_claim.settings")
django.setup()

# Models
from superbill.models import (
    EDIClaim,
    EDIPayer,
    EDILoop,
    EDISegment,
    EDIElement
)

# EDI Engine
from superbill.edi_engine import (
    LoopProcessor,
    SegmentProcessor,
    LoopRepeatResolver,
    EDIClaimGenerator
)



claim = EDIClaim.objects.first()  # or get specific claim
payer = EDIPayer.objects.first()  # or get specific payer

generator = EDIClaimGenerator(claim, payer)
edi_output = generator.generate()

print(edi_output)
