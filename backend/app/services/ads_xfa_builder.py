"""
ads_xfa_builder.py — Generates correct XFA datasets XML for USPTO ADS (PTO/AIA/14).

This module builds the datasets XML by starting from the EXACT skeleton of the
original blank ADS template, then populating fields from your data model.
This guarantees structural completeness and fixes the following bugs:

  [CRITICAL] Bug 1: Residency now correctly determined from residence country
  [CRITICAL] Bug 2: sfUSres fields populated for US-resident inventors
  [CRITICAL] Bug 3: CitizedDropDown populated from citizenship data
  [CRITICAL] Bug 4: Multiple applicant companies fully supported
  [HIGH]     Bug 5: sfInventorRepInfo included in every inventor block
  [HIGH]     Bug 6: All 25+ structural elements present in output
  [FIXED]    Bug 7: Title mapping completely fixed with proper XML structure:
                    - sfInvTitle now contains <invention-title> (not empty)
                    - invention-title placed at ROOT level (not inside ContentArea3)

Usage:
    from ads_xfa_builder import build_ads_datasets_xml

    xml = build_ads_datasets_xml(
        inventors=[...],
        applicants=[...],   # Companies filing under 35 USC 118
        title="...",
        ...
    )
    # Then inject this XML into the ADS PDF template's datasets packet
"""

from dataclasses import dataclass, field
from typing import List, Optional
import html
from app.services.file_validators import sanitize_for_xml


# ─── Data Models ────────────────────────────────────────────────────────────────
# Adjust these to match your actual PatentApplicationMetadata / Inventor models.
# The key additions vs your current model: residence_country on inventors,
# and applicant_authority on applicants.

@dataclass
class InventorInfo:
    """One inventor (maps to sfApplicantInformation in ContentArea1)."""
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    prefix: str = ""       # e.g., "Dr.", "Mr."
    suffix: str = ""       # e.g., "Jr.", "III"

    # --- Residence (where the inventor LIVES) ---
    residence_city: str = ""
    residence_state: str = ""       # 2-letter code for US, e.g., "MA"
    residence_country: str = ""     # Full name or 2-letter code: "United States", "US", "GB", etc.

    # --- Citizenship (nationality) — distinct from residence ---
    citizenship: str = ""           # 2-letter country code or full name: "US", "IN", "United States", "India"

    # --- Mailing address ---
    mail_address1: str = ""
    mail_address2: str = ""
    mail_city: str = ""
    mail_state: str = ""
    mail_postcode: str = ""
    mail_country: str = ""


@dataclass
class ApplicantInfo:
    """
    One applicant under 35 USC 118 (maps to sfAssigneeInformation in ContentArea2).

    ONLY needed when the applicant is NOT the inventor — typically a company/assignee.
    If inventors are filing for themselves, leave the applicants list empty.
    """
    is_organization: bool = True
    org_name: str = ""

    # Individual name (only if is_organization=False)
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    prefix: str = ""
    suffix: str = ""

    # Authority type — maps to LegalRadio
    # Valid: "assignee", "legal-representative", "joint-inventor",
    #        "person", "party-of-interest"
    authority: str = "assignee"

    # Mailing address
    address1: str = ""
    address2: str = ""
    city: str = ""
    state: str = ""
    postcode: str = ""
    country: str = ""
    phone: str = ""
    fax: str = ""
    email: str = ""


@dataclass
class ApplicationData:
    """All data for the ADS form."""
    # --- Inventors ---
    inventors: List[InventorInfo] = field(default_factory=list)

    # --- Applicants (only if applicant ≠ inventor) ---
    applicants: List[ApplicantInfo] = field(default_factory=list)

    # --- Application Info ---
    title: str = ""
    attorney_docket_number: str = ""
    application_type: str = ""              # "utility", "design", "plant", "reissue", "provisional"
    entity_status: str = ""                 # "undiscounted", "small", "micro"  → maps to chkSmallEntity
    total_drawing_sheets: str = ""
    suggested_figure: str = ""

    # --- Secrecy ---
    secrecy_order: bool = False

    # --- Correspondence (use customer_number OR address, not both) ---
    corr_customer_number: str = ""
    corr_name1: str = ""
    corr_name2: str = ""
    corr_address1: str = ""
    corr_address2: str = ""
    corr_city: str = ""
    corr_state: str = ""
    corr_country: str = ""
    corr_postcode: str = ""
    corr_phone: str = ""
    corr_fax: str = ""
    corr_email: str = ""

    # --- Representative ---
    rep_customer_number: str = ""

    # --- Signature ---
    sig_first_name: str = ""
    sig_last_name: str = ""
    sig_registration_number: str = ""
    sig_date: str = ""


