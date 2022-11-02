from email import message
from multiprocessing import context
from django.shortcuts import render, redirect,HttpResponse
from .models import Package, Student, Agent, book, Travel_mode, Photographer, Login, Message
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .forms import AgentSignUpForm, PackageForm, UserSignUpForm, AgentSignUpForm, AgentDetailForm, PhotographerSignUpForm, PhotographerDetailForm
from django.contrib.auth.decorators import login_required
from .decorators import agent_only, customer_only, photographer_only, admin_only
from django.utils import timezone as tz
from django.db.models import Q


# Create your views here.


def padmin(request):
    ag = Agent.objects.all()
    ph = Photographer.objects.all()
    us = Student.objects.filter(is_customer=True)

    context = {

        'ag': ag,
        'ph': ph,
        'us': us

    }
    return render(request, 'admin.html', context)


def home(request):
    return render(request, 'home.html')


def index(request):
    if request.user.is_authenticated and request.user.is_customer:
        return redirect('package')
    elif request.user.is_authenticated and request.user.is_agent:
        return redirect('agent_packages')
    elif request.user.is_authenticated and request.user.is_photographer:
        return redirect('profileview')

    return render(request, 'index.html')


def viewmore(request):
    return render(request, 'view_more.html')


def event1(request):
    return render(request, 'event1.html')


def event2(request):
    return render(request, 'event2.html')


def event3(request):
    return render(request, 'event3.html')


def event4(request):
    return render(request, 'event4.html')


def user_signup(request):
    form = UserSignUpForm

    context = {

        'form': form
    }
    if request.method == 'POST':
        form = UserSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('package')
        else:
            messages.error(request, 'An error occurred during registration')
            return redirect('signup')
    else:
        return render(request, "signup.html", context)


def agent_signup(request):
    profile_form = AgentSignUpForm
    detail_form = AgentDetailForm
    context = {
        'profile_form': profile_form,
        'detail_form': detail_form
    }
    if request.method == 'POST':
        profile_form = AgentSignUpForm(request.POST)
        detail_form = AgentDetailForm(request.POST)
        if all((profile_form.is_valid(), detail_form.is_valid())):
            profile = profile_form.save()
            detail = detail_form.save(commit=False)
            detail.User = profile
            detail.save()
            return redirect('agent_packages')
        else:
            messages.error(request, 'An error occurred during registration')
            return redirect('agent_signup')

    return render(request, "agent_signup.html", context)


