from django.contrib import admin
from .models import UserIncome, Source
# Register your models here.

class UserIncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'Sources', 'date','save_by',)
    search_fields = ('description', 'Sources', 'date',)

    list_per_page = 5


admin.site.register(UserIncome)
admin.site.register(Source)