# ─── Helpers ────────────────────────────────────────────────────────────────────

def _esc(value: str) -> str:
    """Escape XML special characters."""
    if not value:
        return ""
    return html.escape(str(value), quote=True)


def _tag(name: str, value: str = "") -> str:
    """Generate an XML element. Empty string → self-closing tag."""
    if value:
        safe_value = sanitize_for_xml(value)
        return f"<{name}>{safe_value}</{name}>"
    return f"<{name}/>"


def _is_us_country(country: str) -> bool:
    """Check if a country string refers to the United States."""
    if not country:
        return False
    c = country.strip().lower()
    return c in (
        "us", "usa", "united states", "united states of america",
        "u.s.", "u.s.a.", "united states (us)",
    )


def _normalize_state(state: str) -> str:
    """Ensure state is 2-letter uppercase code for US states."""
    s = state.strip().upper()
    # Map full state names to codes
    STATE_MAP = {
        "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR",
        "CALIFORNIA": "CA", "COLORADO": "CO", "CONNECTICUT": "CT", "DELAWARE": "DE",
        "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI", "IDAHO": "ID",
        "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS",
        "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME", "MARYLAND": "MD",
        "MASSACHUSETTS": "MA", "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS",
        "MISSOURI": "MO", "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV",
        "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM", "NEW YORK": "NY",
        "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK",
        "OREGON": "OR", "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC",
        "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT",
        "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV",
        "WISCONSIN": "WI", "WYOMING": "WY", "DISTRICT OF COLUMBIA": "DC",
    }
    return STATE_MAP.get(s, s[:2] if len(s) >= 2 else s)


def _country_to_code(country: str) -> str:
    """Convert a country name to 2-letter ISO code. Falls back to first 2 chars."""
    if not country:
        return ""
    c = country.strip()

    # Common mappings
    COUNTRY_MAP = {
        "united states": "US", "united states of america": "US", "usa": "US", "us": "US",
        "united kingdom": "GB", "uk": "GB", "great britain": "GB", "england": "GB",
        "canada": "CA", "india": "IN", "china": "CN", "japan": "JP",
        "germany": "DE", "france": "FR", "australia": "AU", "brazil": "BR",
        "south korea": "KR", "korea": "KR", "republic of korea": "KR",
        "mexico": "MX", "italy": "IT", "spain": "ES", "netherlands": "NL",
        "switzerland": "CH", "sweden": "SE", "norway": "NO", "denmark": "DK",
        "finland": "FI", "ireland": "IE", "israel": "IL", "singapore": "SG",
        "taiwan": "TW", "new zealand": "NZ", "russia": "RU", "russian federation": "RU",
        "belgium": "BE", "austria": "AT", "poland": "PL", "portugal": "PT",
    }

    normalized = c.lower().strip()
    if normalized in COUNTRY_MAP:
        return COUNTRY_MAP[normalized]

    # If already a 2-letter code, return uppercase
    if len(c) == 2 and c.isalpha():
        return c.upper()

    return c  # Fallback: return as-is


# ─── Entity Status Mapping ──────────────────────────────────────────────────────

def _entity_status_value(status: str) -> str:
    """
    Map entity status to the ADS chkSmallEntity value.
    The ADS form uses:
      0 = Undiscounted (Large Entity)
      1 = Small Entity
      2 = Micro Entity
    """
    s = status.strip().lower() if status else ""
    if s in ("small", "small entity", "1"):
        return "1"
    elif s in ("micro", "micro entity", "2"):
        return "2"
    else:
        return "0"  # Large / undiscounted is the default


# ─── XML Builders ───────────────────────────────────────────────────────────────

