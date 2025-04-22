from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from .models import Task, User, Review, Category
from .forms import TaskForm
from .forms import ReviewForm
from .forms import ReportForm
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.core.paginator import Paginator
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = self.request.build_absolute_uri(
                reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
            )
            self.request.session["reset_link"] = reset_url
        except User.DoesNotExist:
            self.request.session["reset_link"] = None
        return super().form_valid(form)

def index(request):
    tasks = Task.objects.filter(is_completed=False).order_by('-created_at')

    category_id = request.GET.get('category')
    if category_id:
        tasks = tasks.filter(category_id=category_id)

    paginator = Paginator(tasks, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    top_volunteers = User.objects.filter(role='volunteer') \
        .annotate(num_accepted=Count('accepted_tasks')) \
        .order_by('-num_accepted')[:3]

    top_funds = User.objects.filter(role='fund') \
        .annotate(num_tasks=Count('fund_tasks')) \
        .order_by('-num_tasks')[:3]

    top_sponsors = User.objects.filter(role='sponsor') \
        .annotate(num_supported=Count('supported_tasks')) \
        .order_by('-num_supported')[:3]

    return render(request, 'index.html', {
        'tasks': page_obj,
        'categories': categories,
        'top_volunteers': top_volunteers,
        'top_funds': top_funds,
        'top_sponsors': top_sponsors,
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def ratings_view(request):
    users = User.objects.annotate(avg_rating=Avg('received_reviews__rating')).order_by('-avg_rating')
    return render(request, 'ratings.html', {'users': users})

@login_required
def dashboard(request):
    role = request.user.role
    if role == 'volunteer':
        return render(request, 'dashboard/volunteer.html')
    elif role == 'fund':
        tasks = request.user.fund_tasks.all()
        return render(request, 'dashboard/fund.html', {'tasks': tasks})
    elif role == 'sponsor':
        return render(request, 'dashboard/sponsor.html')
    else:
        return redirect('index')
    
@login_required
def create_task(request):
    if request.user.role != 'fund':
        return redirect('dashboard')

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.fund = request.user
            task.save()
            return redirect('dashboard')
    else:
        form = TaskForm()

    return render(request, 'tasks/create_task.html', {'form': form})

@login_required
def accept_task(request, task_id):
    task = Task.objects.get(id=task_id)

    if request.user.role != 'volunteer':
        return redirect('index')

    task.volunteers.add(request.user)
    return redirect('dashboard')

@login_required
def support_task(request, task_id):
    task = Task.objects.get(id=task_id)

    if request.user.role != 'sponsor':
        return redirect('index')

    task.sponsors.add(request.user)
    return redirect('dashboard')

@login_required
def leave_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST, user=request.user)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.save()
            return redirect('dashboard')
    else:
        form = ReviewForm(user=request.user)

    return render(request, 'reviews/leave_review.html', {'form': form})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, author=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ReviewForm(instance=review, user=request.user)

    return render(request, 'reviews/edit_review.html', {'form': form})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, author=request.user)

    if request.method == 'POST':
        review.delete()
        return redirect('dashboard')

    return render(request, 'reviews/delete_review.html', {'review': review})

@login_required
def report_user(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()
            return redirect('dashboard')
    else:
        form = ReportForm()
    return render(request, 'report_user.html', {'form': form})