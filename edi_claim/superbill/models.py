from django.db import models
from django.conf import settings

class BillingProcedureCode(models.Model):

    cpt_code = models.CharField(
        max_length=10, 
        help_text="CPT/HCPCS procedure code."
    )

    name = models.CharField(
        max_length=255, 
        help_text="Short name of the CPT code."
    )

    description = models.TextField(
        help_text="Detailed description of the CPT code."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='billing_codes_created'
    )
    
    changed_at = models.DateTimeField(auto_now=True)

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='billing_codes_changed'
    )
    
    is_active = models.BooleanField(default=True)

    deleted_at = models.DateTimeField(
        null=True, blank=True, 
        help_text="Timestamp when the billing code was soft-deleted."
    )
    
    class Meta:
        db_table = 'superbill_procedure_code'
        verbose_name = "Billing Code"
        verbose_name_plural = "Billing Codes"
    
    def __str__(self):
        return f"{self.cpt_code} - {self.name}"
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
    

class BillingPlaceOfService(models.Model):

    code = models.CharField(
        max_length=10, 
        help_text="POS code, e.g., 11=Office, 21=Inpatient Hospital."
    )

    name = models.CharField(
        max_length=255, 
        help_text="Short name of the place of service."
    )

    description = models.TextField(
        help_text="Detailed description of the place of service."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pos_created'
    )

    changed_at = models.DateTimeField(auto_now=True)

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pos_changed'
    )

    is_active = models.BooleanField(default=True)

    deleted_at = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Timestamp when the place of service was soft-deleted."
    )

    class Meta:
        db_table = 'superbill_place_of_service'
        verbose_name = "Place of Service"
        verbose_name_plural = "Places of Service"

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_deleted(self):
        return self.deleted_at is not None

class BillingNDCCode(models.Model):

    product_code = models.CharField(
        max_length=255, 
        help_text="National Drug Code identifying the medication."
    )

    product_description = models.CharField(
        max_length=255, 
        help_text="Description of the medication or product."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='ndc_codes_created'
    )
    
    changed_at = models.DateTimeField(auto_now=True)

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='ndc_codes_changed'
    )
    
    is_active = models.BooleanField(default=True)

    deleted_at = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Timestamp when the NDC code was soft-deleted."
    )
    
    class Meta:
        db_table = 'superbill_ndc_code'
        verbose_name = "NDC Code"
        verbose_name_plural = "NDC Codes"
    
    def __str__(self):
        return f"{self.product_code} - {self.product_description}"
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None


class BillingICD10Diagnosis(models.Model):

    code = models.CharField(
        max_length=10, 
        help_text="ICD-10 diagnosis code."
    )

    description = models.TextField(
        help_text="Description of the ICD-10 diagnosis."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='icd10_diagnoses_created'
    )
    
    changed_at = models.DateTimeField(auto_now=True)

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='icd10_diagnoses_changed'
    )
    
    is_active = models.BooleanField(default=True)
     
    deleted_at = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Timestamp when the ICD-10 code was soft-deleted."
    )
    
    class Meta:
        db_table = 'superbill_icd_10_diagnoses'
        verbose_name = "ICD-10 Diagnosis"
        verbose_name_plural = "ICD-10 Diagnoses"
    
    def __str__(self):
        return f"{self.code} - {self.description[:50]}"
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
    

class BillingModifier(models.Model):

    modifier_code = models.CharField(
        max_length=5, 
        help_text="CPT/HCPCS modifier code, e.g., LT, RT, 59."
    )

    name = models.CharField(
        max_length=255, 
        help_text="Short name for the modifier."
    )

    description = models.TextField(
        help_text="Detailed description of the modifier."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='modifiers_created'
    )

    changed_at = models.DateTimeField(auto_now=True)

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='modifiers_changed'
    )

    is_active = models.BooleanField(default=True)

    deleted_at = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Timestamp when the modifier was soft-deleted."
    )

    class Meta:
        db_table = 'superbill_modifiers'
        verbose_name = "Billing Modifier"
        verbose_name_plural = "Billing Modifiers"

    def __str__(self):
        return f"{self.modifier_code} - {self.name}"

    @property
    def is_deleted(self):
        return self.deleted_at is not None
    


