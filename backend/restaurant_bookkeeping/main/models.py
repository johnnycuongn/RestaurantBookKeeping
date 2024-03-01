from typing import Iterable
from django.db import models
import uuid
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

class Outlet(models.Model):
    name = models.CharField(max_length=255, blank=False, unique=True)
    code = models.CharField(unique=True, blank=False)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)

    # authorized_user_profiles (M-M UserProfile)
    # expenses (O-M Expense): Expenses that are under this outlet
    # income (O-M Income): Income that are under this outet

class UserProfile(models.Model):
    '''
        Contains user information, extra from existing User model
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    outlets = models.ManyToManyField(Outlet, related_name="authorized_user_profiles")


class MainCategory:
    OPERATING = "OPERATING"
    INVENTORY = "INVENTORY"
    LABOUR = "LABOUR"
    OTHERS = "OTHERS"

    MAIN_CATEGORIES_CHOICES = [
        (OPERATING, 'Operating'),
        (INVENTORY, 'Inventory'),
        (LABOUR, 'Labour'),
        (OTHERS, 'Others'),
    ]


class ExpenseCategory(models.Model):
    '''
        Used for Expense Category

        Used by Expense Model
    '''



    name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.TextField(blank=True)
    main_category = models.CharField(choices=MainCategory.MAIN_CATEGORIES_CHOICES)

    def save(self, *args, **kwargs) -> None:
        if ExpenseCategory.objects.filter(name=self.name).exists():
            raise ValidationError('An ExpenseCategory with this name already exists.') 


        return super().save(*args, **kwargs)

    # payees_with_default (O-M Payee): Payees that set this category as default
    

class AccountInfoAbstractModel(models.Model):
    '''
    '''

    name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.TextField(blank=True)
    note = models.TextField(blank=True)


    class Meta:
        abstract = True

class PaymentAccount(AccountInfoAbstractModel):
    payment_methods_choices = {
        'CASH': 'Cash',
        'CREDITCARD': 'Credit Card',
        'DEBITCARD': 'Debit Card'
    }

    method = models.CharField(choices=payment_methods_choices)

    # payees_with_default (O-M Payee): Payees that use this payment account as default
    # expenses (O-M Expense): Expenses that are deposited into this payment account


class Payee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.TextField(blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    default_expense_category = models.ForeignKey(ExpenseCategory, null=True, on_delete=models.SET_NULL, related_name="payees_with_default")
    default_payment = models.ForeignKey(PaymentAccount, null=True, on_delete=models.SET_NULL, related_name="payees_with_default")

    # expenses (O-M Expense): Expenses that are under this payee

class Expense(models.Model):

    payment_status_choices = {
        'PAID': 'Paid',
        'PENDING': 'Pending',
        'UNPAID': 'Unpaid'
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name="expenses")
    outlet = models.ForeignKey(Outlet, on_delete=models.SET_NULL, null=True, blank=False, related_name="expenses")
    payee = models.ForeignKey(Payee, on_delete=models.SET_NULL, null=True, blank=False, related_name="expenses")
    payment_date = models.DateField()
    payment_status = models.CharField(max_length=10, choices=payment_status_choices)
    payment = models.ForeignKey(PaymentAccount, on_delete=models.SET_NULL, null=True, blank=False, related_name="expenses")

    total_amount = models.IntegerField(blank=False)
    main_category = models.CharField(max_length=10, choices=MainCategory.MAIN_CATEGORIES_CHOICES)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=False, related_name="expenses")
    note = models.TextField(blank=True)

    receipt = models.FileField(upload_to='expenses_receipts/', blank=True, null=True)

class IncomeAccount(AccountInfoAbstractModel):
    income_payment_choices = {
        'CASH': 'Cash',
        'CREDITCARD': 'Credit Card',
        'DEBITCARD': 'Debit Card'
    }

    method = models.CharField(max_length=10, choices=income_payment_choices)


class IncomeCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # income (O-M Income): All income that is under this category

class Income(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name="owned_income")
    outlet = models.ForeignKey(Outlet, on_delete=models.SET_NULL, null=True, blank=False, related_name="income")
    date = models.DateField(blank=False)
    total_amount = models.IntegerField(blank=False)
    deposit_account = models.ForeignKey(IncomeAccount, null=True, on_delete=models.SET_NULL, related_name="income")
    category = models.ForeignKey(IncomeCategory, null=True, on_delete=models.SET_NULL, related_name="income")
    description = models.TextField(blank=True)
    