def _build_inventor_xml(inv: InventorInfo, seq: int) -> str:
    """
    Build one <sfApplicantInformation> block for an inventor.

    Fixes applied:
      - Bug 1: ResidencyRadio set based on residence_country (not citizenship)
      - Bug 2: sfUSres populated when residence is US
      - Bug 3: CitizedDropDown populated from citizenship
      - Bug 5: sfInventorRepInfo included (empty but structurally complete)
    """
    has_residence_data = bool(inv.residence_country and inv.residence_country.strip())
    is_us_resident = _is_us_country(inv.residence_country) if has_residence_data else False

    # Determine residency radio value
    # 3-way: no data → unselected, US → us-residency, non-US → non-us-residency
    if not has_residence_data:
        residency_radio = ""
    elif is_us_resident:
        residency_radio = "us-residency"
    else:
        residency_radio = "non-us-residency"

    # Build residency details
    if not has_residence_data:
        # No data — leave everything empty for manual entry
        us_res = "<sfUSres><rsCityTxt/><rsStTxt/><rsCtryTxt/></sfUSres>"
        non_us_res = "<sfNonUSRes><nonresCity/><nonresCtryList/></sfNonUSRes>"
    elif is_us_resident:
        us_res = (
            f"<sfUSres>"
            f"{_tag('rsCityTxt', inv.residence_city)}"
            f"{_tag('rsStTxt', _normalize_state(inv.residence_state))}"
            f"{_tag('rsCtryTxt', 'US')}"
            f"</sfUSres>"
        )
        non_us_res = "<sfNonUSRes><nonresCity/><nonresCtryList/></sfNonUSRes>"
    else:
        us_res = "<sfUSres><rsCityTxt/><rsStTxt/><rsCtryTxt/></sfUSres>"
        non_us_res = (
            f"<sfNonUSRes>"
            f"{_tag('nonresCity', inv.residence_city)}"
            f"{_tag('nonresCtryList', _country_to_code(inv.residence_country))}"
            f"</sfNonUSRes>"
        )

    # Build citizenship
    citizenship_code = _country_to_code(inv.citizenship) if inv.citizenship else ""

    # Build mailing address
    mail_country = _country_to_code(inv.mail_country or inv.residence_country)
    mail_state = inv.mail_state

    return (
        f"<sfApplicantInformation>"
        # Auth / sequence number
        f"<sfAuth><appSeq>{seq}</appSeq></sfAuth>"
        # Name
        f"<sfApplicantName>"
        f"{_tag('prefix', inv.prefix)}"
        f"{_tag('suffix', inv.suffix)}"
        f"{_tag('firstName', inv.first_name)}"
        f"{_tag('middleName', inv.middle_name)}"
        f"{_tag('lastName', inv.last_name)}"
        f"</sfApplicantName>"
        # Residency
        f"<sfAppResChk>"
        f"<resCheck><ResidencyRadio>{residency_radio}</ResidencyRadio></resCheck>"
        f"{us_res}"
        f"{non_us_res}"
        f"<sfMil><actMilDropDown/></sfMil>"
        f"</sfAppResChk>"
        # Citizenship
        f"<sfCitz>{_tag('CitizedDropDown', citizenship_code)}</sfCitz>"
        # Mailing address
        f"<sfApplicantMail>"
        f"{_tag('mailCountry', mail_country)}"
        f"{_tag('postcode', inv.mail_postcode)}"
        f"{_tag('address1', inv.mail_address1)}"
        f"{_tag('address2', inv.mail_address2)}"
        f"{_tag('city', inv.mail_city)}"
        f"{_tag('state', mail_state)}"
        f"</sfApplicantMail>"
        # ── Bug 5 fix: Include sfInventorRepInfo (empty but structurally complete) ──
        f"<sfInventorRepInfo>"
        f"<sfReporgChoice>"
        f"<chkOrg/>"
        f"<org><orgName/></org>"
        f"<sfRepApplicantName>"
        f"<prefix/><firstName/><middleName/><lastName/><suffix/>"
        f"</sfRepApplicantName>"
        f"</sfReporgChoice>"
        f"<sfRepAppResChk>"
        f"<resCheck/>"
        f"<sfUSres><rsCityTxt/><rsStTxt/><rsCtryTxt/></sfUSres>"
        f"<sfNonUSRes><nonresCity/><nonresCtryList/></sfNonUSRes>"
        f"<sfMil><actMilDropDown/></sfMil>"
        f"</sfRepAppResChk>"
        f"<sfRepCitz><CitizedDropDown/></sfRepCitz>"
        f"<sfRepApplicantMail>"
        f"<address1/><address2/><city/><state/><postcode/><mailCountry/>"
        f"</sfRepApplicantMail>"
        f"</sfInventorRepInfo>"
        f"</sfApplicantInformation>"
    )


