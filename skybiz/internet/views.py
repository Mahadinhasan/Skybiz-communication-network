from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,Group
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from .models import Package, ContactMessage, BusinessQuoteRequest, UserProfile, SpeedTestResult, Branch, NewsTicker
from .forms import AdminLoginForm, AdminRegistrationForm, BranchForm
from django.db.models import Avg
from datetime import timedelta
from django.utils import timezone
import logging
import speedtest
from django.views.decorators.csrf import csrf_exempt

# Ensure user groups exist
Group.objects.get_or_create(name='Staff')
Group.objects.get_or_create(name='User')

# Configure logging
logger = logging.getLogger(__name__)

def home(request):
    popular_packages = Package.objects.filter(is_popular=True)[:12]
    return render(request, 'home.html', {
        'popular_packages': popular_packages,
    })

def packages(request):
    residential_packages = Package.objects.filter(package_type='residential')
    business_packages = Package.objects.filter(package_type='business')
    return render(request, 'packages.html', {
        'residential_packages': residential_packages,
        'business_packages': business_packages
    })

def services(request):
    return render(request,'services.html')

def news_ticker(request):
    news = NewsTicker.objects.filter(is_active=True)
    return {'news_ticker': news}

def business(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        contact_person = request.POST.get('contact_person')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        bandwidth = request.POST.get('bandwidth')
        requirements = request.POST.get('requirements')
        
        BusinessQuoteRequest.objects.create(
            company_name=company_name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            bandwidth=bandwidth,
            requirements=requirements
        )
        messages.success(request, 'Your quote request has been submitted successfully!')
        return redirect('business')
    
    return render(request, 'business.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Save to database (without phone field)
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        if phone:
            try:
                # Send WhatsApp message via Twilio
                twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                whatsapp_message = f"New contact message from {name} ({email}, {phone}): {message}"
                twilio_client.messages.create(
                    body=whatsapp_message,
                    from_=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',
                    to=f'whatsapp:{phone}'
                )
                logger.info(f"WhatsApp message sent to {phone}")
            except Exception as e:
                logger.error(f"Failed to send WhatsApp message: {str(e)}")
                messages.error(request, f"Failed to send WhatsApp message: {str(e)}")
                return redirect('contact')
        # Only mail feature enabled, WhatsApp feature is temporarily disabled
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
    branches = Branch.objects.filter(is_active=True)
    return render(request, 'contact.html',{'branches': branches})

@csrf_exempt
def home_speed_test(request):
    if request.method == 'POST':
        try:
            # Import inside function - critical fix for some hosting environments
            s = speedtest.Speedtest()
            s.get_servers()
            s.get_best_server()
            
            # Fast test - only 8-12 seconds
            download = round(s.download() / 1_000_000, 2)
            upload = round(s.upload() / 1_000_000, 2)
            ping = round(s.results.ping, 1)
            
            server = s.results.server
            
            # Save result
            SpeedTestResult.objects.create(
                user=request.user if request.user.is_authenticated else None,
                download_speed=download,
                upload_speed=upload,
                latency=ping,
                ip_address=request.META.get('REMOTE_ADDR', 'Unknown')
            )
            
            return JsonResponse({
                'success': True,
                'download': download,
                'upload': upload,
                'ping': ping,
                'server': server.get('sponsor', 'Local Server'),
                'location': f"{server.get('name', '')}, {server.get('country', '')}"
            })
            
        except Exception as e:
            logger.error(f"Speed test failed: {e}")
            return JsonResponse({
                'success': False,
                'error': 'No internet connection detected'
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def faq(request):
    return render(request, 'faq.html')

@login_required
def admin_panel(request):#Admin_panel feature
    if not request.user.is_staff:
        messages.error(request, 'You must be an admin to access this page.')
        return redirect('admin_panel')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, 'Logged in successfully.')
            else:
                messages.error(request, 'Invalid credentials or not an admin user.')
            return redirect('admin_panel')
        
        elif action == 'logout':
            logout(request)
            messages.success(request, 'Logged out successfully.')
            return redirect('home')
        
        # Add User
        elif action == 'add_user':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = request.POST.get('role', 'superadmin')  # Default to superadmin
            
            try:
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists.')
                else:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    
                    if role == 'superadmin':
                        user.is_superuser = True
                        user.is_staff = True
                    else:  # user
                        user.is_superuser = False
                        user.is_staff = False
                    user.save()
                    
                    UserProfile.objects.get_or_create(user=user)
                    messages.success(request, f'User {username} added successfully as Super Admin.')
            except Exception as e:
                messages.error(request, f'Failed to add user: {str(e)}')
        
        # Edit User
        elif action == 'edit_user':
            user_id = request.POST.get('user_id')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = request.POST.get('role')
            
            try:
                user = User.objects.get(id=user_id)
                user.username = username
                user.email = email
                if password:
                    user.set_password(password)
                
                if role == 'superadmin':
                    user.is_superuser = True
                    user.is_staff = True
                else:
                    user.is_superuser = False
                    user.is_staff = False
                user.save()
                
                messages.success(request, f'User {username} updated successfully.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
            except Exception as e:
                messages.error(request, f'Failed to update user: {str(e)}')
        
        # Delete User
        elif action == 'delete_user':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                username = user.username
                user.delete()
                messages.success(request, f'User {username} deleted successfully.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
            except Exception as e:
                messages.error(request, f'Delated your account: {str(e)}')    
        
        elif action == 'save_user':
            user_id = request.POST.get('user_id')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            try:
                if user_id:
                    user = User.objects.get(id=user_id)
                    user.username = username
                    user.email = email
                    if password:
                        user.set_password(password)
                    user.save()
                    profile = user.userprofile
                    profile.save()
                    messages.success(request, 'User updated successfully.')
                else:
                    if User.objects.filter(username=username).exists():
                        messages.error(request, 'Username already exists.')
                    else:
                        user = User.objects.create_user(username=username, email=email, password=password)
                        profile = UserProfile.objects.create(user=user)
                        messages.success(request, 'User added successfully.')
            except Exception as e:
                messages.error(request, f'Failed to save user: {str(e)}')
        
        elif action == 'save_package':
            package_id = request.POST.get('package_id')
            name = request.POST.get('name')
            package_type = request.POST.get('package_type')
            download_speed = request.POST.get('download_speed')
            upload_speed = request.POST.get('upload_speed')
            price = request.POST.get('price')
            data_limit = request.POST.get('data_limit')
            features = request.POST.get('features')
            is_popular = request.POST.get('is_popular') == 'on'
            
            try:
                if package_id:
                    package = Package.objects.get(id=package_id)
                    package.name = name
                    package.package_type = package_type
                    package.download_speed = download_speed
                    package.upload_speed = upload_speed
                    package.price = price
                    package.data_limit = data_limit
                    package.features = features
                    package.is_popular = is_popular
                    package.save()
                    messages.success(request, 'Package updated successfully.')
                else:
                    Package.objects.create(
                        name=name,
                        package_type=package_type,
                        download_speed=download_speed,
                        upload_speed=upload_speed,
                        price=price,
                        data_limit=data_limit,
                        features=features,
                        is_popular=is_popular
                    )
                    messages.success(request, 'Package added successfully.')
            except Exception as e:
                messages.error(request, f'Failed to save package: {str(e)}')
        
        elif action == 'delete_package':
            try:
                package_id = request.POST.get('package_id')
                Package.objects.get(id=package_id).delete()
                messages.success(request, 'Package deleted successfully.')
            except Package.DoesNotExist:
                messages.error(request, 'Package not found.')

        elif action =='delete_all_messages':
            if request.method == "POST":
               action = request.POST.get("action")
            # ...existing code...
            if action == "delete_all_messages":
                   ContactMessage.objects.all().delete()
                   messages.success(request, "All contact messages have been deleted.")
            return redirect("admin_panel")
    # ...existing code...
        
        elif action == 'send_reply':
            message_id = request.POST.get('message_id')
            reply_text = request.POST.get('reply_text')
            try:
                message = ContactMessage.objects.get(id=message_id)
                if not reply_text:
                    messages.error(request, 'Reply text cannot be empty.')
                else:
                    subject = f"Re: {message.subject}"
                    from_email = settings.DEFAULT_FROM_EMAIL
                    recipient_list = [message.email]
                    try:
                        send_mail(
                            subject=subject,
                            message=reply_text,
                            from_email=from_email,
                            recipient_list=recipient_list,
                            fail_silently=False,
                        )
                        message.reply_sent = True
                        message.save()
                        messages.success(request, f'Reply sent successfully to {message.email}.')
                    except Exception as e:
                        messages.error(request, f'Failed to send reply: {str(e)}')
            except ContactMessage.DoesNotExist:
                messages.error(request, 'Message not found.')
            return redirect('admin_panel')
        
        # elif action == 'add_carousel':
        #     if request.user.is_authenticated and request.user.is_staff:
        #         form = ImageUploadForm(request.POST, request.FILES)
        #         if form.is_valid():
        #             try:
        #                 carousel_image = form.save(commit=False)
        #                 carousel_image.uploaded_by = request.user
        #                 # (max 5MB)
        #                 if carousel_image.image.size > 5 * 1024 * 1024:
        #                     messages.error(request, 'Image file size exceeds 5MB limit.')
        #                 else:
        #                     carousel_image.save()
        #                     messages.success(request, 'Carousel image added successfully.')
        #             except Exception as e:
        #                 messages.error(request, f'Failed to save image: {str(e)}')
        #         else:
        #             for field, errors in form.errors.items():
        #                 for error in errors:
        #                     messages.error(request, f'Error in {field}: {error}')
        #         return redirect('admin_panel')
        
        # elif action == 'edit_carousel':
        #     if request.user.is_authenticated and request.user.is_staff:
        #         carousel_id = request.POST.get('carousel_id')
        #         try:
        #             carousel_image = CarouselImage.objects.get(id=carousel_id)
        #             form = ImageUploadForm(request.POST, request.FILES, instance=carousel_image)
        #             if form.is_valid():
        #                 if 'image' in request.FILES and request.FILES['image'].size > 5 * 1024 * 1024:
        #                     messages.error(request, 'Image file size exceeds 5MB limit.')
        #                 else:
        #                     form.save()
        #                     messages.success(request, 'Carousel image updated successfully.')
        #             else:
        #                 for field, errors in form.errors.items():
        #                     for error in errors:
        #                         messages.error(request, f'Error in {field}: {error}')
        #         except CarouselImage.DoesNotExist:
        #             messages.error(request, 'Carousel image not found.')
        #         return redirect('admin_panel')
        
        # elif action == 'delete_carousel':
        #     if request.user.is_authenticated and request.user.is_staff:
        #         carousel_id = request.POST.get('carousel_id')
        #         try:
        #             carousel_image = CarouselImage.objects.get(id=carousel_id)
        #             # Delete the image file from storage
        #             if carousel_image.image:
        #                 if os.path.isfile(carousel_image.image.path):
        #                     os.remove(carousel_image.image.path)
        #             carousel_image.delete()
        #             messages.success(request, 'Carousel image deleted successfully.')
        #         except CarouselImage.DoesNotExist:
        #             messages.error(request, 'Carousel image not found.')
        #         return redirect('admin_panel')
        elif action == 'delete_all_speed_tests':
                SpeedTestResult.objects.all().delete()
                messages.success(request, 'All speed test results have been deleted.')
                return redirect('admin_panel')
        elif action == 'add_branch':
            if request.user.is_authenticated and request.user.is_staff:
                form = BranchForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Branch added successfully.')
                else:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f'Error in {field}: {error}')
                return redirect('admin_panel')
        
        elif action == 'edit_branch':
            if request.user.is_authenticated and request.user.is_staff:
                branch_id = request.POST.get('branch_id')
                try:
                    branch = Branch.objects.get(id=branch_id)
                    form = BranchForm(request.POST, instance=branch)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Branch updated successfully.')
                    else:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Error in {field}: {error}')
                except Branch.DoesNotExist:
                    messages.error(request, 'Branch not found.')
                return redirect('admin_panel')
        
        elif action == 'delete_branch':
            if request.user.is_authenticated and request.user.is_staff:
                branch_id = request.POST.get('branch_id')
                try:
                    Branch.objects.get(id=branch_id).delete()
                    messages.success(request, 'Branch deleted successfully.')
                except Branch.DoesNotExist:
                    messages.error(request, 'Branch not found.')
                return redirect('admin_panel')
        elif action == 'save_news':
            news_id = request.POST.get('news_id')
            message = request.POST.get('message')
            if news_id:
                news = NewsTicker.objects.get(id=news_id)
                news.message = message
                news.save()
                messages.success(request, 'News updated!')
            else:
                NewsTicker.objects.create(message=message)
                messages.success(request, 'News added!')
                return redirect('admin_panel')
        elif action == 'delete_news':
            news_id = request.POST.get('news_id')
            NewsTicker.objects.filter(id=news_id).delete()
            messages.success(request, 'News deleted!')
            return redirect('admin_panel')    

        return redirect('admin_panel')

    users = User.objects.all()
    all_packages = Package.objects.all()
    news_items = NewsTicker.objects.all()
    messages_list = ContactMessage.objects.all()
    business_requests = BusinessQuoteRequest.objects.all()
    speed_test_results = SpeedTestResult.objects.all()
    # carousel_images = CarouselImage.objects.all().order_by('-created_at')
    branches = Branch.objects.all().order_by('-created_at')
    # image_upload_form = ImageUploadForm()
    branch_form = BranchForm()
    return render(request, 'admin_panel.html', {
        'users': users,
        'all_packages': all_packages,
        'messages': messages_list,
        'news_ticker': news_items,
        'business_requests': business_requests,
        'speed_test_results': speed_test_results,
        # 'carousel_images': carousel_images,
        'branches': branches,
        # 'image_upload_form': image_upload_form,
        'branch_form': branch_form
    })

def admin_dashboard(request):#admin_dashboard feature
    login_form = AdminLoginForm()
    registration_form = AdminRegistrationForm()
    # image_upload_form = ImageUploadForm()
    branch_form = BranchForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'login':
            login_form = AdminLoginForm(request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_staff:
                        login(request, user)
                        messages.success(request, 'Logged in successfully.')
                    else:
                        messages.error(request, 'You must be an admin to access this dashboard.')
                else:
                    messages.error(request, 'Invalid username or password.')
                return redirect('dashboard')
        
        elif action == 'logout':
            logout(request)
            messages.success(request, 'Logged out successfully.')
            return redirect('home')
        
        # elif action == 'register':
        #     registration_form = AdminRegistrationForm(request.POST)
        #     if registration_form.is_valid():
        #         username = registration_form.cleaned_data['username']
        #         email = registration_form.cleaned_data['email']
        #         password = registration_form.cleaned_data['password']
        #         if User.objects.filter(username=username).exists():
        #             messages.error(request, 'Username already exists.')
        #         elif User.objects.filter(email=email).exists():
        #             messages.error(request, 'Email already exists.')
        #         else:
        #             user = User.objects.create_user(
        #                 username=username,
        #                 email=email,
        #                 password=password,
        #                 # is_staff=True,
        #                 # is_active=True
        #             )
        #             UserProfile.objects.create(user=user)
        #             messages.success(request, 'Admin account created successfully. Please log in.')
        #             return redirect('dashboard')
        
        # elif action == 'upload_image':
        #     if request.user.is_authenticated and request.user.is_staff:
        #         # image_upload_form = ImageUploadForm(request.POST, request.FILES)
        #         if image_upload_form.is_valid():
        #             image = image_upload_form.save(commit=False)
        #             image.uploaded_by = request.user
        #             image.save()
        #             messages.success(request, 'Image uploaded successfully.')
        #             return redirect('dashboard')
        #         else:
        #             messages.error(request, 'Failed to upload image. Please check the form.')
        #     else:
        #         messages.error(request, 'You must be an admin to upload images.')
        
        elif action == 'save_branch':
            if request.user.is_authenticated and request.user.is_staff:
                branch_id = request.POST.get('branch_id')
                branch_form = BranchForm(request.POST)
                if branch_form.is_valid():
                    if branch_id:
                        branch = Branch.objects.get(id=branch_id)
                        branch_form = BranchForm(request.POST, instance=branch)
                        branch_form.save()
                        messages.success(request, 'Branch updated successfully.')
                    else:
                        branch_form.save()
                        messages.success(request, 'Branch added successfully.')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Failed to save branch. Please check the form.')
            else:
                messages.error(request, 'You must be an admin to manage branches.')
        
        elif action == 'delete_branch':
            if request.user.is_authenticated and request.user.is_staff:
                branch_id = request.POST.get('branch_id')
                Branch.objects.get(id=branch_id).delete()
                messages.success(request, 'Branch deleted successfully.')
                return redirect('dashboard')
            else:
                messages.error(request, 'You must be an admin to delete branches.')
        
        return redirect('dashboard')

    context = {
        'login_form': login_form,
        'registration_form': registration_form,
        # 'image_upload_form': image_upload_form,
        'branch_form': branch_form,
    }

    if request.user.is_authenticated and request.user.is_staff:
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        users_with_packages = UserProfile.objects.filter(package__isnull=False).count()
        total_packages = Package.objects.count()
        residential_packages = Package.objects.filter(package_type='residential').count()
        business_packages = Package.objects.filter(package_type='business').count()
        recent_messages = ContactMessage.objects.order_by('-created_at')[:2]
        recent_business_requests = BusinessQuoteRequest.objects.order_by('-created_at')[:2]
        recent_speed_tests = SpeedTestResult.objects.order_by('-timestamp')[:2]
        speed_tests_total = SpeedTestResult.objects.count()
        avg_download_speed = SpeedTestResult.objects.aggregate(avg_download=Avg('download_speed'))['avg_download'] or 0
        avg_upload_speed = SpeedTestResult.objects.aggregate(avg_upload=Avg('upload_speed'))['avg_upload'] or 0
        avg_latency = SpeedTestResult.objects.aggregate(avg_latency=Avg('latency'))['avg_latency'] or 0
        today = timezone.now().date()
        chart_labels = []
        chart_data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            chart_labels.append(day.strftime('%Y-%m-%d'))
            avg_speed = SpeedTestResult.objects.filter(
                timestamp__date=day
            ).aggregate(avg_download=Avg('download_speed'))['avg_download'] or 0
            chart_data.append(round(avg_speed, 2))

        context.update({
            'total_users': total_users,
            'active_users': active_users,
            'users_with_packages': users_with_packages,
            'total_packages': total_packages,
            'residential_packages': residential_packages,
            'business_packages': business_packages,
            'recent_messages': recent_messages,
            'recent_business_requests': recent_business_requests,
            'recent_speed_tests': recent_speed_tests,
            'speed_tests_total': speed_tests_total,
            'avg_download_speed': round(avg_download_speed, 2),
            'avg_upload_speed': round(avg_upload_speed, 2),
            'avg_latency': round(avg_latency, 2),
            'chart_labels': chart_labels,
            'chart_data': chart_data,
        })

    return render(request, 'admin_dashboard.html', context)
#Creator by Mahadin Hasan