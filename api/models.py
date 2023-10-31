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
    name = models.CharField(max_length=30)
    sortname = models.CharField(max_length=3)
    phonecode = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'countries'
        verbose_name_plural = 'countries'


class State(models.Model):
    name = models.CharField(max_length=30)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'states'
        verbose_name_plural = 'states'


class City(models.Model):
    name = models.CharField(max_length=30)
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
    kyc_type = models.ForeignKey(KYC_Type, on_delete=models.CASCADE, blank=True, null=True)
    kyc_detail = models.CharField(max_length=25, blank=True, null=True)
    kyc_image = models.CharField(max_length=250, blank=True, null=True)
    weekly_closing_day = models.CharField(max_length=250, blank=True, null=True)
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