class EDIPayer(models.Model):
    """
    Represents a health insurance payer (carrier) with its base configuration.
    """
    name = models.CharField(
        max_length=200,
        help_text="Payer name (e.g., UnitedHealthcare, Medicare)."
    )

    edi_version = models.CharField(
        max_length=50,
        default="005010X222A1",
        help_text="EDI version used for claims (default: HIPAA 837P Professional)."
    )

    base_url = models.CharField(
        max_length=500,
        blank=True, null=True,
        help_text="Base API URL or SFTP host for this payer."
    )

    credentials = models.JSONField(
        blank=True, null=True,
        help_text="Authentication credentials (encrypted outside DB)."
    )

    active = models.BooleanField(
        default=True,
        help_text="If disabled, this payer is excluded from claim submission."
    )

    class Meta:
        db_table = 'superbill_edi_payer'
        verbose_name = "EDI Payer"
        verbose_name_plural = "EDI Payers"

    def __str__(self):
        return self.name


class EDIProvider(models.Model):

    """
    Represents a healthcare provider or organization in the EDI (Electronic Data Interchange) system.
    This model stores core provider identifiers, licensing information, and optional billing-related codes.
    This model is intended to unify all provider-related identifiers and credentials into a single reference table
    that can be linked to claims, service lines, and other billing or clinical data.
    """

    npi = models.CharField(
        max_length=10, 
        unique=True, 
        help_text="National Provider Identifier (10-digit unique ID assigned to the provider)."
    )

    name = models.CharField(
        max_length=255, 
        help_text="Full name of the provider or organization."
    )

    taxonomy_code = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        help_text="Optional: Provider's specialty code (taxonomy code)."
    )

    provider_code = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="Internal system code."
    )
    
    license_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
    )

    license_type = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
    )

    tax_id = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="TIN/EIN for billing."
    )

    dea_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="DEA number for controlled substances."
    )

    upn = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="Universal Provider Number, if applicable."
    )

    type = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Optional: Type of provider, e.g., 'individual' or 'organization'."
    )

    class Meta:
        db_table = 'superbill_edi_provider'
        verbose_name = "EDI Provider"
        verbose_name_plural = "EDI Providers"

    def __str__(self):
        return f"{self.name} ({self.npi})"
    

class EDIClaim(models.Model):
    """
    Represents a healthcare claim (professional or institutional) to be submitted to a payer.
    """

    claim_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique identifier for this claim (e.g., C12345)."
    )

    patient_id = models.CharField(
        max_length=50,
        help_text="Patient identifier used by payer (e.g., insurance member ID)."
    )

    patient_first_name = models.CharField(
        max_length=50,
        help_text="Patient first name used by payer."
    )

    patient_middle_name = models.CharField(
        max_length=50,
        help_text="Patient middle name used by payer."
    )

    patient_last_name = models.CharField(
        max_length=50,
        help_text="Patient middle name used by payer."
    )


    date_of_service = models.DateField(
        help_text="Date the service was provided to the patient."
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total charge amount for the entire claim."
    )

    claim_type = models.CharField(
        max_length=50,
        choices=[("professional", "Professional"), ("institutional", "Institutional")],
        help_text="Indicates the type of claim (professional vs institutional)."
    )

    billing_provider_npi = models.ForeignKey(
        "superbill.EDIProvider",
        on_delete=models.PROTECT,
        related_name="billed_claims",
        help_text="The provider or organization submitting the claim (billing NPI)."
    )

    payer = models.ForeignKey(
        "superbill.EDIPayer",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Identifier for the payer (used to select the correct EDI endpoint)."
    )

    transaction_id = models.CharField(
        blank=True,
        null=True,
        help_text="Unique transaction ID returned after successfully submitting the claim."
    )

    encounter_id = models.CharField(
        blank=True,
        null=True,
        help_text="Encounter Id first encounter with the rendering provider."
    )

    class Meta:
        db_table = 'superbill_edi_claim'
        verbose_name = "EDI Claim"
        verbose_name_plural = "EDI Claims"

    def __str__(self):
        return f"Claim {self.claim_number} - {self.patient_last_name}, {self.patient_first_name}"
    

