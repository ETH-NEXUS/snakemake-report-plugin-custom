# from typing import Optional
# import snakemake.common.tests
# from snakemake_interface_report_plugins.settings import ReportSettingsBase


# Check out the base classes found here for all possible options and methods:
# https://github.com/snakemake/snakemake/blob/main/snakemake/common/tests/__init__.py
# seems to be not functional for now, come back to this later
# class TestWorkflowsBase(snakemake.common.tests.TestReportBase):
#    __test__ = True
#
#    def get_reporter(self) -> str:
#        return "custom"
#
#    def get_report_settings(self) -> Optional[ReportSettingsBase]:
#        # instantiate ReportSettings of this plugin as appropriate
#        ...
def test_mock():
    assert True
