
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, ngettext
from django.utils import timezone
from num2words import num2words

from core.mixins import HybridCreateView, HybridDeleteView, HybridDetailView, HybridListView, HybridTemplateView, HybridUpdateView
from core.pdfview import PDFView

from .forms import UmrahPaymentForm
from .models import Agency, Applicant, Batch, PaymentPurpose, UmrahPayment, Voucher
from .tables import AgencyTable, ApplicantTable, BatchTable, PaymentPurposeTable, UmrahPaymentTable, VoucherTable


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


# Umrah Payments
class UmrahPaymentCreateView(HybridCreateView):
    model = UmrahPayment


class UmrahPaymentDetailView(HybridDetailView):
    model = UmrahPayment


class UmrahPaymentUpdateView(HybridUpdateView):
    model = UmrahPayment


class UmrahPaymentDeleteView(HybridDeleteView):
    model = UmrahPayment


class UmrahPaymentListView(HybridListView):
    model = UmrahPayment
    filterset_fields = ("applicant", "applicant__batch", "applicant__agency", "is_archived")
    table_class = UmrahPaymentTable
    search_fields = ("applicant",)
    title = "Payment Receipts"
    exclude_columns = ("pk", "action", "reciept")
    metadata = {
        "actions": [
            {"label": _("Archive selected"), "value": "archive"},
            {"label": _("Print selected"), "value": "print"},
        ]
    }

    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        selected_raw = request.POST.get("selected_objects", "")
        selected_ids = [value.strip() for value in selected_raw.split(",") if value.strip()]

        if action == "print":
            if not selected_ids:
                messages.warning(request, _("Select at least one payment before printing."))
                return redirect(request.get_full_path())

            # Redirect to print view with selected payment IDs
            ids_param = "&".join([f"ids={pid}" for pid in selected_ids])
            print_url = reverse("umrah:print_selected_payments") + "?" + ids_param
            return redirect(print_url)

        if action == "archive":
            if not selected_ids:
                messages.warning(request, _("Select at least one payment before running the action."))
                return redirect(request.get_full_path())

            queryset = self.model.objects.filter(pk__in=selected_ids, is_archived=False)
            updated = queryset.update(is_archived=True)

            if updated:
                messages.success(
                    request,
                    ngettext(
                        "%d payment was archived successfully.",
                        "%d payments were archived successfully.",
                        updated,
                    )
                    % updated,
                )
            else:
                messages.info(request, _("No payments were archived. They might already be archived."))

            return redirect(request.get_full_path())

        messages.warning(request, _("Please choose a valid action."))
        return redirect(request.get_full_path())


class UmrahPaymentArchivedListView(HybridListView):
    model = UmrahPayment
    filterset_fields = ("applicant", "is_archived")
    table_class = UmrahPaymentTable
    search_fields = ("applicant",)
    title = "Archived Umrah Payments"
    exclude_columns = ("pk", "action", "reciept")
    metadata = {
        "actions": [
            {"label": _("Unarchive selected"), "value": "unarchive"},
            {"label": _("Print selected"), "value": "print"},
        ]
    }

    def get_queryset(self):
        return super().get_queryset().filter(is_archived=True)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        selected_raw = request.POST.get("selected_objects", "")
        selected_ids = [value.strip() for value in selected_raw.split(",") if value.strip()]

        if action == "print":
            if not selected_ids:
                messages.warning(request, _("Select at least one payment before printing."))
                return redirect(request.get_full_path())
            
            # Redirect to print view with selected payment IDs
            ids_param = "&".join([f"ids={pid}" for pid in selected_ids])
            print_url = reverse("umrah:print_selected_payments") + "?" + ids_param
            return redirect(print_url)

        if action == "unarchive":
            if not selected_ids:
                messages.warning(request, _("Select at least one payment before running the action."))
                return redirect(request.get_full_path())

            queryset = self.model.objects.filter(pk__in=selected_ids, is_archived=True)
            updated = queryset.update(is_archived=False)

            if updated:
                messages.success(
                    request,
                    ngettext(
                        "%d payment was unarchived successfully.",
                        "%d payments were unarchived successfully.",
                        updated,
                    )
                    % updated,
                )
            else:
                messages.info(request, _("No payments were unarchived. They might already be unarchived."))

            return redirect(request.get_full_path())

        messages.warning(request, _("Please choose a valid action."))
        return redirect(request.get_full_path())


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