def _build_applicant_xml(app: ApplicantInfo, seq: int) -> str:
    """
    Build one <sfAssigneeInformation> block (Applicant under 35 USC 118).

    Fixes applied:
      - Bug 4: Supports multiple applicants (called once per applicant)
      - Authority type (LegalRadio) populated
      - chkOrg properly set for organizations
    """
    chk_org = "1" if app.is_organization else "0"

    return (
        f"<sfAssigneeInformation>"
        # Sequence and authority
        f"<sfAssigneebtn>"
        f"<appSeq>{seq}</appSeq>"
        f"{_tag('lstInvType')}"
        f"{_tag('LegalRadio', app.authority)}"
        f"</sfAssigneebtn>"
        # Organization choice
        f"<sfAssigneorgChoice>"
        f"<chkOrg>{chk_org}</chkOrg>"
        f"<sforgName>{_tag('orgName', app.org_name if app.is_organization else '')}</sforgName>"
        f"</sfAssigneorgChoice>"
        # Individual name (empty if organization)
        f"<sfApplicantName>"
        f"{_tag('prefix', '' if app.is_organization else app.prefix)}"
        f"{_tag('first-name', '' if app.is_organization else app.first_name)}"
        f"{_tag('middle-name', '' if app.is_organization else app.middle_name)}"
        f"{_tag('last-name', '' if app.is_organization else app.last_name)}"
        f"{_tag('suffix', '' if app.is_organization else app.suffix)}"
        f"</sfApplicantName>"
        # Address
        f"<sfAssigneeAddress>"
        f"{_tag('address-1', app.address1)}"
        f"{_tag('address-2', app.address2)}"
        f"{_tag('city', app.city)}"
        f"{_tag('state', app.state)}"
        f"{_tag('postcode', app.postcode)}"
        f"{_tag('phone', app.phone)}"
        f"{_tag('fax', app.fax)}"
        f"{_tag('txtCorrCtry', _country_to_code(app.country))}"
        f"</sfAssigneeAddress>"
        # Email
        f"<sfAssigneeEmail>{_tag('email', app.email)}</sfAssigneeEmail>"
        f"</sfAssigneeInformation>"
    )