class EDIClaimDiagnosis(models.Model):

    claim = models.ForeignKey(
        'superbill.EDIClaim', 
        on_delete=models.CASCADE, 
        related_name="diagnoses",
        help_text="The claim this diagnosis is associated with."
    )

    diagnosis_code = models.ForeignKey(
        'superbill.BillingICD10Diagnosis', 
        on_delete=models.PROTECT,
        help_text="ICD diagnosis code representing the medical condition."
    )

    class Meta:
        db_table = 'superbill_edi_claim_diagnosis'
        verbose_name = "EDI Claim Diagnosis"
        verbose_name_plural = "EDI Claims Diagnosis"


class EDIMedicationLine(models.Model):

    service_line = models.ForeignKey(
        'superbill.EDIServiceLine', 
        on_delete=models.CASCADE, 
        related_name="medications",
        help_text="The service line this medication is associated with."
    )

    ndc_code = models.ForeignKey(
        'superbill.BillingNDCCode', 
        on_delete=models.PROTECT,
        help_text="National Drug Code identifying the specific medication or drug administered."
    )
    
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="The quantity of medication administered for this service line."
    )

    class Meta:
        db_table = 'superbill_edi_medication_line'
        verbose_name = "EDI Medication Line"
        verbose_name_plural = "EDI Medication Lines"

class EDIServiceLineDiagnosisPointer(models.Model):

    service_line = models.ForeignKey(
        "superbill.EDIServiceLine",
        on_delete=models.CASCADE,
        related_name="diagnosis_pointer_links"
    )

    diagnosis = models.ForeignKey(
        "superbill.EDIClaimDiagnosis",
        on_delete=models.CASCADE,
        related_name="pointer_links"
    )

    pointer_order = models.PositiveSmallIntegerField(
        choices=[(1, "Pointer 1"), (2, "Pointer 2"), (3, "Pointer 3"), (4, "Pointer 4")],
        help_text="Order of this diagnosis pointer in SV107 (max 4)."
    )

    class Meta:
        db_table = "superbill_edi_service_line_pointer"
        unique_together = ("service_line", "pointer_order")
        ordering = ["pointer_order"]

    def __str__(self):
        return f"ServiceLine {self.service_line.line_number} → {self.diagnosis.diagnosis_code} (Pointer {self.pointer_order})"


