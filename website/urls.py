from django.urls import path

from . import views

app_name = 'website'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('dealers/', views.DealersView.as_view(), name='dealers'),
    path('support/', views.SupportView.as_view(), name='support'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('api/vehicle-estimate/', views.VehicleEstimateView.as_view(), name='vehicle_estimate'),
    path('api/fetch-vehicle/', views.FetchVehicleDetailsView.as_view(), name='fetch_vehicle'),
    path('api/calculate-estimate/', views.CalculatePriceEstimateView.as_view(), name='calculate_estimate'),
    path('api/capture-lead/', views.CaptureLeadView.as_view(), name='capture_lead'),
    path('api/dealer-lead/', views.CaptureDealerLeadView.as_view(), name='dealer_lead'),
    path('api/support-enquiry/', views.SupportEnquiryView.as_view(), name='support_enquiry'),
]
