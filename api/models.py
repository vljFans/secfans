from django.db import models
from django.contrib.auth.models import AbstractBaseUser, Permission
from .managers import UserManager
from django.utils.timezone import now
from datetime import datetime
from django.core.validators import RegexValidator
from django.utils.text import gettext_lazy as _
import django

class Role(models.Model):
    name = models.CharField(max_length=50)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'roles'
        verbose_name_plural = 'roles'


class Role_Permission(models.Model):
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, blank=True, null=True)
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, blank=True, null=True)
    permitted = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)

    def __str__(self):
        return self.role.name + "=>" + self.permission.codename

    class Meta:
        managed = True
        db_table = 'role_permissions'
        verbose_name_plural = 'role_permissions'


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=100,
        unique=True,
        error_messages={'unique': 'A user with that email already exists.'},
        help_text='Required. 100 characters or fewer. Letters, digits and @/./_ only.',
    )
    name = models.CharField(max_length=50, blank=True, null=True)
    pswd_token = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    user_sign = models.CharField(max_length=250, blank=True, null=True)
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    USERNAME_FIELD = 'email'
    # removes email from REQUIRED_FIELDS
    REQUIRED_FIELDS = ['name', 'phone']

    objects = UserManager()

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'users'
        verbose_name_plural = 'users'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser


class Configuration_User(models.Model):
    client_name = models.CharField(max_length=50, blank=True, null=True)
    client_address = models.CharField(max_length=50, blank=True, null=True)
    client_work_address = models.CharField(max_length=50, blank=True, null=True)
    client_gst = models.CharField(max_length=50, blank=True, null=True)
    client_contact = models.CharField(max_length=50, blank=True, null=True)
    pan_no = models.CharField(max_length=50, blank=True, null=True)
    cin_no = models.CharField(max_length=50, blank=True, null=True)
    ice_code = models.CharField(max_length=50, blank=True, null=True)
    udyam_no = models.CharField(max_length=50, blank=True, null=True)
    mail_id = models.CharField(max_length=50, blank=True, null=True)
    website = models.CharField(max_length=50, blank=True, null=True)
    logo = models.CharField(max_length=250, blank=True, null=True)
    finacial_year_start = models.DateField(blank=True, null=True)
    finacial_year_end =models.DateField(blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)


    def __str__(self):
        return self.client_name

    class Meta:
        managed = True
        db_table = 'configuration_user'
        verbose_name_plural = 'configuration_user'


class Country(models.Model):
    name = models.CharField(max_length=50)
    sortname = models.CharField(max_length=3)
    phonecode = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'countries'
        verbose_name_plural = 'countries'