class EDIServiceLine(models.Model):
    """
    Represents a single billable service within a claim (corresponds to 2400 loop in 837).
    """

    claim = models.ForeignKey(
        "superbill.EDIClaim",
        on_delete=models.CASCADE,
        related_name="service_lines",
        help_text="The claim this service line belongs to."
    )

    rendering_provider = models.ForeignKey(
        'superbill.EDIProvider',
        on_delete=models.PROTECT,
        related_name="rendered_service_lines",
        help_text="The provider who actually performed the service (rendering NPI)."
    )

    procedure = models.ForeignKey(
        'superbill.BillingProcedureCode',
        on_delete=models.PROTECT,
        help_text="The CPT or HCPCS code representing the medical \
        procedure or service performed for this service line."
    ) 

    line_number = models.PositiveIntegerField(
        help_text="Sequential line number for this service within the claim."
    )

    emg_service_pointer = models.BooleanField(
        default=False,
        help_text="Indicates if this service line was an emergency service."
    ) 

    charge_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Charge amount for this individual service line."
    )

    place_of_service = models.ForeignKey(
        'superbill.BillingPlaceOfService',
        on_delete=models.PROTECT,
        help_text="Place of Service (POS) code indicating where the service was performed, \
        e.g., 11=Office, 21=Inpatient Hospital."
    )

    units = models.IntegerField(
        default=1,
        help_text="The number of times the procedure or service was performed. \
        For example, if a lab test was done twice, set units=2."
    )
    
    service_date = models.DateField(
        help_text="Date the specific service was provided."
    )

    class Meta:
        db_table = 'superbill_edi_service_line'
        verbose_name = "EDI Service Line"
        verbose_name_plural = "EDI Service Lines"

    def save(self, *args, **kwargs):
        if self.line_number is None:
            last_line = EDIServiceLine.objects.filter(claim=self.claim).aggregate(
                models.Max('line_number')
            )['line_number__max'] or 0
            self.line_number = last_line + 1
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"ServiceLine {self.line_number}"


class EDIServiceModifier(models.Model):
    """
    Represents a modifier for a service line (corresponds to 2410 loop in 837).
    """

    service_line = models.ForeignKey(
        "superbill.EDIServiceLine",
        on_delete=models.CASCADE,
        related_name="modifiers",
        help_text="The service line this modifier belongs to."
    )

    modifier_code = models.ForeignKey(
        'superbill.BillingModifier',
        on_delete=models.PROTECT,
        help_text="Modifier code that provides additional \
        context for the service (e.g., LT, RT, 59)."
    )

    class Meta:
        db_table = 'superbill_edi_service_modifier'
        verbose_name = "EDI Service Modifier"
        verbose_name_plural = "EDI Service Modifiers"

    def __str__(self):
        return f"{self.service_line.line_number} Modifier {self.modifier_code}"
    
class EDILoop(models.Model):

    code = models.CharField(
        max_length=20,
        help_text="Loop identifier (e.g., '2010BA' for Subscriber Loop)."
    )

    name = models.CharField(
        max_length=200,
        help_text="Human-readable loop name (e.g., 'Subscriber', 'Billing Provider')."
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subloops",
        help_text="Parent loop if nested (e.g., 2000B → 2010BA)."
    )

    max_repeat = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'superbill_edi_loop'
        verbose_name = "EDI Service Loop"
        verbose_name_plural = "EDI Service Loops"

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def child_loops(self):
        return EDILoop.objects.filter(parent_loop=self)
    

class EDISegment(models.Model):

    loop = models.ForeignKey(
        "superbill.EDILoop",
        on_delete=models.CASCADE,
        related_name="segments",
        null=True,
        help_text="The loop this segment belongs to."
    )

    name = models.CharField(
        max_length=20,
        help_text="Segment ID (e.g., 'NM1', 'REF', 'DTP')."
    )

    position = models.PositiveIntegerField(
        help_text="Ordering of this segment inside the loop."
    )

    class Meta:
        db_table = 'superbill_edi_segment'
        verbose_name = "EDI Segment"
        verbose_name_plural = "EDI Segments"

    def __str__(self):
        return f"{self.name} (pos {self.position})"
    

class EDIElement(models.Model):

    segment = models.ForeignKey(
        'superbill.EDISegment',
        on_delete=models.CASCADE,
        related_name="elements",
        help_text="The segment this element belongs to."
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='sub_elements'
    )
    
    position = models.PositiveIntegerField(
        help_text="Element order within the segment (e.g., 1 for NM101, 2 for NM102)."
    )
    x12_id = models.CharField(max_length=10, help_text="X12 element identifier (e.g., 'NM1', 'DTM').")
    name = models.CharField(
        max_length=200,
        help_text="Human-readable element name (e.g., 'Last Name', 'Entity Identifier Code')."
    )

    data_type = models.CharField(
        max_length=50,
        help_text="X12 element data type (e.g., 'AN' = Alphanumeric, 'DT' = Date, 'N2' = Numeric)."
    )

    length = models.PositiveIntegerField(
        default=50,
        blank=True,
        null=True,
        help_text="Maximum length allowed for this element."
    )
    required = models.BooleanField(
        default=False,
        help_text="Indicates if this element is required in the segment."
    )

    class Meta:
        db_table = 'superbill_edi_element'
        verbose_name = "EDI Element"
        verbose_name_plural = "EDI Elements"

    def __str__(self):
        return f"{self.segment.name} - {self.name} (pos {self.position})"
    
