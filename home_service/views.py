from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import HttpResponse

from django.conf import settings

from home_service.forms import CustomerServiceSearchForm

import random
import string
from .models import *
import razorpay
import datetime

# Create your views here.

def Home(request):
    user=""
    error=""
    try:
        user = User.objects.get(id=request.user.id)
        try:
            sign = Customer.objects.get(user=user)
            error = "pat"
        except:
            pass
    except:
        pass
    ser1 = Service_Man.objects.all()
    ser = Service_Category.objects.all()
    for i in ser:
        count=0
        for j in ser1:
            if i.category==j.service_name:
                count+=1
        i.total = count
        i.save()
    d = {'error': error, 'ser': ser}
    return render(request,'home.html',d)

def contact(request):
    error=False
    if request.method=="POST":
        n = request.POST['name']
        e = request.POST['email']
        m = request.POST['message']
        status = Status.objects.get(status="unread")
        Contact.objects.create(status=status,name=n,email=e,message1=m)
        error=True
    d = {'error':error}
    return render(request,'contact.html',d)

def Admin_Home(request):
    cus = Customer.objects.all()
    ser = Service_Man.objects.all()
    cat = Service_Category.objects.all()
    count1=0
    count2=0
    count3=0
    for i in cus:
        count1+=1
    for i in ser:
        count2+=1
    for i in cat:
        count3+=1
    d = {'customer':count1,'service_man':count2,'service':count3}
    
    return render(request,'admin_home.html',d)

def about(request):
    return render(request,'about.html')

class LoginUserView(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name, {'error': ''})

    def post(self, request):
        error = ""
        u = request.POST.get('uname')
        p = request.POST.get('pwd')
        user = authenticate(username=u, password=p)
        sign = ""

        if user:
            try:
                sign = Customer.objects.get(user=user)
            except Customer.DoesNotExist:
                pass

            if sign:
                login(request, user)
                return redirect('user_home')  # Replace 'success_redirect_url_pat1' with your desired URL
            else:
                stat = Status.objects.get(status="Accept")
                pure = False

                try:
                    pure = Service_Man.objects.get(status=stat, user=user)
                except Service_Man.DoesNotExist:
                    pass

                if pure:
                    login(request, user)
                    return redirect('user_home')  # Replace 'success_redirect_url_pat2' with your desired URL
                else:
                    login(request, user)
                    return redirect('login')  # Replace 'notmember_redirect_url' with your desired URL

        else:
            error = "not"

        return render(request, self.template_name, {'error': error})
class LoginAdminView(View):
    template_name = 'admin_login.html'

    def get(self, request):
        return render(request, self.template_name, {'error': ''})

    def post(self, request):
        error = ""
        u = request.POST.get('uname')
        p = request.POST.get('pwd')
        user = authenticate(username=u, password=p)

        if user and user.is_staff:
            login(request, user)
            error = "pat"
        else:
            error = "not"

        return render(request, self.template_name, {'error': error})


def Signup_User(request):
    error = ""
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        e = request.POST['email']
        p = request.POST['pwd']
        con = request.POST['contact']
        add = request.POST['address']
        type = request.POST['type']
        im = request.FILES['image']
        dat = datetime.date.today()
        user = User.objects.create_user(email=e, username=u, password=p, first_name=f,last_name=l)
        if type=="customer":
            Customer.objects.create(user=user,contact=con,address=add,image=im)
        else:
            stat = Status.objects.get(status='pending')
            Service_Man.objects.create(doj=dat,image=im,user=user,contact=con,address=add,status=stat)
        error = "create"
    d = {'error':error}
    return render(request,'signup.html',d)


@method_decorator(login_required, name='dispatch')
class UserHomeView(View):
    template_name = 'service_home.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        error = ""

        if user.is_authenticated:
            try:
                sign = Customer.objects.get(user=user)
                error = "pat"
            except Customer.DoesNotExist:
                pass

        context = {'error': error}
        return render(request, self.template_name, context)
def Service_home(request):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    terro=""
    if None == sign.service_name:
        terro = "message"
    else:
        if sign.status.status == "pending":
            terro="message1"
    d = {'error':error,'terro':terro}
    return render(request,'service_home.html',d)

def Service_Order(request):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    terro=""
    if None == sign.service_name:
        terro = "message"
    else:
        if sign.status.status == "pending":
            terro="message1"
    order = Order.objects.filter(service=sign)
    d = {'error':error,'terro':terro,'order':order}
    return render(request,'service_order.html',d)

