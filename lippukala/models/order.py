from django.db import models


class Order(models.Model):

    """Encapsulates an order, which may contain zero or more codes.

    :var event: An (optional) event identifier for this order. May be used at the client app's discretion.
    """

    event = models.CharField(max_length=32, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    reference_number = models.CharField(
        blank=True,
        null=True,
        max_length=64,
        unique=True,
        help_text="Reference number, unique",
    )
    address_text = models.TextField(blank=True, help_text="Text printed in the PDF address area")
    free_text = models.TextField(blank=True, help_text="Text printed on PDF")
    comment = models.TextField(blank=True, help_text="Administrative comment")

    def __str__(self):
        return "LK-%08d (ref %s)" % (self.pk, self.reference_number)
