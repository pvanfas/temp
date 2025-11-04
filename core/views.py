from .mixins import HybridCreateView, HybridDeleteView, HybridDetailView, HybridListView, HybridTemplateView, HybridUpdateView
from .models import Country, Department, Designation, District, Language, State, Unit, Year, Zone
from .tables import CountryTable, DepartmentTable, DesignationTable, DistrictTable, LanguageTable, StateTable, UnitTable, YearTable, ZoneTable


class DashboardView(HybridTemplateView):
    template_name = "app/main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CountryListView(HybridListView):
    model = Country
    filterset_fields = ("name",)
    table_class = CountryTable
    search_fields = ("name", "code")


class CountryCreateView(HybridCreateView):
    model = Country


class CountryDetailView(HybridDetailView):
    model = Country


class CountryUpdateView(HybridUpdateView):
    model = Country


class CountryDeleteView(HybridDeleteView):
    model = Country


class DepartmentListView(HybridListView):
    model = Department
    filterset_fields = ("name",)
    table_class = DepartmentTable
    search_fields = ("name",)


class DepartmentCreateView(HybridCreateView):
    model = Department


class DepartmentDetailView(HybridDetailView):
    model = Department


class DepartmentUpdateView(HybridUpdateView):
    model = Department


class DepartmentDeleteView(HybridDeleteView):
    model = Department


class DesignationListView(HybridListView):
    model = Designation
    filterset_fields = ("name",)
    table_class = DesignationTable
    search_fields = ("name",)


class DesignationCreateView(HybridCreateView):
    model = Designation


class DesignationDetailView(HybridDetailView):
    model = Designation


class DesignationUpdateView(HybridUpdateView):
    model = Designation


class DesignationDeleteView(HybridDeleteView):
    model = Designation


class YearListView(HybridListView):
    model = Year
    filterset_fields = ("name",)
    table_class = YearTable
    search_fields = ("name",)


class YearCreateView(HybridCreateView):
    model = Year


class YearDetailView(HybridDetailView):
    model = Year


class YearUpdateView(HybridUpdateView):
    model = Year


class YearDeleteView(HybridDeleteView):
    model = Year


class LanguageListView(HybridListView):
    model = Language
    filterset_fields = ("name",)
    table_class = LanguageTable
    search_fields = ("name", "family", "native_name", "lang_code")


class LanguageCreateView(HybridCreateView):
    model = Language


class LanguageDetailView(HybridDetailView):
    model = Language


class LanguageUpdateView(HybridUpdateView):
    model = Language


class LanguageDeleteView(HybridDeleteView):
    model = Language


class StateListView(HybridListView):
    model = State
    filterset_fields = ("name", "state_code", "tin_number")
    table_class = StateTable
    search_fields = ("name", "state_code", "tin_number")


class StateCreateView(HybridCreateView):
    model = State


class StateDetailView(HybridDetailView):
    model = State


class StateUpdateView(HybridUpdateView):
    model = State


class StateDeleteView(HybridDeleteView):
    model = State


class DistrictListView(HybridListView):
    model = District
    filterset_fields = ("name",)
    table_class = DistrictTable
    search_fields = ("name", "state")


class DistrictCreateView(HybridCreateView):
    model = District


class DistrictDetailView(HybridDetailView):
    model = District


class DistrictUpdateView(HybridUpdateView):
    model = District


class DistrictDeleteView(HybridDeleteView):
    model = District


class ZoneListView(HybridListView):
    model = Zone
    filterset_fields = ("name",)
    table_class = ZoneTable
    search_fields = ("name", "district")


class ZoneCreateView(HybridCreateView):
    model = Zone


class ZoneDetailView(HybridDetailView):
    model = Zone


class ZoneUpdateView(HybridUpdateView):
    model = Zone


class ZoneDeleteView(HybridDeleteView):
    model = Zone


class UnitListView(HybridListView):
    model = Unit
    table_class = UnitTable
    search_fields = ("zone",)
    filterset_fields = ("name",)


class UnitCreateView(HybridCreateView):
    model = Unit


class UnitDetailView(HybridDetailView):
    model = Unit


class UnitUpdateView(HybridUpdateView):
    model = Unit


class UnitDeleteView(HybridDeleteView):
    model = Unit