def Admin_Order(request):
    order = Order.objects.all()
    d = {'order':order}
    return render(request,'admin_order.html',d)

def Customer_Order(request):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    order = Order.objects.filter(customer=sign)
    d = {'error':error,'order':order}
    return render(request,'customer_order.html',d)


def Customer_Booking(request,pid):
    if not request.user.is_authenticated:
        return redirect('login')
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    terror=False
    ser1 = Service_Man.objects.get(id=pid)
    if request.method == "POST":
        n = request.POST['name']
        c = request.POST['contact']
        add = request.POST['add']
        dat = request.POST['date']
        da = request.POST['day']
        ho = request.POST['hour']
        st = Status.objects.get(status="pending")
        Order.objects.create(status=st,service=ser1,customer=sign,book_date=dat,book_days=da,book_hours=ho)
        terror=True
    d = {'error':error,'ser':sign,'terror':terror}
    return render(request,'booking.html',d)

def Booking_detail(request,pid):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    order = Order.objects.get(id=pid)
    d = {'error':error,'order':order}
    return render(request,'booking_detail.html',d)

def All_Service(request):
    user = ""
    error = ""
    try:
        user = User.objects.get(id=request.user.id)
        try:
            sign = Customer.objects.get(user=user)
            error = "pat"
        except:
            pass
    except:
        pass
    ser1 = Service_Man.objects.all()
    ser = Service_Category.objects.all()
    for i in ser:
        count=0
        for j in ser1:
            if i.category==j.service_name:
                count+=1
        i.total = count
        i.save()
    d = {'error': error,'ser':ser}
    return render(request,'services.html',d)

def Explore_Service(request,pid):
    if not request.user.is_authenticated:
        return redirect('login')
    user = ""
    error = ""
    try:
        user = User.objects.get(id=request.user.id)
        try:
            sign = Customer.objects.get(user=user)
            error = "pat"
        except:
            pass
    except:
        pass
    ser = Service_Category.objects.get(id=pid)
    sta = Status.objects.get(status="Accept")
    order = Service_Man.objects.filter(service_name=ser.category,status=sta)
    d = {'error': error,'ser':ser,'order':order}
    return render(request,'explore_services.html',d)

def Logout(request):
    logout(request)
    return redirect('home')

def Edit_Profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    terror = False
    ser = Service_Category.objects.all()
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        try:
            i = request.FILES['image']
            sign.image=i
            sign.save()
        except:
            pass
        ad = request.POST['address']
        e = request.POST['email']
        con = request.POST['contact']
        sign.address = ad
        sign.contact=con
        user.first_name = f
        user.last_name = l
        user.email = e
        user.save()
        sign.save()
        terror = True
    d = {'terror':terror,'error':error,'pro':sign,'ser':ser}
    return render(request, 'edit_profile.html',d)


def Edit_Service_Profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    terror = False
    ser = Service_Category.objects.all()
    car = ID_Card.objects.all()
    city = City.objects.all()
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        try:
            i = request.FILES['image']
            sign.image=i
            sign.save()
        except:
            pass
        try:
            i1 = request.FILES['image1']
            sign.id_card=i1
            sign.save()
        except:
            pass
        ad = request.POST['address']
        e = request.POST['email']
        con = request.POST['contact']
        se = request.POST['service']
        card = request.POST['card']
        cit = request.POST['city']
        ex = request.POST['exp']
        dob = request.POST['dob']
        if dob:
            sign.dob=dob
            sign.save()
        ci=City.objects.get(city=cit)
        sign.address = ad
        sign.contact=con
        sign.city=ci
        user.first_name = f
        user.last_name = l
        user.email = e
        sign.id_type = card
        sign.experience = ex
        sign.service_name = se
        user.save()
        sign.save()
        terror = True
    d = {'city':city,'terror':terror,'error':error,'pro':sign,'car':car,'ser':ser}
    return render(request, 'edit_service_profile.html',d)

def Edit_Admin_Profile(request):
    error = False
    user = User.objects.get(id=request.user.id)
    pro = Customer.objects.get(user=user)
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        try:
            i = request.FILES['image']
            pro.image=i
            pro.save()
        except:
            pass
        ad = request.POST['address']
        e = request.POST['email']
        con = request.POST['contact']
        pro.address = ad
        pro.contact=con
        user.first_name = f
        user.last_name = l
        user.email = e
        user.save()
        pro.save()
        error = True
    d = {'error':error,'pro':pro}
    return render(request, 'edit_admin_profile.html',d)

def profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    terror = False
    d = {'pro':sign,'error':error}
    return render(request,'profile.html',d)

def service_profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    terror = False
    d = {'pro':sign,'error':error}
    return render(request,'service_profile.html',d)

def admin_profile(request):
    
    user = User.objects.get(id=request.user.id)
    pro = Customer.objects.get(user=user)
    d = {'pro':pro}
    return render(request,'admin_profile.html',d)



def Admin_Change_Password(request):
    terror = ""
    if request.method=="POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']
        if c == n:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            terror = "yes"
        else:
            terror = "not"
    d = {'terror':terror}
    return render(request,'admin_change_password.html',d)

def New_Service_man(request):
    status = Status.objects.get(status="pending")
    ser = Service_Man.objects.filter(status=status)
    d = {'ser':ser}
    return render(request,'new_service_man.html',d)

def All_Service_man(request):

    ser = Service_Man.objects.all()
    d = {'ser':ser}
    return render(request,'all_service_man.html',d)

def All_Customer(request):

    ser = Customer.objects.all()
    d = {'ser':ser}
    return render(request,'all_customer.html',d)



def Add_Service(request):

    error=False
    if request.method == "POST":
        n = request.POST['cat']
        i = request.FILES['image']
        de = request.POST['desc']
        Service_Category.objects.create(category=n,image=i,desc=de)
        error=True
    d = {'error':error}
    return render(request,'add_service.html',d)



def Edit_Service(request,pid):

    error=False
    ser = Service_Category.objects.get(id=pid)
    if request.method == "POST":
        n = request.POST['cat']
        try:
            i = request.FILES['image']
            ser.image = i
            ser.save()
        except:
            pass
        de = request.POST['desc']
        ser.category = n
        ser.desc = de
        ser.save()
        error=True
    d = {'error':error,'ser':ser}
    return render(request,'edit_service.html',d)

def View_Service(request):

    ser = Service_Category.objects.all()
    d = {'ser':ser}
    return render(request,'view_service.html',d)

def View_City(request):
    
    ser = City.objects.all()
    d = {'ser':ser}
    return render(request,'view_city.html',d)

def accept_confirmation(request,pid):
    ser = Order.objects.get(id=pid)
    sta = Status.objects.get(status='Accept')
    ser.status = sta
    ser.save()
    return redirect('service_order')

def confirm_message(request,pid):
    ser = Contact.objects.get(id=pid)
    sta = Status.objects.get(status='read')
    ser.status = sta
    ser.save()
    return redirect('new_message')

def delete_service(request,pid):
    ser = Service_Category.objects.get(id=pid)
    ser.delete()
    return redirect('view_service')

def delete_city(request,pid):
    ser = City.objects.get(id=pid)
    ser.delete()
    return redirect('view_city')

def delete_admin_order(request,pid):
    ser = Order.objects.get(id=pid)
    ser.delete()
    return redirect('admin_order')

def delete_Booking(request,pid):
    ser = Order.objects.get(id=pid)
    ser.delete()
    return redirect('customer_order')

def delete_service_man(request,pid):
    ser = Service_Man.objects.get(id=pid)
    ser.delete()
    return redirect('all_service_man')

def delete_customer(request,pid):
    ser = Customer.objects.get(id=pid)
    ser.delete()
    return redirect('all_customer')

def Change_status(request,pid):
    
    error = False
    pro1 = Service_Man.objects.get(id=pid)
    if request.method == "POST":
        stat = request.POST['stat']
        sta = Status.objects.get(status=stat)
        pro1.status=sta
        pro1.save()
        error=True
    d = {'pro':pro1,'error':error}
    return render(request,'status.html',d)

def Order_status(request,pid):
    
    error = False
    pro1 = Order.objects.get(id=pid)
    if request.method == "POST":
        stat = request.POST['stat']
        sta = Status.objects.get(status=stat)
        pro1.status=sta
        pro1.save()
        error=True
    d = {'pro':pro1,'error':error}
    return render(request,'order_status.html',d)

def Order_detail(request,pid):

    pro1 = Order.objects.get(id=pid)
    d = {'pro':pro1}
    return render(request,'order_detail.html',d)

def service_man_detail(request,pid):
    
    pro1 = Service_Man.objects.get(id=pid)
    d = {'pro':pro1}
    return render(request,'service_man_detail.html',d)