class State(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'states'
        verbose_name_plural = 'states'


class City(models.Model):
    name = models.CharField(max_length=50)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'cities'
        verbose_name_plural = 'cities'


class Vendor(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, null=True)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, blank=True, null=True)
    pin = models.CharField(max_length=6, blank=True, null=True)
    gst_no = models.CharField(max_length=16, blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    contact_name = models.CharField(max_length=50, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    store_present = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'vendors'
        verbose_name_plural = 'vendors'


class Customer_Type(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'customer_types'
        verbose_name_plural = 'customer_types'


class KYC_Type(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'kyc_types'
        verbose_name_plural = 'kyc_types'


class Customer(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    customer_type = models.ForeignKey(Customer_Type, on_delete=models.CASCADE, blank=True, null=True)
    landmark = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null=True)
    # city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    pin = models.CharField(max_length=6, blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    contact_no_std = models.CharField(max_length=15, blank=True, null=True)
    contact_name = models.CharField(max_length=50, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_anniversary = models.CharField(max_length=5, blank=True, null=True)
    photo = models.CharField(max_length=250, blank=True, null=True)
    kyc_type = models.ForeignKey(
        KYC_Type, on_delete=models.CASCADE, blank=True, null=True)
    kyc_detail = models.CharField(max_length=25, blank=True, null=True)
    kyc_image = models.CharField(max_length=250, blank=True, null=True)
    weekly_closing_day = models.CharField(
        max_length=250, blank=True, null=True)
    morning_from_time = models.TimeField(blank=True, null=True)
    morning_to_time = models.TimeField(blank=True, null=True)
    evening_from_time = models.TimeField(blank=True, null=True)
    evening_to_time = models.TimeField(blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'customers'
        verbose_name_plural = 'customers'


class Uom(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'uoms'
        verbose_name_plural = 'uoms'


class Child_Uom(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    uom = models.ForeignKey(
        Uom, on_delete=models.CASCADE, blank=True, null=True)
    conversion_rate = models.DecimalField(
        default=1, max_digits=30, decimal_places=5)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'child_uoms'
        verbose_name_plural = 'child_uoms'


class Item_Category(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'item_categories'
        verbose_name_plural = 'item_categories'


class Item_Type(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    item_category = models.ForeignKey(
        Item_Category, on_delete=models.CASCADE, blank=True, null=True)
    gst_percentage = models.DecimalField(
        default=0, max_digits=10, decimal_places=2)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'item_types'
        verbose_name_plural = 'item_types'


class Item_Color(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    color_code = models.CharField(max_length=7, blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'item_colors'
        verbose_name_plural = 'item_colors'


class Item(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    item_type = models.ForeignKey(
        Item_Type, on_delete=models.CASCADE, blank=True, null=True)
    uom = models.ForeignKey(
        Uom, on_delete=models.CASCADE, blank=True, null=True)
    hsn_code = models.CharField(max_length=40, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'items'
        verbose_name_plural = 'items'


class Store(models.Model):
    name = models.CharField(max_length=60, blank=False, null=False)
    address = models.TextField(blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    pin = models.CharField(max_length=6, validators=[RegexValidator(
        '^[0-9]{6}$', _('Invalid Pin Number'))], blank=True, null=True)
    contact_name = models.CharField(max_length=50, blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    manager_name = models.CharField(max_length=50, blank=True, null=True)
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'stores'
        verbose_name_plural = 'stores'


class Store_Item(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, blank=True, null=True)
    opening_qty = models.DecimalField(
        max_digits=10, decimal_places=5, default=0)
    on_hand_qty = models.DecimalField(
        max_digits=10, decimal_places=5, default=0)
    closing_qty = models.DecimalField(
        max_digits=10, decimal_places=5, default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.store.name + "=>" + self.item.name

    class Meta:
        managed = True
        db_table = 'store_items'
        verbose_name_plural = 'store_items'


class Bill_Of_Material(models.Model):
    bom_item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    # name = models.CharField(max_length=250, blank=True, null=True)
    uom = models.ForeignKey(Uom, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_final = models.SmallIntegerField(default=0)
    level = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.bom_item.name

    class Meta:
        managed = True
        db_table = 'bill_of_material_headers'
        verbose_name_plural = 'bill_of_material_headers'


class Bill_Of_Material_Detail(models.Model):
    bill_of_material_header = models.ForeignKey(Bill_Of_Material, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    bom_level = models.ForeignKey(Bill_Of_Material, related_name="bomLevel", on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.pk

    class Meta:
        managed = True
        db_table = 'bill_of_material_details'
        verbose_name_plural = 'bill_of_material_details'


class Purchase_Order(models.Model):
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, blank=True, null=True)
    order_number = models.CharField(max_length=50, blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    quotation_number = models.CharField(max_length=50, blank=True, null=True)
    quotation_date = models.DateField(blank=True, null=True)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    business_terms = models.CharField(max_length=250, blank=True, null=True)
    discount_type = models.CharField(max_length=20, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounted_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    excise_duty_percentage = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    insurance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    octroi = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    freight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    packing = models.CharField(max_length=250, blank=True, null=True)
    payment_terms = models.CharField(max_length=250, blank=True, null=True)
    delivery_schedule = models.CharField(max_length=150, blank=True, null=True)
    delivery_at = models.CharField(max_length=150, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivered_total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_status = models.SmallIntegerField(default=1)
    creator = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.order_number

    class Meta:
        managed = True
        db_table = 'purchase_order_headers'
        verbose_name_plural = 'purchase_order_headers'


class Purchase_Order_Detail(models.Model):
    purchase_order_header = models.ForeignKey(Purchase_Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_with_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivered_quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    delivered_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivered_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivered_gst_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivered_amount_with_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.purchase_order_header.order_number

    class Meta:
        managed = True
        db_table = 'purchase_order_details'
        verbose_name_plural = 'purchase_order_details'


class Transaction_Type(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    desc = models.CharField(max_length=100, blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'transaction_types'
        verbose_name_plural = 'transaction_types'


class Job_Order(models.Model):
    order_number = models.CharField(max_length=50, blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    manufacturing_type = models.CharField(max_length=20, choices=[("Self","Self"), ("Third party","Third party")], blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, null=True)
    with_item = models.CharField(max_length=20, choices=[("True", True), ("False", False)], blank=True,null=True)
    job_status = models.SmallIntegerField(default=0)
    estimated_time_day = models.CharField(max_length=20, blank=True, null=True)
    actual_time_take = models.CharField(max_length=20, blank=True, null=True)
    # total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1) #0 for not recieved 1 for recieved without inspection 2 for recived with inspection 
    deleted = models.BooleanField(default=0)
    material_reciept = models.SmallIntegerField(default=0)
    material_issue = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    updated_at = models.DateTimeField(default=django.utils.timezone.now)
    def __str__(self):
        return self.order_number

    class Meta:
        managed = True
        db_table = 'job_order_headers'
        verbose_name_plural = 'job_order_headers'


class Job_Order_Detail(models.Model):
    DIRECTION_CHOICES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]

    job_order_header = models.ForeignKey(Job_Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    quantity_result = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default='outgoing')

    def __str__(self):
        return self.job_order_header.order_number

    class Meta:
        managed = True
        db_table = 'job_order_details'
        verbose_name_plural = 'job_order_details'


# class Job_Order_Detail_Sent(models.Model):
#     job_order_detail = models.ForeignKey(Job_Order_Detail, on_delete=models.CASCADE)
#     item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
#     bill_of_material = models.ForeignKey(Bill_Of_Material, on_delete=models.CASCADE, blank=True, null=True)
#     quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
#     rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     status = models.SmallIntegerField(default=1)
#     deleted = models.BooleanField(default=0)
#     created_at = models.DateTimeField(default=now)
#     updated_at = models.DateTimeField(default=now)
#
#     def __str__(self):
#         return self.job_order_detail.job_order_header.order_number
#
#     class Meta:
#         managed = True
#         db_table = 'job_order_detail_sent'
#         verbose_name_plural = 'job_order_detail_sent'

class Grn_Inspection_Transaction(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, null=True)
    transaction_type = models.ForeignKey(Transaction_Type, on_delete=models.CASCADE, blank=True, null=True)
    purchase_order_header = models.ForeignKey(Purchase_Order, on_delete=models.CASCADE, blank=True, null=True)
    job_order = models.ForeignKey(Job_Order, on_delete=models.CASCADE, blank=True, null=True) 
    transaction_number = models.CharField(max_length=25, blank=True, null=True)
    transaction_date = models.DateField(blank=True, null=True)
    ins_done = models.SmallIntegerField(default=0, blank=True, null=True)
    ins_completed = models.SmallIntegerField(default=0, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.transaction_number

    class Meta:
        managed = True
        db_table = 'grn_inspection_transaction_headers'
        verbose_name_plural = 'grn_inspection_transaction_headers'


class Grn_Inspection_Transaction_Detail(models.Model):
    grn_inspection_transaction_header = models.ForeignKey(Grn_Inspection_Transaction, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    accepted_quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    reject_quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    inspection_date = models.DateField(blank=True, null=True)
    ins_done = models.SmallIntegerField(default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_with_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self. grn_Inspection_Transaction_header.transaction_number

    class Meta:
        managed = True
        db_table = 'grn_inspection_transaction_Detail'
        verbose_name_plural = 'grn_inspection_transaction_Detail'


class Store_Transaction(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, null=True,related_name="vendor" )
    vendor_from = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, null=True, related_name="vendor_from")
    transaction_type = models.ForeignKey(Transaction_Type, on_delete=models.CASCADE, blank=True, null=True)
    purchase_order_header = models.ForeignKey(Purchase_Order, on_delete=models.CASCADE, blank=True, null=True)
    transaction_number = models.CharField(max_length=25, blank=True, null=True)
    transaction_date = models.DateField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vehicle = models.CharField(max_length=25, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)
    job_order = models.ForeignKey(Job_Order, on_delete=models.CASCADE, blank=True, null=True)
    grn_inspection =  models.ForeignKey(Grn_Inspection_Transaction, on_delete=models.CASCADE, blank=True, null=True)
    reference_id = models.SmallIntegerField(default=0)
    creator = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)


    def __str__(self):
        return self.transaction_number

    class Meta:
        managed = True
        db_table = 'store_transaction_headers'
        verbose_name_plural = 'store_transaction_headers'


class Store_Transaction_Detail(models.Model):
    store_transaction_header = models.ForeignKey(Store_Transaction, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_with_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.store_transaction_header.transaction_number

    class Meta:
        managed = True
        db_table = 'store_transaction_details'
        verbose_name_plural = 'store_transaction_details'

# on transit transaction -- developed by saswata 
# transaction_date date when material out  happned flag be 1 if material in on that particular transaction occured


class On_Transit_Transaction(models.Model):
    transaction_number = models.CharField(max_length=25, blank=True, null=True)
    transaction_date = models.DateField(blank=True, null=True)
    transaction_in_date = models.DateField(blank=True, null=True)
    vechical_no = models.CharField(max_length=50, blank=True, null=True)
    source_store =  models.ForeignKey(
        Store, on_delete=models.CASCADE, blank=True, null=True , related_name="source_store")
    destination_store =  models.ForeignKey(
        Store, on_delete=models.CASCADE, blank=True, null=True, related_name="destination_store")
    creator = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    flag = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.transaction_number

    class Meta:
        managed = True
        db_table = 'on_transit_transaction_headers'
        verbose_name_plural = 'on_transit_transaction_headers'


class On_Transit_Transaction_Details(models.Model):
    on_transit_transaction_header = models.ForeignKey(On_Transit_Transaction, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    recieved_quntity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    reject_quantity = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.on_transit_transaction_header.transaction_number

    class Meta:
        managed = True
        db_table = 'On_Transit_Transaction_details'
        verbose_name_plural = 'On_Transit_Transaction_details'


# physical Inspection on Store Items --- developed by saswata
class Physical_Inspection(models.Model):
    transaction_number = models.CharField(max_length=50, blank=True, null=True)
    inspection_date = models.DateField(blank=True, null=True)
    store =  models.ForeignKey(Store, on_delete=models.CASCADE, blank=True, null=True)
    item_catagories = models.ForeignKey(Item_Category, on_delete=models.CASCADE, blank=True, null=True)
    item_type = models.ForeignKey(Item_Type, on_delete=models.CASCADE, blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)



    def __str__(self):
        return self.transaction_number

    class Meta:
        managed = True
        db_table = 'physical_inspection_headers'
        verbose_name_plural = 'physical_inspection_headers'


class Physical_Inspection_Details(models.Model):
    physical_inspection_header = models.ForeignKey(Physical_Inspection, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    booked_quantity = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    physical_quantity = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    adjusted_quantity = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    notes = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)



    def __str__(self):
        return self.physical_inspection_header.transaction_number

    class Meta:
        managed = True
        db_table = 'physical_inspection_details'
        verbose_name_plural = 'physical_inspection_details'


# purchase bill ---developed by saswata
class Purchase_Bill(models.Model):
    transaction_number = models.CharField(max_length=50, blank=True, null=True)
    transaction_date = models.DateField(blank=True, null=True)
    invoice_no = models.CharField(max_length=50, blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, null=True)
    e_way_no =  models.CharField(max_length=50, blank=True, null=True)
    e_way_date = models.DateField(blank=True, null=True)
    vechical_no = models.CharField(max_length=50, blank=True, null=True)
    total_igst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    flag = models.SmallIntegerField(default=0)
    purchase_tally_report = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)


    def __str__(self):
        return self.transaction_number

    class Meta:
        managed = True
        db_table = 'purchase_bill_header'
        verbose_name_plural = 'purchase_bill_header'


class Purchase_Bill_Details(models.Model):
    purchase_bill_header = models.ForeignKey(Purchase_Bill, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    hsn_code = models.CharField(max_length=50, blank=True, null=True)
    uom = models.ForeignKey(
        Uom, on_delete=models.CASCADE, blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igst_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cgst_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_with_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.purchase_bill_header.transaction_number

    class Meta:
        managed = True
        db_table = 'purchase_bill_details'
        verbose_name_plural = 'purchase_bill_details'

class Item_Stock_Report(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True, null=True)
    closing_quantity = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    closing_value = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    next_month_start_date = models.DateField(blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'Item_Stock_Report: {self.pk}'

    class Meta:
        managed = True
        db_table = 'item_stock_report_header'
        verbose_name_plural = 'item_stock_report_header'

class Item_Stock_Report_Details(models.Model):
    item_stock_report_header =  models.ForeignKey(Item_Stock_Report, on_delete=models.CASCADE, blank=True, null=True)
    store_transaction_header = models.ForeignKey(Store_Transaction, on_delete=models.CASCADE, blank=True, null=True) 
    store_transaction_detail = models.ForeignKey(Store_Transaction_Detail, on_delete=models.CASCADE, blank=True, null=True)
    transaction_type = models.ForeignKey(Transaction_Type, on_delete=models.CASCADE, blank=True, null=True)
    transaction_number = models.CharField(max_length=50, blank=True, null=True)
    transaction_date = models.DateField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    value = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        
        return f'Item_Stock_Report: {self.item_stock_report_header.id}'

    class Meta:
        managed = True
        db_table = 'item_stock_report_details'
        verbose_name_plural = 'item_stock_report_details'

class Outgoing_Incoming_Ratio(models.Model):
    transaction_number = models.CharField(max_length=50, blank=True, null=True)
    transaction_date = models.DateField(blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, null=True)
    job_order = models.ForeignKey(Job_Order, on_delete=models.CASCADE, blank=True, null=True) 
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.transaction_number

    class Meta:
        managed = True
        db_table = 'outgoing_incoming_ratio_header'
        verbose_name_plural = 'outgoing_incoming_ratio_header'

class Outgoing_Incoming_Ratio_Details(models.Model):
    outgoing_incoming_ratio_header = models.ForeignKey(Outgoing_Incoming_Ratio, on_delete=models.CASCADE, blank=True, null=True)
    item_outgoing = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True, related_name="item_outgoing")
    item_incomming = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True ,related_name="item_incomming")
    numerator = models.IntegerField(default=0)
    denominator = models.PositiveIntegerField(default=1)
    ratio = models.CharField(max_length=50, blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.outgoing_incoming_ratio_header.transaction_number

    class Meta:
        managed = True
        db_table = 'outgoing_incoming_ratio_details'
        verbose_name_plural = 'outgoing_incoming_ratio_details'

class User_Log_Details(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    task_name = models.CharField(max_length=100, blank=True, null=True)
    time_stamp = models.DateTimeField(default=now)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)

    def __str__(self):
        return self.task_name

    class Meta:
        managed = True
        db_table = 'user_log_details'
        verbose_name_plural = 'user_log_details'


class Test_Corn_Job(models.Model):
    test_message =  models.CharField(max_length=10, blank=True, null=True)
   
    created_at = models.DateTimeField(default=now)
    
    def __str__(self):
        return self.test_message

    class Meta:
        managed = True
        db_table = 'test_corn_job'
        verbose_name_plural = 'test_corn_job'

class Invoice(models.Model):
    date = models.DateField(blank=True, null=True)
    invoice_no = models.CharField(max_length=50, blank=True, null=True, unique=True)
    invoice_ref_no = models.CharField(max_length=50, blank=True, null=True)
    total_quantity = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    total_value = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True )
    gross_total= models.DecimalField(max_digits=30, decimal_places=5, default=0)
    gst_sales= models.DecimalField(max_digits=30, decimal_places=5, default=0)
    cgst= models.DecimalField(max_digits=30, decimal_places=5, default=0)
    sgst= models.DecimalField(max_digits=30, decimal_places=5, default=0)
    round_off= models.DecimalField(max_digits=30, decimal_places=5, default=0)
    igst_sales= models.DecimalField(max_digits=30, decimal_places=5, default=0)
    igst= models.DecimalField(max_digits=30, decimal_places=5, default=0)
    rent= models.DecimalField(max_digits=30, decimal_places=5, default=0)
    export_sales= models.DecimalField(max_digits=30, decimal_places=5, default=0)
    store_transaction_add = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.invoice_no

    class Meta:
        managed = True
        db_table = 'invoice_header'
        verbose_name_plural = 'invoice_header'

class Invoice_Details(models.Model):
    invoice_header = models.ForeignKey(Invoice, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True )
    quantity = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    value = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    rate = models.DecimalField(max_digits=30, decimal_places=5, default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.invoice_header.invoice_no

    class Meta:
        managed = True
        db_table = 'invoice_details'
        verbose_name_plural = 'invoice_details'