class EDIPayerEndpoint(models.Model):
    """
    Represents a specific endpoint under a payer, such as claims,
    eligibility, or remittance.
    """

    class EDIEndPointType(models.TextChoices):
        """
        Defines the standard endpoint types for EDI/API connectivity with payers.
        """
        CLAIMS = "CLAIMS", "Claims"
        ELIGIBILITY = "ELIGIBILITY", "Eligibility"
        REMITTANCE = "REMITTANCE", "Remittance"
        OTHER = "OTHER", "Other"

    payer = models.ForeignKey(
        "superbill.EDIPayer",
        on_delete=models.CASCADE,
        related_name="endpoints",
        help_text="The payer this endpoint belongs to."
    )

    endpoint_type = models.CharField(
        max_length=50,
        choices=EDIEndPointType.choices,
        help_text="Type of EDI/API endpoint."
    )

    path = models.CharField(
        max_length=500,
        help_text="Relative path or folder (e.g., '/claims/submit' or 'inbox/')."
    )

    protocol = models.CharField(
        max_length=10,
        choices=[("API", "API"), ("SFTP", "SFTP")],
        help_text="Protocol for communication with this endpoint."
    )

    query_params = models.JSONField(
        blank=True,
        null=True,
        help_text="Optional query parameters (e.g., {'version': 'v1', 'format': 'EDI'})."
    )

    class Meta:
        db_table = 'superbill_edi_payer_endpoint'
        verbose_name = "EDI Payer Endpoint"
        verbose_name_plural = "EDI Payer Endpoints"

    def __str__(self):
        return f"{self.payer.name} - {self.endpoint_type}"
    

class EDIPayerPayload(models.Model):
    """
    Defines how a payload should be constructed for a specific endpoint.
    """

    endpoint = models.ForeignKey(
        "superbill.EDIPayerEndpoint",
        on_delete=models.CASCADE,
        related_name="payload_profiles",
        help_text="The endpoint this payload profile maps to."
    )

    profile_type = models.CharField(
        max_length=20,
        choices=[("EDI837", "EDI837"), ("FHIR", "FHIR"), ("JSON", "JSON")],
        help_text=(
            "The type of payload this profile generates: "
            "EDI837 (X12 text), FHIR (HL7 JSON/XML), or custom JSON API format."
        )
    )

    payload_template = models.JSONField(
        help_text=(
            "A JSON structure or template that defines the payload shape. "
            "Use placeholders like {{claim.total_amount}}, {{patient.dob}}, "
            "or {{service_line.cpt_code}}. Placeholders will be resolved "
            "dynamically at runtime."
        )
    )

    query_params = models.JSONField(
        blank=True,
        null=True,
        help_text=(
            "Optional query parameters specific to this profile. "
            "These override or extend the endpoint-level parameters. "
            "Example: {'useFhirVersion': 'R4'}"
        )
    )

    version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Optional version (e.g., 'v1.0', '2025-Q1')."
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this profile is active."
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp."
    )

    class Meta:
        db_table = 'superbill_edi_payer_payload'
        verbose_name = "EDI Payer Payload"
        verbose_name_plural = "EDI Payer Payloads"

    def __str__(self):
        return (
            f"{self.endpoint.payer.name} - "
            f"{self.endpoint.endpoint_type} - "
            f"{self.profile_type} ({self.version or 'default'})"
        )
    