def build_ads_datasets_xml(data: ApplicationData) -> str:
    """
    Build the complete XFA datasets XML for the USPTO ADS form.

    This produces structurally complete XML that matches the original blank
    ADS template skeleton, with all sections present even when empty.

    Returns:
        str: Complete <xfa:datasets> XML string ready for injection into the
             ADS PDF template's XFA datasets packet.
    """
    # ── ContentArea1: Inventors ──
    inventors_xml = ""
    for i, inv in enumerate(data.inventors, start=1):
        inventors_xml += _build_inventor_xml(inv, i)

    # If no inventors, include one empty block (form requires at least one)
    if not data.inventors:
        inventors_xml = (
            "<sfApplicantInformation>"
            "<sfAuth><appSeq>1</appSeq></sfAuth>"
            "<sfApplicantName><prefix/><suffix/></sfApplicantName>"
            "<sfAppResChk>"
            "<resCheck><ResidencyRadio/></resCheck>"
            "<sfUSres><rsCityTxt/><rsStTxt/><rsCtryTxt/></sfUSres>"
            "<sfNonUSRes><nonresCity/><nonresCtryList/></sfNonUSRes>"
            "<sfMil><actMilDropDown/></sfMil>"
            "</sfAppResChk>"
            "<sfCitz><CitizedDropDown/></sfCitz>"
            "<sfApplicantMail><mailCountry/><postcode/><address1/><address2/><city/><state/></sfApplicantMail>"
            "<sfInventorRepInfo>"
            "<sfReporgChoice><chkOrg/><org><orgName/></org>"
            "<sfRepApplicantName><prefix/><firstName/><middleName/><lastName/><suffix/></sfRepApplicantName>"
            "</sfReporgChoice>"
            "<sfRepAppResChk><resCheck/>"
            "<sfUSres><rsCityTxt/><rsStTxt/><rsCtryTxt/></sfUSres>"
            "<sfNonUSRes><nonresCity/><nonresCtryList/></sfNonUSRes>"
            "<sfMil><actMilDropDown/></sfMil></sfRepAppResChk>"
            "<sfRepCitz><CitizedDropDown/></sfRepCitz>"
            "<sfRepApplicantMail><address1/><address2/><city/><state/><postcode/><mailCountry/></sfRepApplicantMail>"
            "</sfInventorRepInfo>"
            "</sfApplicantInformation>"
        )

    content_area1 = (
        f"<ContentArea1>"
        f"<chkSecret>{'1' if data.secrecy_order else '0'}</chkSecret>"
        f"{inventors_xml}"
        f"</ContentArea1>"
    )

    # ── ContentArea2: Everything else ──

    # Correspondence
    has_corr_address = bool(data.corr_customer_number or data.corr_address1 or data.corr_name1)
    corr_info_chk = "1" if has_corr_address else "0"

    correspondence_xml = (
        f"<sfCorrepondInfo><corresInfoChk>{corr_info_chk}</corresInfoChk></sfCorrepondInfo>"
        f"<sfCorrCustNo>{_tag('customerNumber', data.corr_customer_number)}</sfCorrCustNo>"
        f"<sfCorrAddress>"
        f"{_tag('Name1', data.corr_name1)}"
        f"{_tag('Name2', data.corr_name2)}"
        f"{_tag('address1', data.corr_address1)}"
        f"{_tag('address2', data.corr_address2)}"
        f"{_tag('city', data.corr_city)}"
        f"{_tag('state', data.corr_state)}"
        f"{_tag('corrCountry', _country_to_code(data.corr_country))}"
        f"{_tag('postcode', data.corr_postcode)}"
        f"{_tag('phone', data.corr_phone)}"
        f"{_tag('fax', data.corr_fax)}"
        f"</sfCorrAddress>"
        f"<sfemail>{_tag('email', data.corr_email)}</sfemail>"
    )

    # Application info - FIXED: sfInvTitle now contains invention-title (not inventionTitle)
    entity_val = _entity_status_value(data.entity_status)
    app_info_xml = (
        f"<sfInvTitle>{_tag('invention-title', data.title)}</sfInvTitle>"
        f"<sfversion/>"
        f"<sfAppinfoFlow><sfAppPos>"
        f"<chkSmallEntity>{entity_val}</chkSmallEntity>"
        f"<class/><subclass/>"
        f"<us_suggested-tech_center/>"
        f"{_tag('us-total_number_of_drawing-sheets', data.total_drawing_sheets)}"
        f"{_tag('us-suggested_representative_figure', data.suggested_figure)}"
        f"{_tag('application_type', data.application_type)}"
        f"<us_submission_type/>"
        f"</sfAppPos></sfAppinfoFlow>"
    )

    # Plant (always empty for utility)
    plant_xml = "<sfPlant><latin_name/><variety/></sfPlant>"

    # Filing by reference (almost always blank)
    filing_by_xml = "<sffilingby><app/><date/><intellectual/></sffilingby>"

    # Publication
    pub_xml = "<sfPub><early>0</early><nonPublication/></sfPub>"

    # Representative info
    rep_choice = "customer-number" if data.rep_customer_number else "customer-number"
    rep_xml = (
        f"<sfRepHeader/>"
        f"<sfAttorny>"
        f"<sfrepheader><attornyChoice>{rep_choice}</attornyChoice></sfrepheader>"
        f"<sfAttornyFlow>"
        f"<sfcustomerNumber>{_tag('customerNumberTxt', data.rep_customer_number)}</sfcustomerNumber>"
        f"<sfAttrynyName>"
        f"<prefix/><first-name/><middle-name/><last-name/><suffix/>"
        f"<attrnyRegNameTxt/><attsequence>1</attsequence>"
        f"</sfAttrynyName>"
        f"<sfrepcfr119>"
        f"<repcfr119RegNameTxt/><prefix/><first-name/><middle-name/><last-name/><suffix/>"
        f"<repsequence>1</repsequence>"
        f"</sfrepcfr119>"
        f"</sfAttornyFlow>"
        f"</sfAttorny>"
    )

    # Domestic continuity (empty default)
    domestic_xml = (
        "<sfDomContinuityHeader/>"
        "<sfDomesticContinuity>"
        "<sfDomesContinuity><sfdomesContAppStat>"
        "<domAppStatusList/><domsequence>1</domsequence>"
        "</sfdomesContAppStat></sfDomesContinuity>"
        "<sfDomesContInfo><domappNumber/><domesContList/><domPriorAppNum/><DateTimeField1/></sfDomesContInfo>"
        "<sfDomesContinfoPatent>"
        "<patAppNum/><domesContList/><patContType/><patprDate/><patPatNum/><patIsDate/>"
        "</sfDomesContinfoPatent>"
        "</sfDomesticContinuity>"
    )

    # Foreign priority (empty default)
    foreign_xml = (
        "<sfForeignPriorityHeader/>"
        "<sfForeignPriorityInfo>"
        "<frprAppNum/><accessCode/><frprctryList/><frprParentDate/>"
        "<prClaim/><forsequence>1</forsequence>"
        "</sfForeignPriorityInfo>"
    )

    # Permit / AIA / Authorization
    permit_xml = (
        "<sfpermit><check/></sfpermit>"
        "<AIATransition><AIACheck>0</AIACheck></AIATransition>"
        "<authorization><IP>0</IP><EPO>0</EPO></authorization>"
    )

    # ── Applicant Information (sfAssigneeInformation) — Bug 4 fix ──
    applicants_xml = "<sfAssigneeHeader/>"
    if data.applicants:
        for i, app in enumerate(data.applicants, start=1):
            applicants_xml += _build_applicant_xml(app, i)
    else:
        # Include empty structural block even with no applicants
        applicants_xml += (
            "<sfAssigneeInformation>"
            "<sfAssigneebtn><appSeq>1</appSeq><lstInvType/><LegalRadio/></sfAssigneebtn>"
            "<sfAssigneorgChoice><chkOrg>0</chkOrg><sforgName><orgName/></sforgName></sfAssigneorgChoice>"
            "<sfApplicantName><prefix/><first-name/><middle-name/><last-name/><suffix/></sfApplicantName>"
            "<sfAssigneeAddress>"
            "<address-1/><address-2/><city/><state/><postcode/><phone/><fax/><txtCorrCtry/>"
            "</sfAssigneeAddress>"
            "<sfAssigneeEmail/>"
            "</sfAssigneeInformation>"
        )

    # ── Non-Applicant Assignee (Bug 6 fix: always include this section) ──
    non_applicant_xml = (
        "<NonApplicantHeader/>"
        "<sfNonApplicantInfo>"
        "<sfNonAsigneeBtn><appSeq>1</appSeq></sfNonAsigneeBtn>"
        "<sfNonapplicantOrg><chkOrg>0</chkOrg><sfNonOrg><orgName/></sfNonOrg></sfNonapplicantOrg>"
        "<sfApplicantName><prefix/><first-name/><middle-name/><last-name/><suffix/></sfApplicantName>"
        "<sfAssigneeAddress>"
        "<address-1/><address-2/><city/><state/><postcode/><phone/><fax/><txtCorrCtry/><email/>"
        "</sfAssigneeAddress>"
        "</sfNonApplicantInfo>"
    )

    # ── Signature ──
    signature_xml = (
        f"<sfSignature>"
        f"<sfSig>"
        f"{_tag('registration-number', data.sig_registration_number)}"
        f"{_tag('last-name', data.sig_last_name)}"
        f"{_tag('signature')}"
        f"{_tag('date', data.sig_date)}"
        f"{_tag('first-name', data.sig_first_name)}"
        f"</sfSig>"
        f"</sfSignature>"
    )

    content_area2 = (
        f"<ContentArea2>"
        f"{correspondence_xml}"
        f"{app_info_xml}"
        f"{plant_xml}"
        f"{filing_by_xml}"
        f"{pub_xml}"
        f"{rep_xml}"
        f"{domestic_xml}"
        f"{foreign_xml}"
        f"{permit_xml}"
        f"{applicants_xml}"
        f"{non_applicant_xml}"
        f"{signature_xml}"
        f"</ContentArea2>"
    )

    # ── ContentArea3: EMPTY (as per original USPTO template) ──
    content_area3 = "<ContentArea3/>"

    # ── Assemble complete datasets XML ──
    # CRITICAL FIX: invention-title and attorney-docket-number are at ROOT level
    datasets_xml = (
        '<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/">'
        '<xfa:data>'
        '<us-request>'
        f'{content_area1}'
        f'{content_area2}'
        f'{content_area3}'
        f'{_tag("invention-title", data.title)}'
        f'{_tag("attorney-docket-number", data.attorney_docket_number)}'
        '<version-info>2.1</version-info>'
        '<clientversion>21.00720099</clientversion>'
        '<numofpages>8</numofpages>'
        '</us-request>'
        '</xfa:data>'
        '</xfa:datasets>'
    )

    return datasets_xml


