from django.core.management.base import BaseCommand
from . import models  # Import your models here
from django.utils import timezone
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Update store item quantities'

    def handle(self, *args, **kwargs):
        context = {}
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1)
        next_month_start_date = (start_date.replace(day=1) + timedelta(days=31))
        
        # try:
        #     store_items = models.Store_Item.objects.select_related('store').prefetch_related(
        #         'store__store_transaction_detail_set'
        #     )
            
        #     for store_item in store_items:
        #         total_In_quantity = 0.00
        #         total_Out_quantity = 0.00
        #         total_Out_Value = 0.00
        #         total_IN_Value = 0.00
        #         total_quantity = float(store_item.opening_qty)
        #         total_value = total_quantity * float(store_item.item.price)
        #         item_rate = 0.00
                
        #         store_transaction_dets = store_item.store.store_transaction_detail_set.filter(
        #             item=store_item.item, store=store_item.store
        #         ).filter(store_transaction_header__transaction_date__range=(start_date, end_date))

        #         item_stock_report = models.Item_Stock_Report()
        #         item_stock_report.item = store_item.item
        #         item_stock_report.store = store_item.store
        #         item_stock_report.start_date = start_date
        #         item_stock_report.end_date = end_date
        #         item_stock_report.next_month_start_date = next_month_start_date
        #         item_stock_report.closing_quantity = store_item.closing_qty
        #         item_stock_report.closing_value = float(store_item.closing_qty) * float(store_item.item.price)
        #         item_stock_report.rate = store_item.item.price
        #         item_stock_report.save()
                
        #         if store_transaction_dets:
        #             order_details = []
        #             for store_transact_det in store_transaction_dets:
        #                 transaction_type = store_transact_det.store_transaction_header.transaction_type.name
        #                 quantity = float(store_transact_det.quantity)
        #                 if transaction_type in ['GRN', 'MIN', 'GRNT']:
        #                     total_In_quantity += quantity
        #                     total_IN_Value += (float(store_transact_det.rate) * quantity) if float(store_transact_det.rate) > 0.00 else (float(store_transact_det.item.price) * quantity)
        #                 elif transaction_type in ['MIS', 'MOUT']:
        #                     total_Out_quantity += quantity
        #                     total_Out_Value += (float(store_transact_det.rate) * quantity) if float(store_transact_det.rate) > 0.00 else (float(store_transact_det.item.price) * quantity)
        #                 else:
        #                     total_quantity -= quantity
        #                     total_value -= (float(store_transact_det.rate) * quantity) if float(store_transact_det.rate) > 0.00 else (float(store_transact_det.item.price) * quantity)
                        
        #                 order_details.append(
        #                     models.Item_Stock_Report_Details(
        #                         item_stock_report_header_id=item_stock_report.id,
        #                         store_transaction_header_id=store_transact_det.store_transaction_header_id,
        #                         store_transaction_detail_id=store_transact_det.id,
        #                         transaction_type_id=store_transact_det.store_transaction_header.transaction_type_id,
        #                         transaction_number=store_transact_det.store_transaction_header.transaction_number,
        #                         transaction_date=store_transact_det.store_transaction_header.transaction_date,
        #                         quantity=store_transact_det.quantity,
        #                         rate=store_transact_det.rate,
        #                         value=float(store_transact_det.quantity) * float(store_transact_det.rate)
        #                     )
        #                 )
        #             models.Item_Stock_Report_Details.objects.bulk_create(order_details)
        #             total_quantity = (total_quantity + total_In_quantity) - total_Out_quantity
        #             total_value = (total_value + total_IN_Value) - total_Out_Value
        #             item_rate = total_value / total_quantity if total_quantity > 0.00 else 0.00
        #             item_stock_report.closing_quantity = total_quantity
        #             item_stock_report.closing_value = total_value
        #             item_stock_report.rate = item_rate
        #             item_stock_report.save()
        #             store_item = models.Store_Item.objects.get(item=store_item.item, store=store_item.store)
        #             store_item.opening_qty = total_quantity
        #             store_item.closing_qty = total_quantity
        #             store_item.updated_at = timezone.now()
        #             store_item.save()
            
        #     self.stdout.write(self.style.SUCCESS('Store item quantities updated successfully'))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Error: {e}'))
        try:
           with transaction.atomic():
                cornjobTest = models.Test_Corn_Job()
                cornjobTest.test_message = 'cornjob run succesfully'

            transaction.commit()
            self.stdout.write(self.style.SUCCESS('cornjob run sucessfully'))
        except Exception as e:
             self.stdout.write(self.style.ERROR(f'Error: {e}'))   