class PrintSelectedPayments(PDFView, LoginRequiredMixin):
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
        payment_ids = self.request.GET.getlist("ids")
        if not payment_ids:
            queryset = UmrahPayment.objects.none()
        else:
            queryset = UmrahPayment.objects.filter(pk__in=payment_ids).order_by("-created_at")
        context["queryset"] = queryset
        return context


# Vouchers
class VoucherCreateView(HybridCreateView):
    model = Voucher


class VoucherDetailView(HybridDetailView):
    model = Voucher


class VoucherUpdateView(HybridUpdateView):
    model = Voucher


class VoucherDeleteView(HybridDeleteView):
    model = Voucher


class VoucherListView(HybridListView):
    model = Voucher
    filterset_fields = ("voucher_number", "purpose", "batch", "batch__year", "amount", "date", "mode")
    table_class = VoucherTable
    search_fields = ("voucher_number",)
    title = "Vouchers"
    exclude_columns = ("pk", "action", "reciept")
    metadata = {
        "actions": [
            {"label": _("Archive selected"), "value": "archive"},
            {"label": _("Print selected"), "value": "print"},
        ]
    }

    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        selected_raw = request.POST.get("selected_objects", "")
        selected_ids = [value.strip() for value in selected_raw.split(",") if value.strip()]

        if action == "print":
            if not selected_ids:
                messages.warning(request, _("Select at least one voucher before printing."))
                return redirect(request.get_full_path())

            # Redirect to print view with selected voucher IDs
            ids_param = "&".join([f"ids={vid}" for vid in selected_ids])
            print_url = reverse("umrah:print_selected_vouchers") + "?" + ids_param
            return redirect(print_url)

        if action == "archive":
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

            return redirect(request.get_full_path())

        messages.warning(request, _("Please choose a valid action."))
        return redirect(request.get_full_path())


class VoucherArchivedListView(HybridListView):
    model = Voucher
    filterset_fields = ("voucher_number", "batch", "batch__year", "amount", "date", "mode")
    table_class = VoucherTable
    search_fields = ("voucher_number",)
    title = "Archived Vouchers"
    exclude_columns = ("pk", "action", "reciept")
    metadata = {
        "actions": [
            {"label": _("Unarchive selected"), "value": "unarchive"},
            {"label": _("Print selected"), "value": "print"},
        ]
    }

    def get_queryset(self):
        return super().get_queryset().filter(is_archived=True)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        selected_raw = request.POST.get("selected_objects", "")
        selected_ids = [value.strip() for value in selected_raw.split(",") if value.strip()]

        if action == "print":
            if not selected_ids:
                messages.warning(request, _("Select at least one voucher before printing."))
                return redirect(request.get_full_path())
            
            # Redirect to print view with selected voucher IDs
            ids_param = "&".join([f"ids={vid}" for vid in selected_ids])
            print_url = reverse("umrah:print_selected_vouchers") + "?" + ids_param
            return redirect(print_url)

        if action == "unarchive":
            if not selected_ids:
                messages.warning(request, _("Select at least one voucher before running the action."))
                return redirect(request.get_full_path())

            queryset = self.model.objects.filter(pk__in=selected_ids, is_archived=True)
            updated = queryset.update(is_archived=False)

            if updated:
                messages.success(
                    request,
                    ngettext(
                        "%d voucher was unarchived successfully.",
                        "%d vouchers were unarchived successfully.",
                        updated,
                    )
                    % updated,
                )
            else:
                messages.info(request, _("No vouchers were unarchived. They might already be unarchived."))

            return redirect(request.get_full_path())

        messages.warning(request, _("Please choose a valid action."))
        return redirect(request.get_full_path())


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


