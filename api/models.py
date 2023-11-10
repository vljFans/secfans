from django.db import models
from django.contrib.auth.models import AbstractBaseUser, Permission
from .managers import UserManager
from django.utils.timezone import now


class Role(models.Model):
    name = models.CharField(max_length=30)
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
    name = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, null=True)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, blank=True, null=True)
    pin = models.CharField(max_length=6, blank=True, null=True)
    gst_no = models.CharField(max_length=16, blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    contact_name = models.CharField(max_length=30, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
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
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'customer_types'
        verbose_name_plural = 'customer_types'


class KYC_Type(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'kyc_types'
        verbose_name_plural = 'kyc_types'


class Customer(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True)
    customer_type = models.ForeignKey(
        Customer_Type, on_delete=models.CASCADE, blank=True, null=True)
    landmark = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, null=True)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, blank=True, null=True)
    pin = models.CharField(max_length=6, blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    contact_no_std = models.CharField(max_length=15, blank=True, null=True)
    contact_name = models.CharField(max_length=30, blank=True, null=True)
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
    name = models.CharField(max_length=30, blank=True, null=True)
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
    name = models.CharField(max_length=30, blank=True, null=True)
    uom = models.ForeignKey(
        Uom, on_delete=models.CASCADE, blank=True, null=True)
    conversion_rate = models.DecimalField(
        default=1, max_digits=30, decimal_places=5, blank=True, null=True)
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
    name = models.CharField(max_length=30, blank=True, null=True)
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
    name = models.CharField(max_length=30, blank=True, null=True)
    item_category = models.ForeignKey(
        Item_Category, on_delete=models.CASCADE, blank=True, null=True)
    hsn_code = models.CharField(max_length=40, blank=True, null=True)
    gst_percentage = models.DecimalField(
        default=1, max_digits=10, decimal_places=2)
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
    name = models.CharField(max_length=30, blank=True, null=True)
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
    price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
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


class Bill_Of_Material(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    uom = models.ForeignKey(
        Uom, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(
        max_digits=10, decimal_places=5, blank=True, null=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    is_final = models.SmallIntegerField(default=1)
    level = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'bill_of_material_headers'
        verbose_name_plural = 'bill_of_material_headers'


class Bill_Of_Material_Detail(models.Model):
    bill_of_material_header = models.ForeignKey(
        Bill_Of_Material, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, blank=True, null=True)
    bom_level = models.ForeignKey(
        Bill_Of_Material, related_name="bomLevel", on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(
        max_digits=10, decimal_places=5, blank=True, null=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
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
