from django.contrib import admin
from .models import Student, Package, Agent, book, Login, Photographer,Message,Payment

# Register your models here.
admin.site.register(Login)
admin.site.register(Package)
admin.site.register(Agent)
admin.site.register(Student)
admin.site.register(book)
admin.site.register(Photographer)
admin.site.register(Message)
admin.site.register(Payment)