class PrintSelectedVouchers(PDFView, LoginRequiredMixin):
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
        voucher_ids = self.request.GET.getlist("ids")
        if not voucher_ids:
            queryset = Voucher.objects.none()
        else:
            queryset = Voucher.objects.filter(pk__in=voucher_ids).order_by("voucher_number")
        context["queryset"] = queryset
        return context


class CashDaybookView(HybridTemplateView):
    template_name = "umrah/daybook.html"
    title = "Cash Daybook"

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        start_date = self._parse_date(self.request.GET.get("start_date")) or today.replace(day=1)
        end_date = self._parse_date(self.request.GET.get("end_date")) or today

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        base_payments = (
            UmrahPayment.objects.filter(mode="CASH", is_active=True)
            .select_related("applicant", "applicant__batch")
        )
        base_vouchers = (
            Voucher.objects.filter(mode="CASH", is_active=True)
            .select_related("batch", "purpose")
        )

        payments = base_payments.filter(date__range=(start_date, end_date))
        vouchers = base_vouchers.filter(date__range=(start_date, end_date))

        payments_before = base_payments.filter(date__lt=start_date).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        vouchers_before = base_vouchers.filter(date__lt=start_date).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        opening_balance = Decimal("849255.00") if (start_date.month == 4 and start_date.day == 1) else payments_before - vouchers_before

        entries = []
        zero = Decimal("0.00")

        for payment in payments:
            applicant = payment.applicant
            batch_name = applicant.batch.name if applicant and applicant.batch else "-"
            entries.append(
                {
                    "date": payment.date,
                    "label": _("Receipt"),
                    "number": payment.reciept_number or "-",
                    "batch": batch_name,
                    "head": applicant.get_name() if applicant else "-",
                    "credit": payment.amount,
                    "debit": zero,
                    "notes": payment.notes,
                    "created_at": payment.created_at,
                    "sort_index": 0,
                }
            )

        for voucher in vouchers:
            batch = voucher.batch
            entries.append(
                {
                    "date": voucher.date,
                    "label": _("Voucher"),
                    "number": voucher.voucher_number or "-",
                    "batch": batch.name if batch else "-",
                    "head": voucher.purpose.name if voucher.purpose else "-",
                    "credit": zero,
                    "debit": voucher.amount,
                    "notes": voucher.notes,
                    "created_at": voucher.created_at,
                    "sort_index": 1,
                }
            )

        entries.sort(key=lambda item: (item["date"], item["created_at"], item["sort_index"]))

        running_balance = opening_balance
        total_credit = zero
        total_debit = zero
        daily_totals = OrderedDict()
        monthly_totals = OrderedDict()

        for entry in entries:
            credit = entry["credit"]
            debit = entry["debit"]

            total_credit += credit
            total_debit += debit
            running_balance += credit
            running_balance -= debit
            entry["balance"] = running_balance

            day_key = entry["date"]
            if day_key not in daily_totals:
                daily_totals[day_key] = {"credit": zero, "debit": zero, "closing": zero}
            daily_totals[day_key]["credit"] += credit
            daily_totals[day_key]["debit"] += debit
            daily_totals[day_key]["closing"] = running_balance

            month_key = day_key.replace(day=1)
            if month_key not in monthly_totals:
                monthly_totals[month_key] = {"label": day_key.strftime("%B %Y"), "credit": zero, "debit": zero, "closing": zero}
            monthly_totals[month_key]["credit"] += credit
            monthly_totals[month_key]["debit"] += debit
            monthly_totals[month_key]["closing"] = running_balance

        context.update(
            {
                "entries": entries,
                "filters": {"start_date": start_date, "end_date": end_date},
                "opening_balance": opening_balance,
                "closing_balance": running_balance,
                "total_credit": total_credit,
                "total_debit": total_debit,
                "daily_summary": [{"date": key, **values} for key, values in daily_totals.items()],
                "monthly_summary": [{"month": key, **values} for key, values in monthly_totals.items()],
            }
        )
        return context


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
