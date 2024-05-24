from datetime import datetime, timedelta
from api import models
from django.db.models import Count, Sum
from django.contrib import messages
from django.shortcuts import redirect
import logging
from decimal import Decimal
from . import models
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def monthlyCron():
    print('Hello')
