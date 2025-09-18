from django.db import models


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

    def __str__(self):
        return self.key
    

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

    def __str__(self):
        return self.name
    

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
        "EDIPayer",
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

    def __str__(self):
        return f"{self.payer.name} - {self.endpoint_type}"

class EDIPayloadProfile(models.Model):
    """
    Defines how a payload should be constructed for a specific endpoint.
    """

    endpoint = models.ForeignKey(
        "EDIPayerEndpoint",
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

    def __str__(self):
        return (
            f"{self.endpoint.payer.name} - "
            f"{self.endpoint.endpoint_type} - "
            f"{self.profile_type} ({self.version or 'default'})"
        )



class EDIProvider(models.Model):
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
    type = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Optional: Type of provider, e.g., 'individual' or 'organization'."
    )

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

    billing_provider_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of the billing provider or facility submitting the claim."
    )

    billing_provider_npi = models.ForeignKey(
        "Provider",
        on_delete=models.PROTECT,
        related_name="billed_claims",
        help_text="The provider or organization submitting the claim (billing NPI)."
    )

    payer = models.ForeignKey(
        "EDIPayer",
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

    def __str__(self):
        return f"Claim {self.claim_number} - {self.patient_last_name}, {self.patient_first_name}"



class EDIClaimDiagnosis(models.Model):

    claim = models.ForeignKey(
        EDIClaim, 
        on_delete=models.CASCADE, 
        related_name="diagnoses",
        help_text="The claim this diagnosis is associated with."
    )

    diagnosis_code = models.ForeignKey(
        'ICDCode', 
        on_delete=models.PROTECT,
        help_text="ICD diagnosis code representing the medical condition."
    )


class EDIMedicationLine(models.Model):

    service_line = models.ForeignKey(
        'ServiceLine', 
        on_delete=models.CASCADE, 
        related_name="medications",
        help_text="The service line this medication is associated with."
    )

    ndc_code = models.ForeignKey(
        'NDCCode', 
        on_delete=models.PROTECT,
        help_text="National Drug Code identifying the specific medication or drug administered."
    )
    
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="The quantity of medication administered for this service line."
    )

class ServiceLine(models.Model):
    """
    Represents a single billable service within a claim (corresponds to 2400 loop in 837).
    """

    claim = models.ForeignKey(
        "EDIClaim",
        on_delete=models.CASCADE,
        related_name="service_lines",
        help_text="The claim this service line belongs to."
    )

    rendering_provider = models.ForeignKey(
        'EDIProvider',
        on_delete=models.PROTECT,
        related_name="rendered_service_lines",
        help_text="The provider who actually performed the service (rendering NPI)."
    )

    procedure = models.ForeignKey(
        'ProcedureCode',
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

    place_of_service = models.CharField(
        max_length=2,
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

    def __str__(self):
        return f"ServiceLine {self.line_number} - {self.cpt_code}"


class ServiceModifier(models.Model):
    """
    Represents a modifier for a service line (corresponds to 2410 loop in 837).
    """

    service_line = models.ForeignKey(
        "ServiceLine",
        on_delete=models.CASCADE,
        related_name="modifiers",
        help_text="The service line this modifier belongs to."
    )

    modifier_code = models.CharField(
        max_length=5,
        help_text="Modifier code that provides additional context for the service (e.g., LT, RT, 59)."
    )

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

    def __str__(self):
        return f"{self.code} - {self.name}"
    

class EDISegment(models.Model):

    loop = models.ForeignKey(
        "EDILoop",
        on_delete=models.CASCADE,
        related_name="segments",
        help_text="The loop this segment belongs to."
    )

    name = models.CharField(
        max_length=20,
        help_text="Segment ID (e.g., 'NM1', 'REF', 'DTP')."
    )

    position = models.PositiveIntegerField(
        help_text="Ordering of this segment inside the loop."
    )

    def __str__(self):
        return f"{self.loop.code} - {self.name} (pos {self.position})"
    

class EDIElement(models.Model):

    segment = models.ForeignKey(
        EDISegment,
        on_delete=models.CASCADE,
        related_name="elements",
        help_text="The segment this element belongs to."
    )

    position = models.PositiveIntegerField(
        help_text="Element order within the segment (e.g., 1 for NM101, 2 for NM102)."
    )

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
        help_text="Maximum length allowed for this element."
    )

    def __str__(self):
        return f"{self.segment.name} - {self.name} (pos {self.position})"
    
class EDIPayerRule(models.Model):
    """
    Dynamic rule to populate an EDI element per payer.
    """

    class EDIRuleType(models.TextChoices):
        """
        Defines the standard endpoint types for EDI/API connectivity with payers.
        """
        FIELD = "FIELD", "Field"
        CONSTANT = "CONSTANT", "Constant"
        MAPPING = "MAPPING", "Mapping"
        FUNC = "FUNC", "Func"

    element = models.ForeignKey(
        "EDIElement",
        on_delete=models.CASCADE,
        related_name="rules",
        help_text="The EDI element this rule applies to."
    )

    payer = models.ForeignKey(
        "EDIPayer",
        on_delete=models.CASCADE,
        related_name="rules",
        help_text="The payer this rule applies to."
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
        "EDIDataKey",
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

    def __str__(self):
        return f"{self.payer.name} - {self.element.segment.name}{self.element.position} ({self.rule_type})"