class EDIDataKey(models.Model):

    """
    Represents an abstract data concept, independent of payer.
    Stores a dynamic way to extract the value from a claim object.
    """

    key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique abstract data key, e.g., SUBSCRIBER_LAST_NAME"
    )

    description = models.TextField(
        blank=True,
        help_text="Human-readable description of what this data key represents."
    )

    extractor = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=(
            "Optional: path or instruction to extract value from claim object "
            "(e.g., subscriber.last_name, service_lines.0.date)."
        )
    )

    class Meta:
        db_table = 'superbill_edi_data_key'
        verbose_name = "EDI Data Key"
        verbose_name_plural = "EDI Data Keys"

    def __str__(self):
        return self.key
    

class EDIPayerRule(models.Model):
    """
    Dynamic rule to populate an EDI element per payer.
    """

    class RuleTarget(models.TextChoices):
        ELEMENT = "ELEMENT", "Element"
        LOOP = "LOOP", "Loop"

    class EDIRuleType(models.TextChoices):
        """
        Defines the standard endpoint types for EDI/API connectivity with payers.
        """
        FIELD = "FIELD", "Field"
        CONSTANT = "CONSTANT", "Constant"
        MAPPING = "MAPPING", "Mapping"
        FUNC = "FUNC", "Func"

    element = models.ForeignKey(
        "superbill.EDIElement",
        on_delete=models.CASCADE,
        related_name="rules",
        blank=True,
        null=True,
        help_text="The EDI element this rule applies to."
    )

    target_type = models.CharField(
        max_length=10,
        choices=RuleTarget.choices,
        default=RuleTarget.ELEMENT
    )

    payer = models.ForeignKey(
        "superbill.EDIPayer",
        on_delete=models.CASCADE,
        related_name="rules",
        help_text="The payer this rule applies to."
    )

    loop = models.ForeignKey(
        "superbill.EDILoop",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="rules"
    )

    min_length = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Minimum length for this element. Used for padding."
    )

    max_length = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Maximum length for this element. Used for truncation/padding."
    )

    pad_char = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        help_text="Character used for padding (default space for most, 0 for control numbers)."
    )

    pad_side = models.CharField(
        max_length=5,
        choices=[("left", "Left"), ("right", "Right")],
        default="right",
        help_text="Which side to pad on if length < max_length."
    )

    # Rule type: FIELD, CONSTANT, MAPPING, FUNC
    rule_type = models.CharField(
        max_length=50,
        choices=EDIRuleType.choices,
        help_text="How to resolve the value for this element."
    )

    # Dynamic pointer to data
    data_key = models.ForeignKey(
        "superbill.EDIDataKey",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Reference to a DataKey to resolve the value dynamically."
    )

    # For CONSTANT type
    constant_value = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Fixed value for CONSTANT rule type."
    )

    # Transformations applied to resolved value
    transformation = models.JSONField(
        blank=True,
        null=True,
        help_text="Optional transformations (uppercase, truncate, date format)."
    )

    # Conditional logic for this rule
    condition = models.JSONField(
        blank=True,
        null=True,
        help_text="Apply rule only if conditions are met (e.g., {'claim_type': 'professional'})."
    )

    # Execution order for multiple rules on same element
    order = models.PositiveIntegerField(
        default=0,
        help_text="Execution order if multiple rules exist for the same element."
    )

    # Is element required
    required = models.BooleanField(
        default=True,
        help_text="Whether this element must be populated for this payer."
    )

    class Meta:
        db_table = 'superbilling_edi_payer_rule'
        verbose_name = "EDI Payer Rule"
        verbose_name_plural = "EDI Payer Rules"

    def __str__(self):
        return f"{self.payer.name} - {self.element.segment.name}{self.element.position} ({self.rule_type})"



 



 


 


 
    
 