from cStringIO import StringIO
from reportlab.lib.units import cm, mm
from reportlab.pdfgen.canvas import Canvas
from lippukala.settings import PRINT_LOGO_PATH, PRINT_LOGO_SIZE_CM
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.renderPDF import draw as draw_on_pdf


class Bold(unicode):
    pass


def draw_tabular(canvas, x0, y0, fontSize, leading, x_offsets, lines):
    y = y0
    for i, line in enumerate(lines):
        x = x0
        y -= leading
        for j, datum in enumerate(line):
            canvas.setFont("Helvetica-Bold" if isinstance(datum, Bold) else "Helvetica", fontSize)
            canvas.drawString(x, y, datum)
            if j <= len(x_offsets) - 1:
                x += x_offsets[j]
    return y


def draw_multiline(canvas, x0, y0, fontSize, leading, lines):
    return draw_tabular(canvas, x0, y0, fontSize, leading, (0, ), ((l,) for l in lines if l is not None))


class OrderPrinter(object):
    PAGE_WIDTH = 21.0 * cm
    PAGE_HEIGHT = 29.7 * cm
    PAGE_MARGIN_Y = 20 * mm
    PAGE_MARGIN_X = 18 * mm
    TEXT_Y = 80 * mm

    INTRA_TICKET_X_MARGIN = 5 * mm
    INTERTICKET_MARGIN = 0.5 * cm
    TICKET_HEIGHT = 3 * cm

    def __init__(self):
        self.output = StringIO()
        self.canvas = Canvas(self.output, pagesize=(self.PAGE_WIDTH, self.PAGE_HEIGHT))
        self.n_orders = 0

    def finish(self):
        self.canvas.save()
        return self.output.getvalue()

    def _align_draw_y(self, draw_y):
        resolution_cm = 0.5
        return int(draw_y / cm / resolution_cm) * resolution_cm * cm

    def _prime_new_order(self, order):
        canvas = self.canvas

        if self.n_orders > 0:
            canvas.showPage()
        self.n_orders += 1

        # Draw address
        y0 = self.PAGE_HEIGHT - 40 * mm
        x0 = 18 * mm

        if 0:
            canvas.setStrokeColor("silver")
            canvas.rect(x0, y0 - 35 * mm, 94 * mm, 35 * mm)

        canvas.setFillColor("black")
        fontSize = 13
        leading = fontSize * 1.3
        draw_multiline(canvas, x0 + 2 * mm, y0 - (1 * mm), fontSize, leading, order.address_text.splitlines())

        canvas.setFillColor("black")
        fontSize = 11
        leading = fontSize * 1.3

        draw_multiline(canvas, 115 * mm, y0 - (1 * mm), fontSize, leading, [
            (("Viitenumero: %s" % order.reference_number) if order.reference_number else None),
            "Tilausaika: %s" % order.created_on.strftime("%d.%m.%Y klo %H:%M"),
        ])

        if PRINT_LOGO_PATH:
            image_width, image_height = [n * cm for n in PRINT_LOGO_SIZE_CM]
            canvas.drawImage(
                PRINT_LOGO_PATH,
                115 * mm, y0 + 1 * mm,
                image_width, image_height,
            )

        y = 297 * mm - self.TEXT_Y
        canvas.line(self.PAGE_MARGIN_X, y, self.PAGE_WIDTH - self.PAGE_MARGIN_X, y)
        y -= 3 * mm
        fontSize = 11.5
        leading = fontSize * 1.4
        y = draw_multiline(canvas, 18 * mm, y, fontSize, leading, order.free_text.strip().splitlines())
        y -= 6 * mm
        canvas.line(self.PAGE_MARGIN_X, y, self.PAGE_WIDTH - self.PAGE_MARGIN_X, y)

        self.draw_y = self._align_draw_y(y - self.INTERTICKET_MARGIN)

    def process_order(self, order):
        self._prime_new_order(order)
        for index, code in enumerate(order.code_set.order_by("literate_code", "code")):
            self._print_code(index, order, code)

    def _print_code(self, index, order, code):

        if self.draw_y - self.TICKET_HEIGHT < max(self.INTERTICKET_MARGIN, self.PAGE_MARGIN_Y):
            self.canvas.showPage()
            self.canvas.setFont("Helvetica", 9, 8)

            page_id_text = "Sivu %d" % self.canvas._pageNumber
            if order.reference_number:
                page_id_text += " - Viitenumero: %s" % order.reference_number
            self.canvas.drawString(self.PAGE_MARGIN_X, self.PAGE_HEIGHT - self.PAGE_MARGIN_Y, page_id_text)
            self.draw_y = self._align_draw_y(self.PAGE_HEIGHT - self.PAGE_MARGIN_Y - 10 * mm)

        ticket_width = self.PAGE_WIDTH - 2 * self.PAGE_MARGIN_X

        self.canvas.saveState()
        self.canvas.translate(self.PAGE_MARGIN_X, self.draw_y - self.TICKET_HEIGHT)

        self.canvas.roundRect(0, 0, ticket_width, self.TICKET_HEIGHT, 0.15 * cm)
        self.canvas.setFont("Helvetica", 9, 8)
        self.canvas.drawString(self.INTRA_TICKET_X_MARGIN, 3 * mm, "%s - %s - %s" % (code.product_text, code.full_code, code.literate_code))
        linear_barcode_width = self.PAGE_WIDTH * 0.6
        barcode_y_offset = 0.25 * self.TICKET_HEIGHT
        barcode_height = 0.7 * self.TICKET_HEIGHT
        linear_barcode = createBarcodeDrawing(
            "Standard39",
            checksum=False, # Seems to be extraneous (using Android's Barcode reader app),
            quiet=False, # We'll deal with these ourselves
            value=code.full_code,
            width=linear_barcode_width,
            height=barcode_height
        )

        draw_on_pdf(linear_barcode, self.canvas, self.INTRA_TICKET_X_MARGIN, barcode_y_offset)
        qr_barcode_size = barcode_height
        qr_barcode = createBarcodeDrawing("QR",
                                          value=code.full_code,
                                          barBorder=0, # We'll deal with these ourselves
                                          width=qr_barcode_size,
                                          height=qr_barcode_size
        )

        draw_on_pdf(qr_barcode, self.canvas, ticket_width - self.INTRA_TICKET_X_MARGIN - qr_barcode_size, barcode_y_offset)

        self.canvas.restoreState()

        self.draw_y -= (self.INTERTICKET_MARGIN + self.TICKET_HEIGHT)