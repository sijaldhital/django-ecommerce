from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.models import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time
from .models import Order
@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    # Add a ten second pause for paypal to send IPN data
    time.sleep(10)

    # Grab the info that paypal sends
    paypal_obj = sender
    # Grab the Invoice
    my_Invoice = str(paypal.obj.invoice)

    # Match the paypal invoice to the Order invoice
    my_Order = Order.objects.get(invoice=my_Invoice)

    # Record that the Order was paid
    my_Order.paid = True
    # Save the Order
    my_Order.save()


    # print(paypal_obj)
    # print(f"Amount Paid: {paypal_obj.mc_gross}")
    