# ─── Convenience: Build from your existing data model ───────────────────────────
# Adapt this function to bridge YOUR current PatentApplicationMetadata model
# to the ApplicationData model above.

def build_from_patent_metadata(metadata) -> str:
    """
    Bridge function: converts your existing PatentApplicationMetadata object
    to the corrected XFA XML.

    Adapt the attribute names below to match your actual data model.
    """
    data = ApplicationData()
    data.title = getattr(metadata, 'title', '') or ''
    data.attorney_docket_number = getattr(metadata, 'attorney_docket_number', '') or ''
    data.application_type = getattr(metadata, 'application_type', '') or ''
    data.total_drawing_sheets = str(getattr(metadata, 'total_drawing_sheets', '') or '')
    data.suggested_figure = str(getattr(metadata, 'suggested_figure', '') or '')

    # Entity status
    entity = getattr(metadata, 'entity_status', '') or ''
    data.entity_status = entity

    # ── NEW: Correspondence Address ────────────────────────────────────────────
    corr = getattr(metadata, 'correspondence_address', None)
    if corr:
        data.corr_name1 = getattr(corr, 'name', '') or ''
        data.corr_name2 = getattr(corr, 'name2', '') or ''
        data.corr_address1 = getattr(corr, 'address1', '') or ''
        data.corr_address2 = getattr(corr, 'address2', '') or ''
        data.corr_city = getattr(corr, 'city', '') or ''
        data.corr_state = getattr(corr, 'state', '') or ''
        data.corr_country = _country_to_code(getattr(corr, 'country', '') or '')
        data.corr_postcode = getattr(corr, 'postcode', '') or ''
        data.corr_phone = getattr(corr, 'phone', '') or ''
        data.corr_fax = getattr(corr, 'fax', '') or ''
        data.corr_email = getattr(corr, 'email', '') or ''
        data.corr_customer_number = getattr(corr, 'customer_number', '') or ''
    # ──────────────────────────────────────────────────────────────────────────

    # Inventors
    for inv in getattr(metadata, 'inventors', []):
        data.inventors.append(InventorInfo(
            first_name=getattr(inv, 'first_name', '') or '',
            middle_name=getattr(inv, 'middle_name', '') or '',
            last_name=getattr(inv, 'last_name', '') or '',

            # CRITICAL: These must be the RESIDENCE fields, not citizenship
            residence_city=getattr(inv, 'city', '') or getattr(inv, 'residence_city', '') or '',
            residence_state=getattr(inv, 'state', '') or getattr(inv, 'residence_state', '') or '',
            residence_country=getattr(inv, 'country', '') or getattr(inv, 'residence_country', '') or '',

            # Citizenship is separate
            citizenship=getattr(inv, 'citizenship', '') or '',

            # Mailing address (often same as residence)
            mail_address1=getattr(inv, 'street_address', '') or getattr(inv, 'mail_address1', '') or '',
            mail_address2=getattr(inv, 'address2', '') or getattr(inv, 'mail_address2', '') or '',
            mail_city=getattr(inv, 'city', '') or '',
            mail_state=getattr(inv, 'state', '') or '',
            mail_postcode=getattr(inv, 'zip_code', '') or getattr(inv, 'postcode', '') or '',
            mail_country=getattr(inv, 'country', '') or '',
        ))

    # Applicants / companies
    for app in getattr(metadata, 'applicants', []):
        data.applicants.append(ApplicantInfo(
            is_organization=True,  # Adjust if you support individual applicants
            org_name=getattr(app, 'name', '') or getattr(app, 'org_name', '') or '',
            authority=getattr(app, 'authority', 'assignee') or 'assignee',
            address1=getattr(app, 'street_address', '') or getattr(app, 'address1', '') or '',
            address2=getattr(app, 'address2', '') or '',
            city=getattr(app, 'city', '') or '',
            state=getattr(app, 'state', '') or '',
            postcode=getattr(app, 'zip_code', '') or getattr(app, 'postcode', '') or '',
            country=getattr(app, 'country', '') or '',
            phone=getattr(app, 'phone', '') or '',
            email=getattr(app, 'email', '') or '',
        ))

    return build_ads_datasets_xml(data)


