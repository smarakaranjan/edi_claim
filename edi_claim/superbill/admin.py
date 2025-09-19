from django.contrib import admin

from superbill.models import(
    EDIClaim,
    EDIClaimDiagnosis,
    EDIPayer,
    EDIPayerEndpoint,
    EDIPayerPayload,
    EDILoop,
    EDISegment,
    EDIElement,
    EDIMedicationLine,
    EDIServiceModifier,
    EDIServiceLine,
    EDIProvider,
    EDIPayerRule,
    EDIDataKey,
    BillingProcedureCode,
    BillingNDCCode,
    BillingICD10Diagnosis,
    BillingModifier,
    BillingPlaceOfService
)
# Register your models here.

admin.site.register(EDIClaim)
admin.site.register(EDIClaimDiagnosis)
admin.site.register(EDIPayer)
admin.site.register(EDIPayerEndpoint)
admin.site.register(EDIPayerPayload)
admin.site.register(EDILoop)
admin.site.register(EDISegment)
admin.site.register(EDIElement)
admin.site.register(EDIMedicationLine)
admin.site.register(EDIServiceModifier)
admin.site.register(EDIServiceLine)
admin.site.register(EDIProvider)
admin.site.register(EDIPayerRule)
admin.site.register(EDIDataKey)
admin.site.register(BillingProcedureCode)
admin.site.register(BillingNDCCode)
admin.site.register(BillingICD10Diagnosis)
admin.site.register(BillingModifier)
admin.site.register(BillingPlaceOfService)
