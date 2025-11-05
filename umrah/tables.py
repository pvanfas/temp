from django_tables2 import columns

from core.base import BaseTable

from .models import Agency, Applicant, Batch, PaymentPurpose, UmrahPayment, Voucher


class AgencyTable(BaseTable):
    class Meta:
        model = Agency
        fields = ("name", "applicants_count", "location", "mobile", "whatsapp")
        attrs = {"class": "table key-buttons border-bottom table-hover"}  # noqa: RUF012


class BatchTable(BaseTable):
    class Meta:
        model = Batch
        fields = ("name", "year", "applicants_count", "code", "bulk_id_card", "bulk_reciepts", "bulk_tags")
        attrs = {"class": "table key-buttons border-bottom table-hover nowrap"}  # noqa: RUF012


class ApplicantTable(BaseTable):
    action = columns.TemplateColumn(template_name="umrah/partials/applicant_table_actions.html", orderable=False)

    class Meta:
        model = Applicant
        fields = (
            "serial",
            "image_tag",
            "fullname",
            "whatsapp_link",
            "id_card",
            "passport_number",
            "expiry_validity",
            "balance_amount",
            "dob",
            "age",
            "gender",
            "total_amount",
            "discount",
            "payable_amount",
            "paid_amount",
        )
        attrs = {"class": "table key-buttons border-bottom table-hover"}  # noqa: RUF012


class UmrahPaymentTable(BaseTable):
    checkbox = columns.TemplateColumn(
        '<div class="checkbox-column"><div class="round"><input type="checkbox" id="checkbox-{{ record.pk }}" value="{{ record.pk }}" /><label for="checkbox-{{ record.pk }}"></label></div></div>',
        orderable=False,
    )
    applicant = columns.Column(accessor="applicant.fullname", orderable=False, linkify=True)

    class Meta:
        model = UmrahPayment
        fields = ("checkbox", "serial", "reciept_number", "applicant", "amount", "date", "mode", "reciept")
        attrs = {"class": "table key-buttons border-bottom table-hover"}  # noqa: RUF012
        sequence = ("checkbox", "serial", "...", "action")


class PaymentPurposeTable(BaseTable):
    class Meta:
        model = PaymentPurpose
        fields = (
            "serial",
            "name",
        )
        attrs = {"class": "table key-buttons border-bottom table-hover"}  # noqa: RUF012


class VoucherTable(BaseTable):
    checkbox = columns.TemplateColumn(
        '<div class="checkbox-column"><div class="round"><input type="checkbox" id="checkbox-{{ record.pk }}" value="{{ record.pk }}" /><label for="checkbox-{{ record.pk }}"></label></div></div>',
        orderable=False,
    )
    batch = columns.Column(verbose_name="Batch", orderable=True, linkify=True)

    class Meta:
        model = Voucher
        fields = ("checkbox", "serial", "voucher_number", "batch", "amount", "date", "purpose")
        attrs = {"class": "table key-buttons border-bottom table-hover"}  # noqa: RUF012
        sequence = ("checkbox", "serial", "...", "action")
