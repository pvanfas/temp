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
        fields = (
            "name",
            "year",
            "applicants_count",
            "code",
            "bulk_id_card",
            "bulk_reciepts",
            "bulk_tags",
            # "amount",
            # "subtotal",
            # "payment_bank_total",
            # "payment_cash_total",
            # "voucher_total",
            # "cash_balance",
        )
        attrs = {"class": "table key-buttons border-bottom table-hover nowrap"}  # noqa: RUF012


class ApplicantTable(BaseTable):
    action = columns.TemplateColumn(template_name="umrah/partials/applicant_table_actions.html", orderable=False)

    class Meta:
        model = Applicant
        fields = (
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
    class Meta:
        model = UmrahPayment
        fields = ("reciept_number", "applicant", "amount", "date", "mode", "reciept")
        attrs = {"class": "table key-buttons border-bottom table-hover"}  # noqa: RUF012


class PaymentPurposeTable(BaseTable):
    class Meta:
        model = PaymentPurpose
        fields = ("name",)
        attrs = {"class": "table key-buttons border-bottom table-hover"}  # noqa: RUF012


class VoucherTable(BaseTable):
    class Meta:
        model = Voucher
        fields = ("voucher_number", "batch", "amount", "date", "purpose", "voucher")
        attrs = {"class": "table key-buttons border-bottom table-hover"}  # noqa: RUF012