def photographer_signup(request):
    profile_form = PhotographerSignUpForm
    detail_form = PhotographerDetailForm
    context = {
        'profile_form': profile_form,
        'detail_form': detail_form
    }
    if request.method == 'POST':
        profile_form = PhotographerSignUpForm(request.POST)
        detail_form = PhotographerDetailForm(request.POST)
        if all((profile_form.is_valid(), detail_form.is_valid())):
            profile = profile_form.save()
            detail = detail_form.save(commit=False)
            detail.User = profile
            detail.save()
            return redirect('profileview')
        else:
            messages.error(request, 'An error occurred during registration')
            return redirect('photographer_signup')

    return render(request, "photographer_signup.html", context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect('package')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = Student.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            messages.error(
                request, 'Username OR password is  not correct ,recheck and try again')
            return redirect('login')
        if user.is_customer == True:
            log = Login()
            log.username = request.POST['username']
            log.password = request.POST['password']
            log.usertype = 'student'
            log.save()
            return redirect('package')
        elif user.is_agent == True:
            ob = Agent.objects.get(email=user.email)
            if ob.status == 'accepted':
                log = Login()
                log.username = request.POST['username']
                log.password = request.POST['password']
                log.usertype = 'agent'
                log.save()
                return redirect('agent_packages')
            else:
                messages.error(request, 'You are not accepted by admin')
                return render(request, 'login.html')
        elif user.is_photographer == True:
            log = Login()
            log.username = request.POST['username']
            log.password = request.POST['password']
            log.usertype = 'photographer'
            log.save()
            return redirect('profileview')
        elif user.is_admin == True:
            log = Login()
            log.username = request.POST['username']
            log.password = request.POST['password']
            log.usertype = 'admin'
            log.save()
            return redirect('padmin')

    return render(request, 'login.html')


def logoutUser(request):
    logout(request)
    return redirect('index')


def is_valid_queryparam(param):
    return param != '' and param is not None


@login_required(login_url='login')
@customer_only
def package(request):
    today = tz.localtime(tz.now()).date()

    packages = Package.objects.filter(ddate__gt=today)
    packages = packages.filter(slots__gt=0)
    agents = Agent.objects.all()
    destination = request.GET.get('destination')
    departure = request.GET.get('departure')
    min_cost = request.GET.get('min_cost')
    max_cost = request.GET.get('max_cost')
    min_date = request.GET.get('min_date')
    max_date = request.GET.get('max_date')
    department = request.GET.get('department')
    agent = request.GET.get('agent')
    min_dur = request.GET.get('min_dur')
    max_dur = request.GET.get('max_dur')
    type = request.GET.get('type')

    if is_valid_queryparam(destination):
        packages = packages.filter(Location__icontains=destination)

    if is_valid_queryparam(departure):
        packages = packages.filter(dloc__icontains=departure)
    if is_valid_queryparam(min_cost):
        packages = packages.filter(cost__gte=min_cost)
    if is_valid_queryparam(max_cost):
        packages = packages.filter(cost__lte=max_cost)
    if is_valid_queryparam(min_date):
        packages = packages.filter(ddate__gte=min_date)
    if is_valid_queryparam(max_date):
        packages = packages.filter(ddate__lte=max_date)
    if is_valid_queryparam(department) and agent != 'Choose...':
        packages = packages.filter(Department__icontains=department)
    if is_valid_queryparam(agent) and agent != 'Choose...':
        packages = packages.filter(agent__name=agent)
    if is_valid_queryparam(min_dur):
        packages = packages.filter(duration__gte=min_dur)
    if is_valid_queryparam(max_dur):
        packages = packages.filter(duration__lte=max_dur)
    if is_valid_queryparam(type) and type != 'Choose...':
        packages = packages.filter(mode__contains=type)
    # # if is_valid_queryparam(type) and type != 'Choose...':
    # #     packages = packages.filter(mode=type)

    user = request.user
    ob = Student.objects.get(username=user)
    context = {
        'packages': packages,
        'agents': agents,
        'pack': ob
    }
    return render(request, 'contents.html', context)


@login_required(login_url='login')
@customer_only
def package_details(request, pk):
    package = Package.objects.get(id=pk)
    context = {'package': package}
    if request.method == "POST":

        nos = int(request.POST.get('nos'))
        bord = request.POST.get('station')
        if nos >= 1:
            price = nos * package.cost
            user = request.user
            package_name = package
            agent_name = package.agent
            books = book.objects.create(user=user, package=package_name, price=price,
                                        nos=nos, agent=agent_name, boarding=bord, status=True)
            package.slots = package.slots - nos
            if request.user not in package.users.all():
                package.users.add(request.user)
            package.save()
            request.session['book_id'] = books.id

            return redirect('booking_success')
        else:
            messages.error(request, 'An error occured')

    return render(request, 'package_details.html', context)


@login_required(login_url='login')
@customer_only
def booking_success(request):
    bookid = request.session['book_id']
    order = book.objects.get(id=bookid)
    context = {
        'order': order
    }

    return render(request, 'booking_success.html', context)


@login_required(login_url='login')
@customer_only
def bookinglist(request):
    user = request.user
    order = book.objects.filter(user=user)
    # package=Package.objects.filter()

    context = {
        'order': order,

    }

    return render(request, 'bookinglist.html', context)


@login_required(login_url='login')
@customer_only
def cancel_booking(request, pk):
    ord = book.objects.get(id=pk)
    package = Package.objects.get(title=ord.package)
    if request.method == 'POST':
        nos = int(request.POST.get('nos'))
        package.slots = package.slots + nos
        print(package)
        print(package.slots)
        package.save()
        ord.nos = ord.nos - nos
        print(ord.nos)
        if ord.nos == 0:
            ord.status = False
        ord.save()
        return redirect('bookinglist')

    context = {
        'ord': ord
    }

    return render(request, 'bookingcancel.html', context)

@login_required(login_url='login')
@customer_only
def payment(request):
    return render(request, 'payment.html')

def pay(request):
    return HttpResponse("Payment successfully completed.....")



@login_required(login_url='login')
@agent_only
def agent_packages(request):
    user = request.user
    age = Agent.objects.get(User=user)
    pack = Package.objects.filter(agent=age)

    context = {
        'pack': pack,

    }
    return render(request, "agent_packages.html", context)


@login_required(login_url='login')
@agent_only
def package_status(request, pk):
    package = Package.objects.get(id=pk)
    ps = package.users.all()
    print(ps)

    orders = book.objects.filter(package=package)

    x = 0
    for ord in orders:
        x = x + ord.nos

    context = {
        'ps': ps,
        'package': package,
        'x': x,

    }

    return render(request, "packagestatus.html", context)


def user_detail(request, pk):
    u = Student.objects.get(id=pk)

    context = {
        'u': u
    }
    return render(request, "userdetail.html", context)


@login_required(login_url='login')
@agent_only
def create_package(request):
    form = PackageForm
    context = {
        'form': form
    }
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            u = request.user
            age = Agent.objects.get(User=u)
            p.agent = age

            print(age)
            print(p.agent)
            p.save()
            return redirect('agent_packages')
        else:
            print(form.errors)
            return HttpResponse(form.errors.values())

            # messages.error(request, 'An error occurred during registration')
            # return redirect('create')
    return render(request, "create_package.html", context)


@login_required(login_url='login')
@agent_only
def package_edit(request, pk):
    package = Package.objects.get(id=pk)
    form = PackageForm(request.POST or None, instance=package)

    if request.method == 'POST':
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect('agent_packages')
        else:
            messages.error(request, 'An error occurred during editing')
            return redirect('agent_packages')

    context = {
        'package': package,
        'form': form
    }
    return render(request, "create_package.html", context)


@login_required(login_url='login')
@photographer_only
def viewagent(request):
    data = Agent.objects.all()
    content = {

        'profile': data

    }
    return render(request, "agent_view.html", content)


@login_required(login_url='login')
@photographer_only
def profileview(request):
    user = request.user
    data = Photographer.objects.filter(email=user.email)
    content = {

        'profile': data

    }
    return render(request, "profile.html", content)


@login_required(login_url='login')
@agent_only
def viewphoto(request):
    data = Photographer.objects.all()
    content = {

        'profile': data

    }
    return render(request, "photo_view.html", content)


@login_required(login_url='login')
@photographer_only
def profile_edit(request, pk):
    person = Photographer.objects.get(id=pk)
    detail_form = PhotographerDetailForm(request.POST or None, instance=person)

    if request.method == 'POST':
        if request.method == 'POST':
            if detail_form.is_valid():
                detail_form.save()
                return redirect('profileview')

        else:
            messages.error(request, 'An error occurred during editing')
            return redirect('profileview')

    context = {
        'person': person,
        'detail_form': detail_form
    }
    return render(request, "photographer_signup.html", context)


def accept(request, pk):
    ag = Agent.objects.get(phone=pk)
    ag.status = 'accepted'
    ag.save()
    return redirect('padmin')


def reject(request, pk):
    ag = Agent.objects.get(phone=pk)
    ag.status = 'rejected'
    ag.save()
    return redirect('padmin')


def forgot(request):
    return render(request, 'Resetpassword.html')


def pwdset(request):
    if request.method == 'POST':
        usr = request.POST.get['username']
        pswd = request.POST.get['password']
        pswd2 = request.POST.get['password2']
        print(usr)
        ob = Student.objects.get(username=usr)
        if pswd == pswd2:
            ob.password = pswd
            ob.update(password=pswd)
            return redirect('login_page')
        else:
            return render(request, 'Resetpassword.html')
    return render(request, 'Resetpassword.html')

def agencies(request):
    obj = Agent.objects.all()
    context={
        'obj':obj
    }
    return render(request, 'agencylist.html', context)

def agentlink(request, nm):
    obj = Agent.objects.get(name=nm)
    context = {
        'obj': obj
    }
    return render(request, 'agency.html', context)

def chat(request):

    if request.method == 'POST':
        ob = Message()
        ob.user = request.POST['username']
        ob.agent= request.POST['agent']
        ob.message = request.POST['chat']
        ob.save()
        messages.success(request, 'sent successfully')
        return redirect('chat')
    return render(request, 'chat.html', )

def chatview(request, nm):
    msg = Message.objects.filter(user=nm)
    context={
        'msg':msg
    }
    return render(request, 'achat.html', context)

def reply(request, nm):
    msg = Message.objects.get(id=nm)
    context={
        'msg':msg
    }
    return render(request,'reply.html',context)

def areply(request, nm):
    ob = Message.objects.get(id=nm)
    if request.method == 'POST':
        ob.reply = request.POST['chat']
        ob.save()
        messages.success(request, 'sent successfully')
    return redirect('chatview', ob.agent)

def replyview(request, nm):
    msg = Message.objects.filter(user=nm)
    context={
        'msg':msg
    }
    return render(request, 'viewreply.html', context)