# ─── Test / Demo ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Demonstrate with the exact data from the user's UI screenshots.
    This recreates the scenario and shows the corrected output.
    """
    data = ApplicationData(
        title="Machine Learning System for Real-Time Biomedical Image Analysis and Diagnostic Prediction Using Deep Neural Networks",
        total_drawing_sheets="15",
        entity_status="undiscounted",  # Large Entity
        application_type="utility",

        inventors=[
            InventorInfo(
                first_name="Emily", middle_name="Rose", last_name="Patterson",
                residence_city="Boston", residence_state="MA", residence_country="United States",
                citizenship="US",
                mail_address1="2847 Medical Center Drive",
                mail_city="Boston", mail_state="MA", mail_postcode="02115",
                mail_country="United States",
            ),
            InventorInfo(
                first_name="David", middle_name="Lee", last_name="Thompson",
                residence_city="Cambridge", residence_state="MA", residence_country="United States",
                citizenship="US",
                mail_address1="1523 University Avenue, Unit 12B",
                mail_city="Cambridge", mail_state="MA", mail_postcode="02138",
                mail_country="United States",
            ),
            InventorInfo(
                first_name="Raj", middle_name="Kumar", last_name="Sharma",
                # Lives in US but is Indian citizen — Bug 1 scenario
                residence_city="San Francisco", residence_state="CA", residence_country="United States",
                citizenship="India",  # ← citizenship ≠ residence!
                mail_address1="4891 Innovation Boulevard",
                mail_city="San Francisco", mail_state="CA", mail_postcode="94103",
                mail_country="United States",
            ),
            InventorInfo(
                first_name="Maria", middle_name="Gabriela", last_name="Rodriguez",
                residence_city="Palo Alto", residence_state="CA", residence_country="United States",
                citizenship="US",
                mail_address1="756 Research Park Circle, Apt 8",
                mail_city="Palo Alto", mail_state="CA", mail_postcode="94301",
                mail_country="United States",
            ),
        ],

        applicants=[
            ApplicantInfo(
                is_organization=True,
                org_name="MedTech Innovations Corporation",
                authority="assignee",
                address1="15000 Biomedical Research Parkway, Tower A, 8th Floor",
                city="San Diego", state="California", postcode="92121",
                country="United States of America",
            ),
            # Bug 4 fix: Second company now included!
            ApplicantInfo(
                is_organization=True,
                org_name="Global Health Analytics Ltd.",
                authority="assignee",
                address1="42 Harley Street, Medical Wing, 3rd Floor",
                city="London", state="Greater London", postcode="W1G 9PR",
                country="United Kingdom",
            ),
        ],
    )

    xml = build_ads_datasets_xml(data)

    # Pretty print for verification
    from xml.dom.minidom import parseString
    pretty = parseString(xml).toprettyxml(indent="  ")
    print(pretty)

    # Save raw XML
    with open("corrected_datasets.xml", "w") as f:
        f.write(xml)
    print("\n✅ Saved to corrected_datasets.xml")
