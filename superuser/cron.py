from datetime import datetime, timedelta
from api import models
from django.db.models import Count, Sum
from django.contrib import messages
from django.shortcuts import redirect
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

def monthlyCron():
    print('Hello')