def search_cities(request):
    error=""
    try:
        user = User.objects.get(id=request.user.id)
        error = ""
        try:
            sign = Customer.objects.get(user=user)
            error = "pat"
        except:
            pass
    except:
        pass
   
    terror=False
    pro=""
    car = City.objects.all()
    count1=0
    car1 = Service_Category.objects.all()
    c=""
    c1=""
    if request.method=="POST":
        c=request.POST['city']
        c1 = request.POST['cat']
        ser = City.objects.get(city=c)
        ser1 = Service_Category.objects.get(category=c1)
        pro = Service_Man.objects.filter(service_name=ser1,city=ser)
        for i in pro:
            count1+=1
        terror = True
    d = {'c':c,'c1':c1,'count1':count1,'car1':car1,'car':car,'order':pro,'error':error,'terror':terror}
    return render(request,'search_cities.html',d)

def search_services(request):

    error=False
    pro=""
    car = Service_Category.objects.all()
    c=""
    if request.method=="POST":
        c=request.POST['cat']
        ser = Service_Category.objects.get(category=c)
        pro = Service_Man.objects.filter(service_name=ser)
        error=True
    d = {'service':c,'car':car,'order':pro,'error':error}
    return render(request,'search_services.html',d)

def new_message(request):
    
    sta = Status.objects.get(status='unread')
    pro1 = Contact.objects.filter(status=sta)
    d = {'ser':pro1}
    return render(request,'new_message.html',d)

def read_message(request):

    sta = Status.objects.get(status='read')
    pro1 = Contact.objects.filter(status=sta)
    d = {'ser':pro1}
    return render(request,'read_message.html',d)



def customer_service_search(request):
    if request.method == 'GET':
        form = CustomerServiceSearchForm(request.GET)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            print(category)
            # services = Service_Category.objects.filter(category__icontains=category)
            services = Service_Category.objects.filter(category__icontains=category)
            print(services)
            if services:
                return render(request, 'search_results.html', {'services': services})
            else:
                error_message = "No services found for the provided category"
                return render(request, 'search_results.html', {'form': form, 'error_message': error_message})
        else:
            error_message = "Invalid search criteria."
            return render(request, 'search_results.html', {'form': form, 'error_message': error_message})
    else:
        form = CustomerServiceSearchForm()
        return render(request, 'search_results.html', {'form': form})
    
# Forgot password
    
def generate_otp(length=6):
    """Generate a random OTP of specified length."""
    characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))    
    
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return HttpResponse("No user with this email exists.")
        
        # Generate OTP
        otp = generate_otp()

        # Update user's profile with OTP (You might want to create a profile model)
        user.profile.otp = otp
        user.profile.save()

        # Send OTP via email
        subject = 'Password Reset OTP'
        message = f'Your OTP for password reset is: {otp}'
        from_email = 'chinchuofficialweb@gmail.com'  # Update this with your email
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        return HttpResponse("An OTP has been sent to your email. Please check your inbox.")
    else:
        return render(request, 'forgot_password.html')
    


# Razorpay

def create_order(request):
    if request.method == 'POST':
        # Retrieve necessary data from the form
        service_id = request.POST.get('service_id')
        customer_id = request.POST.get('customer_id')
        amount = request.POST.get('amount')

        # Create an order in your database
        order = Order.objects.create(
            service_id=service_id,
            customer_id=customer_id,
            amount=amount
        )

        # Initialize Razorpay client with your API keys
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        # Create Razorpay order
        razorpay_order = client.order.create({
            'amount': int(amount) * 100,  # Amount in paisa
            'currency': 'INR',
            'receipt': str(order.id),  # Unique ID for the order
            'payment_capture': '1'  # Auto capture payment
        })

        # Redirect user to Razorpay checkout page
        return render(request, 'checkout.html', {'order': razorpay_order})

    return render(request, 'create_order.html')

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        # Get the Razorpay order ID and payment ID from the request
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')

        # Fetch the corresponding order from your database
        order = Order.objects.get(id=razorpay_order_id)

        # Update the order status as paid
        order.report_status = 'Payment Successful'
        order.save()

        return render(request, 'payment_success.html')

    return redirect('home')  # Redirect to home page if the request is not a POST request

@csrf_exempt
def payment_failure(request):
    if request.method == 'POST':
        # Get the Razorpay order ID and payment ID from the request
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')

        # Fetch the corresponding order from your database
        order = Order.objects.get(id=razorpay_order_id)

        # Update the order status as failed
        order.report_status = 'Payment Failed'
        order.save()

        return render(request, 'payment_failure.html')

    return redirect('home')