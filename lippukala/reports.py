import time
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse

from lippukala.models import Code


class CodeReportWriter:

    def __init__(self, code_queryset):
        self.code_queryset = code_queryset

    def get_fields_iterator(self):
        return ((code.full_code, code.literate_code, "Käytetty %s" % code.used_on if code.used_on else "") for code in
                self.code_queryset.iterator())

    def get_report(self, format, as_response):
        format = str(format).lower()
        filename = "code_report_%d.%s" % (time.time(), format)
        format_writer = getattr(self, "format_%s_report" % format, None)
        if not format_writer:  # pragma: no cover
            raise ValueError("Unknown format: %r" % format)
        return format_writer(filename=filename, as_response=as_response)

    def format_xls_report(self, filename, as_response):
        import xlwt
        workbook = xlwt.Workbook("UTF-8")
        sheet = workbook.add_sheet("Koodit")
        y = 0
        for fields in self.get_fields_iterator():
            for x, val in enumerate(fields):
                sheet.write(y, x, val)
            y += 1

        sio = BytesIO()
        workbook.save(sio)

        if as_response:
            response = HttpResponse(sio.getvalue(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = "attachment; filename=%s" % filename
            return response
        else:
            return sio.getvalue()

    def _format_delimited_report(self, filename, as_response, field_delimiter=";", record_delimiter="\r\n"):
        content_type = "text/csv; charset=%s" % settings.DEFAULT_CHARSET

        iterator = (field_delimiter.join(fields) + record_delimiter for fields in self.get_fields_iterator())
        if as_response:
            response = HttpResponse(iterator, content_type=content_type)
            response["Content-Disposition"] = "attachment; filename=%s" % filename
            return response
        else:
            return ("".join(iterator)).encode(settings.DEFAULT_CHARSET)

    def format_csv_report(self, filename, as_response):
        return self._format_delimited_report(filename, as_response, field_delimiter=";")

    def format_tsv_report(self, filename, as_response):
        return self._format_delimited_report(filename, as_response, field_delimiter="\t")

    def format_pdf_report(self, filename, as_response):
        from reportlab.pdfgen.canvas import Canvas
        sio = BytesIO()
        c = Canvas(sio)
        c.save()

        if as_response:
            response = HttpResponse(sio.getvalue(), content_type="application/pdf")
            response["Content-Disposition"] = "attachment; filename=%s" % filename
            return response
        else:
            return sio.getvalue()


def get_code_report(format, as_response, order_by_literate_code=False):
    if order_by_literate_code:
        order_by_tuple = ("literate_code",)
    else:
        order_by_tuple = ("prefix", "code")
    code_queryset = Code.objects.order_by(*order_by_tuple)
    rw = CodeReportWriter(code_queryset)
    return rw.get_report(format, as_response)
