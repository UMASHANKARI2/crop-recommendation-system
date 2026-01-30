from django.shortcuts import render, redirect  
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, CropRecommendationForm
from .models import CropHistory
import pickle
import os
from django.http import JsonResponse
from django.db.models import Count, Avg

# Load the model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'Recomender', 'RandomForest.pkl')

with open(MODEL_PATH, 'rb') as file:
    model = pickle.load(file)

def index(request):
    return render(request, 'Recomender/index.html')

def about(request):
    return render(request, 'Recomender/about_us.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'Recomender/signup.html', {'form': form})

@login_required
def recommend_crop(request):
    if request.method == 'POST':
        form = CropRecommendationForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            # Soil type encoding mapping (matches the training data encoding)
            soil_type_mapping = {
                'Chalky': 0,
                'Clay': 1,
                'Loam': 2,
                'Peaty': 3,
                'Sandy': 4,
                'Silty': 5,
            }
            soil_type_encoded = soil_type_mapping.get(instance.soil_type, 2)  # Default to Loam (2)
            # Create prediction data with all 8 features
            user_data = [instance.N, instance.P, instance.K, instance.temperature, instance.humidity, instance.ph, instance.rainfall, soil_type_encoded]
            predicted_crop = model.predict([user_data])[0]
            instance.recommended_crop = predicted_crop
            instance.save()
            return render(request, 'Recomender/recommendation_result.html', {'predicted_crop': predicted_crop})
    else:
        form = CropRecommendationForm()
    return render(request, 'Recomender/recommend_crop.html', {'form': form})

@login_required
def history(request):
    history = CropHistory.objects.filter(user=request.user)
    return render(request, 'Recomender/history.html', {'history': history})

@login_required
def user_logout(request):
    logout(request)
    return redirect('index')


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Redirect to a homepage or dashboard after login
    else:
        form = LoginForm()
    return render(request, 'Recomender/login.html', {'form': form})


@login_required
def dashboard(request):
    # Overall metrics
    total_recommendations = CropHistory.objects.count()
    recent = CropHistory.objects.select_related('user').order_by('-timestamp')[:10]

    # Aggregation: top recommended crops
    crop_counts = CropHistory.objects.values('recommended_crop').annotate(count=Count('recommended_crop')).order_by('-count')[:10]
    crop_labels = [c['recommended_crop'] for c in crop_counts]
    crop_values = [c['count'] for c in crop_counts]

    # Nutrient averages
    nutrient_avgs = CropHistory.objects.aggregate(
        avg_N=Avg('N'), avg_P=Avg('P'), avg_K=Avg('K'), avg_ph=Avg('ph')
    )

    context = {
        'total_recommendations': total_recommendations,
        'recent': recent,
        'crop_labels': crop_labels,
        'crop_values': crop_values,
        'nutrient_avgs': nutrient_avgs,
    }
    return render(request, 'Recomender/dashboard.html', context)


@login_required
def dashboard_data(request):
    # Return JSON for charts (simple endpoint)
    crop_counts = CropHistory.objects.values('recommended_crop').annotate(count=Count('recommended_crop')).order_by('-count')[:20]
    labels = [c['recommended_crop'] for c in crop_counts]
    values = [c['count'] for c in crop_counts]
    return JsonResponse({'labels': labels, 'values': values})
