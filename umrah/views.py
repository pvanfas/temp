import calendar
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _, ngettext
from num2words import num2words

from core.mixins import HybridCreateView, HybridDeleteView, HybridDetailView, HybridListView, HybridUpdateView
from core.pdfview import PDFView

from .forms import UmrahPaymentForm
from .models import Agency, Applicant, Batch, PaymentPurpose, UmrahPayment, Voucher
from .tables import AgencyTable, ApplicantTable, BatchTable, PaymentPurposeTable, UmrahPaymentTable, VoucherTable


class IDCard(PDFView, LoginRequiredMixin):
    template_name = "umrah/id_card.html"
    pdfkit_options = {
        "page-height": "238",
        "page-width": "168",
        "encoding": "UTF-8",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        applicant = get_object_or_404(Applicant, pk=self.kwargs["pk"])
        context["object"] = applicant
        return context


class BulkIDCard(PDFView, LoginRequiredMixin):
    template_name = "umrah/bulk_id_card.html"
    pdfkit_options = {
        "page-height": "237.6",
        "page-width": "168",
        "encoding": "UTF-8",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        batch = get_object_or_404(Batch, pk=self.kwargs["pk"])
        queryset = Applicant.objects.filter(batch=batch)
        context["batch"] = batch
        context["queryset"] = queryset
        return context


class BulkTags(PDFView, LoginRequiredMixin):
    template_name = "umrah/bulk_tags.html"
    pdfkit_options = {
        "page-height": "292",
        "page-width": "112",
        "encoding": "UTF-8",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        batch = get_object_or_404(Batch, pk=self.kwargs["pk"])
        queryset = Applicant.objects.filter(batch=batch)
        context["batch"] = batch
        context["queryset"] = queryset
        return context


class Reciept(PDFView, LoginRequiredMixin):
    template_name = "umrah/reciept.html"
    pdfkit_options = {
        "page-height": "297",
        "page-width": "210",
        "encoding": "UTF-8",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        payment = get_object_or_404(UmrahPayment, pk=self.kwargs["pk"])
        context["object"] = payment
        context["amount"] = num2words(payment.amount, lang="en_IN").upper()
        return context


class BulkReciept(PDFView, LoginRequiredMixin):
    template_name = "umrah/bulk_reciepts.html"
    pdfkit_options = {
        "page-height": "297",
        "page-width": "210",
        "encoding": "UTF-8",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        batch = get_object_or_404(Batch, pk=self.kwargs["pk"])
        queryset = UmrahPayment.objects.filter(applicant__batch=batch)
        context["batch"] = batch
        context["queryset"] = queryset
        return context


class BulkVoucher(PDFView, LoginRequiredMixin):
    template_name = "umrah/bulk_vouchers.html"
    pdfkit_options = {
        "page-height": "297",
        "page-width": "210",
        "encoding": "UTF-8",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        batch = get_object_or_404(Batch, pk=self.kwargs["pk"])
        queryset = Voucher.objects.filter(batch=batch)
        context["batch"] = batch
        context["queryset"] = queryset
        return context


class VoucherView(PDFView, LoginRequiredMixin):
    template_name = "umrah/voucher.html"
    pdfkit_options = {
        "page-height": "297",
        "page-width": "210",
        "encoding": "UTF-8",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        voucher = get_object_or_404(Voucher, pk=self.kwargs["pk"])
        context["object"] = voucher
        context["amount"] = num2words(voucher.amount, lang="en_IN").upper()
        return context


@login_required
def daybook_view(request):
    # Convert month to an integer
    year = int(request.GET.get("year", datetime.now().year))
    month = int(request.GET.get("month", datetime.now().month))

    # Calculate the first day and last day of the selected month
    first_day = datetime(year, month, 1)
    days_in_month = calendar.monthrange(year, month)[1]
    last_day = datetime(year, month, days_in_month) + timedelta(days=1)

    # Filter payments and vouchers for the selected month
    payments = UmrahPayment.objects.filter(date__gte=first_day, date__lt=last_day)
    vouchers = Voucher.objects.filter(date__gte=first_day, date__lt=last_day)

    # Create a dictionary to store transactions for each day
    daywise_transactions = {}

    # Iterate through each day in the selected month
    current_day = first_day
    while current_day < last_day:
        # Filter payments and vouchers for the current day
        daily_payments = payments.filter(date=current_day)
        daily_vouchers = vouchers.filter(date=current_day)

        opening_bank_balance = 0
        opening_cash_balance = 0

        # Calculate the total income and expenses for the day
        total_bank_income = daily_payments.filter(mode="BANK").aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00")
        total_bank_expenses = daily_vouchers.filter(mode="BANK").aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00")
        total_cash_income = daily_payments.filter(mode="CASH").aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00")
        total_cash_expenses = daily_vouchers.filter(mode="CASH").aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00")

        daywise_transactions[current_day] = {
            "opening_bank_balance": (opening_bank_balance),
            "opening_cash_balance": (opening_cash_balance),
            "total_bank_income": "{:.2f}".format(total_bank_income),
            "total_bank_expenses": "{:.2f}".format(total_bank_expenses),
            "total_bank_balance": "{:.2f}".format(total_bank_income - total_bank_expenses),
            "total_cash_income": "{:.2f}".format(total_cash_income),
            "total_cash_expenses": "{:.2f}".format(total_cash_expenses),
            "total_cash_balance": "{:.2f}".format(total_cash_income - total_cash_expenses),
            "payments": daily_payments,
            "vouchers": daily_vouchers,
        }

        # Move to the next day
        current_day = current_day + timedelta(days=1)

    context = {
        "year": year,
        "month": datetime(year, month, 1).strftime("%B %Y"),  # Display the full month and year
        "daywise_transactions": daywise_transactions,
    }

    return render(request, "umrah/daybook.html", context)


class AgencyListView(HybridListView):
    model = Agency
    filterset_fields = ("name",)
    table_class = AgencyTable
    search_fields = ("name",)


class AgencyCreateView(HybridCreateView):
    model = Agency


class AgencyDetailView(HybridDetailView):
    model = Agency


class AgencyUpdateView(HybridUpdateView):
    model = Agency


class AgencyDeleteView(HybridDeleteView):
    model = Agency


class BatchListView(HybridListView):
    model = Batch
    filterset_fields = ("name", "is_completed")
    table_class = BatchTable
    search_fields = ("name",)
    exclude_columns = ("pk", "action", "bulk_id_card", "bulk_reciepts", "bulk_tags")


class BatchCreateView(HybridCreateView):
    model = Batch


class BatchDetailView(HybridDetailView):
    model = Batch


class BatchUpdateView(HybridUpdateView):
    model = Batch


class BatchDeleteView(HybridDeleteView):
    model = Batch


class AllApplicantListView(HybridListView):
    model = Applicant
    filterset_fields = ("first_name", "batch", "agency", "mobile", "gender", "mahram_relation", "batch__is_completed")
    table_class = ApplicantTable
    search_fields = ("first_name",)
    template_name = "umrah/applicant_list.html"
    table_pagination = {"per_page": 50}

    def get_form(self):
        last_obj = UmrahPayment.objects.order_by("created_at").last()
        print(last_obj.reciept_number)
        if last_obj.reciept_number[-3:].isdigit():
            reciept_number = last_obj.reciept_number[:-3] + str(int(last_obj.reciept_number[-3:]) + 1)
        else:
            reciept_number = None
        return UmrahPaymentForm(self.request.POST or None, initial={"reciept_number": reciept_number})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            data = form.save(commit=False)
            applicant_id = request.POST.get("applicant")
            applicant = get_object_or_404(Applicant, pk=applicant_id)
            data.applicant = applicant
            data.save()
        return self.get(request, *args, **kwargs)


class ApplicantListView(AllApplicantListView):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, batch__is_completed=False)


class ApplicantCreateView(HybridCreateView):
    model = Applicant


class ApplicantDetailView(HybridDetailView):
    model = Applicant
    template_name = "umrah/applicant_detail.html"


class ApplicantUpdateView(HybridUpdateView):
    model = Applicant


class ApplicantDeleteView(HybridDeleteView):
    model = Applicant


class UmrahPaymentListView(HybridListView):
    model = UmrahPayment
    filterset_fields = ("applicant",  "applicant__batch", "applicant__agency", "is_archived")
    table_class = UmrahPaymentTable
    search_fields = ("applicant",)
    title = "Payment Receipts"
    exclude_columns = ("pk", "action", "reciept")

    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)


class UmrahPaymentArchivedListView(HybridListView):
    model = UmrahPayment
    filterset_fields = ("applicant", "is_archived")
    table_class = UmrahPaymentTable
    search_fields = ("applicant",)
    title = "Archived Umrah Payments"

    def get_queryset(self):
        return super().get_queryset().filter(is_archived=True)


class UmrahPaymentCreateView(HybridCreateView):
    model = UmrahPayment


class UmrahPaymentDetailView(HybridDetailView):
    model = UmrahPayment


class UmrahPaymentUpdateView(HybridUpdateView):
    model = UmrahPayment


class UmrahPaymentDeleteView(HybridDeleteView):
    model = UmrahPayment


class PaymentPurposeListView(HybridListView):
    model = PaymentPurpose
    filterset_fields = ("name",)
    table_class = PaymentPurposeTable
    search_fields = ("name",)


class PaymentPurposeCreateView(HybridCreateView):
    model = PaymentPurpose


class PaymentPurposeDetailView(HybridDetailView):
    model = PaymentPurpose


class PaymentPurposeUpdateView(HybridUpdateView):
    model = PaymentPurpose


class PaymentPurposeDeleteView(HybridDeleteView):
    model = PaymentPurpose


class VoucherListView(HybridListView):
    model = Voucher
    filterset_fields = ("voucher_number","purpose", "batch", "batch__year", "amount", "date", "mode")
    table_class = VoucherTable
    search_fields = ("voucher_number",)
    title = "Vouchers"
    exclude_columns = ("pk", "action", "reciept")
    metadata = {
        "actions": [
            {"label": _("Archive selected"), "value": "archive"},
        ]
    }

    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        selected_raw = request.POST.get("selected_objects", "")
        selected_ids = [value.strip() for value in selected_raw.split(",") if value.strip()]

        if action != "archive":
            messages.warning(request, _("Please choose a valid action."))
            return redirect(request.get_full_path())

        if not selected_ids:
            messages.warning(request, _("Select at least one voucher before running the action."))
            return redirect(request.get_full_path())

        queryset = self.model.objects.filter(pk__in=selected_ids, is_archived=False)
        updated = queryset.update(is_archived=True)

        if updated:
            messages.success(
                request,
                ngettext(
                    "%d voucher was archived successfully.",
                    "%d vouchers were archived successfully.",
                    updated,
                )
                % updated,
            )
        else:
            messages.info(request, _("No vouchers were archived. They might already be archived."))

        return redirect(self.model.get_list_url())


class VoucherArchivedListView(HybridListView):
    model = Voucher
    filterset_fields = ("voucher_number", "batch", "batch__year", "amount", "date", "mode")
    table_class = VoucherTable
    search_fields = ("voucher_number",)
    title = "Archived Umrah Payments"

    def get_queryset(self):
        return super().get_queryset().filter(is_archived=True)


class VoucherCreateView(HybridCreateView):
    model = Voucher


class VoucherDetailView(HybridDetailView):
    model = Voucher


class VoucherUpdateView(HybridUpdateView):
    model = Voucher


class VoucherDeleteView(HybridDeleteView):
    model = Voucher
