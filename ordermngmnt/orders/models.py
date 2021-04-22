from django.db import models

# Create your models here.
"""
class QATable(models.Model):
	#docstring for Destination
	question = models.TextField()
	answer = models.TextField()
	date_time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "User:"+self.question+", Bot:"+self.answer+", Time:"+str(self.date_time)
class customers(models.Model):
	customer_id = models.CharField(max_length=128, primary_key=True)

class brands(models.Model):
	brand_id = models.CharField(max_length=128, primary_key=True)
	brand_name = models.CharField(max_length=128)

class plant_orders(models.Model):
	epricer = models.CharField(max_length=128)
	purchase_order = models.CharField(max_length=128)
	plant_order_id = models.CharField(max_length=128, primary_key=True)

class managers(models.Model):
	first_name = models.CharField(max_length=128)
	last_name = models.CharField(max_length=128)
	manager_id = models.CharField(max_length=128, primary_key=True)
	squad = models.CharField(max_length=128)

class transactions(models.Model):
	brand = models.ForeignKey(brands, on_delete= models.CASCADE)
	customer = models.ForeignKey(customers, on_delete= models.CASCADE)
	transaction_date = models.DateField()
	support_region = models.CharField(max_length=128)
	user = models.CharField(max_length=128)
	plant_order = models.ForeignKey(plant_orders, on_delete= models.CASCADE)
	sales_office = models.CharField(max_length=128)
	sales_group = models.CharField(max_length=128)
	transaction_status = models.CharField(max_length=128)
	manager = models.ForeignKey(managers, on_delete= models.CASCADE)
	transaction_id = models.CharField(max_length=128, primary_key=True)

class orders(models.Model):
	order_id = models.CharField(max_length=128, primary_key=True)
	order_status = models.CharField(max_length=128)
	customer = models.ForeignKey(customers, on_delete= models.CASCADE)
	order_date = models.DateField()
	brand = models.ForeignKey(brands, on_delete= models.CASCADE)
	order_country = models.CharField(max_length=128)
	cps = models.CharField(max_length=128)
	machine_serial_no = models.CharField(max_length=128)
	manager = models.ForeignKey(managers, on_delete= models.CASCADE)

class quotes(models.Model):
	quote_status = models.CharField(max_length=128)
	brand = models.ForeignKey(brands, on_delete= models.CASCADE)
	quote_country = models.CharField(max_length=128)
	sales_group = models.CharField(max_length=128)
	sales_office = models.CharField(max_length=128)
	fop_status = models.CharField(max_length=128)
	epricer = models.CharField(max_length=128)
	squad = models.CharField(max_length=128)
	quote_id = models.CharField(max_length=128, primary_key=True)
	quote_price = models.IntegerField()
	end_user = models.CharField(max_length=128)
	quote_user = models.CharField(max_length=128)
	sold_to = models.ForeignKey(customers, on_delete= models.CASCADE)
	quote_date = models.DateField()


class invoices(models.Model):
	invoice_id = models.CharField(max_length=128, primary_key=True)
	order = models.ForeignKey(orders, on_delete= models.CASCADE)
	plant_order = models.ForeignKey(plant_orders, on_delete=models.CASCADE)
	purchase_order = models.CharField(max_length=128)

"""
